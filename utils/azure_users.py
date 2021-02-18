import msal
import os
import requests
import json
from typing import List
from utils.environment_variables import check_variables_are_defined


class MSConfig:
    ms_variables = [
        'MS_CLIENT_ID',
        'MS_AUTHORITY',
        'MS_SECRET',
        'MS_SCOPE',
        'MS_ENDPOINT',
    ]

    check_variables_are_defined(ms_variables)

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
        'time-tracker-admin',
    ),
    'test': (
        'extension_1d76efa96f604499acc0c0ee116a1453_role_test',
        'time-tracker-tester',
    ),
}


class AzureConnection:
    def __init__(self, config=MSConfig):
        self.config = config
        self.client = self.get_msal_client()
        self.access_token = self.get_token()

    def get_msal_client(self):
        client = msal.ConfidentialClientApplication(
            self.config.CLIENT_ID,
            authority=self.config.AUTHORITY,
            client_credential=self.config.SECRET,
        )
        return client

    def get_token(self):
        response = self.client.acquire_token_for_client(
            scopes=self.config.SCOPE
        )
        if "access_token" in response:
            return response['access_token']
        else:
            error_info = f"{response['error']} {response['error_description']}"
            raise ValueError(error_info)

    def get_user(self, user_id) -> AzureUser:
        endpoint = "{endpoint}/users/{user_id}?api-version=1.6".format(
            endpoint=self.config.ENDPOINT, user_id=user_id
        )
        response = requests.get(endpoint, auth=BearerAuth(self.access_token))
        assert 200 == response.status_code
        return self.to_azure_user(response.json())

    def users(self) -> List[AzureUser]:
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
        return [self.to_azure_user(item) for item in response.json()['value']]

    def to_azure_user(self, item) -> AzureUser:
        there_is_email = len(item['otherMails']) > 0

        id = item['objectId']
        name = item['displayName']
        email = item['otherMails'][0] if there_is_email else ''
        roles = [
            item[field_name]
            for (field_name, field_value) in ROLE_FIELD_VALUES.values()
            if field_name in item
        ]
        return AzureUser(id, name, email, roles)

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

        return self.to_azure_user(response.json())

    def get_non_test_users(self) -> List[AzureUser]:
        test_user_ids = self.get_test_user_ids()
        return [user for user in self.users() if user.id not in test_user_ids]

    def get_role_data(self, role_id, is_grant=True):
        assert role_id in ROLE_FIELD_VALUES.keys()
        field_name, field_value = ROLE_FIELD_VALUES[role_id]
        if is_grant:
            return {field_name: field_value}
        else:
            return {field_name: None}

    def is_test_user(self, user_id):
        endpoint = "{endpoint}/users/{user_id}?api-version=1.6".format(
            endpoint=self.config.ENDPOINT, user_id=user_id
        )
        response = requests.get(endpoint, auth=BearerAuth(self.access_token))
        assert 200 == response.status_code
        item = response.json()
        field_name, field_value = ROLE_FIELD_VALUES['test']
        return field_name in item and field_value == item[field_name]

    def get_test_user_ids(self):
        field_name, field_value = ROLE_FIELD_VALUES['test']
        endpoint = "{endpoint}/users?api-version=1.6&$select=objectId,{field_name}&$filter={field_name} eq '{field_value}'".format(
            endpoint=self.config.ENDPOINT,
            field_name=field_name,
            field_value=field_value,
        )
        response = requests.get(endpoint, auth=BearerAuth(self.access_token))
        assert 200 == response.status_code
        assert 'value' in response.json()
        return [item['objectId'] for item in response.json()['value']]

    def get_group_id_by_group_name(self, group_name):
        endpoint_get_groups = "{endpoint}/groups?api-version=1.6&$select=objectId&$filter=displayName eq '{group_name}'".format(
            endpoint=self.config.ENDPOINT, group_name=group_name
        )

        response_get_groups = requests.get(
            endpoint_get_groups, auth=BearerAuth(self.access_token)
        )

        assert 200 == response_get_groups.status_code

        return response_get_groups.json()['value'][0]['objectId']

    def is_user_in_group(self, user_id, group_name):
        group_id = self.get_group_id_by_group_name(group_name=group_name)

        endpoint = "{endpoint}/isMemberOf?api-version=1.6".format(
            endpoint=self.config.ENDPOINT
        )

        data = {"groupId": group_id, "memberId": user_id}

        response = requests.post(
            endpoint,
            auth=BearerAuth(self.access_token),
            data=json.dumps(data),
            headers=HTTP_PATCH_HEADERS,
        )

        assert 200 == response.status_code

        item = response.json()['value']
        return {'value': item}
