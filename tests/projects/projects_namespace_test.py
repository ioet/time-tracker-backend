from flask import json


def test_list_should_return_nothing(client):
    """Should return an empty array"""
    response = client.get("/projects", follow_redirects=True)

    assert 200 == response.status_code

    json_data = json.loads(response.data)
    assert [] == json_data