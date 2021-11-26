from faker import Faker

from time_tracker.time_entries._domain import TimeEntryService


def test__create_time_entries__uses_the_time_entry_dao__to_create_an_time_entry(mocker, time_entry_factory):
    expected_time_entry = mocker.Mock()
    time_entry_dao = mocker.Mock(
        create=mocker.Mock(return_value=expected_time_entry)
    )
    time_entry_service = TimeEntryService(time_entry_dao)

    actual_time_entry = time_entry_service.create(time_entry_factory())

    assert time_entry_dao.create.called
    assert expected_time_entry == actual_time_entry


def test__delete_time_entry__uses_the_time_entry_dao__to_delete_time_entry_selected(
    mocker,
):
    expected_time_entry = mocker.Mock()
    time_entry_dao = mocker.Mock(
        delete=mocker.Mock(return_value=expected_time_entry)
    )

    time_entry_service = TimeEntryService(time_entry_dao)
    deleted_time_entry = time_entry_service.delete(Faker().pyint())

    assert time_entry_dao.delete.called
    assert expected_time_entry == deleted_time_entry


def test__update_time_entry__uses_the_time_entry_dao__to_update_one_time_entry(
    mocker,
):
    expected_time_entry = mocker.Mock()
    time_entry_dao = mocker.Mock(
        update=mocker.Mock(return_value=expected_time_entry)
    )
    time_entry_service = TimeEntryService(time_entry_dao)

    updated_time_entry = time_entry_service.update(
        Faker().pyint(), Faker().pydict()
    )

    assert time_entry_dao.update.called
    assert expected_time_entry == updated_time_entry


def test__get_all__uses_the_time_entry_dao__to_retrieve_time_entries(mocker):
    expected_time_entries = mocker.Mock()
    time_entry_dao = mocker.Mock(
        get_all=mocker.Mock(return_value=expected_time_entries)
    )
    time_activity_service = TimeEntryService(time_entry_dao)

    actual_activities = time_activity_service.get_all()

    assert time_entry_dao.get_all.called
    assert expected_time_entries == actual_activities


def test__get_by_id__uses_the_time_entry_dao__to_retrieve_one_time_entry(mocker):
    expected_time_entry = mocker.Mock()
    time_entry_dao = mocker.Mock(
        get_by_id=mocker.Mock(return_value=expected_time_entry)
    )
    time_entry_service = TimeEntryService(time_entry_dao)

    actual_time_entry = time_entry_service.get_by_id(Faker().uuid4())

    assert time_entry_dao.get_by_id.called
    assert expected_time_entry == actual_time_entry
