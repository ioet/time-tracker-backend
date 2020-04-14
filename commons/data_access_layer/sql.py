from datetime import datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from commons.data_access_layer.database import CRUDDao, ID_MAX_LENGTH
from time_tracker_api.security import current_user_id

db: SQLAlchemy = None
AuditedSQLModel = None


def handle_commit_issues(f):
    def rollback_if_necessary(*args, **kw):
        try:
            return f(*args, **kw)
        except:  # pragma: no cover
            db.session.rollback()
            raise

    return rollback_if_necessary


def init_app(app: Flask) -> None:
    global db
    db = SQLAlchemy(app)

    global AuditedSQLModel

    class AuditedSQLModelClass():
        created_at = db.Column(db.DateTime, server_default=db.func.now())
        updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
        created_by = db.Column(db.String(ID_MAX_LENGTH), default=current_user_id)
        updated_by = db.Column(db.String(ID_MAX_LENGTH), onupdate=current_user_id)

    AuditedSQLModel = AuditedSQLModelClass


class SQLRepository():
    def __init__(self, model_type: type):
        self.model_type = model_type

    @handle_commit_issues
    def create(self, data: dict):
        element = self.model_type(**data)
        db.session.add(element)
        db.session.commit()
        return element

    def find(self, id: int):
        return self.model_type.query.filter_by(id=id).first_or_404()

    def find_all(self):
        return self.model_type.query.all()

    @handle_commit_issues
    def update(self, id: int, new_data):
        model = self.model_type.query.filter_by(id=id)
        model.update(new_data)
        db.session.commit()
        return model.first_or_404()

    @handle_commit_issues
    def remove(self, id: int) -> None:
        found_element = self.find(id)
        db.session.delete(found_element)
        db.session.commit()

    def find_all_contain_str(self, property, text):
        return self.model_type.query \
            .filter(getattr(self.model_type, property).contains(text)) \
            .all()


class SQLCRUDDao(CRUDDao):
    def __init__(self, model: type):
        self.repository = SQLRepository(model)

    def get_all(self) -> list:
        return self.repository.find_all()

    def get(self, id):
        return self.repository.find(id)

    def create(self, element: dict):
        return self.repository.create(element)

    def update(self, id, data: dict):
        return self.repository.update(id, data)

    def delete(self, id):
        self.repository.remove(id)
