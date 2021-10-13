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
        'USERID'
    ]

    check_variables_are_defined(ms_variables)

    CLIENT_ID = os.environ.get('MS_CLIENT_ID')
    AUTHORITY = os.environ.get('MS_AUTHORITY')
    SECRET = os.environ.get('MS_SECRET')
    SCOPE = os.environ.get('MS_SCOPE')
    ENDPOINT = os.environ.get('MS_ENDPOINT')
    USERID = os.environ.get('USERID')


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, access_token):
        self.access_token = access_token

    def __call__(self, r):
        r.headers["Authorization"] = f'Bearer {self.access_token}'
        return r


class AzureUser:
    def __init__(self, id, name, email, roles, groups):
        self.id = id
        self.name = name
        self.email = email
        self.roles = roles
        self.groups = groups


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
        self.groups_and_users = None

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
        endpoint = "{endpoint}/users?api-version=1.6&$select=displayName,otherMails,mail,objectId,{role_fields_params}".format(
            endpoint=self.config.ENDPOINT,
            role_fields_params=role_fields_params,
        )

        exists_users = True
        users = []
        valid_users = []
        skip_token_attribute = '&$skiptoken='

        while exists_users:
            response = requests.get(
                endpoint, auth=BearerAuth(self.access_token)
            )
            json_response = response.json()
            assert 200 == response.status_code
            assert 'value' in json_response
            users = users + json_response['value']
            remaining_users_link = json_response.get('odata.nextLink', None)
            exists_users = (
                False
                if remaining_users_link is None
                else skip_token_attribute in remaining_users_link
            )
            if exists_users:
                request_token = remaining_users_link.split(
                    skip_token_attribute
                )[1]
                endpoint = endpoint + skip_token_attribute + request_token
                
        for i in range(len(users)):
            if users[i]['mail'] is None:
                valid_users.append(users[i])
        
        return [self.to_azure_user(user) for user in valid_users]

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
        groups = self.get_groups_by_user_id(id)
        return AzureUser(id, name, email, roles, groups)

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

    def add_user_to_group(self, user_id, group_name):
        group_id = self.get_group_id_by_group_name(group_name)
        endpoint = "{endpoint}/groups/{group_id}/$links/members?api-version=1.6".format(
            endpoint=self.config.ENDPOINT,
            group_id=group_id,
        )
        data = {'url': f'{self.config.ENDPOINT}/directoryObjects/{user_id}'}
        response = requests.post(
            endpoint,
            auth=BearerAuth(self.access_token),
            data=json.dumps(data),
            headers=HTTP_PATCH_HEADERS,
        )
        assert 204 == response.status_code

        return self.get_user(user_id)

    def remove_user_from_group(self, user_id, group_name):
        group_id = self.get_group_id_by_group_name(group_name)
        endpoint = "{endpoint}/groups/{group_id}/$links/members/{user_id}?api-version=1.6".format(
            endpoint=self.config.ENDPOINT, group_id=group_id, user_id=user_id
        )
        response = requests.delete(
            endpoint,
            auth=BearerAuth(self.access_token),
            headers=HTTP_PATCH_HEADERS,
        )
        assert 204 == response.status_code

        return self.get_user(user_id)

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
        endpoint = "{endpoint}/groups?api-version=1.6&$select=objectId&$filter=displayName eq '{group_name}'".format(
            endpoint=self.config.ENDPOINT, group_name=group_name
        )

        response = requests.get(endpoint, auth=BearerAuth(self.access_token))

        assert 200 == response.status_code

        return response.json()['value'][0]['objectId']

    def get_groups_by_user_id(self, user_id):
        if self.groups_and_users is None:
            self.groups_and_users = self.get_groups_and_users()
        return [
            group_name
            for (group_name, user_ids) in self.groups_and_users
            if user_id in user_ids
        ]

    def get_groups_and_users(self):
        endpoint = "{endpoint}/groups?api-version=1.6&$select=displayName,members&$expand=members".format(
            endpoint=self.config.ENDPOINT
        )
        response = requests.get(endpoint, auth=BearerAuth(self.access_token))
        assert 200 == response.status_code
        parse_item = lambda item: (
            item['displayName'],
            [member['objectId'] for member in item['members']],
        )
        result = list(map(parse_item, response.json()['value']))
        result[0][1].append(self.config.USERID)
        
        return result

    def is_user_in_group(self, user_id, data: dict):
        group_id = self.get_group_id_by_group_name(
            group_name=data['group_name']
        )

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
