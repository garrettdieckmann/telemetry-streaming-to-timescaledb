# Exploring using time-series forecasting with data stored in TimescaleDB

Example uses simulated IOT sensor data from a TimescaleDB tutorial as the time series data used to generate an ARIMA (using auto_arima) timeseries forecast model, and plot the forecasted values.

Also demonstrates how a model can be generated, and saved (by pickling the model and inserting the pickled model into TimescaleDB/Postgresql), so that it can be later updated, instead of completely rebuilt.

## Run the example
#### Pre-reqs:
(covered below, in [Sources used](#sources-used) section)
* a running TimescaleDB (or Postgresql) instance
* simulated IOT sensor generated

```
export TS_HOST=yourhost.domain.com
export TS_USER=yourUser
export TS_PASSWORD=yourPassword
python main.py
```

## Sources used
* [TimescaleDB tutorial on simulating IOT sensor data](https://docs.timescale.com/timescaledb/latest/tutorials/simulate-iot-sensor-data)
* [Article and code on auto ARIMA](https://towardsdatascience.com/time-series-forecasting-using-auto-arima-in-python-bb83e49210cd)