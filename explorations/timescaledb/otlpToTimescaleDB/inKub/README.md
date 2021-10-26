# OTLP to TimescaleDB - in Kubernetes
Example of getting an OTLP collector, Prometheus, Promscale, TimescaleDB and Grafana all running in Kubernetes.

The data flow of the metrics will look like:
```
metrics source -(publishes)-> OTLP collector <-(scrapes)- Prometheus -(remote write)-> Promscale -(writes to)-> TimescaleDB <-(queries)- Grafana
```

A few of the services listed above will be accessible outside of the Kubernetes cluster, and those are:
* OpenTelemetry Collector - exposed as a nodePort service (on port 30681), to allow for OTLP metrics to be ingested
* Grafana - exposed as a nodePort service (on port 30030), to allow for external access to the Grafana dashboard

## Prerequisites
To run the following scripts and Kubernetes configuration files, will need:
* An accessible Kubernetes cluster
* kubectl installed, with access to the Kubernetes cluster

## Deploying the services
#### Deploy TimescaleDB
- create the timescaledb secret (used as postgres database password)
```
export TIMESCALEDB_PASSWORD=<your-db-password>
./010-create-timescaledb-secret.sh
```
- apply the timescaledb kubernetes declaration (creates a deployment and a service)
```
kubectl apply -f 020-timescaledb-deployment.yaml
```

#### Deploy PromScale
- create the promscale secret (used as the connection string to the timescaledb postgresql database)
```
export PROMSCALE_DB_URI=postgres://postgres:$TIMESCALEDB_PASSWORD@timescaledb-svc:5432/postgres?sslmode=allow
./030-create-promscale-secret.sh
```
- apply the promscale kubernetes declaration (creates a deployment and a service)
```
kubectl apply -f 040-promscale-deployment.yaml
```

#### Deploy Prometheus
- apply the prometheus kubernetes declaration (creates a configmap, a deployment and a service)
```
kubectl apply -f 050-prometheus-deployment.yaml
```

#### Deploy an OpenTelemetry Collector
- apply the prometheus kubernetes declaration (creates a configmap, a deployment and two services)
```
kubectl apply -f 060-otel-collector-deployment.yaml
```

#### Deploy Grafana
- apply the prometheus kubernetes declaration (creates a deployment and a service)
```
kubectl apply -f 070-grafana-deployment.yaml
```

## Publishing metrics to the OpenTelemetry Collector
#### Using Telemetry Streaming on a BIG-IP
Given the successful configuration of the components above, metrics from a BIG-IP can now be published to the OpenTelemetry Collector, by using the [OpenTelemetry_Exporter Consumer](https://clouddocs.f5.com/products/extensions/f5-telemetry-streaming/latest/setting-up-consumer.html#opentelemetry-exporter-experimental) in F5 Telemetry Streaming.

An example declaration would look like:
```
{
    "class": "Telemetry",
    "My_Consumer": {
        "class": "Telemetry_Consumer",
        "type": "OpenTelemetry_Exporter",
        "host": "<your-kubernetes-cluster-ip>",
        "port": 30681,
        "metricsPath": "/v1/metrics"
    }
}
```

## Accessing the Grafana Dashboard
- open a browser to `http://<your-kubernetes-cluster-ip>:30030/`