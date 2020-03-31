from commons.data_access_layer.azure.sql_repository import db, AuditedSQLModel

from sqlalchemy_utils import UUIDType
import uuid


class PersonSQLModel(db.Model, AuditedSQLModel):
    __tablename__ = 'test'
    id = db.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<Test Model %r>' % self.name
