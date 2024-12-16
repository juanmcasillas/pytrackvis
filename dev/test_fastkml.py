from fastkml.utils import find_all
from fastkml import KML
from fastkml import Placemark


if __name__ == "__main__":
    
    mykml = KML.parse("/Archive/Cartography/files/databases/tocheck/myplaces.kml", strict=False)
    placemarks = list(find_all(mykml, of_type=Placemark))
    for p in placemarks:
        print(p.name)