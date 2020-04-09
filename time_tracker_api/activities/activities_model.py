from azure.cosmos import PartitionKey

from time_tracker_api.database import CRUDDao


class ActivityDao(CRUDDao):
    pass


def create_dao() -> ActivityDao:
    from sqlalchemy_utils import UUIDType
    import uuid
    from commons.data_access_layer.sql import db
    from commons.data_access_layer.sql import SQLCRUDDao

    class ActivitySQLModel(db.Model):
        __tablename__ = 'activity'
        id = db.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
        name = db.Column(db.String(50), unique=True, nullable=False)
        description = db.Column(db.String(250), unique=False, nullable=False)
        deleted = db.Column(UUIDType(binary=False), default=uuid.uuid4)
        tenant_id = db.Column(UUIDType(binary=False), default=uuid.uuid4)

        def __repr__(self):
            return '<Activity %r>' % self.name

        def __str___(self):
            return "the activity \"%s\"" % self.name

    class ActivitySQLDao(ActivityDao, SQLCRUDDao):
        def __init__(self):
            SQLCRUDDao.__init__(self, ActivitySQLModel)

    return ActivitySQLDao()


container_definition = {
    'id': 'activity',
    'partition_key': PartitionKey(path='/tenant_id'),
    'unique_key_policy': {
        'uniqueKeys': [
            {'paths': ['/name']},
            {'paths': ['/deleted']},
        ]
    }
}
