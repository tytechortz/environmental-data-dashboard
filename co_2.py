import pandas as pd
from datetime import datetime
import dash
import dash_html_components as html
import dash_core_components as dcc


app = dash.Dash(__name__)
app.config['suppress_callback_exceptions']=True


old_data = pd.read_csv('ftp://aftp.cmdl.noaa.gov/data/trace_gases/co2/in-situ/surface/mlo/co2_mlo_surface-insitu_1_ccgg_DailyData.txt', delim_whitespace=True, header=[146])

old_data = old_data.drop(['hour', 'longitude', 'latitude', 'elevation', 'intake_height', 'qcflag', 'nvalue', 'altitude', 'minute', 'second', 'site_code', 'value_std_dev'], axis=1)

old_data = old_data.iloc[501:]

old_data.index = pd.to_datetime(old_data[['year', 'month', 'day']])
old_data = old_data.drop(['year', 'month', 'day'], axis=1)

new_data = pd.read_csv('https://www.esrl.noaa.gov/gmd/webdata/ccgg/trends/co2_mlo_weekly.csv')

new_data['Date'] = pd.to_datetime(new_data['Date'])
new_data.index = new_data['Date']
new_data = new_data.drop(['month', 'week', 'Date'], axis=1)

new_data['value'] = new_data['day']
new_data = new_data.drop(['day'], axis=1)
new_data = new_data[datetime(2019, 1, 1):]

frames = [old_data, new_data]
data = pd.concat(frames)
print(data)

# with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
#     print(data)

def co2_App():
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
                        dcc.Link('Colorado River', href='/colorado-river'),
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
                    'Atmospheric CO2 Concentration',
                    className='twelve columns',
                    style={'text-align': 'center'}
                ),
            ],
                className='row'
            ),
            html.Div([
                html.Div([
                    dcc.Graph(
                        id='co2',
                    ),
                ],
                    className='nine columns'
                ),
                html.Div([
                    html.Div([
                        html.Div(id='co2-stats') 
                    ],
                        className='round1'
                    ),
                    html.Div([
                        html.Div(id='co2-changes') 
                    ],
                        className='round1'
                    ),
                ],
                    className='three columns'
                ),
            ],
                className='row'
            ),
        ]
    )

app.layout = co2_App