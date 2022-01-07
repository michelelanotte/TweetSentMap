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

app = dash.Dash("Sentiment On Place Twitter")
view_info = ViewSOPInfo()


def view_page():
    buttons = html.Div(
        [
            dbc.Button("Wellington", id="we", outline=True, color="info", className="me-1"),
            dbc.Button("San Francisco", id="sf", outline=True, color="info", className="me-1"),
            dbc.Button("New York", id="ny", outline=True, color="info", className="me-1"),
            dbc.Button("Sydney", id="sy", outline=True, color="info", className="me-1"),
            dbc.Button("London", id="lo", outline=True, color="info", className="me-1"),
        ]
    )
    
    app.layout = html.Div([
        html.Div([
            html.H1("Sentiment On Place Twitter", style={'textAlign': 'center', 'fontSize': 32, 'fontWeight': 'bold'})]
        ),
        html.Hr(),
        html.Div([
            dbc.Container([buttons])],
            style={
                'textAlign': 'center'
            }
        ),
        html.Hr(),
        html.Div([
            html.H1(view_info.get_title(), id="title", style={'textAlign': 'center', 'fontSize': 24, 'marginTop': '50px'})]
        ),
        html.Div([
            dcc.Graph(id="bbox", figure=view_info.get_fig_map())
            ],
            style={
                "display": "inline-block",
                "width": "70%",
                "marginLeft": "50px",            
            }
        ),
        html.Div([
            html.Div([
                dcc.Graph(id="filter-percentage-sentiments", figure=view_info.get_fig_pie())
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
                dcc.Graph(id="selected-area", figure=view_info.get_fig_selected_area(), config={'displayModeBar': False})
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


"""
This method, starting from the input city, builds the map with the tweets of that city and the pie diagram 
with the percentages of positive tweets and negative.
"""
def create_map_bokeh(city):
    df = view_info.get_df_selected_city()
    coords = view_info.get_dict_coords_midpoint()[city]
    midpoint_lat = coords[0]
    midpoint_long = coords[1]
    
    #Size of points in the map
    size = df.shape[0]
    df["Size"] = [5 for i in range(size)]
    view_info.set_df_selected_city(df)
    
    fig_map = set_bbox(df, midpoint_lat, midpoint_long)
       
    #plot percentuale sentiment positivi e negativi
    fig_pie = px.pie(df, names="Sentiment", color='Sentiment', height=350)
    fig_pie.update_traces(hovertemplate=None, title="Sentiment percentage", showlegend=False)
     
    return fig_map, fig_pie

    
def set_bbox(source, midpoint_lat, midpoint_long):
    token = "pk.eyJ1IjoibWxhbm90dGUxNSIsImEiOiJja3c0dmR6d3MwODhmMnVyaDE2aHpxMG11In0.Z9815N56yl0BfjRIiaFUkA"
    px.set_mapbox_access_token(token)
    fig_map = px.scatter_mapbox(source, hover_name="Tweet", lat="Lat", lon="Lon",
                            color="Sentiment", zoom=12, size="Size", size_max=10,
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
    fig_pie = view_info.get_fig_pie()
    fig_selected_area = view_info.get_fig_selected_area()
    if selectedData:
        df = view_info.get_df_selected_city()
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
    

@app.callback(
    Output('title', 'children'), 
    Output('bbox', 'figure'),
    Input('we', 'n_clicks'), 
    Input('ny', 'n_clicks'), 
    Input('sy', 'n_clicks'), 
    Input('sf', 'n_clicks'), 
    Input('lo', 'n_clicks')
)
def display_city_map(we, ny, sy, sf, lo):  
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if 'we' in changed_id:
        city = "wellington"
    elif 'ny' in changed_id:
        city = "new york"
    elif 'sy' in changed_id:
        city = "sydney"
    elif 'sf' in changed_id:
        city = "san francisco"
    elif 'lo' in changed_id:
        city = "london"
    
    df = getDataframeByCity(city, view_info.get_dataset(), view_info.get_dict_coords_bbox())
    view_info.set_df_selected_city(df)
    fig_map, fig_pie = create_map_bokeh(city) 
    title = "Plotting Sentiments for " + city.capitalize() + " city"
    return title, fig_map

  
def setViewInfo():
    locality = view_info.get_cities()
    
    dict_coords_midpoint, dict_coords_bbox = setMidpointAndBBox(locality)
    view_info.set_dict_coords_midpoint(dict_coords_midpoint)
    view_info.set_dict_coords_bbox(dict_coords_bbox)
    
    filename = "dataset/sentiments_and_coords.tsv" 
    view_info.set_dataset(pd.read_csv(filename, sep = '\t', encoding = "utf-8", header = 0))
    
    #The Wellington map is shown by default at system launch
    city = locality[0]
    #get tweets found in city area
    view_info.set_df_selected_city(getDataframeByCity(city, view_info.get_dataset(), view_info.get_dict_coords_bbox()))
    fig_map, fig_pie = create_map_bokeh(city) 
    view_info.set_fig_map(fig_map)
    view_info.set_fig_selected_area(fig_map)
    view_info.set_fig_pie(fig_pie)
    view_info.set_title("Plotting Sentiments for " + city.capitalize() + " city")
    
    return view_info
    

"""********************************START SERVER********************************"""
view_info = setViewInfo()    
if __name__ == '__main__':
    view_page()
    app.run_server(debug=True)
    #app.run_server(debug=False,dev_tools_ui=False,dev_tools_props_check=False)