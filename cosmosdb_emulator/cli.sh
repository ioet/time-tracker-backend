#!/bin/sh
COMMAND=$@
API_CONTAINER_NAME="time-tracker-backend_api"
TIME_TRACKER_CLI_URL="cosmosdb_emulator/time_tracker_cli"
TIME_TRACKER_CLI="python3 $COMMAND"
DEFAULT_SCRIPT_NAME='main.py'
FIRST_ARG=$1

if [ "$FIRST_ARG" != "$DEFAULT_SCRIPT_NAME" ]; then
    echo "Do not forget that the file name is $DEFAULT_SCRIPT_NAME and needs to be sent as first parameter"
    echo "For example: ./cli.sh main.py"
    exit 0
fi

DATABASE_EMULATOR_KEY="C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=="
DATABASE_ENV_KEY=$DATABASE_MASTER_KEY

if [ "$DATABASE_EMULATOR_KEY" != "$DATABASE_ENV_KEY" ]; then
    echo "You are trying to run this CLI in a non-development environment. We can not proceed with this action"
    exit 0
fi

execute(){
    docker exec -ti $API_CONTAINER_NAME sh -c "cd $TIME_TRACKER_CLI_URL && $TIME_TRACKER_CLI"
}

execute