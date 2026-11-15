"""Build the border outlines and the place-name list the page reads.

Usage: python3 build/make_vectors.py [data_dir] [out_dir]
"""
import json, os, sys

D = sys.argv[1] if len(sys.argv) > 1 else "build/data"
OUT = sys.argv[2] if len(sys.argv) > 2 else "build/out"
os.makedirs(OUT, exist_ok=True)

# Borders: keep world-atlas's quantized, delta-encoded arcs and drop everything else.
t = json.load(open(f"{D}/countries-50m.json"))
json.dump({"s": t["transform"]["scale"], "t": t["transform"]["translate"],
           "a": [[c for pt in arc for c in pt] for arc in t["arcs"]]},
          open(f"{OUT}/borders.json", "w"), separators=(",", ":"))

# Places: [name, country code, lon, lat, importance (thousands of people), 1 if island].
cc = {}
for l in open(f"{D}/countryInfo.txt", encoding="utf-8"):
    if l.startswith("#"):
        continue
    p = l.split("\t")
    if len(p) > 4:
        cc[p[0]] = p[4]
P = []
for l in open(f"{D}/cities5000.txt", encoding="utf-8"):
    p = l.rstrip("\n").split("\t")
    lat, lon, pop = float(p[4]), float(p[5]), int(p[14] or 0)
    if lat >= 85 or lat <= -60:
        continue
    imp = pop * (4 if p[7] == "PPLC" else 1) // 1000   # capitals get a boost
    P.append([p[1], p[8], round(lon, 2), round(lat, 2), imp, 0])
RANK = {0: 4000, 1: 4000, 2: 2500, 3: 900, 4: 350, 5: 120, 6: 60}
d = json.load(open(f"{D}/regions.geojson", encoding="utf-8"))
for f in d["features"]:
    pr = f["properties"]
    if pr["FEATURECLA"] not in ("Island", "Island group") or not pr.get("NAME"):
        continue
    g = f["geometry"]
    polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
    ring = max((pl[0] for pl in polys), key=len)
    lon = sum(c[0] for c in ring) / len(ring)
    lat = sum(c[1] for c in ring) / len(ring)
    if lat >= 85 or lat <= -60:
        continue
    P.append([pr["NAME"], "", round(lon, 2), round(lat, 2), RANK.get(int(pr.get("SCALERANK") or 6), 40), 1])
P.sort(key=lambda c: -c[4])
used = {c[1] for c in P}
json.dump({"cc": {k: v for k, v in cc.items() if k in used}, "p": P},
          open(f"{OUT}/cities.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print(len(P), "places")
