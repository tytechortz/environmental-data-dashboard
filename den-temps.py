from connect import norm_records, rec_lows, rec_highs, all_temps

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
    ]
  )

app.layout = temp_App