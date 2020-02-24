import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from co_2 import max_co2, max_co2_date, current_co2, current_co2_date

body = dbc.Container([
   html.Div([
      html.Div([
         html.H2(
         'Arctic Sea Ice',
         ),
         html.P(
            """ Track Arctic Sea Ice extent from 2006 to present, with data from National Snow Ice Data Center MASIE dataset.  Graph sea ice extent by year, display data for current day, average monthly extent, extent for current date by year, and yearly rankings of annual minimum and maximum.  Annual ranks are the sum of points calculated daily with highest extent given a value of 1, and lowest extent with the value equal to years in the dataset."""
         ),
         dbc.Button("Open App", color="primary", href="/ice"),
      ],
         className='six columns'
      ),
      html.Div([
         html.Img(src='assets/ase.jpg', height=350)
      ],
         className='five columns'
      ),
   ],
      className='row'
   ),
   html.Div([
      html.Div([
         html.H2(
         'Denver Temperature Data',
         ),
         html.P(
            """ Denver Weather Record 1950-Present. Data from former official NOAA Denver Stapleton weather station from 1950-present. Data is downloaded from NOAA API to postgresql database automatically, processed and displayed with python pandas and dash libraries.  """
         ),
         dbc.Button("Open App", color="primary", href="/den-temps"),
      ],
         className='six columns'
      ),
      html.Div([
         html.Img(src='assets/den-weather.jpg', height=350)
      ],
         className='five columns'
      ),
   ],
      className='row'
   ),
   html.Div([
      html.Div([
         html.H2(
         'Colorado River Water Storage',
         ),
         html.P(
            """ Colorado River water storage in Lake Powell and Lake Mead.  Data from U.S. Bureau of Reclamation"""
         ),
         dbc.Button("Open App", color="primary", href="/colorado-river"),
      ],
         className='six columns'
      ),
      html.Div([
         html.Img(src='assets/hoover-dam.jpg', height=350)
      ],
         className='five columns'
      ),
   ],
      className='row'
   ),
   html.Div([
      html.Div([
         html.H2(
         'Atmospheric CO2 Concentration',
         ),
         html.P(
            """ Data from Dr. Pieter Tans, NOAA/ESRL (www.esrl.noaa.gov/gmd/ccgg/trends/) and Dr. Ralph Keeling, Scripps Institution of Oceanography (scrippsco2.ucsd.edu/) """
         ),
         html.H4('Record: {} ppm {}'.format(max_co2, max_co2_date)),
         html.H4('Current: {} ppm {}'.format(current_co2, current_co2_date)),
         dbc.Button("Open App", color="primary", href="/co2"),
      ],
         className='six columns'
      ),
      html.Div([
         html.Img(src='assets/mauna-loa.jpg', height=350)
      ],
         className='five columns'
      ),
   ],
      className='row'
   ),

])

def Homepage():
    layout = html.Div([
    body
    ])
    return layout
