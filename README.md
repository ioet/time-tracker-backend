# time-tracker-api

The API of the TSheets killer app.

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
    python3 -m pip install -r requirements/<stage>.txt
    ```
    
    The `stage` can be `dev` or `prod`. 
    Remember to do it with Python 3.

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
We are using Pytest](https://docs.pytest.org/en/latest/index.html) for tests. The tests are located in the package 
`tests` and use the [conventions for python test discovery](https://docs.pytest.org/en/latest/goodpractices.html#test-discovery).

To run the tests just execute:

```bash
python3 -m pytest -v
```

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
Then check in the [htmlcov/index.html](./htmlcov/index.html) to see it

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

## Run as docker container

1. Build image
```bash
docker build -t time_tracker_api:local .
```

2. Run app
```bash
docker run -p 5000:5000 time_tracker_api:local
```

3. Visit `0.0.0.0:5000`

## Built with
- [Python version 3](https://www.python.org/download/releases/3.0/) as backend programming language. Strong typing for 
the win.
- [Flask](http://flask.pocoo.org/) as the micro framework of choice.
- [Flask RestPlus](https://flask-restplus.readthedocs.io/en/stable/) for building Restful APIs with Swagger.
- [Pytest](https://docs.pytest.org/en/latest/index.html) for tests
- [Coverage](https://coverage.readthedocs.io/en/coverage-4.5.4/) for coverage
- [Swagger](https://swagger.io/) for documentation and standardization, taking into account the
[API import restrictions and known issues](https://docs.microsoft.com/en-us/azure/api-management/api-management-api-import-restrictions)
in Azure.


## License

Copyright 2020 ioet Inc. All Rights Reserved.