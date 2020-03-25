import os

from time_tracker_api.security import generate_dev_secret_key


class Config:
    SECRET_KEY = generate_dev_secret_key()
    DATABASE_URI = os.environ.get('DATABASE_URI')
    PROPAGATE_EXCEPTIONS = True
    RESTPLUS_VALIDATE = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEBUG = True
    FLASK_DEBUG = True
    FLASK_ENV = "development"


class SQLConfig(Config):
    SQLALCHEMY_DATABASE_URI = Config.DATABASE_URI
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestConfig(SQLConfig):
    TESTING = True
    FLASK_DEBUG = True
    TEST_TABLE = 'tests'
    DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:///:memory:')
    SQLALCHEMY_DATABASE_URI = DATABASE_URI


class ProductionConfig(Config):
    DEBUG = False
    FLASK_DEBUG = True
    FLASK_ENV = 'production'


class AzureConfig(SQLConfig):
    DATABASE_URI = os.environ.get('SQLAZURECONNSTR_DATABASE_URI')


class AzureDevelopmentConfig(DevelopmentConfig, AzureConfig):
    pass


class AzureProductionConfig(ProductionConfig, AzureConfig):
    pass


DefaultConfig = AzureDevelopmentConfig
ProductionConfig = AzureProductionConfig


class CLIConfig(DefaultConfig):
    FLASK_DEBUG = False
