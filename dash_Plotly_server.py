# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 11:18:56 2021

@author: Utente
"""

import os
from utils import *
import pandas as pd
import plotly.express as px
import webbrowser

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import json
import numpy as np

#istanziazione app
app = dash.Dash(__name__)


#dict con midpoint delle città
dict_coordinates_midpoint = {}

#lista ordinata di latitudini dei tweet(es. i-esima latitudine corrisponde a i-esimo tweet)
lat_list = []

#lista ordinata di longitudini dei tweet(es. i-esima longitudine corrisponde a i-esimo tweet)
long_list = []

#lista ordinata di sentiment dei tweet(es. i-esimo sentiment corrisponde a i-esimo tweet)
sentiment_list = []

tweet_list = []

#gli elementi del dizionario(un elemento per ogni città), coincidono con tuple dove il primo elemento indica
#la latitudine e il secondo la longitudine della città in questione
dict_coordinates_midpoint["we"] = (-41.29219543948838, 174.77965367381586)
dict_coordinates_midpoint["sf"] = (37.77477322350731, -122.44124089571484)
dict_coordinates_midpoint["ny"] = (40.757633413547566, -73.99953802592054)
dict_coordinates_midpoint["sy"] = (-33.82424746385911, 151.21964009440705)
dict_coordinates_midpoint["lo"] = (51.515313767102526, -0.13044504826384007)


def view_page(title, fig_map, fig_pie, fig_selected_area):
    app.layout = html.Div([
        html.H1(title, style={'textAlign': 'center', 'fontSize': 32}),
        html.Div([
            dcc.Graph(id="bbox", figure=fig_map)
            ],
            style={
                "display": "inline-block",
                "width": "70%"
            }
        ),
        html.Div([
            html.Div([
                dcc.Graph(id="filter-percentage-sentiments", figure=fig_pie)
            ]),
        ], 
        style={
            "display": "inline-block",
            "width": "25%",
            "margin-left": "10px",
            "verticalAlign": "top",
        }),
        html.Div([
                html.H1("Selected area", style={'textAlign': 'center', 'fontSize': 32}),
                dcc.Graph(id="selected-area", figure=fig_selected_area)
            ],
            style={
                "width": "70%",
                "margin-top": "5%",
                "margin-left": "auto",
                "margin-right": "auto",
                "border-style": "solid",
                "border-color": "black"
        })
    ])   


def show_map_bokeh(dict_tweet, key_coord):   
    tweets = []
    #ciclo utile per il riempimento di lat_list, long_list e sentiment_list
    for key in dict_tweet:
        sentiment = dict_tweet[key][1]
        long, lat = generate_coord(key_coord)
        lat_list.append(lat)
        long_list.append(long)
        sentiment_list.append(sentiment.lower().capitalize())
        tweet_list.append(dict_tweet[key][0])
        
        #dimensione dei punti nella mappa
        size_list = [5 for i in range(len(lat_list))]
        

    #tweet_list = [cleaning_URLs(line) for line in tweets]
           
    source = pd.DataFrame()
    source = {'lat': lat_list, 'long': long_list, 'sentiment': sentiment_list, 'tweet': tweet_list, 'size': size_list}
    
    #lettura midpoint della città indicata da key_coord
    midpoint_lat = dict_coordinates_midpoint[key_coord][0]
    midpoint_long = dict_coordinates_midpoint[key_coord][1]
    
    city = get_city_name(key_coord)
    title = "Plotting Sentiment for " + city + " city"
    fig_map = set_bbox(source, midpoint_lat, midpoint_long)
       
    #plot percentuale sentiment positivi e negativi
    fig_pie = px.pie(source, names="sentiment", color='sentiment', height=350)
    fig_pie.update_traces(hovertemplate=None, title="Sentiment percentage", showlegend=False)
    
    fig_selected_area = set_bbox(source, midpoint_lat, midpoint_long)
    
    view_page(title, fig_map, fig_pie, fig_selected_area)

    
def set_bbox(source, midpoint_lat, midpoint_long):
    token = "pk.eyJ1IjoibWxhbm90dGUxNSIsImEiOiJja3c0dmR6d3MwODhmMnVyaDE2aHpxMG11In0.Z9815N56yl0BfjRIiaFUkA"
    px.set_mapbox_access_token(token)
    fig_map = px.scatter_mapbox(source, hover_name="tweet", lat="lat", lon="long",
                            color="sentiment", zoom=11, size="size", size_max=10,
                            center={"lat": midpoint_lat, "lon": midpoint_long})
    #fig_map.update_layout(mapbox_style="open-street-map")
    fig_map.update_layout(margin={"r":10,"t":20,"l":10,"b":1})
    fig_map.update_layout(legend=dict(
        title="Colors for sentiments:", orientation="h", y=1, yanchor="bottom", x=0.5, xanchor="center"
    ))
    fig_map.update_traces(mode="markers", hovertemplate=None) 
    
    return fig_map

    
"""
Sfruttando lon e lat in input, si ricavano gli indici di lista in cui si trovano lon e lat 
rispettivamente in long_list e lat_list. Dopodichè s'intersecano gli indici comuni poichè ci sarà necessariamente
un tweet in tali posizioni che farà riferimento alla coppia di coordinate <lon, lat>"""
def get_indexes_for_tweet(lat, lon):
    #ricerca di posizioni in lat_list in cui si trova il valore lat
    indexes_lat = set(np.where(np.asarray(lat_list) == lat)[0])
    #ricerca di posizioni in long_list in cui si trova il valore lon
    indexes_lon = set(np.where(np.asarray(long_list) == lon)[0])
    #indici comuni per lat o lon dati in input (così da poter rilevare i tweet inerenti alle coordinate scandite dagli indici trovati dall'intersection)
    indexes = indexes_lat.intersection(indexes_lon)
    return indexes
    

@app.callback(
    Output('filter-percentage-sentiments', 'figure'), 
    Output('selected-area', 'figure'), 
    Input('bbox', 'selectedData')  #acquisizione dei punti inclusi nella selected box o nel lasso selezionato
)
def display_selected_data(selectedData): 
    points = selectedData["points"] 
    print(points)
    
    sentiments = []
    latitude_list = []
    longitude_list = []
    tweets_list = []
    #si tiene conto delle coordinate già esaminate poichè può succedere che in una certa coordinata ci siano più tweet.
    #I sentiment di questi tweet vengono estratti nella prima chiamata della funzione get_indexes_for_tweet
    coords_checked = []
    for i in range(len(points)):
        lat = points[i]['lat']
        lon = points[i]['lon']
        tweet = points[i]['hovertext']
        coords = tuple((lat, lon))
        if coords not in coords_checked:
            coords_checked.append(coords)
            """
            viene restituito un set di indici perchè può succedere che per una coppia di coordinate ci siano 
            più sentimenti(nonchè più tweet con uguali coordinate), quindi è opportuno prelevarli tutti
            """
            common_indexes = get_indexes_for_tweet(lat, lon) 
            sentiments.extend([sentiment_list[i] for i in common_indexes])
            
            latitude_list.extend([lat_list[i] for i in common_indexes])
            longitude_list.extend([long_list[i] for i in common_indexes])
            tweets_list.extend([tweet_list[i] for i in common_indexes])
            
    df = pd.DataFrame()
    df = {'sentiment': sentiments}
    fig_pie = px.pie(df, names='sentiment', color='sentiment')
    fig_pie.update_traces(hovertemplate=None, title="Sentiment percentage", showlegend=False)
    
    #dimensione dei punti nella mappa
    size_list = [5 for i in range(len(latitude_list))]
    
    
    """********************Visualizzazione delle coordinate selezionate nella bbox**************************"""
    source = pd.DataFrame()
    source = {'lat': latitude_list, 'long': longitude_list, 'sentiment': sentiments,
                    'tweet': tweets_list, 'size': size_list}
    
    fig_selected_area = px.scatter_mapbox(source, lat="lat", lon="long", hover_name="tweet",
                            color="sentiment", size="size", zoom=12, size_max=10) 
    fig_selected_area.update_layout(margin={"r":10,"t":20,"l":10,"b":1})
    fig_selected_area.update_layout(legend=dict(
        title="Colors for sentiments:", orientation="h", y=1, yanchor="bottom", x=0.5, xanchor="center"
    ))
    fig_selected_area.update_traces(mode="markers", hovertemplate=None) 
    
    return fig_pie, fig_selected_area



"""********************************** MAIN **********************************"""
"""#lettura degli output dei vari sistemi di sentiment analysis
files_tsv = []
files_tsv = [file for file in os.listdir('predictions.')]  


for i, tsv in enumerate(files_tsv):
    df = read_tsv(tsv)
    dict_tweet_we, dict_tweet_sf, dict_tweet_ny, dict_tweet_sy = split_dataframe(df)
    
    #decommentare quando neccessario per evitare spreco di richieste
    show_map_bokeh(dict_tweet_we, "we")
    #show_map_bokeh(dict_tweet_sf, "sf")
    #show_map_bokeh(dict_tweet_ny, "ny")
    #show_map_bokeh(dict_tweet_sy, "sy")
    #show_map_bokeh(dict_tweet_sy, "lo")     
    if i == 0:
        break"""

#TO DO: leggere file tsv le cui righe sono nella forma <tweet, sentiment, coordinate> e visualizzare questi dati su mappa
    
    
if __name__ == '__main__':
    #app.run_server(debug=True)
    app.run_server(debug=False,dev_tools_ui=False,dev_tools_props_check=False)