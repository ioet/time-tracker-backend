from flask import Flask
from V2.source.entry_points.flask_api.api import init_app

app = Flask(__name__)
init_app(app)
