import re
import os
import time
import datetime

def parse_fname(fname):
    stamp = None
    tags = None
    places = None
    extension = None

    """
    /Archive/Cartography/files/FENIX3/2023/
    2023-01-02-16-10-14 - [RUN,FENIX3,NB_HIERRO] San Martín - Camino de Pelayos - Acorte (Largo) - Camino Angosto - San Martín.fit
    """
    
    regstr = re.match("(\d{4}-\d{2}-\d{2}-\w{2}-\w{2}-\w{2}|\d{10}|\d{8})?\s*(-+)?\s*(\[.+\])*\s*(.+)\.(.+)", 
                      os.path.basename(fname), 
                      re.I)

    if regstr:
        if regstr.group(1):
            stamp = regstr.group(1)
            stamp = stamp.upper().replace('X', '0')  # to manage UNKNOWN dates (from creation)
            stamp = time.mktime(datetime.datetime.strptime(stamp, "%Y-%m-%d-%H-%M-%S").timetuple())

        if regstr.group(3):
            tags = regstr.group(3)
            tags = re.sub('\]\s*\[', ',', tags)
            tags = re.sub('[\[\]]', '', tags)
            tags = tags.split(',')
            tags = list(filter(lambda x: x.strip(), tags))

        if regstr.group(4):
            places = regstr.group(4)
            places = re.split("\s*[-_]+\s*", places)
            places = list(filter(lambda x: x.strip(), places))

        if regstr.group(5):
            extension = regstr.group(5).lower()

    print(stamp)
    print(tags)
    print(places)
    print(extension)
    return stamp, tags, places, extension
        

if __name__ == "__main__":
    f = "/Archive/Cartography/files/FENIX3/2023/2023-01-02-16-10-14 - [RUN,FENIX3,NB_HIERRO] San Martín - Camino de Pelayos - Acorte (Largo) - Camino Angosto - San Martín.fit"
    parse_fname(f)
    f = "movida chunga.fit"
    parse_fname(f)