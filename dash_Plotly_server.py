# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 11:18:56 2021

@author: Utente
"""

from utility.utils import pd, setMidpointAndBBox, getDataframeByCity, findRowByCoordinate
import plotly.express as px

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

global df, dataset

#Dictionary which will contain the midpoints of the cities indicate as keys.
#the elements will be in the form: <lat, lon>
global dict_coords_midpoint

#Dictionary which will contain the bbox of the cities indicate as keys
#the elements will be in the form: <<lat_min, lat_max>, <lon_min, lon_max>>
global dict_coords_bbox

app = dash.Dash("Sentiment On Place Twitter", external_stylesheets=[dbc.themes.SPACELAB])


def view_page(title, fig_map, fig_pie):
    nav_contents = [
        dbc.NavItem(dbc.NavLink("Wellington", active=True)),
        dbc.NavItem(dbc.NavLink("San Francisco", href="")),
        dbc.NavItem(dbc.NavLink("New York", href="")),
        dbc.NavItem(dbc.NavLink("Sydney", href="")),
        dbc.NavItem(dbc.NavLink("London", href="")),
    ]
    nav = dbc.Nav(nav_contents, pills=True, fill=True)
    
    app.layout = html.Div([
        html.Div([
            html.H1("Sentiment On Place Twitter", style={'textAlign': 'center', 'fontSize': 32, 'fontWeight': 'bold'})]
        ),
        html.Div([
            dbc.Container([nav], fluid=True)]
        ),
        html.Hr(),
        html.Div([
            html.H1(title, id="title", style={'textAlign': 'center', 'fontSize': 24, 'marginTop': '50px'})]
        ),
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
            "marginLeft": "5px",
            "verticalAlign": "top",
        }),
        html.Div([
                html.H1("Selected area", style={'textAlign': 'center', 'fontSize': 32}),
                dcc.Graph(id="selected-area", figure=fig_map, config={'displayModeBar': False})
            ],
            style={
                "width": "70%",
                "marginTop": "5%",
                "marginLeft": "auto",
                "marginRight": "auto",
                "borderStyle": "solid",
                "borderColor": "black"
        }),
        html.Div([
            html.H1(id="pippo", style={'textAlign': 'center', 'fontSize': 24, 'marginTop': '50px'})]
        ),
    ])   


"""
This method, starting from the input city, builds the map with the tweets of that city and the pie diagram 
with the percentages of positive tweets and negative.
"""
def create_map_bokeh(city):
    list_of_globals = globals()
    midpoint_lat = list_of_globals["dict_coords_midpoint"][city][0]
    midpoint_long = list_of_globals["dict_coords_midpoint"][city][1]
    
    #Size of points in the map
    size = list_of_globals["df"].shape[0]
    list_of_globals["df"]["Size"] = [5 for i in range(size)]
    
    fig_map = set_bbox(list_of_globals["df"], midpoint_lat, midpoint_long)
       
    #plot percentuale sentiment positivi e negativi
    fig_pie = px.pie(list_of_globals["df"], names="Sentiment", color='Sentiment', height=350)
    fig_pie.update_traces(hovertemplate=None, title="Sentiment percentage", showlegend=False)
    
    
    return fig_map, fig_pie

    
def set_bbox(source, midpoint_lat, midpoint_long):
    token = "pk.eyJ1IjoibWxhbm90dGUxNSIsImEiOiJja3c0dmR6d3MwODhmMnVyaDE2aHpxMG11In0.Z9815N56yl0BfjRIiaFUkA"
    px.set_mapbox_access_token(token)
    fig_map = px.scatter_mapbox(source, hover_name="Tweet", lat="Lat", lon="Lon",
                            color="Sentiment", zoom=11, size="Size", size_max=10,
                            center={"lat": midpoint_lat, "lon": midpoint_long})
    #fig_map.update_layout(mapbox_style="open-street-map")
    fig_map.update_layout(margin={"r":10,"t":20,"l":10,"b":1})
    fig_map.update_layout(legend=dict(
        title="Colors for sentiments:", orientation="h", y=1, yanchor="bottom", x=0.5, xanchor="center"
    ))
    fig_map.update_traces(mode="markers", hovertemplate=None) 
    
    return fig_map


@app.callback(
    Output('filter-percentage-sentiments', 'figure'), 
    Output('selected-area', 'figure'), 
    Input('bbox', 'selectedData')  #acquisition of the points included in the selected box or in the selected period
)
def display_selected_data(selectedData):
    fig_pie = {}
    fig_selected_area = {}
    points = selectedData["points"] 
    
    data = []
    for i in range(len(points)):
        lat = points[i]['lat']
        lon = points[i]['lon']
        coords = (lat, lon)
        
        row = findRowByCoordinate(list_of_globals["df"], coords)
        if row is not None:
            data.append(row)
    
    selected_df = pd.DataFrame(data, columns = ["Tweet", "Sentiment", "Lat", "Lon", "Size"])
    fig_pie = px.pie(selected_df, names = 'Sentiment', color = 'Sentiment')
    fig_pie.update_traces(hovertemplate = None, title = "Sentiment percentage", showlegend = False)  
    
    
    """********************Display of the coordinates selected in the bbox**************************"""    
    fig_selected_area = px.scatter_mapbox(selected_df, lat="Lat", lon="Lon", hover_name="Tweet",
                            color="Sentiment", size="Size", zoom=14, size_max=10) 
    fig_selected_area.update_layout(margin={"r":10,"t":20,"l":10,"b":1})
    fig_selected_area.update_layout(legend=dict(
        title = "Colors for sentiments:", orientation="h", y=1, yanchor="bottom", x=0.5, xanchor="center"
    ))
    fig_selected_area.update_traces(mode="markers", hovertemplate=None) 
    
    return fig_pie, fig_selected_area
    




#TO DO**********************************
"""@app.callback(
    #Output('pippo', 'children'), 
    Input('select-city', 'value')
)
def display_city_map(city):
    list_of_globals = globals()
    list_of_globals['df'] = getDataframeByCity(city, list_of_globals["dataset"], list_of_globals["dict_coords_bbox"])
    fig_map, fig_pie = create_map_bokeh(city) 
    return {}.format(value)"""

  
"""********************************** MAIN **********************************"""
locality = ["wellington", "new york", "san francisco", "sydney", "london"]

#get all global variables
list_of_globals = globals()
list_of_globals["dict_coords_midpoint"], list_of_globals["dict_coords_bbox"] = setMidpointAndBBox(locality)

filename = "dataset/sentiments_and_coords.tsv" 
list_of_globals["dataset"] = pd.read_csv(filename, sep = '\t', encoding = "utf-8", header = 0)

#The Wellington map is shown by default at system launch
city = locality[3]
list_of_globals["df"] = getDataframeByCity(city, list_of_globals["dataset"], list_of_globals["dict_coords_bbox"])  
fig_map, fig_pie = create_map_bokeh(city) 
title = "Plotting Sentiments for " + city.capitalize() + " city"
view_page(title, fig_map, fig_pie)
    
    
if __name__ == '__main__':
    app.run_server(debug=True)
    #app.run_server(debug=False,dev_tools_ui=False,dev_tools_props_check=False)