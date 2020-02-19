import plotly.graph_objects as go
import pandas as pd
import numpy as np
import math

#read in a list of all countries
countries = pd.read_csv('https://raw.githubusercontent.com/jerguy1928/refugee_map/master/country_centroid_locations.csv')
countries.head()

#read in a list of refugee movements
travel_paths = pd.read_csv('https://raw.githubusercontent.com/jerguy1928/refugee_map/master/movements.csv')

#sorting the data (my functions require the data to be sorted but my data isn't sorted)
travel_paths.head()
travel_paths.sort_values(["origin","year"],inplace=True)
travel_paths = travel_paths.reset_index(drop=True)

#creating two dictionaries for each countries corresponding latitudes/longitudes
country_lat = dict(zip(countries['country'],countries['lat']))
country_long = dict(zip(countries['country'],countries['long']))

#creates a world map as a backdrop
fig = go.Figure(data=go.Choropleth(
    locations = countries['country_code_3'],
    z = countries['zero'],
    text = countries['country'],
    hoverinfo= 'text',
    marker_line_color='darkgray',
    marker_line_width=0.5,
    showscale= False,
    
))

# creates the dropdown menu. Each menu entry works by passing a T/F array to the 'visible' property for the map
def dropdown_menu():
    mentioned_countries = []
    menu_data = []
    menu = []
    k = 0
    for j in range(len(travel_paths)):
        
        ORIGIN = travel_paths['origin'][j]
        desc  = ["Movement of refugees from ",ORIGIN]
        msg = ''.join(desc)
        false_array = list(np.zeros(len(travel_paths),bool))

        if ORIGIN not in mentioned_countries:
            mentioned_countries.append(ORIGIN)
            false_array.insert(j+1,True)
            false_array[0] = True
            menu_data.insert(k,false_array)
            menu.insert(k,dict(args = [{"visible": menu_data[k]},{"title": msg} ], label = ORIGIN, method = "update"))
            k += 1
        else:
            menu_data[k-1].insert(j+1,True)
    #these two lines are used for a 'Show All' paths (all true array)
    true_array = list(np.ones(len(travel_paths),bool))
    menu.insert(0,dict(args = [{"visible": true_array},{"title": "Currently showing all refugees"} ], label = "<i>Show all</i>", method = "update"))
    return menu

#this dictionary descibes the size of each path based on the number of refugees
refugee_lvl = {
    (0,20):0.5,
    (21,50):1,
    (51,100):1.5,
    (101,500):2,
    (501,1000):2.5,
    (1001,10000):3,
    (10001,50000):3.5,
    (50001,100000):4,
    (100001,1000000):4.5,
    (1000001,5000000):5
}

#this dictionary is used for the size of each arrow for each path
marker_lvl = {
    (0,20):3,
    (21,50):3.5,
    (51,100):4,
    (101,500):4.5,
    (501,1000):5,
    (1001,10000):5.5,
    (10001,50000):6,
    (50001,100000):6.5,
    (100001,1000000):7,
    (1000001,5000000):7.5
}
# my code calculates the angle of travel and assigns an appropriate 'arrowhead' (my makeshift draw arrow solution)
angle_calc = {
    (0,22.5):'triangle-up',
    (22.501,67.5):'triangle-ne',
    (67.501,112.5):'triangle-right',
    (112.501,157.5):'triangle-se',
    (157.501,202.5):'triangle-down',
    (202.501,247.5):'triangle-sw',
    (247.501,292.5):'triangle-left',
    (292.501,337.5):'triangle-nw',
    (337.5,360):'triangle-up',
}
#this function returns a value from a dictionary with range values
def get_key(table,num):
    for key in table:
        if key[0] < num < key[1]:
            result = table[key]
            return result
# this function calculates the angle of travel for the travel path
def get_shape(start_lon,start_lat,end_lon,end_lat):
    s2 = (end_lat - start_lat)/(end_lon-start_lon)
    angle = math.atan((900000-s2)/(1+(900000*s2)))
    angle_degrees = math.degrees(angle)
    if start_lat > end_lat:
        angle_degrees +=180
    elif angle_degrees < 0 and start_lat < end_lat:
        angle_degrees += 360
    return get_key(angle_calc,angle_degrees)

#this function draws the traces
def trace_creator():
    #These dictionaries define options for if the refugee movement is internal (IDP) or external (REF)
    IDP = {
        'mode':'markers',
        'size':15,
        'person_type':'IDPs',
        'opacity':1,
        'color':'blue',
        'symbol':'circle-open'
    }
    REF = {
        'mode':'lines+markers',
        'person_type':'Refugees',
        'opacity':[0,1],
        'color':'green',
    }
    #loop through all travel paths
    for i in range(len(travel_paths)):
        ORIGIN = travel_paths['origin'][i]
        DESTINATION = travel_paths['destination'][i]
        YEAR = travel_paths['year'][i]
        REFUGEES = travel_paths['refugees'][i]
        ORIGIN_LAT = country_lat.get(ORIGIN)
        ORIGIN_LON = country_long.get(ORIGIN)
        DEST_LAT = country_lat.get(DESTINATION)
        DEST_LON = country_long.get(DESTINATION)
        lat_list = [ORIGIN_LAT]
        lon_list = [ORIGIN_LON]

        #If internal movement
        if ORIGIN == DESTINATION:
            mode_val = IDP.get('mode')
            size_val = IDP.get('size')
            person_type = IDP.get('person_type')
            marker_opacity = IDP.get('opacity')
            marker_color = IDP.get('color')
            marker_symbol = IDP.get('symbol')
        #if external movement
        else:
            lat_list.append(DEST_LAT)
            lon_list.append(DEST_LON)
            mode_val = REF.get('mode')
            size_val = get_key(marker_lvl,REFUGEES)
            person_type = REF.get('person_type')
            marker_opacity = REF.get('opacity')
            marker_color = REF.get('color')
            marker_symbol = get_shape(ORIGIN_LON,ORIGIN_LAT,DEST_LON,DEST_LAT)
        text_list = [ORIGIN,' → ', DESTINATION, "<br>", person_type, ": ", format(REFUGEES,',d')]    
        s = ''
        # passing the values from above to the add_trace method
        fig.add_trace(
            go.Scattergeo(
                    lat = lat_list,
                    lon = lon_list,
                    mode = mode_val,
                    marker= dict(
                        size = size_val,
                        symbol = marker_symbol,
                        color = marker_color,
                        opacity = marker_opacity
                        ),
                    line = dict(width = get_key(refugee_lvl,REFUGEES),color = 'red'),
                    showlegend= True,
                    legendgroup= str(YEAR),
                    name = str(YEAR),
                    text= s.join(text_list),
                    hoverinfo= 'text'
                    )),
trace_creator()
#adding titles/dropdown menu
fig.update_layout(
    updatemenus=[
        go.layout.Updatemenu(
            buttons = dropdown_menu(),
            direction="down",
            pad={"r": 10, "t": 10},
            showactive=True,
            x=0.37,
            xanchor="left",
            y= 1.08,
            yanchor="top"
        ),
    ],
    title_text = 'Movement of UNHCR Refugees (Choose origin country from the list)',
    geo = go.layout.Geo(
        projection_type = 'mercator',
        showland = True,
        showcountries= True,
        landcolor = 'rgb(243, 243, 243)',
        countrycolor = 'rgb(204, 204, 204)',  
    ),    
)
#draw the figures
fig.show()

