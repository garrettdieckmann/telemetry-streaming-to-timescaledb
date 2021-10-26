# OTLP to TimescaleDB - in Kubernetes
Example of getting an OTLP collector, Prometheus, Promscale, TimescaleDB and Grafana all running in Kubernetes.

A few of the services listed above will be accessible outside of the Kubernetes cluster, and those are:
* OpenTelemetry Collector - exposed as a nodePort service (on port 30681), to allow for OTLP metrics to be ingested
* Grafana - exposed as a nodePort service (on port 30030), to allow for external access to the Grafana dashboard

## Prerequisites
To run the following scripts and Kubernetes configuration files, will need:
* An accessible Kubernetes cluster
* kubectl installed, with access to the Kubernetes cluster

## Deploying the services
<TODO>
run in order 010 -> 070