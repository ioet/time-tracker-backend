from faker import Faker
from flask import Flask

fake = Faker()


def test_create_entry(repository, app: Flask):
    """Should create a new Entry"""
    assert repository is not None
    from .resources import TestModel
    sample_model = TestModel(name=fake.name(),
                             email=fake.safe_email(),
                             age = fake.pyint(min_value=10, max_value=80))

    repository.create(sample_model)
