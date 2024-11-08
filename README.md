# pytrackvis
A simple Python GPX and FIT track file format visualization app on 2D / 3D Map using leafmap. Only accept FIT and GPX files. Try to keep the software standard and simple, getting only the required data. The maplibre install only works on python 3.11.x

## Libs

    * [fitdecode](https://fitdecode.readthedocs.io/en/latest/) To read FIT files
    * [gpxpy](https://github.com/tkrajina/gpxpy) To read GPX files

    * Install the modules with `python -m pip install <modulename>`
    * `%pip install -U "leafmap[maplibre]"`

## Info

    * [Parsing fitness files](https://towardsdatascience.com/parsing-fitness-tracker-data-with-python-a59e7dc17418)
    * [MAPLibre tutorial](https://geog-312.gishub.org/book/geospatial/maplibre.html)

## Fields

    * `timestamp`. Timestamps in FIT messages are almost always given as the number of seconds since the Garmin Epoch `1989–12–31T00:00:00Z`
     