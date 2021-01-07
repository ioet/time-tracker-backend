from azure.appconfiguration import AzureAppConfigurationClient
from time_tracker_api.security import current_user_email
import json
import os


class FeatureToggleManager:
    AZURE_CONNECTION_STRING = os.environ.get(
        'AZURE_APP_CONFIGURATION_CONNECTION_STRING'
    )

    def __init__(self, key: str, label: str = None):
        self.key = key
        self.label = label
        self.configuration = {}

    def _get_configuration(self, key: str, label: str):
        connection_str = self.AZURE_CONNECTION_STRING
        client = AzureAppConfigurationClient.from_connection_string(
            connection_str
        )
        configuration = client.get_configuration_setting(
            key=f".appconfig.featureflag/{self.key}", label=self.label
        )

        return configuration

    def _get_data_configuration(self):
        self.configuration = self._get_configuration(self.key, self.label)
        result = json.loads(self.configuration.value)

        return result

    def _is_toggle_enabled(self):
        data = self._get_data_configuration()
        result = data["enabled"]

        return result

    def is_toggle_enabled_for_user(self):
        data = self._get_data_configuration()
        client_filters = data["conditions"]["client_filters"]
        first_client = client_filters[0]
        list_users = first_client["parameters"]["Audience"]["Users"]
        current_user = current_user_email()

        return (
            True
            if current_user in list_users and self._is_toggle_enabled()
            else False
        )
