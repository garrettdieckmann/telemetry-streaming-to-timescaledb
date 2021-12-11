# Telemetry Streaming Quickstart Helm Chart
Helm chart for the "Telemetry Streaming Quickstart" environment.

## Deploy the chart
```
> helm repo add ts https://garrettdieckmann.github.io/telemetry-streaming-to-timescaledb
> helm install ts/telemetry-streaming-quickstart \
    --generate-name \
    --set timescaledb.password=$TIMESCALE_PASSWORD
```

## Parameters
### **Required parameters**
* timescaledb.password
### Common parameters
| Name | Description | Default Value |
| ---- | ----------- | ------------- |
| `namespace` | Namespace to deploy the quick start components into. | `telemetry-streaming-quickstart` |

### Grafana parameters
| Name | Description | Default Value |
| ---- | ----------- | ------------- |
| `grafana.deploymentName` | Name of the Grafana deployment | `grafana` |
| `grafana.configMapName` | Name of the Grafana ConfigMap | `grafana-conf` |
| `grafana.serviceName` | Name of the Grafana external Service | `grafana-external-svc` |
| `grafana.adminPassword` | Grafana Admin password | `secretAdmin` |
| `grafana.secretName` | Name of the Grafana Secret | `grafana-passwords` |
| `grafana.nodePort` | Default NodePort port | `30030` |
| `grafana.useLoadBalancer` | Whether or not to use a Kubernetes LoadBalancer (uses NodePort by default) | `false` |

### OpenTelemetry Collector parameters
| Name | Description | Default Value |
| ---- | ----------- | ------------- |
| `openTelemetry.deploymentName` | Name of the OpenTelemetry Collector Deployment | `otel-collector` |
| `openTelemetry.configMapName` | Name of the OpenTelemetry ConfigMap  | `otel-collector-conf` |
| `openTelemetry.serviceName` | Name of the OpenTelemetry Service (scraped by Prometheus) | `otel-collector-prom-svc` |
| `openTelemetry.externalServiceName` | Name of the OpenTelemetry external Service (receiver endpoint)  | `otel-collector-ingest-svc` |
| `openTelemetry.nodePort` | Default NodePort port  | `30681` |
| `openTelemetry.useLoadBalancer` | Whether or not to use a Kubernetes LoadBalancer (uses NodePort by default) | `false` |

### Prometheus parameters
| Name | Description | Default Value |
| ---- | ----------- | ------------- |
| `prometheus.deploymentName` | Name of the Prometheus Deployment  | `prometheus` |
| `prometheus.configMapName` | Name of the Prometheus ConfigMap  | `prometheus-conf` |
| `prometheus.serviceName` | Name of the Prometheus Service  | `prometheus-svc` |

### Promscale parameters
| Name | Description | Default Value |
| ---- | ----------- | ------------- |
| `promscale.deploymentName` | Name of the Promscale Deployment  | `promscale` |
| `promscale.serviceName` | Name of the Promscale Service  | `promscale-svc` |
| `promscale.secretName` | Name of the Promscale Secret  | `promscale-connection-string` |

### Telemetry-Model parameters
| Name | Description | Default Value |
| ---- | ----------- | ------------- |
| `telemetryModel.cronJobName` | Name of the Telemetry Model CronJob  | `telemetry-model-builder` |
| `telemetryModel.imageName` | Name of the Telemetry Model Docker image, including the Docker image version  | `gdieckmann/telemetry-models:1.0.2` |
| `telemetryModel.configMapName` | Name of the Telemetry Model ConfigMap  | `telemetry-model-builder-conf` |
| `telemetryModel.secretName` | Name of the Telemetry Model Secret | `telemetry-model-db` |

### TimescaleDB parameters
| Name | Description | Default Value |
| ---- | ----------- | ------------- |
| `timescaledb.deploymentName` | Name of the TimescaleDB Deployment | `timescaledb` |
| `timescaledb.serviceName` | Name of the TimescaleDB Service  | `timescaledb-svc` |
| `timescaledb.secretName` | Name of the TimescaleDB Secret  | `timescaledb-password` |
| `timescaledb.username` | The TimescaleDB database username | `postgres` |
| `timescaledb.password` | The TimescaleDB database user's password | (no default) |