"""
Agnostic database assets

Put here your utils and class independent of
the database solution.
To know more about protocols and subtyping check out PEP-0544
"""
import abc

from flask import Flask

from commons.data_access_layer.cosmos_db import CosmosDBDao
from commons.data_access_layer.database import EventContext
from time_tracker_api.security import current_user_id, current_user_tenant_id


class CRUDDao(abc.ABC):
    @abc.abstractmethod
    def get_all(self, conditions: dict):
        raise NotImplementedError  # pragma: no cover

    @abc.abstractmethod
    def get(self, id):
        raise NotImplementedError  # pragma: no cover

    @abc.abstractmethod
    def create(self, project):
        raise NotImplementedError  # pragma: no cover

    @abc.abstractmethod
    def update(self, id, data, description=None):
        raise NotImplementedError  # pragma: no cover

    @abc.abstractmethod
    def delete(self, id):
        raise NotImplementedError  # pragma: no cover


class ApiEventContext(EventContext):
    def __init__(self, container_id: str, action: str, description: str = None,
                 user_id: str = None, tenant_id: str = None, session_id: str = None):
        super(ApiEventContext, self).__init__(container_id, action, description)
        self._user_id = user_id
        self._tenant_id = tenant_id
        self._session_id = session_id

    @property
    def user_id(self) -> str:
        if self._user_id is None:
            self._user_id = current_user_id()
        return self._user_id

    @property
    def tenant_id(self) -> str:
        if self._tenant_id is None:
            self._tenant_id = current_user_tenant_id()
        return self._tenant_id

    @property
    def session_id(self) -> str:
        return self._session_id


class APICosmosDBDao(CosmosDBDao):
    def create_event_context(self, action: str = None, description: str = None):
        return ApiEventContext(self.repository.container.id, action,
                               description=description)


def init_app(app: Flask) -> None:
    init_cosmos_db(app)


def init_sql(app: Flask) -> None:
    from commons.data_access_layer.sql import init_app
    init_app(app)


def init_cosmos_db(app: Flask) -> None:
    from commons.data_access_layer.cosmos_db import init_app
    init_app(app)
