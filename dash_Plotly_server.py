# -*- coding: utf-8 -*-
"""
Created on Fri Jan  7 12:04:04 2022

@author: Utente
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 11:18:56 2021

@author: Utente
"""

from utility.utils import pd, setMidpointAndBBox, getDataframeByCity, findRowByCoordinate
from utility.viewSOPInfo import ViewSOPInfo
import plotly.express as px

import dash
from dash import dcc, html, callback_context
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

app = dash.Dash("Sentiment On Place Twitter", external_stylesheets=[dbc.themes.SPACELAB])
view_info = ViewSOPInfo()


def viewPage():
    buttons = html.Div(
        [
            dbc.Button("Wellington", id="city0", outline=True, color="info", className="me-1 btn-menu"),
            dbc.Button("San Francisco", id="city1", outline=True, color="info", className="me-1 btn-menu"),
            dbc.Button("New York", id="city2", outline=True, color="info", className="me-1 btn-menu"),
            dbc.Button("Sydney", id="city3", outline=True, color="info", className="me-1 btn-menu"),
            dbc.Button("London", id="city4", outline=True, color="info", className="me-1 btn-menu"),
        ],
        style={'whiteSpace': 'nowrap'}
    )
    
    app.layout = html.Div([
        html.Div([
            html.H1("Sentiment On Place Twitter", className="title")]
        ),
        html.Hr(),
        html.Div([
            dbc.NavbarBrand(buttons),
            ],
            style={
                "textAlign": "center"
            }
        ),
        html.Hr(style={"marginTop": "-10px"}),
        html.Div([
            html.H1(view_info.get_title(), id="title", className="subtitle")
        ]),
        html.Div([
            html.Div([
                dcc.Graph(id="bbox", figure=view_info.get_fig_map())
            ], className="bbox-div"
            ),
            html.Div([
                dcc.Graph(id="filter-percentage-sentiments", figure=view_info.get_fig_pie(), 
                          config={'displayModeBar': False}, style={"textAlign": "center"})
                ],
                style={
                    "display": "inline-block",
                    "width": "25%",
                    "marginLeft": "10px",
                    "verticalAlign": "top",
                })
        ]),
        html.Div([
                html.H1("Selected area", className="subtitle"),
                dcc.Graph(id="selected-area", figure=view_info.get_fig_selected_area(), config={"displayModeBar": False})
            ], className="selected-area-div"
        )
    ])   


"""
This method is used to manage two events: 
    1) selection of a city, in this case the map of that city and the percentages of negative and 
        positive sentiment will be shown;
    2) selection of an area of ​​the current city, in this case the percentages of the feelings inherent 
        to the selection and the map with focus on the selected area will be shown
"""
@app.callback(
    Output("title", "children"), 
    Output("bbox", "figure"),
    Output("filter-percentage-sentiments", "figure"), 
    Output("selected-area", "figure"), 
    [Input(f"city{i}", "n_clicks") for i in range(0, 5)],
    Input("bbox", "selectedData")  #acquisition of the points included in the selected box or in the selected period
)
def updateByCallback(city1, city2, city3, city4, city5, selectedData):
    title = view_info.get_title()
    bbox = view_info.get_fig_map()
    fig_pie = view_info.get_fig_pie()
    fig_selected_area = view_info.get_fig_selected_area()
    changed_id = [p["prop_id"].replace(".n_clicks", "") for p in callback_context.triggered][0]
    if changed_id[:4] == "city":
        #Trigger selection of a city
        city = view_info.get_city_by_index(int(changed_id[4:5]))
        title, bbox, fig_pie, fig_selected_area = displayCityMap(city)
    elif changed_id[:4] == "bbox":
            #Trigger selection of an area of ​​the current city
            fig_pie, fig_selected_area = displaySelectedData(selectedData["points"])
    return title, bbox, fig_pie, fig_selected_area
        

def displaySelectedData(selected_points):
    df = view_info.get_df_selected_city()
    data = []
    for i in range(len(selected_points)):
        lat = selected_points[i]["lat"]
        lon = selected_points[i]["lon"]
        coords = (lat, lon)
        
        row = findRowByCoordinate(df, coords)
        if row is not None:
            data.append(row)
    
    selected_df = pd.DataFrame(data, columns = ["Tweet", "Sentiment", "Lat", "Lon", "Size"])
    
    fig_pie = computePlotlyPie(selected_df)
              
    #Map creation for selected tweets
    fig_selected_area = computeMapbox(selected_df, zoom=14)
    view_info.set_fig_selected_area(fig_selected_area)

    return fig_pie, fig_selected_area
    

def displayCityMap(city):  
    df = getDataframeByCity(city, view_info.get_dataset(), view_info.get_dict_coords_bbox())
    view_info.set_df_selected_city(df)
    fig_map, fig_pie = createMapBokeh(city) 
    view_info.set_fig_map(fig_map)
    view_info.set_fig_selected_area(fig_map)
    view_info.set_fig_pie(fig_pie)
    title = "Plotting Sentiments for " + city.capitalize() + " city"
    view_info.set_title(title)
    return title, fig_map, fig_pie, fig_map


"""
This method, starting from the input city, builds the map with the tweets of that city and the pie diagram 
with the percentages of positive tweets and negative.
"""
def createMapBokeh(city):
    df = view_info.get_df_selected_city()
    coords = view_info.get_dict_coords_midpoint()[city]
    midpoint_lat = coords[0]
    midpoint_long = coords[1]
    
    #Size of points in the map
    size = df.shape[0]
    df["Size"] = [5 for i in range(size)]
    view_info.set_df_selected_city(df)
    
    fig_map = computeMapbox(df, midpoint_lat, midpoint_long)
       
    #Positive and negative sentiment percentage plot
    fig_pie = computePlotlyPie(df)
     
    return fig_map, fig_pie


def computeMapbox(source, midpoint_lat=None, midpoint_lon=None, zoom=10):
    token = "pk.eyJ1IjoibWxhbm90dGUxNSIsImEiOiJja3c0dmR6d3MwODhmMnVyaDE2aHpxMG11In0.Z9815N56yl0BfjRIiaFUkA"
    center = {}
    if (midpoint_lat is not None) and (midpoint_lon is not None):
        center = {"lat": midpoint_lat, "lon": midpoint_lon}
    px.set_mapbox_access_token(token)
    fig_map = px.scatter_mapbox(source, hover_name="Tweet", lat="Lat", lon="Lon",
                            color="Sentiment", zoom=zoom, size="Size", size_max=10,
                            center=center, color_discrete_map={"POSITIVE": "#1688ED",
                                                               "NEGATIVE": "#F84858"})
    #fig_map.update_layout(mapbox_style="open-street-map")
    fig_map.update_layout(margin={"r":10,"t":20,"l":10,"b":1})
    fig_map.update_layout(legend=dict(
        title="Colors for sentiments:", orientation="h", y=1, yanchor="bottom", x=0.5, xanchor="center"
    ))
    fig_map.update_traces(mode="markers", hovertemplate=None) 
    return fig_map


def computePlotlyPie(df):
    fig_pie = px.pie(df, names="Sentiment", color='Sentiment', height=380, color_discrete_map={"POSITIVE": "#1688ED",
                                                                                               "NEGATIVE": "#F84858"})
    fig_pie.update_traces(hovertemplate=None, showlegend=False)
    fig_pie.update_layout(title={
        'text' : 'Sentiments percentage',
        'x':0.5,
        'y':0.9,
        'xanchor': 'center',
        'yanchor': 'top'
    })
    return fig_pie


"""
This method sets the initial parameters useful for a first visualization of the contents on the web page.
"""  
def setViewInfo():
    locality = view_info.get_cities()
    
    dict_coords_midpoint, dict_coords_bbox = setMidpointAndBBox(locality)
    view_info.set_dict_coords_midpoint(dict_coords_midpoint)
    view_info.set_dict_coords_bbox(dict_coords_bbox)
    
    filename = "dataset/sentiments_and_coords.tsv" 
    view_info.set_dataset(pd.read_csv(filename, sep = "\t", encoding = "utf-8", header = 0))
    
    #The Wellington map is shown by default at system launch
    city = locality[0]
    #get tweets found in city area
    view_info.set_df_selected_city(getDataframeByCity(city, view_info.get_dataset(), view_info.get_dict_coords_bbox()))
    fig_map, fig_pie = createMapBokeh(city) 
    view_info.set_fig_map(fig_map)
    view_info.set_fig_selected_area(fig_map)
    view_info.set_fig_pie(fig_pie)
    view_info.set_title("Plotting Sentiments for " + city.capitalize() + " city")
    
    return view_info
    

"""********************************START SERVER********************************"""
view_info = setViewInfo()    
if __name__ == "__main__":
    viewPage()
    app.run_server(debug=True)
    #app.run_server(debug=False,dev_tools_ui=False,dev_tools_props_check=False)