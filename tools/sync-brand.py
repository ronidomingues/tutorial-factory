#!/usr/bin/env python3
"""sync-brand.py — installs, checks and refreshes the brand kit slot.

    python3 tools/sync-brand.py --check
    python3 tools/sync-brand.py --colors
    python3 tools/sync-brand.py --palette
    python3 tools/sync-brand.py --install ~/my-company-brand
    python3 tools/sync-brand.py --from-template
    python3 tools/sync-brand.py --md2book ~/md2book

Tutorial Factory does not carry an identity of its own. It publishes with the
kit installed at `tools/course-factory-brand/`, and that folder is a
**dependency**: usually a separate repository — private, if the brand is —
cloned, copied or symlinked into place.

The slot keeps the `course-factory-brand` name on purpose. The contract is the
same one Course Factory uses, so a single brand repository signs everything its
owner publishes, and `BRAND_PATH` can point both factories at the same folder.

This program handles what that folder needs:

  --check          does the installed kit satisfy the contract?
  --colors         which colour actually wins, and which declaration is dead
  --palette        regenerate palette/tokens.{json,css} from brand.env
  --install <src>  copy a kit from <src> into the slot
  --from-template  seed the slot from the neutral pre-mold, to start your own
  --md2book <src>  refresh the vendored md2book from a checkout of its repo

It never writes to the source. It never touches published documentation.
"""

import argparse
import filecmp
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common                                    # noqa: E402

TOOLS = common.tools_dir()
SLOT = TOOLS / common.BRAND_SLOT
TEMPLATE = SLOT / common.BRAND_TEMPLATE

# What a brand kit is made of. Anything else in the source is ignored: the kit
# may well be a repository with its own README, history and working files.
KIT_CONTENT = [
    ("brand.env", None),
    ("BRAND-MANUAL.md", None),
    ("EDITORIAL-STANDARD.md", None),
    ("latex", "*.sty"),
    ("md2book", "*.json"),
    ("assets", "*"),
    ("logo", "*"),
    ("palette", "*"),
    ("fonts", "*"),
]

# The vendored md2book, refreshed from a checkout of its own repository.
MD2BOOK_CONTENT = [
    ("md2book.py", None),
    ("pyproject.toml", None),
    ("README.md", None),
    ("LICENSE", None),
    ("src/md2book", "*.py"),
    ("modelo", "*"),
]


def copy_plan(source: Path, dest: Path, plan, dry_run: bool, tally: dict,
              skip_names=()) -> None:
    for rel, pattern in plan:
        origin = source / rel
        if not origin.exists():
            continue
        target_base = dest / rel
        items = []
        if origin.is_file():
            items = [(origin, dest / Path(rel).name if Path(rel).parent ==
                      Path(".") else target_base)]
        else:
            items = [(f, target_base / f.name)
                     for f in sorted(origin.glob(pattern or "*"))
                     if f.is_file() and f.name not in skip_names]
        for src, dst in items:
            if dst.is_file() and filecmp.cmp(src, dst, shallow=False):
                tally["same"] += 1
                continue
            tally["changed"].append(str(dst.relative_to(TOOLS)))
            if not dry_run:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, dst)


def do_check(brand_path: str) -> int:
    brand = common.find_brand(brand_path or None)
    print(brand.report())
    print()
    if not brand.exists():
        print("No brand kit installed. Pick one:")
        print()
        print("  Starting from scratch — take the neutral pre-mold and make it")
        print("  yours:")
        print("      python3 tools/sync-brand.py --from-template")
        print()
        print("  You already have a brand repository — clone it OUTSIDE the")
        print("  slot (the slot is not empty, so `git clone` into it fails)")
        print("  and point at it:")
        print("      git clone <your-brand-repo> ~/your-brand")
        print("      echo ~/your-brand > %s/%s" % (SLOT, common.BRAND_POINTER))
        print()
        print("  You have a kit in a folder and want it copied in:")
        print("      python3 tools/sync-brand.py --install <path>")
        print()
        print("  Full contract: docs/03-kit-de-marca.md")
        return 1
    gaps = brand.missing()
    if gaps:
        print("Contract NOT satisfied. Missing: %s" % ", ".join(gaps))
        print("See docs/03-kit-de-marca.md.")
        return 1
    if brand.origin == "template":
        print("Using the neutral pre-mold. It publishes real PDFs, but it is")
        print("nobody's identity — install your own kit before shipping.")
    print("Contract satisfied: this kit can publish.")
    return 0


def do_install(source: str, dry_run: bool, force: bool) -> int:
    src = Path(source).expanduser().resolve()
    if not (src / common.BRAND_MARKER).is_file():
        print("ERROR: %s is not a brand kit (no %s)."
              % (src, common.BRAND_MARKER), file=sys.stderr)
        return 2
    if src == SLOT.resolve():
        print("ERROR: source and destination are the same folder.",
              file=sys.stderr)
        return 2
    if (SLOT / common.BRAND_MARKER).is_file() and not force:
        print("A kit is already installed at %s." % SLOT)
        print("Use --force to overwrite it, or --dry-run to see the diff.")
        return 1

    tally = {"same": 0, "changed": []}
    copy_plan(src, SLOT, KIT_CONTENT, dry_run, tally)
    report(tally, dry_run, "brand kit", src)
    return 0


def do_from_template(dry_run: bool, force: bool) -> int:
    if not (TEMPLATE / common.BRAND_MARKER).is_file():
        print("ERROR: the pre-mold is missing from %s." % TEMPLATE,
              file=sys.stderr)
        return 2
    if (SLOT / common.BRAND_MARKER).is_file() and not force:
        print("A kit is already installed at %s — use --force to overwrite."
              % SLOT)
        return 1
    tally = {"same": 0, "changed": []}
    copy_plan(TEMPLATE, SLOT, KIT_CONTENT, dry_run, tally)
    report(tally, dry_run, "pre-mold", TEMPLATE, next_step="make it yours")
    if not dry_run:
        print()
        print("The kit is yours now. Make it look like you, in this order:")
        print("  1. %s/brand.env — name, tagline, owner AND every colour"
              % SLOT.name)
        print("     (BRAND_COLOR_*: recolouring needs no .sty edit at all)")
        print("  2. logo/*.svg, then convert them:")
        print("     inkscape --export-type=pdf --export-filename=assets/x.pdf "
              "logo/x.svg")
        print("  3. BRAND-MANUAL.md and EDITORIAL-STANDARD.md — write your own")
        print()
        print("Then:")
        print("  python3 tools/sync-brand.py --palette   # regenerate palette/")
        print("  python3 tools/sync-brand.py --colors    # who wins, what is dead")
        print("  python3 tools/publish-doc.py <software>     # and look at the PDF")
        print()
        print("Full contract and checklist: docs/03-kit-de-marca.md")
    return 0


def _sty_colors(brand) -> dict:
    """{name: HEX} of every `\\definecolor` in the kit's .sty files."""
    found = {}
    for sty in sorted(brand.latex.glob("*.sty")):
        for m in re.finditer(r"\\definecolor\s*\{([A-Za-z@]+)\}\s*"
                             r"\{HTML\}\s*\{([0-9A-Fa-f]{6})\}",
                             sty.read_text(encoding="utf-8")):
            found.setdefault(m.group(1), m.group(2).upper())
    return found


def _json_colors(brand) -> dict:
    """{piece: {config key: HEX}} as the kit's base JSONs declare them.

    The slides JSON is read even though this factory publishes no slides: a kit
    is usually shared with Course Factory, and a colour that drifted there is
    still a colour that drifted.
    """
    out = {}
    for piece, name in (("BOOK", "book.base.json"),
                        ("SLIDES", "slides.base.json")):
        path = brand.templates / name
        if not path.is_file():
            continue
        try:
            cfg = json.loads(path.read_text(encoding="utf-8"))
        except ValueError:
            continue
        out[piece] = {k: str(v).lstrip("#").upper()
                      for k, v in cfg.items()
                      if k.startswith("cor_") and isinstance(v, str)}
    return out


def do_colors(brand_path: str) -> int:
    """Which colour actually reaches the PDF, and which declaration is dead.

    Three places can name a colour — brand.env, the .sty defaults and the base
    JSONs — and only one of them wins. Printing all three side by side is how
    you find the edit that did nothing.
    """
    brand = common.find_brand(brand_path or None)
    if not brand.exists():
        print("No brand kit to inspect. Run --check.", file=sys.stderr)
        return 2
    print("Brand kit: %s (%s)" % (brand.root, brand.origin))
    print()

    env = common.read_env(brand.env)
    declared = common.brand_colors(env)
    in_sty = _sty_colors(brand)

    print("== LaTeX colours ==")
    if not declared:
        print("  brand.env declares none — the .sty defaults are what ships.")
        print("  %d colour(s) defined across %s"
              % (len(in_sty), ", ".join(p.name for p in
                                        sorted(brand.latex.glob("*.sty")))))
        print("  Declaring them in brand.env puts every colour in one file:")
        print("      BRAND_COLOR_<name>=RRGGBB      # see docs/03-kit-de-marca.md")
    else:
        print("  %-16s %-10s %-10s %s" % ("NAME", "brand.env", ".sty", "WINNER"))
        for name in sorted(set(declared) | set(in_sty)):
            e, s = declared.get(name, ""), in_sty.get(name, "")
            if e and s and e != s:
                verdict = "brand.env (the .sty value is dead)"
            elif e and s:
                verdict = "brand.env (same value)"
            elif e:
                verdict = "brand.env (no .sty default)"
            else:
                verdict = ".sty (not in brand.env)"
            print("  %-16s %-10s %-10s %s" % (name, e or "—", s or "—", verdict))

    print()
    print("== Converter colours (md2book paints these, not LaTeX) ==")
    in_json = _json_colors(brand)
    drift = 0
    for piece in ("BOOK",):
        from_env = common.converter_colors(env, piece)
        from_json = in_json.get(piece, {})
        print("  %s" % piece.lower())
        keys = sorted(set(from_env) | set(from_json))
        if not keys:
            print("    none declared")
            continue
        for key in keys:
            e, j = from_env.get(key, ""), from_json.get(key, "")
            if e and j and e != j:
                mark, drift = "brand.env wins; the JSON value is dead", drift + 1
            elif e:
                mark = "brand.env wins"
            else:
                mark = "from the base JSON"
            print("    %-20s env=%-8s json=%-8s %s"
                  % (key, e or "—", j or "—", mark))

    print()
    if drift:
        print("%d converter colour(s) disagree between brand.env and the base "
              "JSON." % drift)
        print("brand.env is what reaches the PDF. Align the JSON, or drop the "
              "key from it.")
    stale = palette_is_stale(brand, env)
    if stale:
        print("palette/ is out of date with brand.env — regenerate it:")
        print("  python3 tools/sync-brand.py --palette")
    return 0


# ------------------------------------------------------------------ palette

def _css_name(name: str) -> str:
    """cfBlueDeep -> --cf-blue-deep."""
    return "--" + re.sub(r"(?<!^)(?=[A-Z])", "-", name).lower()


def render_palette(brand, env: dict) -> dict:
    """The generated content of palette/tokens.json and tokens.css.

    Generated, not written by hand: two files claiming to be the source of a
    colour is exactly the drift this whole change exists to remove.
    """
    notes = _color_comments(brand.env)
    colors = common.brand_colors(env)
    if not colors:
        return {}

    header = ("GERADO por tools/sync-brand.py --palette a partir de brand.env. "
              "NÃO EDITE À MÃO: a fonte das cores é o brand.env.")
    data = {
        "_generated": header,
        "brand": env.get("BRAND_NAME", ""),
        "colors": {name: {"hex": "#" + value,
                          "use": notes.get(name, "")}
                   for name, value in colors.items()},
        "converter": {
            "book": {k: "#" + v
                     for k, v in common.converter_colors(env, "BOOK").items()},
            "slides": {k: "#" + v
                       for k, v in common.converter_colors(env, "SLIDES").items()},
        },
    }

    css = ["/* %s */" % header, ":root {"]
    for name, value in colors.items():
        use = notes.get(name, "")
        css.append("  %-22s #%s;%s" % (_css_name(name) + ":", value,
                                       "   /* %s */" % use if use else ""))
    css += ["}", ""]

    return {"tokens.json": json.dumps(data, indent=2, ensure_ascii=False) + "\n",
            "tokens.css": "\n".join(css)}


def _color_comments(env_path: Path) -> dict:
    """{colour name: the comment written next to it in brand.env}."""
    notes = {}
    if not env_path.is_file():
        return notes
    for line in env_path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\s*(%s\w+)\s*=\s*#?[0-9A-Fa-f]{6}\s*#\s*(.+?)\s*$"
                     % common.COLOR_PREFIX, line)
        if m:
            notes[m.group(1)[len(common.COLOR_PREFIX):]] = m.group(2)
    return notes


def palette_is_stale(brand, env: dict) -> bool:
    rendered = render_palette(brand, env)
    if not rendered:
        return False
    for name, content in rendered.items():
        path = brand.root / "palette" / name
        if not path.is_file() or path.read_text(encoding="utf-8") != content:
            return True
    return False


def do_palette(brand_path: str, dry_run: bool) -> int:
    brand = common.find_brand(brand_path or None)
    if not brand.exists():
        print("No brand kit to generate a palette for. Run --check.",
              file=sys.stderr)
        return 2
    env = common.read_env(brand.env)
    rendered = render_palette(brand, env)
    if not rendered:
        print("brand.env declares no BRAND_COLOR_* keys — nothing to generate.")
        print("Declare the colours there first; see docs/03-kit-de-marca.md.")
        return 1
    destination = brand.root / "palette"
    changed = []
    for name, content in rendered.items():
        path = destination / name
        if path.is_file() and path.read_text(encoding="utf-8") == content:
            continue
        changed.append(path)
        if not dry_run:
            destination.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    print("Source: %s" % brand.env)
    if not changed:
        print("palette/ is already up to date (%d colours)."
              % len(common.brand_colors(env)))
        return 0
    verb = "Would write" if dry_run else "Wrote"
    for path in changed:
        print("%s %s" % (verb, path))
    return 0


def do_md2book(source: str, dry_run: bool) -> int:
    src = Path(source).expanduser().resolve()
    if not (src / "src" / "md2book").is_dir():
        print("ERROR: %s does not look like an md2book checkout." % src,
              file=sys.stderr)
        return 2
    tally = {"same": 0, "changed": []}
    copy_plan(src, TOOLS / "md2book", MD2BOOK_CONTENT, dry_run, tally)
    report(tally, dry_run, "md2book", src)
    return 0


def report(tally: dict, dry_run: bool, what: str, source: Path,
           next_step: str = "republish") -> None:
    print("Source: %s" % source)
    print("Unchanged: %d file(s)" % tally["same"])
    if not tally["changed"]:
        print("Nothing changed: the %s is up to date." % what)
        return
    verb = "Would change" if dry_run else "Updated"
    print("%s: %d" % (verb, len(tally["changed"])))
    for name in tally["changed"][:40]:
        print("  %s" % name)
    if len(tally["changed"]) > 40:
        print("  ... and %d more" % (len(tally["changed"]) - 40))
    if dry_run or next_step != "republish":
        return
    # Telling someone to republish documentation they have not written yet is
    # noise; only the paths that change an existing identity say this.
    print()
    print("Republish the documentation so the change reaches the PDFs:")
    print("  python3 tools/publish-all.py --jobs 6")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description="Installs, checks and refreshes the brand kit slot.")
    p.add_argument("--check", action="store_true",
                   help="verify the installed kit against the contract")
    p.add_argument("--colors", "--colours", action="store_true",
                   dest="colors",
                   help="show which colour wins and which declaration is dead")
    p.add_argument("--palette", action="store_true",
                   help="regenerate palette/tokens.{json,css} from brand.env")
    p.add_argument("--install", default="",
                   help="copy a brand kit from this path into the slot")
    p.add_argument("--from-template", action="store_true",
                   help="seed the slot from the neutral pre-mold")
    p.add_argument("--md2book", default="",
                   help="refresh the vendored md2book from this checkout")
    p.add_argument("--brand", default="",
                   help="check this path instead of the installed slot")
    p.add_argument("--dry-run", action="store_true",
                   help="say what would change, change nothing")
    p.add_argument("--force", action="store_true",
                   help="overwrite a kit that is already installed")
    args = p.parse_args(argv)

    if args.colors:
        return do_colors(args.brand)
    if args.palette:
        return do_palette(args.brand, args.dry_run)
    if args.install:
        return do_install(args.install, args.dry_run, args.force)
    if args.from_template:
        return do_from_template(args.dry_run, args.force)
    if args.md2book:
        return do_md2book(args.md2book, args.dry_run)
    return do_check(args.brand)


if __name__ == "__main__":
    sys.exit(main())
