import os

from time_tracker_api.security import generate_dev_secret_key


class Config:
    SECRET_KEY = generate_dev_secret_key()
    DATABASE_URI = os.environ.get('DATABASE_URI')
    PROPAGATE_EXCEPTIONS = True
    RESTPLUS_VALIDATE = True


class DevelopConfig(Config):
    DEBUG = True
    FLASK_DEBUG = True
    FLASK_ENV = "develop"


class TestConfig(Config):
    TESTING = True
    FLASK_DEBUG = True
    TEST_TABLE = 'tests'


class SQLConfig(Config):
    SQLALCHEMY_DATABASE_URI = Config.DATABASE_URI
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class AzureConfig(SQLConfig):
    pass


class AzureSQLDatabaseDevelopConfig(DevelopConfig, AzureConfig):
    pass


class AzureSQLDatabaseDevelopTestConfig(TestConfig, AzureSQLDatabaseDevelopConfig):
    pass


DefaultConfig = AzureSQLDatabaseDevelopConfig


class CLIConfig(DefaultConfig):
    FLASK_DEBUG = False
