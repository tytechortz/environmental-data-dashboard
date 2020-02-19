import dash
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd

app = dash.Dash(__name__)
app.config['suppress_callback_exceptions']=True

# df_water = pd.read_json('https://water.usbr.gov/api/web/app.php/api/series?sites=lakepowell&parameters=Day.Inst.ReservoirStorage.af&start=1850-01-01&end=2020-02-19&format=json')

# print(df_water)

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