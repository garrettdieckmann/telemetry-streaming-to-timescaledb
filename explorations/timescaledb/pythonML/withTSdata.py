import os
import psycopg2
import psycopg2.extras
import pandas as pd
import numpy as np
import datetime
import yaml
from pmdarima.arima import auto_arima

timescale_host = os.environ.get('TS_HOST')
timescale_user = os.environ.get('TS_USER')
timescale_password = os.environ.get('TS_PASSWORD')
timescale_port = os.getenv('TS_PORT', 5432)

# establish connection
conn = psycopg2.connect(host=timescale_host, user=timescale_user, password=timescale_password, port=timescale_port)


def make_model_by_dimension(df, dimension_name):
    # set the index of dataframes to the 'bucketed_time'
    df.set_index('bucketed_time', inplace = True)
    host_df = df.drop([dimension_name], axis = 1)
    host_df.dropna(inplace = True)
    # convert trip_length into a numeric value in seconds
    arima_model = auto_arima(host_df)

    predicted_data_start_time = host_df.index.max() + datetime.timedelta(minutes = 1)
    forecast_datetime_index = pd.date_range(start=predicted_data_start_time, periods=20, freq='1min')
    # get conf_int, which is our lower and upper bounds of the prediction
    _, conf_int = arima_model.predict(n_periods = 20, return_conf_int=True)

    # predicted, with confidence interval
    with_conf_interval = pd.DataFrame(conf_int, index=forecast_datetime_index)
    with_conf_interval.index.name = 'time_bucket'
    with_conf_interval.columns = ['lower_bounds', 'upper_bounds']
    return with_conf_interval

def replace_model_predictions(model, dimension_name, dimension):
    model[dimension_name] = dimension
    model.reset_index(inplace=True)
    df_columns = list(model)
    # create (col1,col2,...)
    columns = ",".join(df_columns)

    # create VALUES('%s', '%s",...) one '%s' per column
    values = "VALUES({})".format(",".join(["%s" for _ in df_columns])) 

    cur = conn.cursor()
    cur.execute("DELETE FROM %s WHERE %s = %s", ('TABLE_NAME', 'DIMENSION', dimension))
    conn.commit()

    # create INSERT INTO table (columns) VALUES('%s',...)
    insert_stmt = "INSERT INTO %s ({}) {}".format('TABLE_NAME', columns, values)

    psycopg2.extras.execute_batch(cur, insert_stmt, model.values)
    conn.commit()
    cur.close()

def process_by_the_dimension(dimension_name, all_time_series_df):
    for dimension in all_time_series_df[dimension_name].unique():
        df = all_time_series_df.loc[all_time_series_df[dimension_name] == dimension]
        model = make_model_by_dimension(df, dimension_name)
        replace_model_predictions(model, dimension_name, dimension)

with open("model_configuration.yaml", 'r') as stream:
    loaded_configuration = yaml.safe_load(stream)

for model_config in loaded_configuration['models']:
    cursor = conn.cursor()
    # execute SQL query
    cursor.execute(model_config['sql_query'])
    # make records into a pandas dataframe
    columns = ['bucketed_time', 'value']
    columns.extend([model_config['dimension']])
    all_time_series_df = pd.DataFrame(np.array(cursor.fetchall()), columns = columns)
    process_by_the_dimension(model_config['dimension'], all_time_series_df)
    cursor.close()