#!/usr/bin/env python3

print("****************")
print("TimeTracker CLI")
print("****************")

import os

from flask import json
from flask_script import Manager

from time_tracker_api import create_app
from time_tracker_api.api import api

app = create_app()
cli_manager = Manager(app)


@cli_manager.command
@cli_manager.option('-f', '--filename',
                    dest='filename',
                    help='Path of the swagger file. By default swagger.json')
def gen_swagger_json(filename='swagger.json'):
    """ Exports swagger specifications in json format """
    schema_json_data = json.dumps(api.__schema__)
    save_data(schema_json_data, filename)


@cli_manager.command
@cli_manager.option('-f', '--filename',
                    dest='filename',
                    help='Path of the postman collection file.'
                         'By default it is timetracker-api-postman-collection.json')
@cli_manager.option('-b', '--base-url-placeholder',
                    dest='base_url_placeholder',
                    help='Text used as placeholder. E.g. {{timetracker_api_host}}.'
                         'By default the base url will be http://localhost')
def gen_postman_collection(filename='timetracker-api-postman-collection.json',
                           base_url_placeholder=None):
    """ Generates a Postman collection for the API """
    data = api.as_postman(urlvars=False, swagger=True)
    postman_collection_json_data = json.dumps(data)
    if base_url_placeholder is not None:
        parsed_json = postman_collection_json_data.replace("http://localhost", base_url_placeholder)
    else:
        parsed_json = postman_collection_json_data

    save_data(parsed_json, filename)


def save_data(data: str, filename: str) -> None:
    """ Save text content to a file """
    if filename:
        try:
            real_path = os.path.expanduser(filename)
            with open(real_path, "w") as f:
                f.write(data)
                print("%s was generated successfully" % real_path)
        except OSError as err:
            print("Error while generating '%s': %s" % filename, err)
    else:
        print(data)


if __name__ == "__main__":
    cli_manager.run()
