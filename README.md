# time-tracker-api

[![Build status](https://dev.azure.com/IOET-DevOps/TimeTracker-API/_apis/build/status/TimeTracker-API%20-%20CI)](https://dev.azure.com/IOET-DevOps/TimeTracker-API/_build/latest?definitionId=1)

This is the mono-repository for the backend services and their common codebase

## Getting started

Follow the following instructions to get the project ready to use ASAP.

### Requirements

Be sure you have installed in your system

- [Python version 3](https://www.python.org/download/releases/3.0/) (recommended 3.8 or less) in your path. It will install
  automatically [pip](https://pip.pypa.io/en/stable/) as well.
- A virtual environment, namely [venv](https://docs.python.org/3/library/venv.html).
- Optionally for running Azure functions locally: [Azure functions core tool](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=macos%2Ccsharp%2Cbash).

### Setup

- Create and activate the environment,

  In Windows:

  ```
  #Create virtual enviroment
  python -m venv .venv

  #Execute virtual enviroment
  .venv\Scripts\activate.bat
  ```

  In Unix based operative systems:

  ```
  #Create virtual enviroment
  virtualenv .venv

  #Execute virtual enviroment
  source .venv/bin/activate
  ```

**Note:** If you're a linux user you will need to install an additional dependency to have it working.

Type in the terminal the following command to install the required dependency to have pyodbc working locally:

```sh
sudo apt-get install unixodbc-dev
```

- Install the requirements:

  ```
  python3 -m pip install -r requirements/<app>/<stage>.txt
  ```

  If you use Windows, you will use this comand:

  ```
  python -m pip install -r requirements/<app>/<stage>.txt
  ```

  Where `<app>` is one of the executable app namespace, e.g. `time_tracker_api` or `time_tracker_events` (**Note:** Currently, only `time_tracker_api` is used.). The `stage` can be

  - `dev`: Used for working locally
  - `prod`: For anything deployed

Remember to do it with Python 3.

Bear in mind that the requirements for `time_tracker_events`, must be located on its local requirements.txt, by
[convention](https://docs.microsoft.com/en-us/azure/azure-functions/functions-reference-python#folder-structure).

- Run `pre-commit install -t pre-commit -t commit-msg`. For more details, see section Development > Git hooks.

### Set environment variables

Set environment variables with the content pinned in our slack channel #time-tracker-developer:

When you use Bash or GitBash you should use:

```
export MS_AUTHORITY=XXX
export MS_CLIENT_ID=XXX
export MS_SCOPE=XXX
export MS_SECRET=XXX
export MS_ENDPOINT=XXX
export DATABASE_ACCOUNT_URI=XXX
export DATABASE_MASTER_KEY=XXX
export DATABASE_NAME=XXX
export FLASK_APP=XXX
export AZURE_APP_CONFIGURATION_CONNECTION_STRING=XXX
export FLASK_DEBUG=True
```

If you use PowerShell, you should use:

```
$env:MS_AUTHORITY="XXX"
$env:MS_CLIENT_ID="XXX"
$env:MS_SCOPE="XXX"
$env:MS_SECRET="XXX"
$env:MS_ENDPOINT="XXX"
$env:DATABASE_ACCOUNT_URI="XXX"
$env:DATABASE_MASTER_KEY="XXX"
$env:DATABASE_NAME="XXX"
$env:FLASK_APP="XXX"
$env:AZURE_APP_CONFIGURATION_CONNECTION_STRING="XXX"
$env:FLASK_DEBUG="True"
```

If you use Command Prompt, you should use:

```
set "MS_AUTHORITY=XXX"
set "MS_CLIENT_ID=XXX"
set "MS_SCOPE=XXX"
set "MS_SECRET=XXX"
set "MS_ENDPOINT=XXX"
set "DATABASE_ACCOUNT_URI=XXX"
set "DATABASE_MASTER_KEY=XXX"
set "DATABASE_NAME=XXX"
set "FLASK_APP=XXX"
set "AZURE_APP_CONFIGURATION_CONNECTION_STRING=XXX"
set "FLASK_DEBUG=True"
```

**Note:** You can create .env (Bash, GitBash), .env.bat (Command Prompt), .env.ps1 (PowerShell) files with environment variables and run them in the corresponding console.

Important: You should set the environment variables each time the application is run.

### How to use it

- Start the app:

  ```
  flask run
  ```

- Open `http://127.0.0.1:5000/` in a browser. You will find in the presented UI
  a link to the swagger.json with the definition of the api.

### Handling Cosmos DB triggers for creating events with time_tracker_events

The project `time_tracker_events` is an Azure Function project. Its main responsibility is to respond to calls related to
events, like those [triggered by Change Feed](https://docs.microsoft.com/en-us/azure/cosmos-db/change-feed-functions).
Every time a write action (`create`, `update`, `soft-delete`) is done by CosmosDB, thanks to [bindings](https://docs.microsoft.com/en-us/azure/azure-functions/functions-bindings-cosmosdb?toc=%2Fazure%2Fcosmos-db%2Ftoc.json&bc=%2Fazure%2Fcosmos-db%2Fbreadcrumb%2Ftoc.json&tabs=csharp)
these functions will be called. You can also run them in your local machine:

- You must have the [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/get-started-with-azure-cli?view=azure-cli-latest)
  and the [Azure Functions Core Tools](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=macos%2Ccsharp%2Cbash)
  installed in your local machine.
- Be sure to [authenticate](https://docs.microsoft.com/en-us/cli/azure/authenticate-azure-cli?view=azure-cli-latest)
  with the Azure CLI if you are not.

```bash
az login
```

- Execute the project

```bash
cd time_tracker_events
source run.sh
```

You will see that a large console log will appear ending with a message like

```log
Now listening on: http://0.0.0.0:7071
Application started. Press Ctrl+C to shut down.
```

- Now you are ready to start generating events. Just execute any change in your API and you will see how logs are being
  generated by the console app you ran before. For instance, this is the log generated when I restarted a time entry:

```log
[04/30/2020 14:42:12] Executing 'Functions.handle_time_entry_events_trigger' (Reason='New changes on collection time_entry at 2020-04-30T14:42:12.1465310Z', Id=3da87e53-0434-4ff2-8db3-f7c051ccf9fd)
[04/30/2020 14:42:12]  INFO: Received FunctionInvocationRequest, request ID: 578e5067-b0c0-42b5-a1a4-aac858ea57c0, function ID: c8ac3c4c-fefd-4db9-921e-661b9010a4d9, invocation ID: 3da87e53-0434-4ff2-8db3-f7c051ccf9fd
[04/30/2020 14:42:12]  INFO: Successfully processed FunctionInvocationRequest, request ID: 578e5067-b0c0-42b5-a1a4-aac858ea57c0, function ID: c8ac3c4c-fefd-4db9-921e-661b9010a4d9, invocation ID: 3da87e53-0434-4ff2-8db3-f7c051ccf9fd
[04/30/2020 14:42:12] {"id": "9ac108ff-c24d-481e-9c61-b8a3a0737ee8", "project_id": "c2e090fb-ae8b-4f33-a9b8-2052d67d916b", "start_date": "2020-04-28T15:20:36.006Z", "tenant_id": "cc925a5d-9644-4a4f-8d99-0bee49aadd05", "owner_id": "709715c1-6d96-4ecc-a951-b628f2e7d89c", "end_date": null, "_last_event_ctx": {"user_id": "709715c1-6d96-4ecc-a951-b628f2e7d89c", "tenant_id": "cc925a5d-9644-4a4f-8d99-0bee49aadd05", "action": "update", "description": "Restart time entry", "container_id": "time_entry", "session_id": null}, "description": "Changing my description for testing Change Feed", "_metadata": {}}
[04/30/2020 14:42:12] Executed 'Functions.handle_time_entry_events_trigger' (Succeeded, Id=3da87e53-0434-4ff2-8db3-f7c051ccf9fd)
```

### Security

In this API we are requiring authenticated users using JWT. To do so, we are using the library
[PyJWT](https://pypi.org/project/PyJWT/), so in every request to the API we expect a header `Authorization` with a format
like:

> Bearer <JWT>

In the Swagger UI, you will now see a new button called "Authorize":
![image](https://user-images.githubusercontent.com/6514740/80011459-841f7580-8491-11ea-9c23-5bfb8822afe6.png)

when you click it then you will be notified that you must enter the content of the Authorization header, as mentioned
before:
![image](https://user-images.githubusercontent.com/6514740/80011702-d95b8700-8491-11ea-973a-8aaf3cdadb00.png)

Click "Authorize" and then close that dialog. From that moment forward you will not have to do it anymore because the
Swagger UI will use that JWT in every call, e.g.
![image](https://user-images.githubusercontent.com/6514740/80011852-0e67d980-8492-11ea-9dd3-2b1efeaa57d8.png)

If you want to check out the data (claims) that your JWT contains, you can also use the CLI of
[PyJWT](https://pypi.org/project/PyJWT/):

```
pyjwt decode --no-verify "<JWT>"
```

Bear in mind that this API is not in charge of verifying the authenticity of the JWT, but the API Management.

### Important notes

Due to the used technology and particularities on the implementation of this API, it is important that you respect the
following notes regarding to the manipulation of the data from and towards the API:

- The [recommended](https://docs.microsoft.com/en-us/azure/cosmos-db/working-with-dates#storing-datetimes) format for
  DateTime strings in Azure Cosmos DB is `YYYY-MM-DDThh:mm:ss.fffffffZ` which follows the ISO 8601 **UTC standard**.

The Azure function project `time_tracker_events` also have some constraints to have into account. It is recommended that
you read the [Azure Functions Python developer guide](https://docs.microsoft.com/en-us/azure/azure-functions/functions-reference-python#folder-structure).

If you require to deploy `time_tracker_events` from your local machine to Azure Functions, you can execute:

```bash
func azure functionapp publish time-tracker-events  --build local
```

## Development

### Git hooks

We use [pre-commit](https://github.com/pre-commit/pre-commit) library to manage local git hooks, as developers we just need to run in our virtual environment:

```
pre-commit install -t pre-commit -t commit-msg
```

With this command the library will take configuration from `.pre-commit-config.yaml` and will set up the hooks by us.

### Commit message style

Use the following commit message style. e.g:

```
'feat: TT-123 Applying some changes'
'fix: TT-321 Fixing something broken'
'feat(config): TT-00 Fix something in config files'
```

The value `TT-###` refers to the Jira issue that is being solved. Use TT-00 if the commit does not refer to any issue.

### Branch names format

For example if your task in Jira is **TT-48 implement semantic versioning** your branch name is:

```
   TT-48-implement-semantic-versioning
```

### Test

We are using [Pytest](https://docs.pytest.org/en/latest/index.html) for tests. The tests are located in the package
`tests` and use the [conventions for python test discovery](https://docs.pytest.org/en/latest/goodpractices.html#test-discovery).

#### Integration tests

The [integrations tests](https://en.wikipedia.org/wiki/Integration_testing) verifies that all the components of the app
are working well together. These are the default tests we should run:

This command run all tests:

```dotenv
python3 -m pytest -v --ignore=tests/commons/data_access_layer/azure/sql_repository_test.py
```

In windows

```
python -m pytest -v --ignore=tests/commons/data_access_layer/azure/sql_repository_test.py
```

**Note:** If you get the error "No module named azure.functions", execute the command:

```
pip install azure-functions
```

To run a sigle test:

```
pytest -v -k name-test
```

As you may have noticed we are ignoring the tests related with the repository.

#### System tests

In addition to the integration testing we might include tests to the data access layer in order to verify that the
persisted data is being managed the right way, i.e. it actually works. We may classify the execution of all the existing
tests as [system testing](https://en.wikipedia.org/wiki/System_testing):

```dotenv
python3 -m pytest -v
```

The database tests will be done in the table `tests` of the database specified by the variable `SQL_DATABASE_URI`. If this
variable is not specified it will automatically connect to SQLite database in-memory. This will do, because we are using
[SQL Alchemy](https://www.sqlalchemy.org/features.html) to be able connect to any SQL database maintaining the same
codebase.

The option `-v` shows which tests failed or succeeded. Have into account that you can also debug each test
(test\_\* files) with the help of an IDE like PyCharm.

#### Coverage

To check the coverage of the tests execute

```bash
 coverage run -m pytest -v
```

To get a report table

```bash
 coverage report
```

To get a full report in html

```bash
 coverage html
```

Then check in the [htmlcov/index.html](./htmlcov/index.html) to see it.

If you want that previously collected coverage data is erased, you can execute:

```
coverage erase
```

### CLI

There are available commands, aware of the API, that can be very helpful to you. You
can check them out by running

```
python cli.py
```

If you want to run an specific command, e.g. `gen_swagger_json`, specify it as a param
as well as its correspondent options.

```
python cli.py gen_swagger_json -f ~/Downloads/swagger.json
```

## Semantic versioning

### Style

We use [angular commit message style](https://github.com/angular/angular.js/blob/master/DEVELOPERS.md#commits) as the
standard commit message style.

### Release

1. The release is automatically done by the [TimeTracker CI](https://dev.azure.com/IOET-DevOps/TimeTracker-API/_build?definitionId=1&_a=summary)
   although can also be done manually. The variable `GH_TOKEN` is required to post releases to Github. The `GH_TOKEN` can
   be generated following [these steps](https://help.github.com/es/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line).

2. We use the command `semantic-release publish` after a successful PR to make a release. Check the library
   [python-semantic-release](https://python-semantic-release.readthedocs.io/en/latest/commands.html#publish) for details of
   underlying operations.

## Run as docker container

1. Build image

```bash
docker build -t time_tracker_api:local .
```

2. Run app

```bash
docker run -p 5000:5000 time_tracker_api:local
```

3. Visit `127.0.0.1:5000`

## Migrations

Looking for a DB-agnostic migration tool, the only choice I found was [migrate-anything](https://pypi.org/project/migrate-anything/).
A specific requirement file was created to run the migrations in `requirements/migrations.txt`. This way we do not mix
any possible vulnerable dependency brought by these dependencies to the environment `prod`. Therefore the dependencies
to run the migrations shall be installed this way:

```bash
pip install -r requirements/<app>/prod.txt
pip install -r requirements/migrations.txt
```

All the migrations will be handled and created in the python package `migrations`. In order to create a migration we
must do it manually (for now) and prefixed by a number, e.g. `migrations/01-initialize-db.py` in order to guarantee the
order of execution alphabetically.
Inside every migration there is an `up` and `down` method. The `down` method is executed from the persisted migration in
the database. When a `down` logic that used external dependencies was tested, it failed; whilst, I put that same logic in
the `up` method, it run correctly. In general, the library seems to present [design issues](https://github.com/Lieturd/migrate-anything/issues/3).
Therefore, it is recommended to apply changes just in one direction: `up`.
For more information, please check out [some examples](https://github.com/Lieturd/migrate-anything/tree/master/examples)
that illustrate the usage of this migration tool.

Basically, for running the migrations you must execute:

```bash
migrate-anything migrations
```

They will be automatically run during the Continuous Deployment process.

## Built with

- [Python version 3](https://www.python.org/download/releases/3.0/) as backend programming language. Strong typing for
  the win.
- [Flask](http://flask.pocoo.org/) as the micro framework of choice.
- [Flask RestPlus](https://flask-restplus.readthedocs.io/en/stable/) for building Restful APIs with Swagger.
- [Pytest](https://docs.pytest.org/en/latest/index.html) for tests.
- [Coverage](https://coverage.readthedocs.io/en/coverage-4.5.4/) for coverage.
- [Swagger](https://swagger.io/) for documentation and standardization, taking into account the
  [API import restrictions and known issues](https://docs.microsoft.com/en-us/azure/api-management/api-management-api-import-restrictions) in Azure.
- [Azure Functions bindings](https://docs.microsoft.com/en-us/azure/azure-functions/functions-bindings-cosmosdb?toc=%2Fazure%2Fcosmos-db%2Ftoc.json&bc=%2Fazure%2Fcosmos-db%2Fbreadcrumb%2Ftoc.json&tabs=csharp)
  for making `time_tracker_events` to handle the triggers [generated by our Cosmos DB database throw Change Feed](https://docs.microsoft.com/bs-latn-ba/azure/cosmos-db/change-feed-functions).

## Feature Toggles dictionary

Shared file with all the Feature Toggles we create, so we can have a history of them
[Feature Toggles dictionary](https://github.com/ioet/time-tracker-ui/wiki/Feature-Toggles-dictionary)

## Support for docker-compose and cosmosdb emulator

To run the dev enviroment in docker-compose:
```bash
docker-compose up
```

## More information about the project

[Starting in Time Tracker](https://github.com/ioet/time-tracker-ui/wiki/Time-tracker)

## License

Copyright 2020 ioet Inc. All Rights Reserved.
