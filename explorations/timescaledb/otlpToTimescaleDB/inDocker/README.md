# OTLP to TimescaleDB - in Docker
Example of getting an OTLP collector, Prometheus, Promscale, TimescaleDB and Grafana all running in Docker containers.

(note: below commands do not use a Docker network, since Docker networks tend to conflict with host networking in my test environment)

## TimescaleDB
Run TimescaleDB, with the promscale extension included:
```
docker run --name timescaledb --rm -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD -d -p 5432:5432 timescaledev/promscale-extension:latest-ts2-pg13 postgres -csynchronous_commit=off
```
## Promscale
Run Promscale, with connection information to the TimescaleDB container
```
docker run --name promscale --rm -d -p 9201:9201 timescale/promscale:latest -db-password=$POSTGRES_PASSWORD -db-port=5432 -db-name=postgres -db-host=$DOCKER_HOST -db-ssl-mode=allow
```
**Note:** can also provide connection string via a single environment variable:
```
docker run --name promscale --rm -d -p 9201:9201 -e PROMSCALE_DB_URI=$PROMSCALE_DB_URI timescale/promscale:latest
```

## Prometheus
Using the example prometheus.yml file:
```
# my global config
global:
  scrape_interval: 15s # Set the scrape interval to every 15 seconds. Default is every 1 minute.
  evaluation_interval: 15s # Evaluate rules every 15 seconds. The default is every 1 minute.
  # scrape_timeout is set to the global default (10s).

# A scrape configuration containing exactly one endpoint to scrape:
# Here it's Prometheus itself.
scrape_configs:
  # The job name is added as a label `job=<job_name>` to any timeseries scraped from this config.
  - job_name: "prometheus"
    static_configs:
      - targets: ["localhost:9090"]
  - job_name: "otel"
    static_configs:
      - targets: ["1.2.3.4:9088"]

remote_write:
  - url: "http://1.2.3.4:9201/write"
remote_read:
  - url: "http://1.2.3.4:9201/read"
    read_recent: true
```
run a Prometheus container:
```
docker run --rm -d -p 9090:9090 --name prometheus -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml prom/prometheus
```

## OpenTelemetry Collector
Using the example OpenTelemetry Collector configuration file:
```
receivers:
  otlp:
    protocols:
      http:

processors:
  batch:

exporters:
  prometheus:
    endpoint: "0.0.0.0:9088"

service:
  pipelines:
    metrics:
      receivers: [otlp]
      processors: [batch]
      exporters: [prometheus]
```
run the OpenTelemetry collector as a container:
```
docker run --rm -d --name otel-collector -p 55681:55681 -p 9088:9088 -v $(pwd)/otelconfig.yaml:/etc/otel/config.yaml otel/opentelemetry-collector-contrib
```

## Grafana
Run a Grafana container:
```
docker run --rm -d --name grafana -p 3000:3000 grafana/grafana
```

# Run the Promscale maintenance task
Promscale has a maintenance task to run (recommendation is every 30 minutes) - https://github.com/timescale/promscale/blob/master/docs/docker.md#-setting-up-cron-jobs
Can be run in Docker:
```
docker run -d --name promscale-maintenance --rm jbergknoff/postgresql-client $PROMSCALE_DB_URI psql -c "CALL execute_maintenance();"
```