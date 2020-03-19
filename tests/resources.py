from time_tracker_api.sql_repository import db, SQLAuditedModel


class PersonSQLModel(db.Model, SQLAuditedModel):
    __tablename__ = 'tests'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<Test Model %r>' % self.name
