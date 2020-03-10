# time-tracker-api

## Set new environment in Windows
- `mkdir .venv`
- `python -m venv .venv`
- `.venv\Scripts\activate.bat`
- `pip install -r requirements/prod.txt`

## Example usage in Windows
- `export FLASK_APP=time_tracker_api` or `set FLASK_APP=time_tracker_api`
- `flask run`
- Open `http://127.0.0.1:5000/` in a browser