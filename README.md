# time-tracker-api

## Setup

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
    python3 -m pip install -r requirements/prod.txt
    ```
    Remember to do it with Python 3.

## How to use it
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

- Open `http://127.0.0.1:5000/` in a browser