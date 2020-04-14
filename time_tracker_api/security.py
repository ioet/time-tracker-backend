"""
This is where we handle everything regarding to authorization
and authentication. Also stores helper functions related to it.
"""
from faker import Faker

fake = Faker()

dev_secret_key: str = None


def current_user_id() -> str:
    """
    Returns the id of the authenticated user in
    Azure Active Directory
    """
    return 'anonymous'


def current_user_tenant_id() -> str:
    # TODO Get this from the JWT
    return "ioet"


def generate_dev_secret_key():
    from time_tracker_api import flask_app as app
    """
    Generates a security key for development purposes
    :return: str
    """
    global dev_secret_key
    dev_secret_key = fake.password(length=16, special_chars=True, digits=True, upper_case=True, lower_case=True)
    if app.config.get("FLASK_DEBUG", False):
        print('*********************************************************')
        print("The generated secret is \"%s\"" % dev_secret_key)
        print('*********************************************************')
    return dev_secret_key

