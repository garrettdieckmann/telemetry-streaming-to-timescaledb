import os
import psycopg2
import psycopg2.extras
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import pickle
from pmdarima.arima import auto_arima

timescale_host = os.environ.get('TS_HOST')
timescale_user = os.environ.get('TS_USER')
timescale_password = os.environ.get('TS_PASSWORD')

# establish connection
conn = psycopg2.connect(host=timescale_host, user=timescale_user, password=timescale_password)

# cursor object allows querying of database
# server-side cursor is created to prevent records to be downloaded until explicitly fetched
cursor = conn.cursor('sensor_data', cursor_factory=psycopg2.extras.DictCursor)

# execute SQL query
cursor.execute('''
SELECT time_bucket('30 minutes', time) AS period,
  AVG(temperature) AS avg_temp
FROM sensor_data JOIN sensors on sensor_data.sensor_id = sensors.id
GROUP BY period;
''')

# fetch records from database
sensor_train = cursor.fetchall()

# make records into a pandas dataframe
sensor_train = pd.DataFrame(np.array(sensor_train), columns = ['period', 'avg_temp'])

# convert the type of columns of dataframe to datetime and timedelta

# set the index of dataframes to the timestamp
sensor_train.set_index('period', inplace = True)

# convert trip_length into a numeric value in seconds
arima_model = auto_arima(sensor_train, trace=True)

# Insert and retrieve from postgresql
model_cursor = conn.cursor()
model_cursor.execute('''INSERT INTO test VALUES (%s, %s)''', ('arima_model', pickle.dumps(arima_model)))
conn.commit()

# Retrieve the model
model_cursor.execute('''SELECT model FROM test where model_name = %s''', ['arima_model'])
reloaded_arima_model = pickle.loads(bytes(model_cursor.fetchone()[0]))

predicted_data_start_time = sensor_train.index.max() + datetime.timedelta(minutes = 30)
forecast_datetime_index = pd.date_range(start=predicted_data_start_time, periods=20, freq='30min')
# get conf_int, which is our lower and upper bounds of the prediction
predicted_data, conf_int = reloaded_arima_model.predict(n_periods = 20, return_conf_int=True)

# Create a new data frame using the predicted data
prediction = pd.DataFrame(predicted_data, index=forecast_datetime_index)
prediction.columns = ['predicted_temp']

# Plot on a graph
plt.figure(figsize=(8,5))
plt.plot(sensor_train,label="Training")
plt.plot(prediction,label="Predicted")
plt.legend(loc = 'best')
plt.show()