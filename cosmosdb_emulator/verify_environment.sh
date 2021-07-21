#!/bin/bash

echo "We are checking the development environment..."

DATABASE_EMULATOR_KEY="C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=="
DATABASE_ENV_KEY=$DATABASE_MASTER_KEY

if [ "$DATABASE_EMULATOR_KEY" != "$DATABASE_ENV_KEY" ]; then
  echo "You are trying to run this CLI in a non-development environment. We can not proceed with this action"
  exit 0
fi

echo "GREAT! You are on development environment"