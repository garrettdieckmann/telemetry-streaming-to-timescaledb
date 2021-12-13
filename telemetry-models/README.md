# Telemetry Models
Proof-of-concept project which builds timeseries models from Telemetry Streaming timeseries data.

## Description
The Telemetry Models project demonstrates how timeseries models can be built on existing telemetry data, from F5 Telemetry Streaming.

Given that Telemetry Streaming data has been stored in a TimescaleDB database, via Timescle's PromScale extension, those Telemetry Streaming metrics can be used to build forecasts of what the future values will be for those metrics. Those forecasts can then be stored (inserted back into TimescaleDB), and graphed along with the actual timeseries data from Telemetry Streaming.

The generated ARIMA models output forecasted "lower_bounds" and "upper_bounds" values, in addition to a single forecasted value, which can then be used to generate a forecasted "range" (ex: from 30% to 50% memory usage for a given future point-in-time).

## Running the Docker Image
```
docker run -it -e TS_HOST=$TS_HOST \
    -e TS_USER=$TS_USER \
    -e TS_PASSWORD=$TS_PASSWORD \
    -e TS_PORT=$TS_PORT \
    -v $(pwd)/examples/model_configuration.yaml:/etc/telemetry-models/model_configuration.yaml \
    gdieckmann/telemetry-models:1.0.2
```

# Disclaimer
This project is intended for demonstration purposes only (demonstrating how future time series points can be predicted from historical time series data). No claims of model validity, accuracy or appropriateness are intended.