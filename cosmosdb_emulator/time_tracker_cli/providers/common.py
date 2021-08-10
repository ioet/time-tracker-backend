from faker.providers import BaseProvider

from utils.enums.status import Status


class CommonProvider(BaseProvider):
    def status(self) -> str:
        available_status = [Status.ACTIVE.value, Status.INACTIVE.value]
        return self.random_element(elements=available_status)
