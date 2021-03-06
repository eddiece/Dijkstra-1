import requests
from math import cos, sin, atan2, pi, sqrt


def degToRad(deg):
    return deg/360*2*pi


def distance(u, v):
    if type(u) is tuple and type(v) is tuple:
        r_lat1 = float(u[0])
        r_lon1 = float(u[1])
        r_lat2 = float(v[0])
        r_lon2 = float(v[1])
    else:
        r_lat1 = float(u.get("lat"))
        r_lon1 = float(u.get("lon"))
        r_lat2 = float(v.get("lat"))
        r_lon2 = float(v.get("lon"))

    R = 6371000
    lat1 = degToRad(r_lat1) / 2
    lat2 = degToRad(r_lat2) / 2
    lon1 = degToRad(r_lon1) / 2
    lon2 = degToRad(r_lon2) / 2

    dlat = lat2-lat1
    dlon = lon2-lon1
    a = (pow(sin(dlat)/2, 2)
         + cos(lat1)*cos(lat2)*pow(sin(dlon)/2, 2))
    c = 2*atan2(sqrt(a), sqrt(1-a))
    dist = R*c
    return dist


def nearestRoad(latitude, longitude, radius, number_to_get=2):
    ''' Returns the 2 closest points from the coordinates given.'''
    req = '''<osm-script output="json">
  <query type="way">
    <around lat="{lat}" lon="{long}" radius="{rad}"/>
    <has-kv k="highway" modv="" regv="residential|tertiary|secondary|primary"/>
  </query>
  <union>
    <item/>
    <recurse type="down"/>
  </union>
  <print/>
</osm-script>'''.format(lat=latitude, long=longitude, rad=radius)
    headers = {'content-type': 'application/xml'}
    r = requests.post("http://overpass-api.de/api/interpreter",
                      headers=headers, data=req)
    assert (r.status_code == 200)
    json = r.json()["elements"]

    nodes = dict()
    for node in json:
        if node['type'] == 'node':
            d = distance((latitude, longitude),
                         (node['lat'], node['lon']))
            nodes[d] = int(node['id'])

    keys = list(nodes.keys())
    keys.sort()

    return [(nodes[dist], dist) for dist in keys[:number_to_get]]


def nearestTransport(latitude, longitude, radius, number_to_get=2):
    req = '''
<osm-script output="json" timeout="25">
  <union into="_">
    <query into="_" type="node">
      <has-kv k="highway" modv="" v="bus_stop"/>
      <around from="_" into="_" lat="{lat}" lon="{lon}" radius="{rad}"/>
    </query>
    <query into="_" type="node">
      <has-kv k="railway" modv="" v="subway_entrance"/>
      <around from="_" into="_" lat="{lat}" lon="{lon}" radius="{rad}"/>
    </query>
  </union>
  <print e="" from="_" geometry="skeleton" limit="" mode="body" n="" order="id" s="" w=""/>
  <recurse from="_" into="_" type="down"/>
  <print e="" from="_" geometry="skeleton" limit="" mode="skeleton" n="" order="quadtile" s="" w=""/>
</osm-script>'''.format(lat=latitude, lon=longitude, rad=radius)

    headers = {'content-type': 'application/xml'}
    r = requests.post("http://overpass-api.de/api/interpreter",
                      headers=headers, data=req)

    assert (r.status_code == 200)
    json = r.json()["elements"]

    stations = dict()
    for station in json:
        if station['type'] == 'node':
            d = distance((latitude, longitude),
                         (station['lat'], station['lon']))

            stations[d] = {'id': int(station['id']),
                           'lat': float(station['lat']),
                           'lon': float(station['lon']),
                           'all': station}

    keys = list(stations.keys())
    keys.sort()

    return [stations[k] for k in keys[:number_to_get]]


def coordinates(adress):
    url = "http://nominatim.openstreetmap.org/search?q=" + \
          "{}&format=json".format("+".join(adress.split()))
    r = requests.get(url)
    assert (r.status_code == 200)
    json = r.json()[0]
    lat = json["lat"]
    lon = json["lon"]
    id = int(json["osm_id"])

    return (lat, lon, id)


def processClosest(ls, get_id, add):
    ''' ls is a list of dictionaries in the form :
    'from': …, 'to': …, 'dist': …

    The function applies get_id on each element of from and to and then
    add them using the add function.
    '''
    nearest = []
    for d in ls:
        try:
            _from, _to, _d = d['from'], d['to'], d['dist']
            print(_from, _to, _d)
            id1 = get_id(_from)
            id2 = get_id(_to)
            add(id1, id2, _d)
            nearest += {'from': d['from'], 'to': d['to'], 'dist': d['dist']}
        except:
            pass

    return nearest
