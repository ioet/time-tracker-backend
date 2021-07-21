from cosmosdb_emulator.time_tracker_cli.data_target.data_target import (
    DataTarget,
)
from cosmosdb_emulator.time_tracker_cli.strategies.management_strategy import (
    ManagementStrategy,
)


class ManagementContext:
    def __init__(
        self, strategy: ManagementStrategy, data_target: DataTarget
    ) -> None:
        self._strategy = strategy
        self._data_target = data_target

    @property
    def strategy(self) -> ManagementStrategy:
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: ManagementStrategy) -> None:
        self._strategy = strategy

    def create_data(self):
        user_answers = self._strategy.get_answers_needed_to_create_data()
        entities = self._strategy.generate_entities(user_answers)
        conflict_entities = self._strategy.get_conflict_entities()
        print(
            'We are trying to create all the requested information, so please wait and be patient!'
        )
        print('Creating the data...')
        self._data_target.delete(conflict_entities)
        self._data_target.save(entities)
        print('Great Job! The needed data was created!')

    def delete_data(self):
        is_user_agree_to_delete_data = (
            self._strategy.get_confirmation_to_delete_data()
        )
        if is_user_agree_to_delete_data:
            conflict_entities = self._strategy.get_conflict_entities()
            print(
                'We are trying to delete all the requested information, hope you do not regret it later'
            )
            self._data_target.delete(conflict_entities)
            print('The requested entity and related entities were eliminated.')
