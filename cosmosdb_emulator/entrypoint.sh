#!/bin/sh

until curl -ksf "${DATABASE_ACCOUNT_URI}/_explorer/emulator.pem" -o 'cosmosdb_emulator/emulatorcert.crt'; do
    echo "Waiting for Cosmosdb to start..."
    sleep 10
done

echo "Development environment check..."
DATABASE_EMULATOR_KEY="C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=="
DATABASE_ENV_KEY=$DATABASE_MASTER_KEY

if [ "$DATABASE_EMULATOR_KEY" != "$DATABASE_ENV_KEY" ]; then
    echo "You are trying to build an environment different from the development, this can have negative effects."
    exit 0
fi
echo "GREAT! You are on development environment"

echo "Container cosmosemulator started."

echo "Importing SSL..."
cp cosmosdb_emulator/emulatorcert.crt /usr/local/share/ca-certificates/
cp cosmosdb_emulator/emulatorcert.crt /usr/share/ca-certificates/
update-ca-certificates --fresh
echo "Importing Containers..."
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/
python3 ./cosmosdb_emulator/init_emulator_db.py
echo "Installation succeed!!"

echo "Starting Flask!!"
flask run