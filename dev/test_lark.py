
import sys
from pprint import pprint
import sqlite3


import sys
sys.path.append('..')

from pytrackvis.qparser import QueryParser

if __name__ == "__main__":

    parser = QueryParser(get_attr="id", limit=0, offset=0, verbose=True)

    sentences = []

    # sentences.append('all')
    # sentences.append('all order by stamp desc limit 10')
    # sentences.append('* order by stamp desc limit 10')
    # sentences.append('similar 2420')
    #sentences.append('similar 2420 order by stamp desc limit 10')
    # sentences.append('similar 2420 order by stamp desc')
    sentences.append('similar 2420 limit 1')
    # sentences.append('title "navas del rey"')
    # sentences.append("title 'navas del rey'")
    # sentences.append('sport \'BIKE\'')
    # sentences.append('sport "BIKE"')
    # sentences.append('sport BIKE')
    # sentences.append('sport RUN order by length')
    # sentences.append('device FENIX3 order by length')
    # sentences.append('distance > 100 or kind = "run"')
    # sentences.append('distance between 100 and 200')
    # sentences.append('distance >= 100 or length_2d <= 100 or elevation is null')
    # sentences.append('(length_2d > 20000.0 and distance < 1000 KM) or stamp = NOW()')
    # sentences.append('(length_2d > 20000.0 and distance < 1000 KM) or DATE(stamp) = TODAY()')
    # sentences.append('sport "BIKE"')
    # sentences.append('title "navas del rey" and elevation > 30')
    # sentences.append('(kind = "xxx" or kind = "run")')
    # sentences.append('sport BIKE and ELEVATION<30m or DISTANCE>10Km')
    # sentences.append('sport BIKE and ELEVATION<30m or DISTANCE>10Km limit 10 offset 5')
    # sentences.append('sport BIKE and ELEVATION<30m or DISTANCE>10Km order by stamp, length_2d desc, stamp asc limit 10 offset 5')
    # sentences.append('this is an error')
    # sentences.append("title  'san martin' and date(stamp) < TODAY()")
    # sentences.append("title  'san martin' and TRACK_DATE() < TODAY()")
    # sentences.append("title  'san martin' and TRACK_DATE() < TODAY('-1 day')")
    # sentences.append("title  'san martin' and TRACK_DATE() < TODAY('-1 day')")
    # sentences.append("title  'san martin' and DATE(stamp,'+1 day') < TODAY('-1 day')")
    # sentences.append("title  'san martin' and TIME(stamp,'+1 hour') < TODAY('-1 day')")
    # sentences.append("title  'san martin' and TRACK_DATE('+1 hour') < TODAY('-1 day')")
    # sentences.append("title 'san martin' and  TRACK_DATE() < DATE('2024/11/01')")

    for s in sentences:
    
        db = sqlite3.connect("../db/trackdb.db", check_same_thread=False)
        db.row_factory = sqlite3.Row
    
        result, sql = parser.run(s)
        print("-" * 80)
        print(s)
        print(sql)
        if result:
            cursor = db.cursor()
            cursor.execute(sql)
            data = cursor.fetchall()
            cursor.close()
            data = map(lambda x: dict(x), data)
            for i in data:
                pprint(i)
        print("-" * 80)
        # make_png(sys.argv[1])
        # make_dot(sys.argv[1])