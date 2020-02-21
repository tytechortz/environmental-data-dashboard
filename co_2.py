import pandas as pd
from datetime import datetime

old_data = pd.read_csv('ftp://aftp.cmdl.noaa.gov/data/trace_gases/co2/in-situ/surface/mlo/co2_mlo_surface-insitu_1_ccgg_DailyData.txt', delim_whitespace=True, header=[146])

old_data = old_data.drop(['hour', 'longitude', 'latitude', 'elevation', 'intake_height', 'qcflag', 'nvalue', 'altitude', 'minute', 'second', 'site_code', 'value_std_dev'], axis=1)
print(old_data)
# data.columns = ['1','2', '3', '4', '5', '6', '7', '8', '9']
old_data = old_data.iloc[501:]
# print(data)
old_data.index = pd.to_datetime(old_data[['year', 'month', 'day']])
old_data = old_data.drop(['year', 'month', 'day'], axis=1)
# data = data.iloc[10000:]
print(old_data)