import pandas as pd
from datetime import datetime
import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go
import numpy as np

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
co2_data = pd.concat(frames)
co2_data['value'] = co2_data['value'].replace(-999.99, np.nan)
max_co2 = co2_data['value'].max()
print(max_co2)
max_co2_date = co2_data['value'].idxmax().strftime('%Y-%m-%d')
print(max_co2_date)
current_co2 = co2_data['value'].iloc[-1]
current_co2_date = co2_data.index[-1].strftime('%Y-%m-%d')

fig = go.Figure(data=[go.Scatter(x=co2_data.index, y=co2_data['value'], mode='markers')])



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
                        id='co2-levels',
                        figure=fig
                    ),
                ],
                    className='nine columns'
                ),
                html.Div([
                    html.Div([
                        html.Div('Maximum CO2 Value (ppm)', style={'text-align':'center'}) 
                    ],
                        className='round1'
                    ),
                    html.Div([
                        html.Div('{}'.format(max_co2), style={'text-align':'center'}),
                        html.Div('{}'.format(max_co2_date), style={'text-align':'center'}) 
                    ],
                        className='round1'
                    ),
                ],
                    className='three columns'
                ),
            ],
                className='row'
            ),
            # html.Div(id='co2-data', style={'display': 'none'}),
        ]
    )

app.layout = co2_App