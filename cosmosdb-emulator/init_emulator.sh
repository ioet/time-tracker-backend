#!/bin/sh

containerId=$(docker ps --all | grep 'Time-Tracker-Cosmos-Db' | awk '{print $1}')
if [ -z "$containerId" ]; then
    ipaddr="`ifconfig | grep "inet " | grep -Fv 127.0.0.1 | awk '{print $2}' | head -n 1`"
    containerId=$(docker create -p 8081:8081 -p 10251:10251 -p 10252:10252 -p 10253:10253 -p 10254:10254  -m 3g --cpus=2.0 --name=Time-Tracker-Cosmos-Db -e AZURE_COSMOS_EMULATOR_PARTITION_COUNT=10 -e AZURE_COSMOS_EMULATOR_ENABLE_DATA_PERSISTENCE=true -e AZURE_COSMOS_EMULATOR_IP_ADDRESS_OVERRIDE=$ipaddr -it mcr.microsoft.com/cosmosdb/linux/azure-cosmos-emulator)
    echo "##vso[task.setvariable variable=cosmosDbContainerId]$containerId"> /dev/tty
fi
docker start $containerId

until curl -ksf "127.0.0.1:8081/_explorer/emulator.pem" -o 'cosmosdb-emulator/emulatorcert.crt'; do
    echo "Waiting for Cosmosdb to start..."
    sleep 10
done

echo "Container cosmosemulator started."

echo "Checking SSL"
isInstalled=$( awk -v cmd='openssl x509 -noout -subject' '/BEGIN/{close(cmd)};{print | cmd}' < /etc/ssl/certs/ca-certificates.crt | grep host ) || :

echo "ps"
echo "$isInstalled"

if [ -z "$isInstalled" ]; then
    echo "Importing SSL..."
    cp cosmosdb-emulator/emulatorcert.crt /usr/local/share/ca-certificates/
    cp cosmosdb-emulator/emulatorcert.crt /usr/share/ca-certificates/
    update-ca-certificates --fresh
    echo "Importing Containers..."
    export REQUESTS_CA_BUNDLE=/etc/ssl/certs/
    python3 ./cosmosdb-emulator/init_emulator_db.py
    echo "Installation succeed!!"
fi

echo "Starting Flask!!" 
flask run