import msal
import os
import requests
from typing import List


class MSConfig:
    def check_variables_are_defined():
        auth_variables = [
            'MS_CLIENT_ID',
            'MS_AUTHORITY',
            'MS_SECRET',
            'MS_SCOPE',
            'MS_ENDPOINT',
        ]
        for var in auth_variables:
            if var not in os.environ:
                raise EnvironmentError(
                    "{} is not defined in the environment".format(var)
                )

    check_variables_are_defined()
    CLIENT_ID = os.environ.get('MS_CLIENT_ID')
    AUTHORITY = os.environ.get('MS_AUTHORITY')
    SECRET = os.environ.get('MS_SECRET')
    SCOPE = os.environ.get('MS_SCOPE')
    ENDPOINT = os.environ.get('MS_ENDPOINT')


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, access_token):
        self.access_token = access_token

    def __call__(self, r):
        r.headers["Authorization"] = f'Bearer {self.access_token}'
        return r


class AzureUser:
    def __init__(self, id, name, email, role):
        self.id = id
        self.name = name
        self.email = email
        self.role = role


class AzureConnection:
    def __init__(self, config=MSConfig):
        self.client = msal.ConfidentialClientApplication(
            config.CLIENT_ID,
            authority=config.AUTHORITY,
            client_credential=config.SECRET,
        )
        self.config = config
        self.access_token = self.get_token()

    def get_token(self):
        response = self.client.acquire_token_for_client(
            scopes=self.config.SCOPE
        )
        if "access_token" in response:
            return response['access_token']
        else:
            error_info = f"{response['error']} {response['error_description']}"
            raise ValueError(error_info)

    def users(self) -> List[AzureUser]:
        def to_azure_user(item) -> AzureUser:
            there_is_email = len(item['otherMails']) > 0
            there_is_role = (
                'extension_1d76efa96f604499acc0c0ee116a1453_role' in item
            )

            id = item['objectId']
            name = item['displayName']
            email = item['otherMails'][0] if there_is_email else ''
            role = (
                item['extension_1d76efa96f604499acc0c0ee116a1453_role']
                if there_is_role
                else None
            )
            return AzureUser(id, name, email, role)

        endpoint = "{endpoint}/users?api-version=1.6&$select=displayName,otherMails,objectId,{role_field}".format(
            endpoint=self.config.ENDPOINT,
            role_field='extension_1d76efa96f604499acc0c0ee116a1453_role',
        )
        response = requests.get(endpoint, auth=BearerAuth(self.access_token))

        assert 200 == response.status_code
        assert 'value' in response.json()
        return [to_azure_user(item) for item in response.json()['value']]
