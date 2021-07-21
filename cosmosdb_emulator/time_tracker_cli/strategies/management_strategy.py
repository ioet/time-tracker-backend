from abc import abstractmethod, ABC


class ManagementStrategy(ABC):
    @abstractmethod
    def get_confirmation_to_delete_data(self) -> bool:
        """
        Ask the user if he/she agrees to delete the information
        :return: True if user agrees to remove the information else False
        """
        pass

    @abstractmethod
    def get_answers_needed_to_create_data(self) -> dict:
        """
        Ask the user all information needed to create a specific entity.
        :return: a dict with all information needed to generate the entities
        """
        pass

    @abstractmethod
    def generate_entities(self, entity_information: dict) -> dict:
        """
        Create all the entities related with a specific strategy.
        """
        pass

    @abstractmethod
    def get_conflict_entities(self) -> set:
        """
        Returns all the entities that generate conflict with a specific entity
        at the moment of generating the information
        """
        pass
