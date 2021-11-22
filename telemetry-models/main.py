import os
import psycopg2
import psycopg2.extras
from psycopg2 import sql
import pandas as pd
import numpy as np
import datetime
import yaml
import logging
from pmdarima.arima import auto_arima
import sys

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

timescale_host = os.environ.get('TS_HOST')
timescale_user = os.environ.get('TS_USER')
timescale_password = os.environ.get('TS_PASSWORD')
timescale_port = os.getenv('TS_PORT', 5432)

if timescale_host is None or timescale_user is None or timescale_password is None:
    sys.exit("Environment variables are required to connect to TimescaleDB: TS_HOST, TS_USER, TS_PASSWORD")

CONFIG_FILE = os.getenv('TM_CONFIG_FILE', "/etc/telemetry-models/model_configuration.yaml")

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

def replace_model_predictions(model, model_config, dimension):
    model[model_config['dimension']] = dimension
    model.reset_index(inplace=True)
    df_columns = list(model)

    cur = conn.cursor()
    # Create the table if it does not exist
    cur.execute(
        sql.SQL("create table if not exists {} ({})")
            .format(
                sql.Identifier(model_config['model_name']),
                sql.SQL("time_bucket timestamp with time zone, "
                        "lower_bounds double precision, "
                        "upper_bounds double precision, "
                        "{} varchar".format(model_config['dimension']))
            )
    )
    # Convert table to Hypertable if it does not exist
    cur.execute(
        sql.SQL("SELECT create_hypertable('{}', 'time_bucket', if_not_exists => TRUE, migrate_data => TRUE)")
            .format(sql.Identifier(model_config['model_name']))
    )

    # Create index
    cur.execute(
        sql.SQL("create unique index if not exists {} on {} using btree (\"time_bucket\", {})")
            .format(
                sql.Identifier("{}_idx".format(model_config['model_name'])),
                sql.Identifier(model_config['model_name']),
                sql.Identifier(model_config['dimension'])
            )
    )

    # Upsert new model values
    insert_str = sql.SQL(
        '''INSERT INTO {} ({}) VALUES ({})
        ON CONFLICT (\"time_bucket\", {}) DO UPDATE
        SET lower_bounds = EXCLUDED.lower_bounds, upper_bounds = EXCLUDED.upper_bounds'''
    ).format(
        sql.Identifier(model_config['model_name']),
        sql.SQL(",").join(map(sql.Identifier, df_columns)),
        sql.SQL(",").join(map(sql.Placeholder, df_columns)),
        sql.Identifier(model_config['dimension'])
    )
    psycopg2.extras.execute_batch(cur, insert_str, model.to_dict('records'))
    conn.commit()
    cur.close()

def process_by_the_dimension(model_config, all_time_series_df):
    dimension_name = model_config['dimension']
    for dimension in all_time_series_df[dimension_name].unique():
        df = all_time_series_df.loc[all_time_series_df[dimension_name] == dimension]
        logging.info("[model = {}] - building model for dimension: {}".format(model_config['model_name'], dimension))
        model = make_model_by_dimension(df, dimension_name)
        logging.info("[model = {}] - saving model values for dimension: {}".format(model_config['model_name'], dimension))
        replace_model_predictions(model, model_config, dimension)

if not os.path.exists(CONFIG_FILE):
    sys.exit("Configuration file required at: {}".format(CONFIG_FILE))

with open(CONFIG_FILE, 'r') as stream:
    loaded_configuration = yaml.safe_load(stream)

for model_config in loaded_configuration['models']:
    logging.info("Running query for model: {}".format(model_config['model_name']))
    cursor = conn.cursor()
    # execute SQL query
    cursor.execute(model_config['sql_query'])
    # make records into a pandas dataframe
    columns = ['bucketed_time', 'value']
    columns.extend([model_config['dimension']])
    all_time_series_df = pd.DataFrame(np.array(cursor.fetchall()), columns = columns)
    process_by_the_dimension(model_config, all_time_series_df)
    cursor.close()

logging.info("All models built and saved")