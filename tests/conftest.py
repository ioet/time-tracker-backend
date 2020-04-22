from datetime import datetime, timedelta

import jwt
import pytest
from faker import Faker
from flask import Flask, url_for
from flask.testing import FlaskClient

from commons.data_access_layer.cosmos_db import CosmosDBRepository, datetime_str, current_datetime
from time_tracker_api import create_app
from time_tracker_api.security import get_or_generate_dev_secret_key
from time_tracker_api.time_entries.time_entries_model import TimeEntryCosmosDBRepository

fake = Faker()
Faker.seed()

TEST_USER = {
    "name": "testuser@ioet.com",
    "password": "secret"
}


class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password


class AuthActions:
    """Auth actions container in tests"""

    def __init__(self, app, client):
        self._app = app
        self._client = client

    # def login(self, username=TEST_USER["name"],
    #           password=TEST_USER["password"]):
    #     login_url = url_for("security.login", self._app)
    #     return open_with_basic_auth(self._client,
    #                                 login_url,
    #                                 username,
    #                                 password)
    #
    # def logout(self):
    #     return self._client.get(url_for("security.logout", self._app),
    #                             follow_redirects=True)


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
        cosmos_helper.create_container_if_not_exists(cosmos_db_model)
        app.logger.info("Cosmos DB test models created!")

        yield CosmosDBRepository.from_definition(cosmos_db_model)

        app.logger.info("Removing Cosmos DB test models...")
        cosmos_helper.delete_container(cosmos_db_model["id"])
        app.logger.info("Cosmos DB test models removed!")


@pytest.fixture(scope="session")
def tenant_id() -> str:
    return fake.uuid4()


@pytest.fixture(scope="session")
def another_tenant_id(tenant_id) -> str:
    return tenant_id[:-5] + 'fffff'


@pytest.fixture(scope="session")
def owner_id() -> str:
    return fake.uuid4()


@pytest.fixture(scope="function")
def sample_item(cosmos_db_repository: CosmosDBRepository, tenant_id: str) -> dict:
    sample_item_data = dict(id=fake.uuid4(),
                            name=fake.name(),
                            email=fake.safe_email(),
                            age=fake.pyint(min_value=10, max_value=80),
                            tenant_id=tenant_id)

    return cosmos_db_repository.create(sample_item_data)


@pytest.fixture(scope="function")
def another_item(cosmos_db_repository: CosmosDBRepository, tenant_id: str) -> dict:
    sample_item_data = dict(id=fake.uuid4(),
                            name=fake.name(),
                            email=fake.safe_email(),
                            age=fake.pyint(min_value=10, max_value=80),
                            tenant_id=tenant_id)

    return cosmos_db_repository.create(sample_item_data)


@pytest.fixture(scope="module")
def time_entry_repository() -> TimeEntryCosmosDBRepository:
    return TimeEntryCosmosDBRepository()


@pytest.yield_fixture(scope="module")
def running_time_entry(time_entry_repository: TimeEntryCosmosDBRepository,
                       owner_id: str,
                       tenant_id: str):
    created_time_entry = time_entry_repository.create({
        "project_id": fake.uuid4(),
        "start_date": datetime_str(current_datetime()),
        "owner_id": owner_id,
        "tenant_id": tenant_id
    })

    yield created_time_entry

    time_entry_repository.delete(id=created_time_entry.id,
                                 partition_key_value=tenant_id)


@pytest.fixture(scope="session")
def valid_jwt(app: Flask) -> str:
    expiration_time = datetime.utcnow() + timedelta(seconds=3600)
    return jwt.encode({
        "iss": "https://securityioet.b2clogin.com/%s/v2.0/" % fake.uuid4(),
        "oid": fake.uuid4(),
        'exp': expiration_time
    }, key=get_or_generate_dev_secret_key()).decode("UTF-8")


@pytest.fixture(scope="session")
def valid_header(valid_jwt: str) -> dict:
    return {'Authorization': "Bearer %s" % valid_jwt}
