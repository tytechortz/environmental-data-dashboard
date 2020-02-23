import pandas as pd
from datetime import datetime

old_data = pd.read_csv('ftp://aftp.cmdl.noaa.gov/data/trace_gases/co2/in-situ/surface/mlo/co2_mlo_surface-insitu_1_ccgg_DailyData.txt', delim_whitespace=True, header=[146])

old_data = old_data.drop(['hour', 'longitude', 'latitude', 'elevation', 'intake_height', 'qcflag', 'nvalue', 'altitude', 'minute', 'second', 'site_code', 'value_std_dev'], axis=1)
# print(old_data)
# data.columns = ['1','2', '3', '4', '5', '6', '7', '8', '9']
old_data = old_data.iloc[501:]
# print(data)
old_data.index = pd.to_datetime(old_data[['year', 'month', 'day']])
old_data = old_data.drop(['year', 'month', 'day'], axis=1)
# data = data.iloc[10000:]
# print(old_data)

new_data = pd.read_csv('https://www.esrl.noaa.gov/gmd/webdata/ccgg/trends/co2_mlo_weekly.csv')

new_data['Date'] = pd.to_datetime(new_data['Date'])
new_data.index = new_data['Date']
new_data = new_data.drop(['month', 'week', 'Date'], axis=1)
# print(new_data)
new_data['value'] = new_data['day']
new_data = new_data.drop(['day'], axis=1)
new_data = new_data[datetime(2019, 1, 1):]
print(new_data)
frames = [old_data, new_data]
data = pd.concat(frames)
# print(data)
# data = data.drop_duplicates(keep='last')




with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    print(data)