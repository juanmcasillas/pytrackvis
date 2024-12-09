from .helpers import C

def GetStatsFromDB(db):
    """
    select count(*) from tracks;
    select count(*) from places;
    select sum(distance) from tracks;
    select sum(elevation) from tracks;

    select sum(elevation), kind from tracks group by kind;
    select sum(distance), kind from tracks group by kind;

    select sum(elevation), equipment from tracks group by equipment;
    select sum(distance), equipment from tracks group by equipment;

    """

    # number_of_places = db.execute("")[0]
    s = {}
    row = db.execute("select count(*),sum(length_2d),sum(uphill_climb) from tracks").fetchone()
   
    s['number_of_tracks'] = row[0]
    s['total_length_2d']   = row[1]
    s['total_uphill_climb']  = row[2]
 
    s['by_kind'] = []
    for row in db.execute("select sum(uphill_climb),sum(length_2d),count(*),kind from tracks group by kind"):
        d = {}
        d['uphill_climb'] = row[0]
        d['length_2d'] = row[1]
        d['number'] = row[2]
        d['kind'] = row[3]
        s['by_kind'].append(d)


    s['by_equipment'] = []
    for row in db.execute("select sum(uphill_climb),sum(length_2d),count(*),kind,equipment from tracks group by kind, equipment"):
        d = {}
        d['uphill_climb'] = row[0]
        d['length_2d'] = row[1]
        d['number'] = row[2]
        d['kind'] = row[3]
        d['equipment'] = row[4]
        s['by_equipment'].append(d)

    s['kinds'] = list(map(lambda x: str(x[0]), db.execute("select distinct kind from tracks order by kind").fetchall()))
  
    s['years'] = []
    for row in db.execute("SELECT strftime('%Y', datetime(stamp, 'unixepoch')) as year, sum(uphill_climb),sum(length_2d),count(*) FROM TRACKS group by year"):
        d = {}
        d['year'] = row[0]
        d['uphill_climb'] = row[1]
        d['length_2d'] = row[2]
        d['number'] = row[3] 
        s['years'].append(d)

    s['by_equipment_and_year'] = {}
    for y in s['years']:
        s['by_equipment_and_year'][y['year']] = []
        for row in db.execute("select sum(uphill_climb),sum(length_2d),count(*),kind,equipment,strftime('%Y', datetime(stamp, 'unixepoch')) as year from tracks where year='" + y['year'] + "' group by kind, equipment"):
            d = {}
            d['uphill_climb'] = row[0]
            d['length_2d'] = row[1]
            d['number'] = row[2]
            d['kind'] = row[3]
            d['equipment'] = row[4]
            d['year'] = row[5]

            s['by_equipment_and_year'][y['year']].append(d)

    return s