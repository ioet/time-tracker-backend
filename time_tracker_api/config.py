import os


class Config:
    DEBUG = False


class DevelopConfig(Config):
    DEBUG = True
    FLASK_DEBUG = True
    FLASK_ENV = "develop"
    DATABASE_URI = os.environ.get('DATABASE_URI')


class AzureSQLDatabaseDevelopConfig(DevelopConfig):
    DATABASE = 'sql'
    TEST_TABLE = 'tests'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class AzureSQLDatabaseDevelopTestConfig(AzureSQLDatabaseDevelopConfig):
    DEBUG = True
    TESTING = True


DefaultConfig = AzureSQLDatabaseDevelopConfig
