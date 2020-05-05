"""
Agnostic database assets

Put here your utils and class independent of
the database solution.
To know more about protocols and subtyping check out PEP-0544
"""
import abc

COMMENTS_MAX_LENGTH = 500
ID_MAX_LENGTH = 64


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
    def update(self, id, data):
        raise NotImplementedError  # pragma: no cover

    @abc.abstractmethod
    def delete(self, id):
        raise NotImplementedError  # pragma: no cover


class EventContext():
    def __init__(self, container_id: str, action: str, description: str = None,
                 user_id: str = None, tenant_id: str = None, session_id: str = None,
                 app_id: str = None):
        self._container_id = container_id
        self._action = action
        self._description = description
        self._user_id = user_id
        self._tenant_id = tenant_id
        self._session_id = session_id
        self._app_id = app_id

    @property
    def container_id(self):
        return self._container_id

    @property
    def action(self):
        return self._action

    @property
    def description(self):
        return self._description

    @property
    def user_id(self):
        return self._user_id

    @property
    def tenant_id(self):
        return self._tenant_id

    @property
    def session_id(self):
        return self._session_id

    @property
    def app_id(self):
        return self._app_id
