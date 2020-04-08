# time-tracker-api

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
    
    
- Install the [Microsoft ODBC Driver for SQL Server](https://docs.microsoft.com/en-us/sql/connect/odbc/microsoft-odbc-driver-for-sql-server?view=sql-server-ver15) 
in your operative system. Then you have to check out what is the name of the SQL Driver installation. 
Check it out with:

```bash
vim /usr/local/etc/odbcinst.ini
```

It may display something like

```.ini
[ODBC Driver 17 for SQL Server] 
Description=Microsoft ODBC Driver 17 for SQL Server 
Driver=/usr/local/lib/libmsodbcsql.17.dylib 
UsageCount=2
```

Then specify the driver name, in this case _DBC Driver 17 for SQL Server_ in the `DATABASE_URI`, e.g.:

```.dotenv
DATABASE_URI=mssql+pyodbc://<user>:<password>@time-tracker-srv.database.windows.net/<database>?driver\=ODBC Driver 17 for SQL Server
```

To troubleshoot issues regarding this part please check out:
- [Install the Microsoft ODBC driver for SQL Server (macOS)](https://docs.microsoft.com/en-us/sql/connect/odbc/linux-mac/install-microsoft-odbc-driver-sql-server-macos?view=sql-server-ver15).
- Github issue [odbcinst: SQLRemoveDriver failed with Unable to find component name](https://github.com/Microsoft/homebrew-mssql-preview/issues/2).
- Stack overflow solution to [Can't open lib 'ODBC Driver 13 for SQL Server'? Sym linking issue?](https://stackoverflow.com/questions/44527452/cant-open-lib-odbc-driver-13-for-sql-server-sym-linking-issue).

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


## Development

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

The database tests will be done in the table `tests` of the database specified by the variable `DATABASE_URI`. If this
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
We use [angular commit message style](https://github.com/angular/angular.js/blob/master/DEVELOPERS.md#commits) as the standard commit message style.

### Release
1. A Release can be done manually or automatically using CI, in either case the variable `GH_TOKEN` is required
to post releases to Github. The `GH_TOKEN` can be generated following [these steps](https://help.github.com/es/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line)

2. We use the command `semantic-release publish` after a successful PR to make a release. Check the library
[python-semantic-release](https://python-semantic-release.readthedocs.io/en/latest/commands.html#publish) for details of underlying operations.

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