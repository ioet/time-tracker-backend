import os

from time_tracker_api.security import generate_dev_secret_key

DISABLE_STR_VALUES = ("false", "0", "disabled")


class Config:
    SECRET_KEY = generate_dev_secret_key()
    SQL_DATABASE_URI = os.environ.get('SQL_DATABASE_URI')
    PROPAGATE_EXCEPTIONS = True
    RESTPLUS_VALIDATE = True
    DEBUG = True
    CORS_ORIGINS = "*"


class DevelopmentConfig(Config):
    DEBUG = True
    FLASK_DEBUG = True
    FLASK_ENV = "development"


class SQLConfig(Config):
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQL_DATABASE_URI = os.environ.get('SQL_DATABASE_URI')
    SQLALCHEMY_DATABASE_URI = SQL_DATABASE_URI


class CosmosDB(Config):
    COSMOS_DATABASE_URI = os.environ.get('COSMOS_DATABASE_URI')
    DATABASE_ACCOUNT_URI = os.environ.get('DATABASE_ACCOUNT_URI')
    DATABASE_MASTER_KEY = os.environ.get('DATABASE_MASTER_KEY')
    DATABASE_NAME = os.environ.get('DATABASE_NAME')


class TestConfig(CosmosDB, SQLConfig):
    TESTING = True
    FLASK_DEBUG = True
    TEST_TABLE = 'tests'
    SQL_DATABASE_URI = os.environ.get('SQL_DATABASE_URI')
    SQLALCHEMY_DATABASE_URI = SQL_DATABASE_URI or 'sqlite:///:memory:'


class ProductionConfig(Config):
    DEBUG = os.environ.get('DEBUG', "false").lower() not in DISABLE_STR_VALUES
    FLASK_DEBUG = True
    FLASK_ENV = 'production'


class AzureConfig(CosmosDB):
    SQL_DATABASE_URI = os.environ.get('SQL_DATABASE_URI', os.environ.get('SQLCONNSTR_DATABASE_URI'))
    COSMOS_DATABASE_URI = os.environ.get('COSMOS_DATABASE_URI', os.environ.get('CUSTOMCONNSTR_COSMOS_DATABASE_URI'))
    SQLALCHEMY_DATABASE_URI = SQL_DATABASE_URI


class AzureDevelopmentConfig(DevelopmentConfig, AzureConfig):
    pass


class AzureProductionConfig(ProductionConfig, AzureConfig):
    pass


DefaultConfig = AzureDevelopmentConfig
ProductionConfig = AzureProductionConfig


class CLIConfig(DefaultConfig):
    FLASK_DEBUG = False
