import dash
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd
import time
import json
import requests
from datetime import datetime, date

# from lake_connect import flaminggorge, powell_latest, powell


app = dash.Dash(__name__)
app.config['suppress_callback_exceptions']=True


capacities = {'Lake Powell Glen Canyon Dam and Powerplant': 24322000, 'Lake Mead Hoover Dam and Powerplant': 26134000, 'FLAMING GORGE RESERVOIR': 3788700, 'NAVAJO RESERVOIR': 1708600, 'BLUE MESA RESERVOIR': 940800 }

# today = time.strftime("%Y-%m-%d")
today = datetime.now()
year = datetime.now().year
# print(year)
f_date = datetime(year, 1, 1)

# print(today)
delta = today - f_date
days = delta.days
# print(days)


# url = 'https://water.usbr.gov/api/web/app.php/api/series?sites=lakepowell&parameters=Day.Inst.ReservoirStorage.af&start=2020-02-01&end=2020-02-20&format=csv'

# df_water = pd.read_csv('data.csv', skiprows=4)



def river_App():
    return html.Div(
        [
            html.Div([
                html.Div([
                    html.Div([
                        dcc.Link('Home', href='/'),
                    ],
                        className='two columns'
                    ),
                    html.Div([
                        dcc.Link('Arctic Ice', href='/ice'),
                    ],
                        className='two columns'
                    ),
                    html.Div([
                        dcc.Link('Denver Temps', href='/den-temps'),
                    ],
                        className='two columns'
                    ),
                    html.Div([
                        dcc.Link('CO2', href='/co2'),
                    ],
                        className='two columns'
                    ),
                ],
                className='twelve columns'
                ),
            ],
                className='row'
            ),
            html.Div([
                html.H2(
                    'Colorado River Water Storage',
                    className='twelve columns',
                    style={'text-align': 'center'}
                ),
            ],
                className='row'
            ),
            html.Div([
                html.Div([
                    html.Div([
                        html.Div('Select Reservoir', style={'text-align': 'center'}),
                        dcc.Dropdown(
                        id='lake',
                        options=[
                            {'label': 'Powell', 'value': 'lakepowell'},
                            {'label': 'Mead', 'value': 'hdmlc'},
                            {'label': 'Mead + Powell', 'value': 'combo'},
                            # {'label': 'Flaming Gorge', 'value': 'flaminggorge'},
                            # {'label': 'Navajo', 'value': 'navajo'},
                            # {'label': 'Blue Mesa', 'value': 'bluemesa'},
                        ],
                        value='lakepowell'
                        ),
                    ],
                        className='pretty_container'
                    ),
                ],
                    className='three columns'
                ),
            ],
                className='row'
            ),
            html.Div([
                html.Div([
                    dcc.Graph(
                        id='lake-levels',
                    ),
                ],
                    className='nine columns'
                ),
                html.Div([
                    html.Div([
                        html.Div(id='water-stats') 
                    ],
                        className='round1'
                    ),
                    html.Div([
                        dcc.RadioItems(
                            id='period',
                            options=[
                                {'label':'D', 'value':'2'},
                                {'label':'W', 'value':'8'},
                                {'label':'M', 'value':'31'},
                                {'label':'Y', 'value':'366'},
                                {'label':'CY', 'value': days},
                            ],
                            value='2',
                            labelStyle={'display': 'inline'},
                            ), 
                    ],
                        className='round1'
                    ),
                    html.Div([
                        html.Div(id='changes') 
                    ],
                        className='round1'
                    ),
                    html.Div([
                        html.Div(id='all-changes') 
                    ],
                        className='round1'
                    ),
                ],
                    className='three columns'
                ),
            ],
                className='row'
            ),
            html.Div([
                html.Div([
                    html.Div([
                        html.Div([
                            html.Div(id='lake-annual-min-table'),
                        ]),
                    ],
                        className='four columns'
                    ),
                    
                ],
                    className='twelve columns'
                ),
            ],
                className='row'
            ),
            html.Div(id='selected-water-data', style={'display': 'none'}),
            html.Div(id='powell-water-data', style={'display': 'none'}),
            html.Div(id='mead-water-data', style={'display': 'none'}),
            html.Div(id='combo-water-data', style={'display': 'none'}),
            html.Div(id='current-volume', style={'display': 'none'}),
            html.Div(id='site', style={'display': 'none'}),
            html.Div(id='cvd', style={'display': 'none'}),
            html.Div(id='last_v', style={'display': 'none'}),
            html.Div(id='d_min', style={'display': 'none'})
            # html.Div([
            #     dcc.Interval(
            #         id='interval-component',
            #         interval=1000,
            #         n_intervals=0
            #     ),
            # ]),
        ]
    )

app.layout = river_App