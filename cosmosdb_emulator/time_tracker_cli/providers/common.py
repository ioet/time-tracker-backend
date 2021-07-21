from faker.providers import BaseProvider


class CommonProvider(BaseProvider):
    def status(self) -> str:
        available_status = ['active', 'inactive']
        return self.random_element(elements=available_status)
