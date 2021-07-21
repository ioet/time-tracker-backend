#!/bin/sh
COMMAND=$@
API_CONTAINER_NAME="time-tracker-backend_api"
TIME_TRACKER_CLI_URL="cosmosdb_emulator/time_tracker_cli"
DEFAULT_SCRIPT_NAME="main.py"
FIRST_ARG=$1

execute(){
  docker exec -it $API_CONTAINER_NAME sh "cosmosdb_emulator/verify_environment.sh"

  if [ "$FIRST_ARG" != "$DEFAULT_SCRIPT_NAME" ]; then
    echo "Do not forget that the file name is $DEFAULT_SCRIPT_NAME and needs to be sent as first parameter"
    echo "For example: ./cli.sh main.py"
    exit 0
  fi

  TIME_TRACKER_CLI="python3 $COMMAND"

  docker exec -it $API_CONTAINER_NAME sh -c "cd $TIME_TRACKER_CLI_URL && $TIME_TRACKER_CLI"
}

execute