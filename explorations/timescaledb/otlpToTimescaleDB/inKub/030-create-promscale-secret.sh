if [[ -z "$PROMSCALE_DB_URI" ]]; then
    echo "PROMSCALE_DB_URI Environment Variable is required to create database secret"
else
    kubectl create secret generic promscale --from-literal=db-uri=$PROMSCALE_DB_URI
fi