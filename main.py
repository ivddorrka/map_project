"""
Working with html
"""
import folium
import pandas as pd
import csv
import geopy
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderUnavailable
from geopy.distance import geodesic
from datetime import date

def where_user():
    """
    To find where user is
    """
    ask_for_input = input("Enter your coordinates: ")
    ask_for_year = input("Enter year: ")
    app = Nominatim(user_agent="tutorial")
    return ask_for_input, ask_for_year


def read_file(file):
    """Reads file content"""
    file_here = open(file, 'r+', encoding="latin1")
    all_it = []
    for line in file_here.readlines():
        fields = ''.join(line.split('\n')).split('\t')
        all_it.append(fields)
    return all_it
# print(read_file('locations_smaller'))
# print(read_file("locations.list"))


def into_field(file):
    """To modify output from read_file"""
    lst = read_file(file)[15:-1]
    years = [i[0].split('(')[1].split(')')[0] for i in lst]
    titles = [i[0].split('(')[0] for i in lst]
    places_1 = [''.join(i[1:]) for i in lst]
    places = []
    for a in places_1:
        last = (a.split(',')[-1].split('(')[0])
        last_1 = []
        for _ in last:
            if _ != ' ':
                last_1.append(_)
        first_two = a.split(',')[-3:-1]
        result = '{} {}'.format(''.join(first_two), ''.join(last_1))
        places.append(result)

    df = pd.DataFrame({'TITLES': titles, 'YEAR': years, 'PLACES': places})
    return df

def modify_df(file, year):
    """To select according to years"""
    df = into_field(file)
    df = df[df['YEAR'] == year]
    return df

def geolocc(file, year, user_inp):
    df = modify_df(file, year)
    geolocator = Nominatim(user_agent="Map_app")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1/20)
    places = list(df['PLACES'])
    coor = []
# 
    for i in places:
        try:
            res_0 = str(geolocator.geocode(i).latitude)
            res_1 = str(geolocator.geocode(i).longitude)
            res = res_0, res_1
            coor.append(res)
        except AttributeError:
            coor.append('None')

    df['COORDINATES'] = coor
    df = df[df['COORDINATES'] != 'None']
    distance = []
    for elem in list(df['COORDINATES']):
        miles = geodesic(user_inp, elem).miles
        distance.append(round(miles, 2))

    # distance_1 = [round(dist, 2) for dist in distance]
    df['DISTANCE'] = distance
    df = df.sort_values(by=['DISTANCE'])
    df = df[:10]
    return df

def map_work(file, year, user_inp):
    """To generate map"""
    df = geolocc(file, year, user_inp)
    today = date.today()
    df_today = geolocc(file,str(int(str(today).split('-')[0])-1), user_inp)
    map = folium.Map(location=[user_inp[0], user_inp[1]], tiles="Stamen Terrain", zoom_start=10)
    folium.Marker([user_inp[0], user_inp[1]], popup="You're here", icon=folium.Icon(color='darkgreen', icon="home")).add_to(map)
    lst = []
    fg_pp = folium.FeatureGroup(name="Film markers")
    fg_today = folium.FeatureGroup(name="This year")

    for i in range(len(list(df['PLACES']))):
        res = list(df['PLACES'])[i], list(df['TITLES'])[i]
        lst.append(res)
    for j in range(len(lst)):
        folium.Marker([list(df['COORDINATES'])[j][0], list(df['COORDINATES'])[j][1]], popup="{}".format(list(df['TITLES'])[j]), icon=folium.Icon(color='red')).add_to(fg_pp)

    lst_1 = []
    for yer in range(len(list(df_today['PLACES']))):
        res_1 = list(df_today['PLACES'])[yer], list(df_today['TITLES'])[yer]
        lst_1.append(res_1)
    for jer in range(len(lst_1)):
        folium.Marker([list(df_today['COORDINATES'])[jer][0], list(df_today['COORDINATES'])[jer][1]], popup="{}".format(list(df_today['TITLES'])[jer]), icon=folium.Icon(color='pink')).add_to(fg_today)
    
    map.add_child(fg_pp)
    map.add_child(fg_today)
    map.add_child(folium.LayerControl())
    return map.save("Map_2.html")


def last_func(file):
    """Checks user input and creates map"""
    user_data = where_user()
    if user_data[0].split(',') == 1:
        return "Error, try again"
    else:
        try:
            int(user_data[1])
        except ValueError:
            return "Error, try again"
        try:
            return map_work(file, user_data[1], user_data[0].split(','))
        except ValueError:
            return "Error, try again"
print(last_func('locations_smaller'))
    