#!/bin/sh
PYTHON_COMMAND="pip install azure-functions"
PYTHON_TEST="python3 -m pytest -v --ignore=tests/commons/data_access_layer/azure/sql_repository_test.py"
API_CONTAINER_NAME="time-tracker-backend_api"
execute(){
    
    docker exec -ti $API_CONTAINER_NAME sh -c "$PYTHON_COMMAND"
    docker exec -ti $API_CONTAINER_NAME sh -c "awk -v cmd='openssl x509 -noout -subject' '/BEGIN/{close(cmd)};{print | cmd}' < /etc/ssl/certs/ca-certificates.crt | grep host"
    docker exec -ti $API_CONTAINER_NAME sh -c "env"
    docker exec -ti $API_CONTAINER_NAME sh -c "$PYTHON_TEST"

}


execute