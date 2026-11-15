"""Insert the generated data into build/template.html and write index.html.

Usage: python3 build/build.py [out_dir] [dest]
"""
import sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "build/out"
DEST = sys.argv[2] if len(sys.argv) > 2 else "index.html"
t = open("build/template.html", encoding="utf-8").read()
safe = lambda name: open(f"{OUT}/{name}", encoding="utf-8").read().replace("<", "\\u003c")
t = (t.replace("__GRID__", open(f"{OUT}/grid.b64").read())
      .replace("__BORDERS__", safe("borders.json"))
      .replace("__CITIES__", safe("cities.json")))
open(DEST, "w", encoding="utf-8").write(t)
print(f"wrote {DEST}, {len(t)} characters")
