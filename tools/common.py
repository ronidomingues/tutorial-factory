"""common.py — where the brand kit, the fonts and md2book live on this machine.

Tutorial Factory publishes with **someone's** identity, never with a built-in
one. That identity is a *dependency*, not part of the engine: a folder that
satisfies the `course-factory-brand` contract, dropped into

    tools/course-factory-brand/

The contract is deliberately the same one Course Factory uses. A brand kit is a
repository of its own, and a person who owns one wants it to sign every piece
their factories publish — a tutorial and a course should not disagree about
what the logo is. One kit, many factories.

The engine looks for a kit in this order, and the first hit wins:

1. an explicit path — `--brand <path>` or `TUTORIAL_FACTORY_BRAND=<path>`
   (`COURSE_FACTORY_BRAND` is honoured too, so one exported variable serves
   both factories);
2. `tools/course-factory-brand/BRAND_PATH` — a one-line pointer file naming the
   folder where the kit really lives. This is how a brand kept in its own
   repository, outside this tree, stays wired in without an environment
   variable that every shell has to remember;
3. `tools/course-factory-brand/` itself, when the brand kit was installed
   there (cloned, copied or symlinked — typically a private repository);
4. `tools/course-factory-brand/template/`, the neutral pre-mold that ships
   with this repository, so a fresh clone publishes a real PDF on day one.

A folder is a brand kit when it has `latex/coursebook.sty`. That single file is
the marker: it is the one piece the book cannot be built without.

The same pointer idea answers a second question — **where the documentation
goes**. The default is `documentation/` beside this repository, but the
material almost always belongs somewhere else (a documents folder, a synced
drive, a repository of its own — and it will never ride along to the public
git). `DOCUMENTATION_PATH` at the repository root names that place, once, and
the machine remembers it instead of the person.

See `docs/03-kit-de-marca.md` for the full contract.
"""

import json
import os
import re
import shutil
import sys
from pathlib import Path

# The file that proves a folder is a brand kit.
BRAND_MARKER = Path("latex") / "coursebook.sty"
BRAND_SLOT = "course-factory-brand"
BRAND_TEMPLATE = "template"
BRAND_POINTER = "BRAND_PATH"      # one line: where the kit really lives

# Where the generated documentation lives. Same shape as BRAND_PATH, one level
# up: a one-line file at the repository root.
DOCS_POINTER = "DOCUMENTATION_PATH"
DOCS_DEFAULT = "documentation"
DOCS_LEGACY = "documentacao"      # an accepted spelling, if someone used it

# The two pieces produced for every software, in the order they are written.
# `stem` is the file name without the date; `label` is what the cover prints.
PIECES = {
    "installation": {
        "stem": "installation",
        "label": "Manual de instalação",
        "kind": "instalação",
    },
    "manual": {
        "stem": "manual",
        "label": "Manual de uso",
        "kind": "uso",
    },
}


class Brand:
    """The resolved paths of one brand kit.

    Every attribute is a `Path`. `exists()` says whether this kit can actually
    publish; `report()` prints what is in place and what is missing.
    """

    def __init__(self, root: Path, origin: str = "installed"):
        self.root = root
        self.origin = origin                      # explicit | pointer | installed | template
        self.latex = root / "latex"
        self.book_style = root / BRAND_MARKER
        self.templates = root / "md2book"         # book.base.json
        self.assets = root / "assets"             # logos in PDF, for LaTeX
        self.fonts = root / "fonts"               # optional
        self.env = root / "brand.env"
        self.manual = root / "BRAND-MANUAL.md"
        self.editorial = root / "EDITORIAL-STANDARD.md"

    # ------------------------------------------------------------------ fonts
    def font_spec(self) -> dict:
        """`fonts/fonts.json`, or `{}` when the kit ships no font files.

        A kit without fonts is not broken — it is a kit that uses typefaces
        already installed on the machine (the pre-mold does exactly that, with
        the Latin Modern family that ships with every TeX Live).
        """
        spec = self.fonts / "fonts.json"
        if not spec.is_file():
            return {}
        try:
            return json.loads(spec.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            return {}

    def has_fonts(self) -> bool:
        return bool(self.font_spec().get("families"))

    # ----------------------------------------------------------------- checks
    def exists(self) -> bool:
        return self.book_style.is_file()

    def missing(self) -> list:
        """What the contract requires and this kit does not have.

        Only the book half of the contract is required here: Tutorial Factory
        publishes documents, not slide decks, so a kit without
        `beamerthemecourseslides.sty` still satisfies it.
        """
        required = [
            ("latex/coursebook.sty", self.book_style),
            ("md2book/book.base.json", self.templates / "book.base.json"),
            ("brand.env", self.env),
            ("BRAND-MANUAL.md", self.manual),
        ]
        return [name for name, path in required if not path.is_file()]

    def report(self) -> str:
        lines = ["Brand kit: %s (%s)" % (self.root, self.origin)]
        for name in ("latex", "templates", "assets", "fonts", "env", "manual",
                     "editorial"):
            target = getattr(self, name)
            mark = "ok " if target and target.exists() else "MISSING"
            lines.append("  %-10s %-8s %s" % (name, mark, target))
        gaps = self.missing()
        if gaps:
            lines.append("  contract not satisfied — missing: %s"
                         % ", ".join(gaps))
        return "\n".join(lines)


def tools_dir() -> Path:
    return Path(__file__).resolve().parent


def repo_root() -> Path:
    """The repository that holds `tools/`."""
    return tools_dir().parent


# ------------------------------------------------------------------ brand.env

# A colour value is six hex digits, with or without the leading "#". Anything
# after them is a comment: the values live next to the explanation of what each
# one is for, and that explanation must not leak into the PDF.
RE_HEX = re.compile(r"^#?([0-9A-Fa-f]{6})\b")

COLOR_PREFIX = "BRAND_COLOR_"     # BRAND_COLOR_<latex name> -> \definecolor

# Colours the *converter* uses, not LaTeX: md2book paints the code blocks and
# the accent rule itself, from the JSON, before any .sty is loaded.
CONVERTER_COLORS = {
    "BOOK": {
        "BRAND_BOOK_ACCENT": "cor_destaque",
        "BRAND_BOOK_CODE_BG": "cor_codigo_fundo",
        "BRAND_BOOK_CODE_BORDER": "cor_codigo_borda",
    },
}


def read_env(path: Path) -> dict:
    """Reads a brand.env, resolving ${VAR} references between entries."""
    data = {}
    if not Path(path).is_file():
        return data
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip()
    for _ in range(3):                       # three passes resolve chains
        for key, value in list(data.items()):
            data[key] = re.sub(r"\$\{(\w+)\}",
                               lambda m: data.get(m.group(1), ""), value)
    return data


def read_hex(raw: str):
    """The six hex digits at the start of a value, or None. Comments ignored."""
    m = RE_HEX.match((raw or "").strip())
    return m.group(1).upper() if m else None


def brand_colors(env: dict) -> dict:
    """{latex colour name: HEX} declared in brand.env, in declaration order."""
    out = {}
    for key, raw in env.items():
        if not key.startswith(COLOR_PREFIX):
            continue
        name = key[len(COLOR_PREFIX):].strip()
        value = read_hex(raw)
        if name and value:
            out[name] = value
    return out


def converter_colors(env: dict, piece: str = "BOOK") -> dict:
    """{md2book config key: HEX} for the book."""
    out = {}
    for key, cfg_key in CONVERTER_COLORS.get(piece, {}).items():
        value = read_hex(env.get(key, ""))
        if value:
            out[cfg_key] = value
    return out


# -------------------------------------------------------------------- pointers

def read_pointer(path: Path):
    """The first real path named by a one-line pointer file, or None.

    Blank lines and lines starting with `#` are comments, so the file can
    explain itself to whoever opens it in a year.
    """
    if not path.is_file():
        return None
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        target = Path(line).expanduser()
        if not target.is_absolute():
            target = path.parent / target
        return target.resolve()
    return None


def docs_root(explicit=None) -> Path:
    """Where the generated documentation lives, in order of precedence:

    1. an explicit path — `--docs <path>`;
    2. `TUTORIAL_FACTORY_DOCS` in the environment;
    3. the `DOCUMENTATION_PATH` pointer at the repository root;
    4. `documentation/` beside the repository — the default;
    5. `documentacao/`, when that is the one that exists.

    This never creates the folder. Deciding where a tutorial goes is one
    thing; creating it is the job of whoever writes the tutorial.
    """
    if explicit:
        return Path(explicit).expanduser().resolve()

    from_env = os.environ.get("TUTORIAL_FACTORY_DOCS")
    if from_env:
        return Path(from_env).expanduser().resolve()

    pointed = read_pointer(repo_root() / DOCS_POINTER)
    if pointed is not None:
        return pointed

    root = repo_root()
    if not (root / DOCS_DEFAULT).is_dir() and (root / DOCS_LEGACY).is_dir():
        return (root / DOCS_LEGACY).resolve()
    return (root / DOCS_DEFAULT).resolve()


def docs_origin(explicit=None) -> str:
    """How `docs_root` was decided — for the diagnosis screen."""
    if explicit:
        return "explicit"
    if os.environ.get("TUTORIAL_FACTORY_DOCS"):
        return "environment"
    if read_pointer(repo_root() / DOCS_POINTER) is not None:
        return "pointer"
    return "default"


def find_brand(explicit=None) -> Brand:
    """Resolve which brand kit to publish with. See the module docstring."""
    slot = tools_dir() / BRAND_SLOT

    if explicit:
        root = Path(explicit).expanduser().resolve()
        return Brand(root, "explicit")

    for variable in ("TUTORIAL_FACTORY_BRAND", "COURSE_FACTORY_BRAND"):
        from_env = os.environ.get(variable)
        if from_env:
            root = Path(from_env).expanduser().resolve()
            if (root / BRAND_MARKER).is_file():
                return Brand(root, "explicit")

    pointed = read_brand_pointer(slot)
    if pointed is not None:
        return Brand(pointed, "pointer")

    if (slot / BRAND_MARKER).is_file():
        return Brand(slot.resolve(), "installed")

    return Brand((slot / BRAND_TEMPLATE).resolve(), "template")


def read_brand_pointer(slot: Path = None):
    """The path named by `<slot>/BRAND_PATH`, when it points at a real kit.

    A kit that lives in its own repository, outside this tree, needs a way to
    stay wired in. An environment variable would work, but it has to be set in
    every shell — including the one an agent runs in — and a kit that silently
    falls back to the neutral pre-mold publishes material signed by nobody.
    A file in the slot is remembered by the machine, not by the person.

    Relative paths resolve against the slot, so a sibling checkout can be
    named `../../../course-factory-brand` and survive the repository moving.
    """
    slot = slot or (tools_dir() / BRAND_SLOT)
    pointer = slot / BRAND_POINTER
    root = read_pointer(pointer)
    if root is None:
        return None
    if (root / BRAND_MARKER).is_file():
        return root
    print("WARNING: %s points at %s, which is not a brand kit — ignoring."
          % (pointer, root), file=sys.stderr)
    return None


def example_doc(piece: str) -> Path:
    """The reference skeleton for one piece — engine-side, not brand-side."""
    return tools_dir() / "example" / ("%s-modelo.md" % piece)


# --------------------------------------------------------------------- md2book

def _md2book_candidates(explicit=None) -> list:
    candidates = []
    if explicit:
        candidates.append(Path(explicit).expanduser())
    candidates.append(tools_dir() / "md2book")          # vendored copy
    if os.environ.get("MD2BOOK"):
        candidates.append(Path(os.environ["MD2BOOK"]).expanduser())
    candidates += [Path.home() / "md2book", Path.home() / "Desktop" / "md2book"]
    return candidates


def find_md2book(explicit=None) -> list:
    """How to call md2book on this machine: returns a ready argv list."""
    def usable(base: Path):
        base = Path(base).expanduser()
        if base.is_file() and base.name.endswith(".py"):
            return [sys.executable, str(base)]
        if (base / "md2book.py").is_file():
            return [sys.executable, str(base / "md2book.py")]
        return None

    for base in _md2book_candidates(explicit):
        cmd = usable(base)
        if cmd:
            return cmd
    if shutil.which("md2book"):
        return [shutil.which("md2book")]
    return []
