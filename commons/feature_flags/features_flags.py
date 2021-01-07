from azure.appconfiguration import AzureAppConfigurationClient
from time_tracker_api.security import current_user_email
import json
import os


class FeatureFlags:
    AZURE_CONNECTION_STRING = os.environ.get(
        'AZURE_APP_CONFIGURATION_CONNECTION_STRING'
    )

    def __init__(self, key: str, label: str = None):
        self.key = key
        self.label = label
        self.configuration = self.get_configuration(self.key, self.label)

    def get_configuration(self, key: str, label: str):
        connection_str = self.AZURE_CONNECTION_STRING
        client = AzureAppConfigurationClient.from_connection_string(
            connection_str
        )
        configuration = client.get_configuration_setting(
            key=f".appconfig.featureflag/{self.key}", label=self.label
        )

        return configuration

    def is_toggle_enabled(self):
        self.configuration = self.get_configuration(self.key, self.label)
        data = json.loads(self.configuration.value)
        result = data["enabled"]

        return result

    def is_toggle_enabled_for_user(self):
        self.configuration = self.get_configuration(self.key, self.label)
        data = json.loads(self.configuration.value)
        list_data = data["conditions"]["client_filters"]
        data2 = list_data[0]
        list_users = data2["parameters"]["Audience"]["Users"]
        user = current_user_email()

        return (
            True if user in list_users and self.is_toggle_enabled() else False
        )
