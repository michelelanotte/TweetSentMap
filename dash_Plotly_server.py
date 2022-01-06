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

global df

app = dash.Dash("SEntiment On Place Tweet")


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
            "marginLeft": "5px",
            "verticalAlign": "top",
        }),
        html.Div([
                html.H1("Selected area", style={'textAlign': 'center', 'fontSize': 32}),
                dcc.Graph(id="selected-area", figure=fig_selected_area)
            ],
            style={
                "width": "70%",
                "marginTop": "5%",
                "marginLeft": "auto",
                "marginRight": "auto",
                "borderStyle": "solid",
                "borderColor": "black"
        })
    ])   


def show_map_bokeh(city, dict_coordinates_midpoint, dict_coordinates_bbox):   
    midpoint_lat = dict_coordinates_midpoint[city][0]
    midpoint_long = dict_coordinates_midpoint[city][1]
    
    #Size of points in the map
    size = df.shape[0]
    df["Size"] = [5 for i in range(size)]
    
    title = "Plotting Sentiment for " + city + " city"
    fig_map = set_bbox(df, midpoint_lat, midpoint_long)
       
    #plot percentuale sentiment positivi e negativi
    fig_pie = px.pie(df, names="Sentiment", color='Sentiment', height=350)
    fig_pie.update_traces(hovertemplate=None, title="Sentiment percentage", showlegend=False)
    
    fig_selected_area = fig_map
    view_page(title, fig_map, fig_pie, fig_selected_area)

    
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
    Input('bbox', 'selectedData')  #acquisizione dei punti inclusi nella selected box o nel lasso selezionato
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
        
        row = findRowByCoordinate(df, coords)
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



"""********************************** MAIN **********************************"""
locality = ["wellington", "new york", "san francisco", "sydney", "london"]

#Dictionary which will contain the midpoints of the cities indicate as keys.
#the elements will be in the form: <lat, lon>
dict_coords_midpoint = dict()

#Dictionary which will contain the bbox of the cities indicate as keys
#the elements will be in the form: <<lat_min, lat_max>, <lon_min, lon_max>>
dict_coords_bbox = dict()
dict_coords_midpoint, dict_coords_bbox = setMidpointAndBBox(locality)

filename = "dataset/sentiments_and_coords.tsv" 
dataset = pd.read_csv(filename, sep = '\t', encoding = "utf-8", header = 0)

#The Wellington map is shown by default at system launch
df = getDataframeByCity(dataset, locality[0], dict_coords_bbox)  
show_map_bokeh(locality[0], dict_coords_midpoint, dict_coords_bbox)    
    
    
if __name__ == '__main__':
    app.run_server(debug=True)
    #app.run_server(debug=False,dev_tools_ui=False,dev_tools_props_check=False)