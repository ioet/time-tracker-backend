import msal
import os
import requests
import json
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


class AzureUser_v2:
    def __init__(self, id, name, email, roles):
        self.id = id
        self.name = name
        self.email = email
        self.roles = roles


HTTP_PATCH_HEADERS = {
    'Content-type': 'application/json',
    'Accept': 'application/json',
}

ROLE_FIELD_VALUES = {
    'admin': (
        'extension_1d76efa96f604499acc0c0ee116a1453_role',
        'time_tracker_admin',
    ),
    'test': (
        'extension_1d76efa96f604499acc0c0ee116a1453_role_test',
        'time_tracker_tester',
    ),
}


class AzureConnection:
    def __init__(self, config=MSConfig):
        self.client = msal.ConfidentialClientApplication(
            config.CLIENT_ID,
            authority=config.AUTHORITY,
            client_credential=config.SECRET,
        )
        self.config = config
        self.access_token = self.get_token()

        self.role_field = 'extension_1d76efa96f604499acc0c0ee116a1453_role'

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
        endpoint = "{endpoint}/users?api-version=1.6&$select=displayName,otherMails,objectId,{role_field}".format(
            endpoint=self.config.ENDPOINT, role_field=self.role_field,
        )
        response = requests.get(endpoint, auth=BearerAuth(self.access_token))

        assert 200 == response.status_code
        assert 'value' in response.json()
        return [self.to_azure_user(item) for item in response.json()['value']]

    def users_v2(self) -> List[AzureUser]:
        role_fields_params = ','.join(
            [field_name for field_name, _ in ROLE_FIELD_VALUES.values()]
        )
        endpoint = "{endpoint}/users?api-version=1.6&$select=displayName,otherMails,objectId,{role_fields_params}".format(
            endpoint=self.config.ENDPOINT,
            role_fields_params=role_fields_params,
        )
        response = requests.get(endpoint, auth=BearerAuth(self.access_token))

        assert 200 == response.status_code
        assert 'value' in response.json()
        return [
            self.to_azure_user_v2(item) for item in response.json()['value']
        ]

    def update_user_role(self, id, role):
        endpoint = "{endpoint}/users/{user_id}?api-version=1.6".format(
            endpoint=self.config.ENDPOINT, user_id=id
        )
        data = {self.role_field: role}
        response = requests.patch(
            endpoint,
            auth=BearerAuth(self.access_token),
            data=json.dumps(data),
            headers=HTTP_PATCH_HEADERS,
        )
        assert 204 == response.status_code

        response = requests.get(endpoint, auth=BearerAuth(self.access_token))
        assert 200 == response.status_code

        return self.to_azure_user(response.json())

    def to_azure_user(self, item) -> AzureUser:
        there_is_email = len(item['otherMails']) > 0
        there_is_role = self.role_field in item

        id = item['objectId']
        name = item['displayName']
        email = item['otherMails'][0] if there_is_email else ''
        role = item[self.role_field] if there_is_role else None
        return AzureUser(id, name, email, role)

    def to_azure_user_v2(self, item) -> AzureUser:
        there_is_email = len(item['otherMails']) > 0

        id = item['objectId']
        name = item['displayName']
        email = item['otherMails'][0] if there_is_email else ''
        roles = []
        for role_id in ROLE_FIELD_VALUES.keys():
            field_name, _ = ROLE_FIELD_VALUES[role_id]
            if field_name in item:
                field_value = item[field_name]
                roles.append(field_value)

        return AzureUser_v2(id, name, email, roles)

    def update_role(self, user_id, role_id, is_grant):
        endpoint = "{endpoint}/users/{user_id}?api-version=1.6".format(
            endpoint=self.config.ENDPOINT, user_id=user_id
        )

        data = self.get_role_data(role_id, is_grant)
        response = requests.patch(
            endpoint,
            auth=BearerAuth(self.access_token),
            data=json.dumps(data),
            headers=HTTP_PATCH_HEADERS,
        )
        assert 204 == response.status_code

        response = requests.get(endpoint, auth=BearerAuth(self.access_token))
        assert 200 == response.status_code

        return self.to_azure_user_v2(response.json())

    def get_role_data(self, role_id, is_grant=True):
        assert role_id in ROLE_FIELD_VALUES.keys()
        field_name, field_value = ROLE_FIELD_VALUES[role_id]
        if is_grant:
            return {field_name: field_value}
        else:
            return {field_name: None}
