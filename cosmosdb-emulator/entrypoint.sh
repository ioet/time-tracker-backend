#!/bin/sh

until curl -ksf "${DATABASE_ACCOUNT_URI}/_explorer/emulator.pem" -o 'cosmosdb-emulator/emulatorcert.crt'; do
    echo "Waiting for Cosmosdb to start..."
    sleep 10
done

echo "Container cosmosemulator started."

echo "Importing SSL..."
cp cosmosdb-emulator/emulatorcert.crt /usr/local/share/ca-certificates/
cp cosmosdb-emulator/emulatorcert.crt /usr/share/ca-certificates/
update-ca-certificates --fresh
echo "Importing Containers..."
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/
python3 ./cosmosdb-emulator/init_emulator_db.py
echo "Installation succeed!!"

echo "Starting Flask!!"
flask run