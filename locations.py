import geohash
import subprocess
from collections import Counter
import os
import json


_dbase = {}

def search_index(place_id):
    y = subprocess.check_output(['java', 'SearchFiles','index/index', place_id])
    if len(y) <=1:
        return
    y = y.split('\n')[0].split('\t')
    return [y[1], y[4], y[5]]

def get_locations(text):
    text = text.replace('\n', ' ')
    ct = Counter(text.split(' '))
    terms = ct.most_common(15)
#    print terms
    st = ""
    for x in terms:
        st = st + " " + x[0]

    #print st
    y = subprocess.check_output(['java', 'SearchFiles','index/countries', st])
    y = y.split('\n')
    countries = []
    y = y[:3]
    for x in y:
        x = x.split('\t')
        if len(x) >6:
            countries.append([x[4], x[len(x)-3], x[len(x)-2]])

    y = subprocess.check_output(['java', 'SearchFiles','index/states', st])
    states = []
    y = y.split('\n')
    y = y[:3]
    #states = [x.split('\t') for x in y]
    for x in y:
        x = x.split('\t')
        if len(x)>=2:
            states.append([x[2], x[len(x)-3], x[len(x)-2]])
#    print "State"
#    for x in y:
#        print x

    y = subprocess.check_output(['java', 'SearchFiles','index/substates', st])
    y = y.split('\n')
    y = y[:3]
    substates = []
#    substates = [x.split('\t') for x in y]
#    substates = substates[:-1]
#    print "Substates"
    for x in y:
        x = x.split('\t')
        if len(x) >=2:
            substates.append([x[2], x[len(x)-3], x[len(x)-2]])


    y = subprocess.check_output(['java', 'SearchFiles','index/cities', st])
    y = y.split('\n')
    cities = []
    for x in y:
        x = x.split('\t')
        if len(x)>=5:
            cities.append([x[2],x[4],x[5]])

    return [countries, states, substates, cities]

def get_most_relevant_place(st):
    psb = {}
    y = subprocess.check_output(['java', 'SearchFiles','index/countries', st])
    y = y.split('\n')
    y = y[0]
    y = y.split('\t')
    if len(y)>2:
        psb[y[4] + '1'] = [y[len(y)-1], [y[len(y)-3], y[len(y)-2]]]
        return [y[4], psb[y[4] + '1']]

    y = subprocess.check_output(['java', 'SearchFiles','index/states', st])
    y = y.split('\n')
    y = y[0]
    y = y.split('\t')
    if len(y)>2:
        psb[y[2] + '2'] = [y[len(y)-1], [y[len(y)-3], y[len(y)-2]]]
        return [y[2], psb[y[2] + '2']]

    y = subprocess.check_output(['java', 'SearchFiles','index/substates', st])
    y = y.split('\n')
    y = y[0]
    y = y.split('\t')
    if len(y)>2:
        psb[y[2] + '3'] = [y[len(y)-1], [y[len(y)-3], y[len(y)-2]]]
        return [y[2], psb[y[2] + '3']]

    y = subprocess.check_output(['java', 'SearchFiles','index/cities', st])
    y = y.split('\n')
    y = y[0]
    y = y.split('\t')
    if len(y)>=5:
        psb[y[2] + '4'] = [y[len(y)-1],[y[4],y[5]]]
        return [y[2], psb[y[2] + '4']]
    return []
    mx = max(psb, key = lambda x : psb[x][0])
    return [mx[:-1], psb[mx]]
    

def get_geohashes(data):
    geohashes = set()
    for y in data:
        for x in y:
            geohashes.add(geohash.encode(float(x[1]), float(x[2]), 5))
    out = []
    for x in geohashes:
        out.append(x)
    out = set(out)
    out = [x for x in out]
    return out

def add_to_database_hash(hsh, data):
    global _dbase
    hsh = hsh[:5]
    _dbase.setdefault(hsh, []).append(data)
    _dbase.setdefault(hsh[:4], []).append(data)
    _dbase.setdefault(hsh[:3], []).append(data)

def query_database_hash(hsh):
    hsh = hsh[:5]
    exact_matches5 = []
    if hsh in _dbase:
        exact_matches5 = _dbase[hsh]
    r = geohash.neighbors(hsh)
    neighbors5 = []
    for x in r:
        if x in _dbase:
            neighbors5.extend(_dbase[x])

    hsh = hsh[:4]
    exact_matches4 = []
    if hsh in _dbase:
        exact_matches4 = _dbase[hsh]
    r = geohash.neighbors(hsh)
    neighbors4 = []
    for x in r:
        if x in _dbase:
            neighbors4.extend(_dbase[x])

    hsh = hsh[:3]
    exact_matches3 = []
    if hsh in _dbase:
        exact_matches3 = _dbase[hsh]
    r = geohash.neighbors(hsh)
    neighbors3 = []
    for x in r:
        if x in _dbase:
            neighbors3.extend(_dbase[x])

    return [exact_matches5, neighbors5, exact_matches4, neighbors4, exact_matches3, neighbors3]

def add_to_database_text(text, data):
    out = get_locations(text)
    hashes = get_geohashes(out)
    for hsh in hashes:
        add_to_database_hash(hsh, data)

def query_database_text(text):
    x = get_most_relevant_place(text)
    if len(x)>1:
        hsh = geohash.encode(float(x[1][1][0]), float(x[1][1][1]), 5)
        return query_database_hash(hsh)
    return []

def write_db():
    f = open('db.txt', 'w')
    f.write(json.dumps(_dbase))
    f.close()

def load_db():
    f = open('db.txt')
    a = f.readline()
    _dbase = json.loads(a)
    f.close()


def index_clusters():
    for r,d,f2 in os.walk('clusters2'):
        for fn in f2:
            print fn
            f = open('clusters2/' + fn)
            a = f.readlines()
            b = ''
            for x in a:
                b = b + x + ' '
            add_to_database_text(b, fn)
    write_db()


if __name__ == '__main__':
    load_db()
    st = raw_input()
    while(st != '*'):
        print query_database_text(st)
        st = raw_input()




