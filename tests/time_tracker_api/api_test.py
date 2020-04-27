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


def test_remove_required_constraint():
    from time_tracker_api.api import remove_required_constraint
    from flask_restplus import fields
    from flask_restplus import Namespace

    ns = Namespace('todos', description='Namespace for testing')
    sample_model = ns.model('Todo', {
        'id': fields.Integer(readonly=True, description='The task unique identifier'),
        'task': fields.String(required=True, description='The task details'),
        'done': fields.Boolean(required=False, description='Has it being done or not')
    })

    new_model = remove_required_constraint(sample_model)

    assert new_model is not sample_model

    for attrib in sample_model:
        assert new_model[attrib].required is False, "No attribute should be required"
        assert new_model[attrib] is not sample_model[attrib], "No attribute should be required"
