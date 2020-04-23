"""
This is where we handle everything regarding to authorization
and authentication. Also stores helper functions related to it.
"""
import re

import jwt
from faker import Faker
from flask import request
from flask_restplus import abort
from flask_restplus._http import HTTPStatus
from jwt import DecodeError, ExpiredSignatureError

fake = Faker()

dev_secret_key: str = None

authorizations = {
    "TimeTracker JWT": {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': "Specify in the value **'Bearer &lt;JWT&gt;'**, where JWT is the token",
    }
}

iss_claim_pattern = re.compile(
    r"(.*).b2clogin.com/(?P<tenant_id>[0-9a-f]{8}\-[0-9a-f]{4}\-4[0-9a-f]{3}\-[89ab][0-9a-f]{3}\-[0-9a-f]{12})")


def current_user_id() -> str:
    oid_claim = get_token_json().get("oid")
    if oid_claim is None:
        abort(message='The claim "oid" is missing in the JWT', code=HTTPStatus.UNAUTHORIZED)

    return oid_claim


def current_user_tenant_id() -> str:
    iss_claim = get_token_json().get("iss")
    if iss_claim is None:
        abort(message='The claim "iss" is missing in the JWT', code=HTTPStatus.UNAUTHORIZED)

    tenant_id = parse_tenant_id_from_iss_claim(iss_claim)
    if tenant_id is None:
        abort(message='The format of the claim "iss" cannot be understood. '
                      'Please contact the development team.',
              code=HTTPStatus.UNAUTHORIZED)

    return tenant_id


def get_or_generate_dev_secret_key():
    global dev_secret_key
    if dev_secret_key is None:
        from time_tracker_api import flask_app as app
        """
        Generates a security key for development purposes
        :return: str
        """
        dev_secret_key = fake.password(length=16, special_chars=True, digits=True, upper_case=True, lower_case=True)
        if app.config.get("FLASK_DEBUG", False):  # pragma: no cover
            print('*********************************************************')
            print("The generated secret is \"%s\"" % dev_secret_key)
            print('*********************************************************')
    return dev_secret_key


def parse_jwt(authentication_header_content):
    if authentication_header_content is not None:
        parsed_content = authentication_header_content.split("Bearer ")

        if len(parsed_content) > 1:
            return jwt.decode(parsed_content[1], verify=False)

    return None


def get_authorization_jwt():
    auth_header = request.headers.get('Authorization')
    return parse_jwt(auth_header)


def get_token_json():
    try:
        return get_authorization_jwt()
    except DecodeError:
        abort(message='Malformed token', code=HTTPStatus.UNAUTHORIZED)
    except ExpiredSignatureError:
        abort(message='Expired token', code=HTTPStatus.UNAUTHORIZED)


def parse_tenant_id_from_iss_claim(iss_claim: str) -> str:
    m = iss_claim_pattern.search(iss_claim)
    if m is not None:
        return m.group('tenant_id')

    return None
