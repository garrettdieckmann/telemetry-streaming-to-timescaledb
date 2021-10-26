if [[ -z "$TIMESCALEDB_PASSWORD" ]]; then
    echo "TIMESCALEDB_PASSWORD Environment Variable is required to create database secret"
else
    kubectl create secret generic timescaledb-password --from-literal=password=$TIMESCALEDB_PASSWORD
fi
