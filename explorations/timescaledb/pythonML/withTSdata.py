import os
import psycopg2
import psycopg2.extras as extras
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import pickle
from pmdarima.arima import auto_arima

timescale_host = os.environ.get('TS_HOST')
timescale_user = os.environ.get('TS_USER')
timescale_password = os.environ.get('TS_PASSWORD')
timescale_port = os.environ.get('TS_PORT')

# establish connection
conn = psycopg2.connect(host=timescale_host, user=timescale_user, password=timescale_password, port=timescale_port)

# cursor object allows querying of database
# server-side cursor is created to prevent records to be downloaded until explicitly fetched
cursor = conn.cursor()

# execute SQL query
cursor.execute('''
SELECT
  time_bucket('60.000s',"time") AS "bucketed_time",
  avg(value) AS "system_cpu",
  jsonb(labels) ->> 'hostname' as "hostname"
FROM system_cpu
GROUP BY bucketed_time, hostname
ORDER BY bucketed_time
''')

# make records into a pandas dataframe
all_time_series_df = pd.DataFrame(np.array(cursor.fetchall()), columns = ['bucketed_time', 'system_cpu', 'hostname'])


def make_model_by_hostname(df):
    # set the index of dataframes to the timestamp
    df.set_index('bucketed_time', inplace = True)
    df = df.drop(['hostname'], axis = 1)
    # convert trip_length into a numeric value in seconds
    arima_model = auto_arima(df)

    predicted_data_start_time = df.index.max() + datetime.timedelta(minutes = 1)
    print(df)
    print(df.index.max())
    print(predicted_data_start_time)
    forecast_datetime_index = pd.date_range(start=predicted_data_start_time, periods=20, freq='1min')
    print(forecast_datetime_index)
    # get conf_int, which is our lower and upper bounds of the prediction
    _, conf_int = arima_model.predict(n_periods = 20, return_conf_int=True)

    # predicted, with confidence interval
    with_conf_interval = pd.DataFrame(conf_int, index=forecast_datetime_index)
    with_conf_interval.index.name = 'time_bucket'
    with_conf_interval.columns = ['lower_bounds', 'upper_bounds']
    return with_conf_interval

def replace_model_predictions(model, hostname):
    model['hostname'] = hostname
    model.reset_index(inplace=True)
    df_columns = list(model)
    # create (col1,col2,...)
    columns = ",".join(df_columns)

    # create VALUES('%s', '%s",...) one '%s' per column
    values = "VALUES({})".format(",".join(["%s" for _ in df_columns])) 

    cur = conn.cursor()
    cur.execute("DELETE FROM predictions_system_cpu WHERE hostname = %s", (hostname,))
    conn.commit()

    # create INSERT INTO table (columns) VALUES('%s',...)
    insert_stmt = "INSERT INTO predictions_system_cpu ({}) {}".format(columns,values)

    psycopg2.extras.execute_batch(cur, insert_stmt, model.values)
    conn.commit()
    cur.close()

for hostname in all_time_series_df.hostname.unique():
    df = all_time_series_df.loc[all_time_series_df['hostname'] == hostname]
    model = make_model_by_hostname(df)
    replace_model_predictions(model, hostname)

cursor.close()