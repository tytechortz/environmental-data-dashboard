import dash
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd
import time
import json
import requests
# from lake_connect import flaminggorge, powell_latest, powell


app = dash.Dash(__name__)
app.config['suppress_callback_exceptions']=True


today = time.strftime("%Y-%m-%d")
print(today)

url = 'https://water.usbr.gov/api/web/app.php/api/series?sites=lakepowell&parameters=Day.Inst.ReservoirStorage.af&start=2020-02-01&end=2020-02-20&format=csv'

df = pd.read_csv('data.csv', skiprows=4)

print(df)


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
                html.H6(
                    'NOAA Stapleton Station Data',
                    className='twelve columns',
                    style={'text-align': 'center'}
                ),
            ],
                className='row'
            ),
        ]
    )

app.layout = river_App