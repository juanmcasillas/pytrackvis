# pytrackvis
A simple Python GPX and FIT track file format visualization app on 2D / 3D Map using leafmap. Only accept FIT and GPX files. Try to keep the software standard and simple, getting only the required data. The maplibre install only works on python 3.11.x

## Libs

* [fitdecode](https://fitdecode.readthedocs.io/en/latest/) To read FIT files
* [gpxpy](https://github.com/tkrajina/gpxpy) To read GPX files
* [leafmap](https://leafmap.org/installation/) Draw awesome maps
* [pydeck](https://pypi.org/project/pydeck/) Large scale interactive data visualization

* Install the modules with `python -m pip install fitdecode gpxpy leafmap[maplibre] pydeck`

## Info

* [Parsing fitness files](https://towardsdatascience.com/parsing-fitness-tracker-data-with-python-a59e7dc17418)
* [MAPLibre tutorial](https://geog-312.gishub.org/book/geospatial/maplibre.html)
* [MAPLibre github](https://github.com/eoda-dev/py-maplibregl?tab=readme-ov-file)
* [Leafmap maplibreGL](https://leafmap.org/maplibregl/)
  
## Fields

* `timestamp`. Timestamps in FIT messages are almost always given as the number of seconds since the Garmin Epoch `1989–12–31T00:00:00Z`
     

## Lets use Maplibre-gl-JS

https://documentation.maptiler.com/hc/en-us/articles/5224821308177-How-to-build-a-3D-map-with-MapLibre-v2-GL-JS

## run the webapp

 C:\Python312\Scripts\flask.exe  --app webapp run --host=0.0.0.0 --debug