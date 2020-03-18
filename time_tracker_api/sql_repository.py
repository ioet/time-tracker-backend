import urllib.parse

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = None


def init_app(app: Flask) -> None:
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['DATABASE_URI']
    global db
    db = SQLAlchemy(app)


class SQLRepository():
    def __init__(self, model_type: type):
        self.model_type = model_type

    def create(self, model: dict) -> dict:
        db.session.add(model)
        db.session.commit()

    def find_all(self):
        return self.model_type.query.all()


repository_model = SQLRepository
