import os
import json
from time_tracker_api.security import current_user_email
from azure.appconfiguration import AzureAppConfigurationClient


class FeatureToggleConfig:
    def check_variables_are_defined():
        azure_app_variable = 'AZURE_APP_CONFIGURATION_CONNECTION_STRING'
        if azure_app_variable not in os.environ:
            raise EnvironmentError(
                "{} is not defined in the environment".format(
                    azure_app_variable
                )
            )

    check_variables_are_defined()
    AZURE_APP_CONFIGURATION_CONNECTION_STRING = os.environ.get(
        'AZURE_APP_CONFIGURATION_CONNECTION_STRING'
    )


class FeatureToggleManager:
    def __init__(
        self, key: str, label: str = None, config=FeatureToggleConfig
    ):
        self.key = key
        self.label = label
        self.config = config
        self.client = self.get_azure_app_configuration_client()

    def get_azure_app_configuration_client(self):
        connection_str = self.config.AZURE_APP_CONFIGURATION_CONNECTION_STRING
        client = AzureAppConfigurationClient.from_connection_string(
            connection_str
        )

        return client

    def get_configuration(self, key: str, label: str):
        configuration = self.client.get_configuration_setting(
            key=f".appconfig.featureflag/{key}", label=label
        )

        return configuration

    def get_data_configuration(self):
        feature_data_configuration = self.get_configuration(
            self.key, self.label
        )
        result = json.loads(feature_data_configuration.value)

        return result

    def is_toggle_enabled(self):
        data = self.get_data_configuration()
        result = data["enabled"]

        return result

    def get_list_users(self):
        data = self.get_data_configuration()
        client_filters = data["conditions"]["client_filters"]
        first_client = client_filters[0]
        list_users = first_client["parameters"]["Audience"]["Users"]

        return list_users

    def is_toggle_enabled_for_user(self):
        list_users = self.get_list_users()
        current_user = current_user_email()

        return current_user in list_users and self.is_toggle_enabled()
