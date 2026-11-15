# Right Month Map

A zoomable world map that shows, for any month, whether it is a good time of year to visit each place, compared with that place's own year.

The site is the single file `index.html`, with the climate grid, borders and place names embedded in it. Hosting needs no build step.

## Rebuilding

`index.html` is generated from `build/template.html`. To change the page, edit the template and rebuild. Run these from the repo root; they need Python 3 and no extra packages.

```sh
sh build/fetch.sh               # download the source data into build/data (about 95 MB)
python3 build/make_grid.py      # climate grid, takes about a minute
python3 build/make_vectors.py   # borders and place names
python3 build/build.py          # writes index.html
```

The scoring formula lives in `computeScores()` in the template. GeoNames updates daily, so a fresh download changes the place list slightly.

## Data and credits

- Climate: CRU CL v2.0 10-minute climatology, 1961–1990 (New, Lister, Hulme and Makin, 2002, *Climate Research* 21:1–25), aggregated to a 1/3° grid.
- Place names: [GeoNames](https://www.geonames.org/), CC BY 4.0.
- Outlines and island names: [Natural Earth](https://www.naturalearthdata.com/), public domain.
- Fonts: Inter and Space Grotesk, SIL Open Font License.

Scores are a rough estimate from temperature, humidity, rain and sunshine averages. They are not a forecast.
