import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from homepage import Homepage
from den_temps import temp_App, today, df_all_temps
import pandas as pd



app = dash.Dash()

app.config.suppress_callback_exceptions = True

app.layout = html.Div([
    dcc.Location(id = 'url', refresh = False),
    html.Div(id = 'page-content')
])


@app.callback(Output('page-content', 'children'),
            [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/den-temps':
        return temp_App()
    elif pathname == '/ice':
        return ice_App()
    else:
        return Homepage()


@app.callback(Output('all-data', 'children'),
            [Input('product', 'value')])
def all_temps_cleaner(product_value):
  
    cleaned_all_temps = df_all_temps
    cleaned_all_temps.columns=['dow','sta','Date','TMAX','TMIN']
    # cleaned_all_temps['Date'] = pd.to_datetime(cleaned_all_temps['Date'])
    cleaned_all_temps = cleaned_all_temps.drop(['dow','sta'], axis=1)

    return cleaned_all_temps.to_json()

@app.callback(
    Output('date-picker', 'children'),
    [Input('product', 'value')])
    # Input('year', 'value')])
def display_date_selector(product_value):
    if product_value == 'climate-for-day':
        return  html.P('Select Date (MM-DD)'), dcc.DatePickerSingle(
                    id='date',
                    display_format='MM-DD',
                    date=today
                )

@app.callback(Output('title-date-range', 'children'),
            [Input('all-data', 'children')])
def title_date(temps):
    title_temps = pd.read_json(temps)
    title_temps['Date'] = pd.to_datetime(title_temps['Date'], unit='ms')
    title_temps['Date']=title_temps['Date'].dt.strftime("%Y-%m-%d")
    last_day = title_temps.iloc[-1, 0] 
    
    return '1950-01-01 through {}'.format(last_day)

@app.callback(
    Output('daily-max-t', 'children'),
    [Input('product', 'value'),
    Input('d-max-max', 'children'),
    Input('avg-of-dly-highs', 'children'),
    Input('d-min-max', 'children')])
def max_stats(product, d_max_max, admaxh, d_min_max):
    dly_max_max = d_max_max
    admaxh = admaxh
    dly_min_max = d_min_max
    print(dly_max_max)
    print(admaxh)
    print(dly_min_max)
    if product == 'climate-for-day':
        return html.Div([
            html.Div([
                html.Div('Maximum Temperatures', style={'text-align':'center', 'color':'red'})
            ]),
            html.Div([
                html.Div([
                    html.Div([
                        html.Div('Maximum', style={'text-align':'center', 'color': 'red'}),
                        html.Div('{}'.format(dly_max_max), style={'text-align':'center'})
                    ],
                        className='round1 four columns'
                    ),
                    html.Div([
                        html.Div('Average', style={'text-align':'center', 'color': 'red'}),
                        html.Div('{:.0f}'.format(admaxh), style={'text-align':'center'})
                    ],
                        className='round1 four columns'
                    ),
                    html.Div([
                        html.Div('Minimum', style={'text-align':'center', 'color': 'red'}),
                        html.Div('{}'.format(dly_min_max), style={'text-align':'center'})
                    ],
                        className='round1 four columns'
                    ),
                ],
                    className='row'
                ),
            ],
                className='pretty_container'
            ),
                
        ],
            # className='twelve columns'
        ),

@app.callback([
    Output('datatable-interactivity', 'data'),
    Output('datatable-interactivity', 'columns'),
    Output('d-max-max', 'children'),
    Output('avg-of-dly-highs', 'children'),
    Output('d-min-max', 'children'),
    Output('d-min-min', 'children'),
    Output('avg-of-dly-lows', 'children'),
    Output('d-max-min', 'children')],
    [Input('all-data', 'children'),
    Input('date', 'date')])
def display_climate_day_table(all_data, selected_date):
    dr = pd.read_json(all_data)
    dr['Date'] = pd.to_datetime(dr['Date'], unit='ms')
    # dr['Date']=dr['Date'].dt.strftime("%Y-%m-%d") 
    dr.set_index(['Date'], inplace=True)
    dr = dr[(dr.index.month == int(selected_date[5:7])) & (dr.index.day == int(selected_date[8:10]))]
    # dr = df_all_temps[(df_all_temps['Date'][5:7] == date[5:7]) & (df_all_temps['Date'][8:10] == date[8:10])]
    dr = dr.reset_index()
    columns=[
        {"name": i, "id": i,"selectable": True} for i in dr.columns
    ]
    
    dr['Date'] = dr['Date'].dt.strftime('%Y-%m-%d')
    d_max_max = dr['TMAX'].max()
    avg_of_dly_highs = dr['TMAX'].mean()
    d_min_max = dr['TMAX'].min()
    d_min_min = dr['TMIN'].min()
    avg_of_dly_lows = dr['TMIN'].mean()
    d_max_min = dr['TMIN'].max()

    return dr.to_dict('records'), columns, d_max_max, avg_of_dly_highs, d_min_max, d_min_min, avg_of_dly_lows, d_max_min  


if __name__ == '__main__':
    app.run_server(debug=False)