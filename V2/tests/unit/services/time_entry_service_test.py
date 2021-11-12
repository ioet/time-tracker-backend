from faker import Faker

from time_tracker.time_entries._domain import TimeEntryService


def test__create_time_entries__uses_the_time_entry_dao__to_create_an_time_entry(mocker):
    expected_time_entry = mocker.Mock()
    time_entry_dao = mocker.Mock(
        create=mocker.Mock(return_value=expected_time_entry)
    )
    time_entry_service = TimeEntryService(time_entry_dao)

    actual_time_entry = time_entry_service.create(Faker().pydict())

    assert time_entry_dao.create.called
    assert expected_time_entry == actual_time_entry
