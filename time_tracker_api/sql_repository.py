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

    def create(self, element: dict) -> dict:
        db.session.add(element)
        db.session.commit()
        return element

    def find(self, id: int) -> dict:
        return self.model_type.query.filter_by(id=id).first_or_404()

    def find_all(self) -> list:
        return self.model_type.query.all()

    def update(self, id: int, new_data: dict) -> dict:
        model = self.model_type.query.filter_by(id=id)
        model.update(new_data)
        return model.first_or_404()

    def remove(self, id: int) -> None:
        found_element = self.find(id)
        db.session.delete(found_element)
        db.session.commit()

    def find_all_contain_str(self, property, text) -> list:
        return self.model_type.query\
            .filter(getattr(self.model_type, property).contains(text))\
            .all()


repository_model = SQLRepository
