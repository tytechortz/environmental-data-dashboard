import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from homepage import Homepage
from den_temps import temp_App, df_all_temps, current_year, ld, df_norms, df_rec_lows, df_rec_highs, year_count, today, last_day
import pandas as pd
import numpy as np
from numpy import arange,array,ones
from scipy import stats
import psycopg2
from sqlalchemy import create_engine
from datetime import datetime, date, timedelta



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


# Temperature callbacks

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

@app.callback(
    Output('year-picker', 'children'),
    [Input('product', 'value')])
def display_year_selector(product_value):
    if product_value == 'temp-graph':
        return html.P('Enter Year (YYYY)') ,dcc.Input(
                    id = 'year',
                    type = 'number',
                    value = current_year,
                    min = 1950, max = current_year
                )

# @app.callback(Output('title-date-range', 'children'),
#             [Input('all-data', 'children')])
# def title_date(temps):
#     print(temps)
#     title_temps = pd.read_json(temps)
#     title_temps['Date'] = pd.to_datetime(title_temps['Date'], unit='ms')
#     title_temps['Date']=title_temps['Date'].dt.strftime("%Y-%m-%d")
#     last_day = title_temps.iloc[-1, 0] 
    
#     return '1950-01-01 through {}'.format(last_day)

@app.callback(
    Output('daily-stats', 'children'),
    [Input('product', 'value'),
    Input('d-max-max', 'children'),
    Input('avg-of-dly-highs', 'children'),
    Input('d-min-max', 'children'),
    Input('d-min-min', 'children'),
    Input('avg-of-dly-lows', 'children'),
    Input('d-max-min', 'children')])
def max_stats(product, d_max_max, admaxh, d_min_max, d_min_min, adminl, d_max_min):
    dly_max_max = d_max_max
    admaxh = admaxh
    dly_min_max = d_min_max
    dly_min_min = d_min_min
    adminl = adminl
    dly_max_min = d_max_min
    if product == 'climate-for-day':
        return html.Div([
          html.Div([
            html.Div([
                html.Div('Maximum Temperatures', style={'text-align':'center', 'color':'red'})
            ],
              className='six columns'
            ),
            html.Div([
                html.Div('Minimum Temperatures', style={'text-align':'center', 'color':'blue'})
            ],
              className='six columns'
            ),
          ],
            className='row'
          ),
          html.Div([
            html.Div([
              html.Div([
                html.Div('Maximum', style={'text-align':'center', 'color': 'red'}),
                html.Div('{}'.format(dly_max_max), style={'text-align':'center'})
              ],
                className='round1 two columns'
              ),
              html.Div([
                html.Div('Average', style={'text-align':'center', 'color': 'red'}),
                html.Div('{:.0f}'.format(admaxh), style={'text-align':'center'})
              ],
                className='round1 two columns'
              ),
              html.Div([
                html.Div('Minimum', style={'text-align':'center', 'color': 'red'}),
                html.Div('{}'.format(dly_min_max), style={'text-align':'center'})
              ],
                className='round1 two columns'
              ),
              html.Div([
                html.Div('Maximum', style={'text-align':'center', 'color': 'blue'}),
                html.Div('{}'.format(dly_min_min), style={'text-align':'center'})
              ],
                className='round1 two columns'
              ),
              html.Div([
                html.Div('Average', style={'text-align':'center', 'color': 'blue'}),
                html.Div('{:.0f}'.format(adminl), style={'text-align':'center'})
              ],
                className='round1 two columns'
              ),
              html.Div([
                html.Div('Minimum', style={'text-align':'center', 'color': 'blue'}),
                html.Div('{}'.format(dly_max_min), style={'text-align':'center'})
              ],
                className='round1 two columns'
              ),
            ],
              className='row'
            ),
          ],
            className='pretty_container'
          ),
        ]),
      

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
    dr.set_index(['Date'], inplace=True)
    dr = dr[(dr.index.month == int(selected_date[5:7])) & (dr.index.day == int(selected_date[8:10]))]
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

@app.callback(
    Output('climate-day-table', 'children'),
    [Input('product', 'value')])
def display_climate_table(value):
    if value == 'climate-for-day':
        return dt.DataTable(id='datatable-interactivity',
        data=[{}], 
        columns=[{}], 
        fixed_rows={'headers': True, 'data': 0},
        style_cell_conditional=[
            {'if': {'column_id': 'Date'},
            'width':'100px'},
            {'if': {'column_id': 'TMAX'},
            'width':'100px'},
            {'if': {'column_id': 'TMIN'},
            'width':'100px'},
        ],
        style_data_conditional=[
            {
            'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(248, 248, 248)'
            },
        ],
        style_header={
        'backgroundColor': 'rgb(230, 230, 230)',
        'fontWeight': 'bold'
        },
        # editable=True,
        # filter_action="native",
        sort_action="native",
        sort_mode="multi",
        column_selectable="single",
        selected_columns=[],
        selected_rows=[],
        # page_action="native",
        page_current= 0,
        page_size= 10,
        )

@app.callback(
    Output('climate-day-bar', 'figure'),
    [Input('date', 'date'),
    Input('all-data', 'children'),
    Input('temp-param', 'value'),
    Input('product', 'value')])
def climate_day_graph(selected_date, all_data, selected_param, selected_product):
    dr = pd.read_json(all_data)
    dr['Date'] = pd.to_datetime(dr['Date'], unit='ms')
    dr.set_index(['Date'], inplace=True)
    dr = dr[(dr.index.month == int(selected_date[5:7])) & (dr.index.day == int(selected_date[8:10]))]
    dr['AMAX'] = dr['TMAX'].mean()
    dr['AMIN'] = dr['TMIN'].mean()
   
    xi = arange(0,len(dr['TMAX']))
    slope, intercept, r_value, p_value, std_err = stats.linregress(xi,dr['TMAX'])
    max_trend = (slope*xi+intercept)
  
    dr['MXTRND'] = max_trend
    xi = arange(0,len(dr['TMIN']))
    slope, intercept, r_value, p_value, std_err = stats.linregress(xi,dr['TMIN'])
    min_trend = (slope*xi+intercept)
    dr['MNTRND'] = min_trend

    all_max_temp_fit = pd.DataFrame(max_trend)
    all_max_temp_fit.index = dr.index
   

    all_min_temp_fit = pd.DataFrame(min_trend)
    all_min_temp_fit.index = dr.index
    
    title_param = dr.index[0].strftime('%B %d')
    if selected_param == 'TMAX':
        y = dr[selected_param]
        base = 0
        color_a = 'tomato'
        color_b = 'red'
        avg_y = dr['AMAX']
        trend_y = dr['MXTRND']
        name = 'temp'
        name_a = 'avg high'
        name_b = 'trend'
        # hovertemplate='TMAX: %{y}'
        

    elif selected_param == 'TMIN':
        y = dr[selected_param]
        base = 0
        color_a = 'blue'
        color_b = 'dodgerblue'
        avg_y = dr['AMIN']
        trend_y = dr['MNTRND']
        name = 'temp'
        name_a = 'avg low'
        name_b = 'trend'
        # hovertemplate='TMIN: %{y}'

    else:
        y = dr['TMAX'] - dr['TMIN']
        base = dr['TMIN']
        color_a = 'dodgerblue'
        color_b = 'tomato'
        avg_y = dr['AMIN']
        trend_y = dr['AMAX']
        name = 'range'
        name_a = 'avg low'
        name_b = 'avg high'
        # hovertemplate='Temp Range: %{y} - %{base}<extra></extra><br>'

    data = [
        go.Bar(
            y=y,
            x=dr.index,
            base=base,
            marker={'color':'black'},
            name=name,
            # hovertemplate=hovertemplate
        ),
        go.Scatter(
            y=avg_y,
            x=dr.index,
            mode = 'lines',
            name=name_a,
            line={'color': color_a},
            # hovertemplate=hovertemplate
        ),
        go.Scatter(
            y=trend_y,
            x=dr.index,
            name=name_b,
            mode = 'lines',
            line={'color': color_b},
            # hovertemplate=hovertemplate
        ),  
    ]
    layout = go.Layout(
        xaxis={'title': 'Year'},
        yaxis={'title': 'Deg F'},
        title='{} for {}'.format(selected_param,title_param),
        plot_bgcolor = 'lightgray',
        height=340
    )
    return {'data': data, 'layout': layout} 

@app.callback(
    Output('period-picker', 'children'),
    [Input('product', 'value')])
def display_period_selector(product_value):
    if product_value == 'temp-graph':
        return html.Div([
            dcc.RadioItems(
                    id = 'period',
                    options = [
                        {'label':'Annual (Jan-Dec)', 'value':'annual'},
                        {'label':'Winter (Dec-Feb)', 'value':'winter'},
                        {'label':'Spring (Mar-May)', 'value':'spring'},
                        {'label':'Summer (Jun-Aug)', 'value':'summer'},
                        {'label':'Fall (Sep-Nov)', 'value':'fall'},
                    ],
                    value = 'annual',
                    labelStyle = {'display':'inline'}
                ),
        ],
            className='pretty_container'
        ), 
    elif product_value == 'climate-for-day':
        return html.Div([
            dcc.RadioItems(
                    id = 'temp-param',
                    options = [
                        {'label':'Max Temp', 'value':'TMAX'},
                        {'label':'Min Temp', 'value':'TMIN'},
                        {'label':'Temp Range', 'value':'RANGE'},
                    ],
                    value = 'TMAX',
                    labelStyle = {'display':'inline-block'}
                )
    ],
        className='pretty_container'
    ),
    elif product_value == 'fyma-graph':
        return html.Div([
            dcc.RadioItems(
                    id = 'fyma-param',
                    options = [
                        {'label':'Max Temp', 'value':'TMAX'},
                        {'label':'Min Temp', 'value':'TMIN'},
                    ],
                    # value = 'TMAX',
                    labelStyle = {'display':'inline-block'}
                )
    ],
        className='pretty_container'
    ),

@app.callback(
    Output('graph', 'children'),
    [Input('product', 'value')])
def display_graph(value):
    if value == 'temp-graph':
        return dcc.Graph(id='graph1')
    elif value == 'fyma-graph':
        return dcc.Graph(id='fyma-graph')
    elif value == 'frbg':
        return dcc.Graph(id='frs-bar')
    elif value == 'frhm':
        return dcc.Graph(id='frs-heat')

@app.callback(
    Output('bar', 'children'),
    [Input('product', 'value' )])
def display_day_bar(selected_product):
    if selected_product == 'climate-for-day':
        return dcc.Graph(id='climate-day-bar')

@app.callback([Output('graph1', 'figure'),
             Output('temps', 'children')],
             [Input('temp-data', 'children'),
             Input('rec-highs', 'children'),
             Input('rec-lows', 'children'),
             Input('norms', 'children'),
             Input('year', 'value'),
             Input('period', 'value')])
def update_figure(temp_data, rec_highs, rec_lows, norms, selected_year, period):
    previous_year = int(selected_year) - 1
    the_selected_year = selected_year
    temps = pd.read_json(temp_data)
    temps = temps.drop([0,1], axis=1)
    temps.columns = ['date','TMAX','TMIN']
    temps['date'] = pd.to_datetime(temps['date'], unit='ms')
    temps = temps.set_index(['date'])
    temps['dif'] = temps['TMAX'] - temps['TMIN']
    
    temps_cy = temps[(temps.index.year==selected_year)]
    temps_py = temps[(temps.index.year==previous_year)][-31:]
   
    df_record_highs_ly = pd.read_json(rec_highs)
    df_record_highs_ly = df_record_highs_ly.set_index(1)
    df_record_lows_ly = pd.read_json(rec_lows)
    df_record_lows_ly = df_record_lows_ly.set_index(1)
    df_rl_cy = df_record_lows_ly[:len(temps_cy.index)]
    df_rh_cy = df_record_highs_ly[:len(temps_cy.index)]

    df_norms = pd.read_json(norms)
    if int(the_selected_year) % 4 == 0:
        df_norms = df_norms
    else:
        df_norms = df_norms.drop(df_norms.index[59])
    df_norms_cy = df_norms[:len(temps_cy.index)]
    df_norms_py = df_norms[:31]
   
  
    temps_cy.loc[:,'rl'] = df_rl_cy[0].values
    temps_cy.loc[:,'rh'] = df_rh_cy[0].values
    temps_cy.loc[:,'nh'] = df_norms_cy[3].values
    temps_cy.loc[:,'nl'] = df_norms_cy[4].values
   
    temps_py.loc[:,'nh'] = df_norms_py[3].values
    temps_py.loc[:,'nl'] = df_norms_py[4].values
   
    if period == 'spring':
        temps = temps_cy[temps_cy.index.month.isin([3,4,5])]
        nh_value = temps['nh']
        nl_value = temps['nl']
        rh_value = temps['rh']
        rl_value = temps['rl']
        bar_x = temps.index
      
    elif period == 'summer':
        temps = temps_cy[temps_cy.index.month.isin([6,7,8])]
        nh_value = temps['nh']
        nl_value = temps['nl']
        rh_value = temps['rh']
        rl_value = temps['rl']
        bar_x = temps.index

    elif period == 'fall':
        temps = temps_cy[temps_cy.index.month.isin([9,10,11])]
        nh_value = temps['nh']
        nl_value = temps['nl']
        rh_value = temps['rh']
        rl_value = temps['rl']
        bar_x = temps.index

    elif period == 'winter':
        date_range = []
        date_time = []
        sdate = date(int(previous_year), 12, 1)
        edate = date(int(selected_year), 12, 31)

        delta = edate - sdate

        for i in range(delta.days + 1):
            day = sdate + timedelta(days=i)
            date_range.append(day)
        for j in date_range:
            day = j.strftime("%Y-%m-%d")
            date_time.append(day)

        temps_py = temps_py[temps_py.index.month.isin([12])]
        temps_cy = temps_cy[temps_cy.index.month.isin([1,2])]
        temp_frames = [temps_py, temps_cy]
        temps = pd.concat(temp_frames, sort=True)
        date_time = date_time[:91]  
        
        df_record_highs_jan_feb = df_record_highs_ly[df_record_highs_ly.index.str.match(pat = '(01-)|(02-)')]
        df_record_highs_dec = df_record_highs_ly[df_record_highs_ly.index.str.match(pat = '(12-)')]
        high_frames = [df_record_highs_dec, df_record_highs_jan_feb]
        df_record_highs = pd.concat(high_frames)

        df_record_lows_jan_feb = df_record_lows_ly[df_record_lows_ly.index.str.match(pat = '(01-)|(02-)')]
        df_record_lows_dec = df_record_lows_ly[df_record_lows_ly.index.str.match(pat = '(12-)')]
        low_frames = [df_record_lows_dec, df_record_lows_jan_feb]
        df_record_lows = pd.concat(low_frames)

        df_high_norms_jan_feb = df_norms[3][0:60]
        df_high_norms_dec = df_norms[3][335:]
        high_norm_frames = [df_high_norms_dec, df_high_norms_jan_feb]
        df_high_norms = pd.concat(high_norm_frames)

        df_low_norms_jan_feb = df_norms[4][0:60]
        df_low_norms_dec = df_norms[4][335:]
        low_norm_frames = [df_low_norms_dec, df_low_norms_jan_feb]
        df_low_norms = pd.concat(low_norm_frames)

        bar_x = date_time
        nh_value = df_high_norms
        nl_value = df_low_norms
        rh_value = df_record_highs[0]
        rl_value = df_record_lows[0]

    elif period == 'annual':
        temps = temps_cy
        nh_value = temps['nh']
        nl_value = temps['nl']
        rh_value = temps['rh']
        rl_value = temps['rl']
        bar_x = temps.index

    mkr_color = {'color':'black'}
      
    trace = [
            go.Bar(
                y = temps['dif'],
                x = bar_x,
                base = temps['TMIN'],
                name='Temp Range',
                marker = mkr_color,
                hovertemplate = 'Temp Range: %{y} - %{base}<extra></extra><br>'
                                # 'Record High: %{temps[6]}'                  
            ),
            go.Scatter(
                y = nh_value,
                x = bar_x,
                # hoverinfo='none',
                name='Normal High',
                marker = {'color':'indianred'}
            ),
            go.Scatter(
                y = nl_value,
                x = bar_x,
                # hoverinfo='none',
                name='Normal Low',
                marker = {'color':'slateblue'}
            ),
            go.Scatter(
                y = rh_value,
                x = bar_x,
                # hoverinfo='none',
                name='Record High',
                marker = {'color':'red'}
            ),
            go.Scatter(
                y = rl_value,
                x = bar_x,
                # hoverinfo='none',
                name='Record Low',
                marker = {'color':'blue'}
            ),
        ]
    layout = go.Layout(
                xaxis = {'rangeslider': {'visible':False},},
                yaxis = {"title": 'Temperature F'},
                title ='Daily Temps',
                plot_bgcolor = 'lightgray',
                height = 500,
        )
    return {'data': trace, 'layout': layout}, temps.to_json()

@app.callback(
    Output('graph-stats', 'children'),
    [Input('temps', 'children'),
    Input('product','value')])
def display_graph_stats(temps, selected_product):
    temps = pd.read_json(temps)
    temps.index = pd.to_datetime(temps.index, unit='ms')
    temps = temps[np.isfinite(temps['TMAX'])]
    day_count = temps.shape[0]
    rec_highs = len(temps[temps['TMAX'] == temps['rh']])
    rec_lows = len(temps[temps['TMIN'] == temps['rl']])
    days_abv_norm = len(temps[temps['TMAX'] > temps['nh']])
    days_blw_norm = len(temps[temps['TMIN'] < temps['nl']])
    nh = temps['nh'].sum()
    nl = temps['nl'].sum()
    tmax = temps['TMAX'].sum()
    tmin = temps['TMIN'].sum()
    # nh_sum = temps['nh'][-31:].sum()
    # nh_sum2 = temps['nh'][:60].sum()

    degree_days = ((temps['TMAX'].sum() - temps['nh'].sum()) + (temps['TMIN'].sum() - temps['nl'].sum())) / 2
    if degree_days > 0:
        color = 'red'
    elif degree_days < 0:
        color = 'blue'
    if selected_product == 'temp-graph':
        return html.Div(
            [
                html.Div([
                    html.Div('Day Count', style={'text-align':'center'}),
                    html.Div('{}'.format(day_count), style={'text-align': 'center'})
                ],
                    className='round1'
                ),
                    html.Div([
                        html.Div('Records', style={'text-align':'center'}),
                        html.Div([
                            html.Div([
                                html.Div('High: {}'.format(rec_highs), style={'text-align': 'center', 'color':'red'}),
                            ],
                                className='six columns'
                            ),
                            html.Div([
                                html.Div('Low: {}'.format(rec_lows), style={'text-align': 'center', 'color':'blue'})
                            ],
                                className='six columns'
                            ),
                        ],
                            className='row'
                        ),
                    ],
                        className='round1'
                    ),
                    html.Div([
                        html.Div('Days Above/Below Normal', style={'text-align':'center'}),
                        html.Div([
                            html.Div([
                                html.Div('Above: {}'.format(days_abv_norm), style={'text-align': 'center', 'color':'red'}),
                            ],
                                className='six columns'
                            ),
                            html.Div([
                                html.Div('Below: {}'.format(days_blw_norm), style={'text-align': 'center', 'color':'blue'})
                            ],
                                className='six columns'
                            ),
                        ],
                            className='row'
                        ),
                    ],
                        className='round1'
                    ),
                    html.Div([
                        html.Div('Degree Days Over/Under Normal', style={'text-align':'center'}),
                        html.Div(html.Div('{:.0f} Degree Days'.format(degree_days), style={'text-align': 'center', 'color':color})),
                    ],
                        className='round1'
                    ),     
            ],
                className='round1'
            ),

@app.callback(Output('temp-data', 'children'),
             [Input('year', 'value'),
             Input('period', 'value')])
def all_temps(selected_year, period):
    previous_year = int(selected_year) - 1
    try:
        connection = psycopg2.connect(user = "postgres",
                                    password = "1234",
                                    host = "localhost",
                                    database = "denver_temps")
        cursor = connection.cursor()

        postgreSQL_select_year_Query = 'SELECT * FROM temps WHERE EXTRACT(year FROM "DATE"::TIMESTAMP) IN ({},{}) ORDER BY "DATE" ASC'.format(selected_year, previous_year)
        # postgreSQL_select_year_Query = 'SELECT * FROM temps WHERE
        cursor.execute(postgreSQL_select_year_Query)
        temp_records = cursor.fetchall()
        df = pd.DataFrame(temp_records)
        
    except (Exception, psycopg2.Error) as error :
        print ("Error while fetching data from PostgreSQL", error)
    
    finally:
        #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

    return df.to_json()

@app.callback(Output('norms', 'children'),
             [Input('product', 'value')])
def norm_highs(product):
    norms = df_norms
    return norms.to_json()

@app.callback(Output('rec-highs', 'children'),
             [Input('year', 'value')])
def rec_high_temps(selected_year):
    if int(selected_year) % 4 == 0:
        rec_highs = df_rec_highs
    else:
        rec_highs = df_rec_highs.drop(df_rec_highs.index[59])
    return rec_highs.to_json()

@app.callback(Output('rec-lows', 'children'),
             [Input('year', 'value')])
def rec_low_temps(selected_year):
    if int(selected_year) % 4 == 0:
        rec_lows = df_rec_lows
    else:
        rec_lows = df_rec_lows.drop(df_rec_lows.index[59])
    return rec_lows.to_json()

@app.callback(Output('frs-bar-controls', 'children'),
             [Input('product', 'value')])
def update_frs_graph(selected_product,):
    if selected_product == 'frbg':
        return html.Div([
            dcc.Markdown('''
            Select Max/Min and temperature to filter bar chart to show number of days 
            per year above or below selected temperature.
            '''),
            html.Div([
                html.Div(['Select Min/Max Temperature'], className='pretty_container'),
                dcc.RadioItems(
                    id='min-max-bar',
                    options=[
                        {'label':'Max', 'value':'TMAX'},
                        {'label':'Min', 'value':'TMIN'},
                    ],
                    labelStyle={'display':'inline'},
                    value='TMAX'   
                ),
                html.Div(['Select Greater/Less Than'], className='pretty_container'),
                dcc.RadioItems(
                    id='greater-less-bar',
                    options=[
                        {'label':'>=', 'value':'>='},
                        {'label':'<', 'value':'<'},
                    ],
                    labelStyle={'display':'inline'},
                    value='>='   
                ),
                html.Div(['Select Temperature'], className='pretty_container'),
                dcc.Input(
                    id='input-range',
                    type='number',
                    min=-30,
                    max=100,
                    step=5,
                    # value=90
                ),
            ])
        ],
            className='round1'
        ),

@app.callback(Output('frs-bar', 'figure'),
             [Input('all-data', 'children'),
             Input('input-range', 'value'),
             Input('greater-less-bar', 'value'),
             Input('min-max-bar', 'value')])
def update_frs_graph(all_data, input_value, g_l, min_max):
    
    all_data = pd.read_json(all_data)
    all_data['Date'] = pd.to_datetime(all_data['Date'], unit='ms')
    all_data.set_index(['Date'], inplace=True)
    if g_l == '>=':
        df = all_data.loc[all_data[min_max]>=input_value]
    else:
        df = all_data.loc[all_data[min_max]<input_value]
    df_count = df.resample('Y').count()[min_max]
    df = pd.DataFrame({'DATE':df_count.index, 'Selected Days':df_count.values})
    
    data = [
        go.Bar(
            y=df['Selected Days'],
            x=df['DATE'],
            marker={'color':'dodgerblue'}               
        )
    ]
    layout = go.Layout(
                xaxis={'title':'Year'},
                yaxis = {'title': '{} Degree Days'.format(input_value)},
                title ='Days Where {} is {} {} Degrees F'.format(min_max, g_l, input_value),
                plot_bgcolor = 'lightgray',
                height = 500,
        )

@app.callback(
    Output('fyma-stats', 'children'),
    [Input('product', 'value')])
def fyma_stuff(product):
    if product == 'fyma-graph':
        return html.Div(id='fyma-max-or-min-stats')

    # return {'data': data, 'layout': layout}

@app.callback(
    Output('fyma-max-or-min-stats', 'children'),
    [Input('fyma-param', 'value'),
    Input('all-data', 'children')])
def display_fyma_stats(selected_param, all_data):
    # print(product)
    fyma_temps = pd.read_json(all_data)
    fyma_temps['Date'] = pd.to_datetime(fyma_temps['Date'], unit='ms')
    fyma_temps.set_index(['Date'], inplace=True)

    all_max_rolling = fyma_temps['TMAX'].dropna().rolling(window=1825)
    all_max_rolling_mean = all_max_rolling.mean()
    
    all_min_rolling = fyma_temps['TMIN'].dropna().rolling(window=1825)
    all_min_rolling_mean = all_min_rolling.mean()

    max_max = all_max_rolling_mean.max().round(2)
    max_max_index = all_max_rolling_mean.idxmax().strftime('%Y-%m-%d')
    min_max = all_max_rolling_mean.min().round(2)
    min_max_index = all_max_rolling_mean.idxmin().strftime('%Y-%m-%d')
    current_max = all_max_rolling_mean[-1].round(2)
    
    min_min = all_min_rolling_mean.min().round(2)
    min_min_index = all_min_rolling_mean.idxmin().strftime('%Y-%m-%d')
    max_min = all_min_rolling_mean.max().round(2)
    max_min_index = all_min_rolling_mean.idxmax().strftime('%Y-%m-%d')
    current_min = all_min_rolling_mean[-1].round(2)
  
    # if product == 'fyma-graph':    
        # print(type(max_index))

    if selected_param == 'TMAX':

        return html.Div(
                [
                    html.Div([
                        html.Div('MAX STATS', style={'text-align':'center'}),
                        # html.Div('{} on {}'.format(max_max, max_index ), style={'text-align': 'center'})
                    ],
                        className='round1'
                    ),
                    html.Div([
                        html.Div('CURRENT VALUE', style={'text-align':'center'}),
                        html.Div('{}'.format(current_max), style={'text-align': 'center'})
                    ],
                        className='round1'
                    ),
                    html.Div([
                        html.Div('HIGH', style={'text-align':'center'}),
                        html.Div('{} on {}'.format(max_max, max_max_index ), style={'text-align': 'center'})
                    ],
                        className='round1'
                    ),
                    html.Div([
                        html.Div('LOW', style={'text-align':'center'}),
                        html.Div('{} on {}'.format(min_max, min_max_index ), style={'text-align': 'center'})
                    ],
                        className='round1'
                    ),
                ],
                    className='round1'
                ),
    elif selected_param == 'TMIN':

        return html.Div(
                [
                    html.Div([
                        html.Div('MIN STATS', style={'text-align':'center'}),
                    ],
                        className='round1'
                    ),
                    html.Div([
                        html.Div('CURRENT VALUE', style={'text-align':'center'}),
                        html.Div('{}'.format(current_min), style={'text-align': 'center'})
                    ],
                        className='round1'
                    ),
                    html.Div([
                        html.Div('LOW', style={'text-align':'center'}),
                        html.Div('{} on {}'.format(min_min, min_min_index ), style={'text-align': 'center'})
                    ],
                        className='round1'
                    ),
                    html.Div([
                        html.Div('HIGH', style={'text-align':'center'}),
                        html.Div('{} on {}'.format(max_min, max_min_index ), style={'text-align': 'center'})
                    ],
                        className='round1'
                    ),
                ],
                    className='round1'
                ),

@app.callback(
    Output('fyma-graph', 'figure'),
    [Input('fyma-param', 'value'),
    Input('df5', 'children'),
    Input('max-trend', 'children'),
    Input('min-trend', 'children'),
    Input('all-data', 'children')])
def update_fyma_graph(selected_param, df_5, max_trend, min_trend, all_data):
    fyma_temps = pd.read_json(all_data)
    fyma_temps['Date'] = pd.to_datetime(fyma_temps['Date'], unit='ms')
    # fyma_temps['Date']=fyma_temps['Date'].dt.strftime("%Y-%m-%d") 
    fyma_temps.set_index(['Date'], inplace=True)

    df_5 = pd.read_json(df_5)

    all_max_temp_fit = pd.DataFrame(max_trend)
    all_max_temp_fit.index = df_5.index
    all_max_temp_fit.index = all_max_temp_fit.index.strftime("%Y-%m-%d")

    all_min_temp_fit = pd.DataFrame(min_trend)
    all_min_temp_fit.index = df_5.index
    all_min_temp_fit.index = all_min_temp_fit.index.strftime("%Y-%m-%d")

    all_max_rolling = fyma_temps['TMAX'].dropna().rolling(window=1825)
    all_max_rolling_mean = all_max_rolling.mean()
    
    all_min_rolling = fyma_temps['TMIN'].dropna().rolling(window=1825)
    all_min_rolling_mean = all_min_rolling.mean()

    if selected_param == 'TMAX':
        trace = [
            go.Scatter(
                y = all_max_rolling_mean,
                x = all_max_rolling_mean.index,
                name='Max Temp'
            ),
            go.Scatter(
                y = all_max_temp_fit[0],
                x = all_max_temp_fit.index,
                name = 'trend',
                line = {'color':'red'}
            ),
        ]
    elif selected_param == 'TMIN':
        trace = [
            go.Scatter(
                y = all_min_rolling_mean,
                x = all_min_rolling_mean.index,
                name='Min Temp'
            ),
            go.Scatter(
                y = all_min_temp_fit[0],
                x = all_min_temp_fit.index,
                name = 'trend',
                line = {'color':'red'}
            ),
        ]
    layout = go.Layout(
        xaxis = {'rangeslider': {'visible':True},},
        yaxis = {"title": 'Temperature F'},
        title ='5 Year Rolling Mean {}'.format(selected_param),
        plot_bgcolor = 'lightgray',
        height = 500,
    )
    return {'data': trace, 'layout': layout}

@app.callback(
    Output('df5', 'children'),
    [Input('all-data', 'children'),
    Input('product', 'value')])
def clean_df5(all_data, product_value):
    dr = pd.read_json(all_data)
    dr['Date'] = pd.to_datetime(dr['Date'], unit='ms')
   
    df_date_index = df_all_temps.set_index(['Date'])

    df_date_index.index = pd.to_datetime(df_date_index.index)
    df_ya_max = df_date_index.resample('Y').mean()
    df5 = df_ya_max[:-1]
    df5 = df5.drop(['dow'], axis=1)

    return df5.to_json(date_format='iso')

@app.callback(
    Output('max-trend', 'children'),
    [Input('df5', 'children'),
    Input('product', 'value')])
def all_max_trend(df_5, product_value):
    
    df5 = pd.read_json(df_5)
    xi = arange(0,year_count)
    slope, intercept, r_value, p_value, std_err = stats.linregress(xi,df5['TMAX'])

    return (slope*xi+intercept)

@app.callback(
    Output('min-trend', 'children'),
    [Input('df5', 'children'),
    Input('product', 'value')])
def all_min_trend(df_5, product_value):
    
    df5 = pd.read_json(df_5)
    xi = arange(0,year_count)
    slope, intercept, r_value, p_value, std_err = stats.linregress(xi,df5['TMIN'])
    
    return (slope*xi+intercept)

@app.callback(Output('frs-heat-controls', 'children'),
             [Input('product', 'value')])
def update_frs_heat_graph(selected_product):

    months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    if selected_product == 'frhm':
        return html.Div([
            dcc.Markdown('''
            Select Month to compare months across the record period.
            '''),
            html.Div([
                dcc.RadioItems(
                    id='heat-param',
                    options=[
                        {'label':'TMAX', 'value':'TMAX'},
                        {'label':'TMIN', 'value':'TMIN'},
                        {'label':'TAVG', 'value':'TAVG'},
                    ],
                    labelStyle={'display':'inline'},
                    # value='TMAX'   
                ),
            ],
                className='pretty_container'
            ),
            html.Div([
                dcc.Markdown('''
            Months arranged in columns JAN at bottom.  Colors represent magnitude of 
            the departure of the mean monthly temperature from the mean monthly normal 
            temperature.
            '''),
            ])
            
        ],
            className='round1'
        ),

@app.callback(Output('frs-heat', 'figure'),
            [Input('all-data', 'children'),
            Input('heat-param', 'value'),
            Input('norms', 'children'),
            Input('product', 'value')])
def update_heat_map(all_data, selected_value, normals, selected_product):
    traces = []
    month_values = {'JAN':1, 'FEB':2, 'MAR':3, 'APR':4, 'MAY':5, 'JUN':6, 'JUL':7, 'AUG':8, 'SEP':9, 'OCT':10, 'NOV':11, 'DEC':12}
    all_data = pd.read_json(all_data)
    all_data['Date'] = pd.to_datetime(all_data['Date'], unit='ms')
    all_data.set_index(['Date'], inplace=True)
    all_data['TAVG'] = (all_data['TMAX'] + all_data['TMIN']) / 2

    new_all_data = pd.DataFrame()
    new_all_data['TMAX'] = all_data['TMAX'].resample('M').mean()
    new_all_data['TMIN'] = all_data['TMIN'].resample('M').mean()
    new_all_data['TAVG'] = all_data['TAVG'].resample('M').mean()
    # new_all_data.index.dt.strftime('%b, %Y')
    
    df_normals = pd.read_json(normals)
    df_normals[2] = pd.to_datetime(df_normals[2], unit='ms')
    df_normals.set_index([2], inplace=True)

    heat_norms = pd.DataFrame()
    heat_norms['TMAX_AVG'] = df_normals[3].resample('M').mean()
    heat_norms['TMIN_AVG'] = df_normals[4].resample('M').mean()
    heat_norms['TAVG_AVG'] = df_normals[5].resample('M').mean()
  
    res = pd.merge(new_all_data.assign(grouper=new_all_data.index.month),
                   heat_norms.assign(grouper=heat_norms.index.month),
                   how='left', on='grouper')
   
    res['TMAX_DIFF'] = res['TMAX'] - res['TMAX_AVG']
    res['TMIN_DIFF'] = res['TMIN'] - res['TMIN_AVG']
    res['TAVG_DIFF'] = res['TAVG'] - res['TAVG_AVG']
   
    colorscale_max = ((((res['TMAX_DIFF'].max()-res['TMAX_DIFF'].min()) - res['TMAX_DIFF'].max()) / (res['TMAX_DIFF'].max() - res['TMAX_DIFF'].min())))
    colorscale_min = ((((res['TMIN_DIFF'].max()-res['TMIN_DIFF'].min()) - res['TMIN_DIFF'].max()) / (res['TMIN_DIFF'].max() - res['TMIN_DIFF'].min())))
    colorscale_avg = ((((res['TAVG_DIFF'].max()-res['TAVG_DIFF'].min()) - res['TAVG_DIFF'].max()) / (res['TAVG_DIFF'].max() - res['TAVG_DIFF'].min())))

    months = ('JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC')

    if selected_value == 'TMAX':
        traces.append(go.Heatmap(
                y=new_all_data.index.month,
                x=new_all_data.index.year,
                z=res['TMAX'] - res['TMAX_AVG'],
                colorscale=[[0, 'blue'],[colorscale_max, 'white'], [1, 'red']],
            ))
    elif selected_value == 'TMIN':
        traces.append(go.Heatmap(
                y=new_all_data.index.month,
                x=new_all_data.index.year,
                z=res['TMIN'] - res['TMIN_AVG'],
                colorscale=[[0, 'blue'],[colorscale_min, 'white'], [1, 'red']]
            ))
    elif selected_value == 'TAVG':
        traces.append(go.Heatmap(
                y=new_all_data.index.month,
                x=new_all_data.index.year,
                z=res['TAVG'] - res['TAVG_AVG'],
                colorscale=[[0, 'blue'],[colorscale_avg, 'white'], [1, 'red']]
            ))
    return {
        'data': traces,
        'layout': go.Layout(
            title='Departure From Norm',
            xaxis={'title':'YEAR'},
            yaxis={'title':'MONTH','tickmode': 'array',
            'tickvals': [2,4,6,8,10,12],
            'ticktext': ['FEB', 'APR', 'JUN', 'AUG', 'OCT', 'DEC']},
        )
    }

# Ice callbacks


  

if __name__ == '__main__':
    app.run_server(debug=False)