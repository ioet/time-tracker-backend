#!/bin/sh
COMMAND=$@
PYTHON_COMMAND="pip install azure-functions"
API_CONTAINER_NAME="time-tracker-backend_api"

execute(){
    docker exec -ti $API_CONTAINER_NAME sh -c "$PYTHON_COMMAND"
    docker exec -ti $API_CONTAINER_NAME sh -c "$COMMAND"
}

execute