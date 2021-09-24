import abc


class ActivitiesDaoInterface(abc.ABC):
    @abc.abstractmethod
    def get_by_id(self, id):
        pass

    @abc.abstractmethod
    def get_all(self):
        pass
