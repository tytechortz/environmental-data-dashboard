import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from homepage import Homepage
from den_temps import temp_App, df_all_temps, current_year, ld, df_norms, df_rec_lows, df_rec_highs, year_count, today, last_day
import pandas as pd
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

@app.callback(Output('title-date-range', 'children'),
            [Input('all-data', 'children')])
def title_date(temps):
    title_temps = pd.read_json(temps)
    title_temps['Date'] = pd.to_datetime(title_temps['Date'], unit='ms')
    title_temps['Date']=title_temps['Date'].dt.strftime("%Y-%m-%d")
    last_day = title_temps.iloc[-1, 0] 
    
    return '1950-01-01 through {}'.format(last_day)

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

if __name__ == '__main__':
    app.run_server(debug=False)