from pytest_mock import MockFixture
from faker import Faker

from time_tracker.time_entries._domain import _use_cases


def test__create_time_entry_function__uses_the_time_entries_service__to_create_time_entry(
    mocker: MockFixture, time_entry_factory
):
    expected_time_entry = mocker.Mock()
    time_entry_service = mocker.Mock(
        create=mocker.Mock(return_value=expected_time_entry)
    )

    time_entry_use_case = _use_cases.CreateTimeEntryUseCase(time_entry_service)
    actual_time_entry = time_entry_use_case.create_time_entry(time_entry_factory())

    assert time_entry_service.create.called
    assert expected_time_entry == actual_time_entry


def test__delete_time_entry_function__uses_the_time_entry_service__to_change_time_entry_deleted(
    mocker: MockFixture,
):
    expected_time_entry = mocker.Mock()
    time_entry_service = mocker.Mock(delete=mocker.Mock(return_value=expected_time_entry))

    time_entry_use_case = _use_cases.DeleteTimeEntryUseCase(time_entry_service)
    deleted_time_entry = time_entry_use_case.delete_time_entry(Faker().pyint())

    assert time_entry_service.delete.called
    assert expected_time_entry == deleted_time_entry