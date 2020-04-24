from flask_restplus.reqparse import RequestParser
from pytest import fail


def test_create_attributes_filter_with_invalid_attribute_should_fail():
    from time_tracker_api.api import create_attributes_filter
    from time_tracker_api.projects.projects_namespace import project, ns

    try:
        create_attributes_filter(ns, project, ['invalid_attribute'])

        fail("It was expected to fail")
    except Exception as e:
        assert type(e) is ValueError


def test_create_attributes_filter_with_valid_attribute_should_succeed():
    from time_tracker_api.api import create_attributes_filter
    from time_tracker_api.projects.projects_namespace import project, ns

    filter = create_attributes_filter(ns, project, ['name'])

    assert filter is not None
    assert type(filter) is RequestParser
