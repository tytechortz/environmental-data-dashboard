import pandas as pd
from datetime import datetime
import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go
import numpy as np

app = dash.Dash(__name__)
app.config['suppress_callback_exceptions']=True


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
                        # figure=fig
                    ),
                ],
                    className='nine columns'
                ),
                html.Div([
                    html.Div(id='max-co2-layout'),
                    html.Div(id='current-co2-layout'),
                    html.Div(id='avg-co2-layout'),
                ],
                    className='three columns'
                ),
            ],
                className='row'
            ),
            html.Div([
                dcc.Interval(
                    id='interval-component',
                    interval=60000,
                    n_intervals=0
                ),
            ]),
            html.Div(id='CO2-data', style={'display': 'none'}),
        ]
    )

app.layout = co2_App