import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

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
            """ Denver Weather Record 1950-Present"""
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
])

def Homepage():
    layout = html.Div([
    body
    ])
    return layout
