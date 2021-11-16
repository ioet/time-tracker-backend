import sqlalchemy

from . import _config

_TEST_DIALECT = "sqlite"

class DB():
    config = _config.load_config()
    connection = None
    engine = None
    conn_string = config.DB_CONNECTION_STRING
    metadata = sqlalchemy.MetaData()

    def __init__(self, conn_string: str = conn_string):
        self.engine = sqlalchemy.create_engine(conn_string)

    def get_session(self):
        self.metadata.create_all(self.engine)
        if self.connection is None:
            self.connection = self.engine.connect()
            if self.engine.dialect.name == _TEST_DIALECT:
                self.connection.execute("pragma foreign_keys=ON")
        return self.connection
