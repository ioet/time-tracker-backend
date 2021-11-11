import sqlalchemy

from . import _config


class DB():
    config = _config.load_config()
    connection = None
    engine = None
    conn_string = config.DB_CONNECTION_STRING
    metadata = sqlalchemy.MetaData()

    def __init__(self, conn_string: str = conn_string):
        self.engine = sqlalchemy.create_engine(conn_string)

    def get_session(self):
        if self.connection is None:
            self.metadata.create_all(self.engine)
            self.connection = self.engine.connect()
        return self.connection
