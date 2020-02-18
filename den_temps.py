import dash
import dash_html_components as html
import dash_core_components as dcc
from connect import norm_records, rec_lows, rec_highs, all_temps

app = dash.Dash(__name__)
app.config['suppress_callback_exceptions']=True

def temp_App():
  return html.Div(
    [
      html.Div([
                html.H4(
                    'DENVER TEMPERATURE RECORD',
                    className='twelve columns',
                    style={'text-align': 'center'}
                ),
            ],
                className='row'
            ),
            html.Div([
                html.Div(
                    'NOAA Stapleton Station Data',
                    className='twelve columns',
                    style={'text-align': 'center'}
                ),
            ],
                className='row'
            ),
            html.Div([
                html.H6(
                    id='title-date-range',
                    className='twelve columns',
                    style={'text-align': 'center'}
                ),
            ],
                className='row'
            ),
            html.Div([
                html.Div([
                    html.Label('Select Product'),
                    dcc.RadioItems(
                        id='product',
                        options=[
                            {'label':'Temperature graphs', 'value':'temp-graph'},
                            {'label':'Climatology for a day', 'value':'climate-for-day'},
                            {'label':'Full Record Bar Graphs', 'value':'frbg'},
                            {'label':'5 Year Moving Avgs', 'value':'fyma-graph'},
                            {'label':'Full Record Heat Map', 'value':'frhm'},
                        ],
                        # value='temp-graph',
                        labelStyle={'display': 'block'},
                    ),
                ],
                    className='three columns',
                ),
                # html.Div([
                #     html.Div(
                #         id='year-picker'
                #     ),
                #     html.Div(
                #         id='date-picker'
                #     ),
                # ],
                #     className='four columns',
                # ),
                # html.Div([
                #     html.Button('Update Data', id='data-button'),
                # ]),
                # html.Div([
                #     html.Div(id='output-data-button')
                # ]),

            ],
                className='row'
            ),
    ]
  )

app.layout = temp_App