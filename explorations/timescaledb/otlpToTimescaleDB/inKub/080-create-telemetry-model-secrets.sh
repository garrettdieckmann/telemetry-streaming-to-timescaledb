if [[ -z "$TIMESCALEDB_PASSWORD" ]] || [[ -z "$TIMESCALEDB_USERNAME" ]]; then
    echo "TIMESCALEDB_PASSWORD and TIMESCALEDB_USERNAME Environment Variables are required to create telemetry model database secret"
else
    kubectl create secret generic telemetry-model-db --from-literal=password=$TIMESCALEDB_PASSWORD --from-literal=username=$TIMESCALEDB_USERNAME
fi