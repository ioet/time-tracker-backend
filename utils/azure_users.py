import msal
import os
import requests


class MSALConfig:
    MSAL_CLIENT_ID = os.environ.get('MSAL_CLIENT_ID')
    MSAL_AUTHORITY = os.environ.get('MSAL_AUTHORITY')
    MSAL_SECRET = os.environ.get('MSAL_SECRET')
    MSAL_SCOPE = os.environ.get('MSAL_SCOPE')
    MSAL_ENDPOINT = os.environ.get('MSAL_ENDPOINT')
    """
    TODO : Add validation to ensure variables are set
    """


class AzureUsers:
    def __init__(self, config=MSALConfig):
        self.client = msal.ConfidentialClientApplication(
            config.MSAL_CLIENT_ID,
            authority=config.MSAL_AUTHORITY,
            client_credential=config.MSAL_SECRET,
        )
        self.config = config
        self.set_token()

    def set_token(self):
        response = self.client.acquire_token_for_client(
            scopes=self.config.MSAL_SCOPE
        )
        if "access_token" in response:
            # Call a protected API with the access token.
            # print(response["access_token"])
            self.access_token = response['access_token']
        else:
            print(response.get("error"))
            print(response.get("error_description"))
            print(
                response.get("correlation_id")
            )  # You might need this when reporting a bug

    def get_user_info_by_id(self, id):
        endpoint = f"{self.config.MSAL_ENDPOINT}/users/{id}?api-version=1.6&$select=displayName,otherMails"
        print(endpoint)
        http_headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        data = requests.get(
            endpoint, headers=http_headers, stream=False
        ).json()
        return data
