#!/bin/sh
# Downloads the source data into build/data (about 95 MB). Run from the repo root.
set -e
mkdir -p build/data && cd build/data
for v in tmp dtr pre rd0 sunp reh; do
  curl -fsSL -O "https://crudata.uea.ac.uk/cru/data/hrg/tmc/grid_10min_$v.dat.gz"
done
curl -fsSL -O "https://cdn.jsdelivr.net/npm/world-atlas@2.0.2/countries-50m.json"
curl -fsSL -O "https://download.geonames.org/export/dump/cities5000.zip"
curl -fsSL -O "https://download.geonames.org/export/dump/countryInfo.txt"
curl -fsSL -o regions.geojson "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_geography_regions_polys.geojson"
unzip -o -q cities5000.zip
