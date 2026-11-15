"""Turn the CRU CL v2.0 10-minute grids into the packed climate grid the page reads.

Usage: python3 build/make_grid.py [data_dir] [out_dir]

Output: out/grid.b64, base64 of a zlib stream holding a land mask (1 bit per cell)
followed by six 8-bit layers (tmax, tmin, pre, wet, sun, reh) x 12 months for land
cells only. Each value is stored as the change from the previous month, then as the
change from the previous land cell, which compresses well.
"""
import base64, gzip, math, os, sys, zlib

D = sys.argv[1] if len(sys.argv) > 1 else "build/data"
OUT = sys.argv[2] if len(sys.argv) > 2 else "build/out"
RES = 3                      # cells per degree (1/3 degree, about 37 km at the equator)
W = 360 * RES
LATN, LATS = 85, -60
H = (LATN - LATS) * RES
N = W * H


def load(v):
    sums = [[0.0] * N for _ in range(12)]
    cnt = [0] * N
    with gzip.open(f"{D}/grid_10min_{v}.dat.gz", "rt") as f:
        for line in f:
            p = line.split()
            lat, lon = float(p[0]), float(p[1])
            if lat >= LATN or lat < LATS:
                continue
            i = int((LATN - lat) * RES) * W + int((lon + 180) * RES)
            cnt[i] += 1
            for m in range(12):
                sums[m][i] += float(p[2 + m])
    return sums, cnt


def q(x):
    return max(0, min(254, int(round(x))))   # 255 is reserved for "no data"


L = {v: load(v) for v in ["tmp", "dtr", "pre", "rd0", "sunp", "reh"]}
ORDER = ["tmax", "tmin", "pre", "wet", "sun", "reh"]
layers = {k: bytearray([255]) * (12 * N) for k in ORDER}
for i in range(N):
    if not all(L[v][1][i] for v in L):
        continue
    for m in range(12):
        g = lambda v: L[v][0][m][i] / L[v][1][i]
        t, d = g("tmp"), g("dtr")
        o = m * N + i
        layers["tmax"][o] = q((t + d / 2 + 50) * 2)          # 0.5 C steps from -50 C
        layers["tmin"][o] = q((t - d / 2 + 50) * 2)
        layers["pre"][o] = q(math.sqrt(max(0, g("pre"))) * 6)  # mm = (v / 6) ** 2
        layers["wet"][o] = q(g("rd0") * 8)                    # wet days = v / 8
        layers["sun"][o] = q(g("sunp") * 2.5)                 # % of possible sunshine = v / 2.5
        layers["reh"][o] = q(g("reh") * 2.5)                  # relative humidity % = v / 2.5
raw = b"".join(bytes(layers[k]) for k in ORDER)

land = [i for i in range(N) if raw[i] != 255]
mask = bytearray((N + 7) // 8)
for i in land:
    mask[i >> 3] |= 1 << (i & 7)
out = bytearray()
for l in range(6):
    for m in range(12):
        base = (l * 12 + m) * N
        prev = 0
        for i in land:
            x = raw[base + i]
            d = x if m == 0 else (x - raw[base - N + i]) & 255
            out.append((d - prev) & 255)
            prev = d
z = zlib.compress(bytes(mask) + bytes(out), 9)
os.makedirs(OUT, exist_ok=True)
open(f"{OUT}/grid.b64", "w").write(base64.b64encode(z).decode())
print(f"{len(land)} land cells, {len(z)} bytes compressed")
