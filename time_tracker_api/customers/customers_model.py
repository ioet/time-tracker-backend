from azure.cosmos import PartitionKey

from time_tracker_api.database import CRUDDao


class CustomerDao(CRUDDao):
    pass


def create_dao() -> CustomerDao:
    from commons.data_access_layer.sql import db
    from time_tracker_api.database import COMMENTS_MAX_LENGTH
    from commons.data_access_layer.sql import SQLCRUDDao
    from sqlalchemy_utils import UUIDType
    import uuid

    class CustomerSQLModel(db.Model):
        __tablename__ = 'customer'
        id = db.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
        name = db.Column(db.String(50), unique=True, nullable=False)
        description = db.Column(db.String(COMMENTS_MAX_LENGTH), unique=False, nullable=False)
        deleted = db.Column(UUIDType(binary=False), default=uuid.uuid4)
        tenant_id = db.Column(UUIDType(binary=False), default=uuid.uuid4)

        def __repr__(self):
            return '<Customer %r>' % self.name

        def __str___(self):
            return "the customer \"%s\"" % self.name

    class CustomerSQLDao(SQLCRUDDao):
        def __init__(self):
            SQLCRUDDao.__init__(self, CustomerSQLModel)

    return CustomerSQLDao()


container_definition = {
    'id': 'customer',
    'partition_key': PartitionKey(path='/tenant_id'),
    'unique_key_policy': {
        'uniqueKeys': [
            {'paths': ['/name']},
            {'paths': ['/deleted']},
        ]
    }
}
