### Data
import pandas as pd
import numpy as np
### Graphing
import plotly.graph_objects as go
### Dash
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input
## Navbar
# from navbar import Navbar

import time
from datetime import datetime
from pandas import Series
from scipy import stats 
from numpy import arange,array,ones 
from scipy.stats import norm
from pandas import DatetimeIndex

app = dash.Dash(__name__)
app.config['suppress_callback_exceptions']=True

server = app.server

pd.options.display.float_format = '{:,}'.format

value_range = [0, 365]

# Read data
df = pd.read_csv('ftp://sidads.colorado.edu/DATASETS/NOAA/G02186/masie_4km_allyears_extent_sqkm.csv', skiprows=1)

# print(df)

# Format date and set indext to date
df['yyyyddd'] = pd.to_datetime(df['yyyyddd'], format='%Y%j')
df.set_index('yyyyddd', inplace=True)
df.columns = ['Total Arctic Sea', 'Beaufort Sea', 'Chukchi Sea', 'East Siberian Sea', 'Laptev Sea', 'Kara Sea',\
     'Barents Sea', 'Greenland Sea', 'Bafin Bay Gulf of St. Lawrence', 'Canadian Archipelago', 'Hudson Bay', 'Central Arctic',\
         'Bering Sea', 'Baltic Sea', 'Sea of Okhotsk', 'Yellow Sea', 'Cook Inlet']

count_row = df.shape[0]
days = count_row

# Dropdown year selector values
year_options = []
for YEAR in df.index.year.unique():
    year_options.append({'label':(YEAR), 'value':YEAR})

# Dropdown month selector values
month_options = [
{'label':'JAN', 'value':1},
{'label':'FEB', 'value':2},
{'label':'MAR', 'value':3},
{'label':'APR', 'value':4},
{'label':'MAY', 'value':5},
{'label':'JUN', 'value':6},
{'label':'JUL', 'value':7},
{'label':'AUG', 'value':8},
{'label':'SEP', 'value':9},
{'label':'OCT', 'value':10},
{'label':'NOV', 'value':11},
{'label':'DEC', 'value':12}
]

# Dropdown sea selector values
sea_options = []
for sea in df.columns.unique():
    sea_options.append({'label':sea, 'value':sea})


# Change dataframe to 5 day trailing average
df_fdta = df.rolling(window=5).mean()

startyr = 2006
presentyr = datetime.now().year
last_year = presentyr-1
year_count = presentyr-startyr
presentday = datetime.now().day
dayofyear = time.strftime("%j")
dayofyear = int(dayofyear)

arctic = df['Total Arctic Sea']
years = []

year_dict = {}
keys = []


for i in df.index.year.unique():
    keys.append(i)

def dictionary_maker():
    for i in keys:
        year_dict[i] = 0
keys = [str(i) for i in keys]
dictionary_maker()


m = 1
d = 1

arctic_r = arctic[(arctic.index.month == m) & (arctic.index.day == d)]
sort_arctic_r = arctic_r.sort_values(axis=0, ascending=True)



def ice_App():
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
                        dcc.Link('Denver Temps', href='/den-temps'),
                    ],
                        className='two columns'
                    ),
                    html.Div([
                        dcc.Link('Colorado River', href='/colorado-river'),
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
                  'Arctic Sea Ice Extent',
                  className='twelve columns',
                  style={'text-align': 'center'}
                ),
            ],
                className='row'
            ),
            html.Div([
                html.H6(
                  '2006-Present',
                  className='twelve columns',
                  style={'text-align': 'center'}
                ),
            ],
                className='row'
            ),
            html.Div([
                html.H6(
                  'Data From National Snow and Ice Data Center',
                  className='twelve columns',
                  style={'text-align': 'center'}
                ),
            ],
                className='row'
            ),
            html.Div([
                html.Div([
                    html.Label('Select Product', style={'text-align': 'center'}),
                        html.Div([
                            dcc.RadioItems(
                            id='product',
                            options=[
                                {'label':'Ice Exent By Year', 'value':'years-graph'},
                                {'label':'Avg Monthy Extent', 'value':'monthly-bar'},
                                {'label':'Extent On Current Date', 'value':'extent-date'},
                                {'label':'Extent Rankings', 'value':'extent-stats'},
                                {'label':'1 Year Moving Avg', 'value':'moving-avg'},
                            ],
                            # value='temp-graph',
                            labelStyle={'display': 'block'},
                            ),
                        ],
                            className='pretty_container'
                        ),
                 ],
                    className='three columns',
                ),
                html.Div([
                    html.Div(id='sea-selector'),
                ],
                    className='two columns'
                ),
                html.Div([
                    html.Div(id='month-selector'),
                ],
                    className='two columns'
                ),
            ],
                className='row'
            ),
            html.Div([
                html.Div([
                    html.Div(
                        id='ice-graph'
                    ), 
                ],
                    className='eight columns'
                ),
                html.Div([
                    html.Div(id='stats-n-stuff')
                ],
                    className='four columns'
                ), 
            ],
                className='row'
            ),
            html.Div([
                html.Div([
                    html.Div(
                        id='moving-avg-graph'
                    ), 
                ],
                    className='eight columns'
                ),
            #     html.Div([
            #         html.Div(id='stats-n-stuff')
            #     ],
            #         className='four columns'
            #     ), 
            ],
                className='row'
            ),
            html.Div([
                html.Div([
                    html.Div(
                        id='stats'
                    ), 
                ],
                    className='twelve columns'
                ),
            ],
                className='row'
            ),
          
            html.Div(id='df-monthly', style={'display': 'none'}),
            html.Div(id='df-fdta', style={'display': 'none'}),
            html.Div(id='df-year-trailing-avg', style={'display': 'none'}),
    ])

app.layout = ice_App