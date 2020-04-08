import pytest
from faker import Faker
from flask import Flask
from flask.testing import FlaskClient

from commons.data_access_layer.cosmos_db import CosmosDBRepository
from time_tracker_api import create_app

fake = Faker()
Faker.seed()


@pytest.fixture(scope='session')
def app() -> Flask:
    return create_app("time_tracker_api.config.TestConfig")


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    with app.test_client() as c:
        return c


@pytest.fixture(scope="module")
def sql_model_class():
    from commons.data_access_layer.sql import db, AuditedSQLModel
    class PersonSQLModel(db.Model, AuditedSQLModel):
        __tablename__ = 'test'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(80), unique=False, nullable=False)
        email = db.Column(db.String(120), unique=True, nullable=False)
        age = db.Column(db.Integer, nullable=False)

        def __repr__(self):
            return '<Test Model %r>' % self.name

    return PersonSQLModel


@pytest.fixture(scope="module")
def sql_repository(app: Flask, sql_model_class):
    with app.app_context():
        from commons.data_access_layer.sql import init_app, db

        if db is None:
            init_app(app)
            from commons.data_access_layer.sql import db

        db.metadata.create_all(bind=db.engine, tables=[sql_model_class.__table__])
        app.logger.info("SQl test models created!")

        from commons.data_access_layer.sql import SQLRepository
        yield SQLRepository(sql_model_class)

        db.metadata.drop_all(bind=db.engine, tables=[sql_model_class.__table__])
        app.logger.info("SQL test models removed!")


@pytest.fixture(scope="module")
def cosmos_db_model():
    from azure.cosmos import PartitionKey
    return {
        'id': 'tests',
        'partition_key': PartitionKey(path='/tenant_id'),
        'unique_key_policy': {
            'uniqueKeys': [
                {'paths': ['/email']},
            ]
        }
    }


@pytest.yield_fixture(scope="module")
def cosmos_db_repository(app: Flask, cosmos_db_model) -> CosmosDBRepository:
    with app.app_context():
        from commons.data_access_layer.cosmos_db import init_app, cosmos_helper

        if cosmos_helper is None:
            init_app(app)
            from commons.data_access_layer.cosmos_db import cosmos_helper

        app.logger.info("Creating Cosmos DB test models...")
        cosmos_helper.create_container(cosmos_db_model)
        app.logger.info("Cosmos DB test models created!")

        yield CosmosDBRepository.from_definition(cosmos_db_model)

        app.logger.info("Removing Cosmos DB test models...")
        cosmos_helper.delete_container(cosmos_db_model["id"])
        app.logger.info("Cosmos DB test models removed!")


@pytest.fixture(scope="session")
def tenant_id() -> str:
    return fake.uuid4()


@pytest.fixture(scope="session")
def another_tenant_id() -> str:
    return fake.uuid4()


@pytest.fixture(scope="function")
def sample_item(cosmos_db_repository: CosmosDBRepository, tenant_id: str) -> dict:
    sample_item_data = dict(id=fake.uuid4(),
                            name=fake.name(),
                            email=fake.safe_email(),
                            age=fake.pyint(min_value=10, max_value=80),
                            tenant_id=tenant_id)

    return cosmos_db_repository.create(sample_item_data)
