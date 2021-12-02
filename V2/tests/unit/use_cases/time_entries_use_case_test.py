from pytest_mock import MockFixture
from faker import Faker

from time_tracker.time_entries._domain import _use_cases

fake = Faker()


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


def test__delete_time_entry_function__uses_the_time_entry_service__to_delete_time_entry_selected(
    mocker: MockFixture,
):
    expected_time_entry = mocker.Mock()
    time_entry_service = mocker.Mock(delete=mocker.Mock(return_value=expected_time_entry))

    time_entry_use_case = _use_cases.DeleteTimeEntryUseCase(time_entry_service)
    deleted_time_entry = time_entry_use_case.delete_time_entry(Faker().pyint())

    assert time_entry_service.delete.called
    assert expected_time_entry == deleted_time_entry


def test__update_time_entries_function__uses_the_time_entry_service__to_update_an_time_entry(
    mocker: MockFixture,
):
    expected_time_entry = mocker.Mock()
    time_entry_service = mocker.Mock(update=mocker.Mock(return_value=expected_time_entry))

    time_entry_use_case = _use_cases.UpdateTimeEntryUseCase(time_entry_service)
    updated_time_entry = time_entry_use_case.update_time_entry(Faker().uuid4(), Faker().pydict())

    assert time_entry_service.update.called
    assert expected_time_entry == updated_time_entry


def test__get_all_time_entries_function__using_the_use_case_get_time_entries__to_get_all_time_entries(
    mocker: MockFixture,
):
    expected_time_entries = mocker.Mock()
    time_entry_service = mocker.Mock(
        get_all=mocker.Mock(return_value=expected_time_entries)
    )

    time_entries_use_case = _use_cases.GetTimeEntriesUseCase(time_entry_service)
    actual_time_entries = time_entries_use_case.get_time_entries()

    assert time_entry_service.get_all.called
    assert expected_time_entries == actual_time_entries


def test__get_time_entry_by_id_function__uses_the_time_entry_service__to_retrieve_time_entry(
    mocker: MockFixture,
):
    expected_time_entries = mocker.Mock()
    time_entry_service = mocker.Mock(
        get_by_id=mocker.Mock(return_value=expected_time_entries)
    )

    time_entry_use_case = _use_cases.GetTimeEntryUseCase(time_entry_service)
    actual_time_entry = time_entry_use_case.get_time_entry_by_id(fake.uuid4())

    assert time_entry_service.get_by_id.called
    assert expected_time_entries == actual_time_entry


def test__get_latest_entries_function__uses_the_time_entry_service__to_get_last_entries(
    mocker: MockFixture,
):
    expected_latest_time_entries = mocker.Mock()
    time_entry_service = mocker.Mock(get_latest_entries=mocker.Mock(return_value=expected_latest_time_entries))

    time_entry_use_case = _use_cases.GetLastestTimeEntryUseCase(time_entry_service)
    latest_time_entries = time_entry_use_case.get_latest_entries(Faker().pyint(), Faker().pyint())

    assert time_entry_service.get_latest_entries.called
    assert expected_latest_time_entries == latest_time_entries


def test__get_time_entries_summary_function__uses_the_time_entry_service__to_get_summary(
    mocker: MockFixture,
):
    expected_time_entries_summary = mocker.Mock()
    time_entry_service = mocker.Mock(get_time_entries_summary=mocker.Mock(return_value=expected_time_entries_summary))

    time_entry_use_case = _use_cases.GetTimeEntriesSummaryUseCase(time_entry_service)
    summary = time_entry_use_case.get_time_entries_summary(Faker().pyint(), Faker().date(), Faker().date())

    assert time_entry_service.get_time_entries_summary.called
    assert expected_time_entries_summary == summary
