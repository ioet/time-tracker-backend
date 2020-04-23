# time-tracker-api

[![Build status](https://dev.azure.com/IOET-DevOps/TimeTracker-API/_apis/build/status/TimeTracker-API%20-%20CI)](https://dev.azure.com/IOET-DevOps/TimeTracker-API/_build/latest?definitionId=1)

This is the mono-repository for the backend services and their common codebase



## Getting started
Follow the following instructions to get the project ready to use ASAP.


### Requirements
Be sure you have installed in your system

- [Python version 3](https://www.python.org/download/releases/3.0/) in your path. It will install
automatically [pip](https://pip.pypa.io/en/stable/) as well.
- A virtual environment, namely [venv](https://docs.python.org/3/library/venv.html).

### Setup
- Create and activate the environment,
    
    In Windows:
    
    ``` 
    python -m venv .venv
    .venv\Scripts\activate.bat
    ```
        
    In Unix based operative systems: 
    ```
    virtualenv .venv
    source .venv/bin/activate
    ```
    
- Install the requirements:
    ```
    python3 -m pip install -r requirements/<app>/<stage>.txt
    ```
    
    Where <app> is one of the executable app namespace, e.g. `time_tracker_api`.
    The `stage` can be 
    
    * `dev`: Used for working locally
    * `prod`: For anything deployed
    
    
    Remember to do it with Python 3.

- Run `pre-commit install`. For more details, check out Development > Git hooks.

### How to use it
- Set the env var `FLASK_APP` to `time_tracker_api` and start the app:

    In Windows
    ```
    set FLASK_APP=time_tracker_api
    flask run
    ```
    In Unix based operative systems: 
    ```
    export FLASK_APP=time_tracker_api
    flask run
    ```

- Open `http://127.0.0.1:5000/` in a browser. You will find in the presented UI 
a link to the swagger.json with the definition of the api.

### Security
In this API we are requiring authenticated users using JWT. To do so, we are using the library 
[PyJWT](https://pypi.org/project/PyJWT/), so in every request to the API we expect a header `Authorization` with a format 
like:

>Bearer <JWT>

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

## Development

### Git hooks
We use [pre-commit](https://github.com/pre-commit/pre-commit) library to manage local git hooks, as developers we just need to run in our virtual environment:

```
pre-commit install
```
With this command the library will take configuration from `.pre-commit-config.yaml` and will set up the hooks by us. 

Currently, we only have a hook to enforce semantic commit message.

### Test
We are using [Pytest](https://docs.pytest.org/en/latest/index.html) for tests. The tests are located in the package 
`tests` and use the [conventions for python test discovery](https://docs.pytest.org/en/latest/goodpractices.html#test-discovery).

#### Integration tests
The [integrations tests](https://en.wikipedia.org/wiki/Integration_testing) verifies that all the components of the app
are working well together. These are the default tests we should run:

```dotenv
python3 -m pytest -v --ignore=tests/commons/data_access_layer/azure/sql_repository_test.py
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
(test_* files) with the help of an IDE like PyCharm.

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
An specific requirement file was created to run the migrations in `requirements/migrations.txt`. This way we do not mix
any possible vulnerable dependency brought by these dependencies to the environment `prod`. Therefore the dependencies
to run the migrations shall be installed this way:

```bash
pip install -r requirements/<app>/prod.txt
pip install -r requirements/migrations.txt
```

All the migrations will be handled and created in the python package `migrations`. In order to create a migration we 
must do it manually (for now) and prefixed by a number, e.g. `migrations/01-initialize-db.py` in order to warranty the 
order of execution alphabetically.
Inside every migration there is an `up` and `down` method. The `down` method is executed from the persisted migration in
the database. Whe a `down` logic that used external dependencies was tested it failed, whilst I put that same logic in 
the an `up` method it run correctly. In general the library seems to present [design issues](https://github.com/Lieturd/migrate-anything/issues/3).
Therefore, it is recommended to apply changes just in one direction: `up`.
For more information, please check out [some examples](https://github.com/Lieturd/migrate-anything/tree/master/examples) 
that illustrates the usage of this migration tool.

Basically, for running the migrations you must execute

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
[API import restrictions and known issues](https://docs.microsoft.com/en-us/azure/api-management/api-management-api-import-restrictions)
in Azure.

## License

Copyright 2020 ioet Inc. All Rights Reserved.