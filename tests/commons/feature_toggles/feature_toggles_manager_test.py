from commons.feature_toggles.feature_toggle_manager import FeatureToggleManager
from unittest.mock import Mock, patch
from pytest import mark


def mock_feature_toggle_config_response(enabled, user):
    return {
        "id": "test-feature-toggle",
        "description": "Feature Toggle test Backend",
        "enabled": enabled,
        "conditions": {
            "client_filters": [
                {
                    "name": "Microsoft.Targeting",
                    "parameters": {
                        "Audience": {
                            "Users": [user],
                            "Groups": [],
                            "DefaultRolloutPercentage": 50,
                        }
                    },
                }
            ]
        },
    }


@patch(
    'azure.appconfiguration.AzureAppConfigurationClient.from_connection_string',
    new_callable=Mock,
)
@patch(
    'commons.feature_toggles.feature_toggle_manager.FeatureToggleManager.get_data_configuration',
    new_callable=Mock,
)
@patch('commons.feature_toggles.feature_toggle_manager.current_user_email')
@mark.parametrize(
    'user_email_enabled,currrent_user_email,is_toggle_enabled,expected_result',
    [
        ('testUser@ioet.com', 'testUser@ioet.com', True, True),
        ('testUser@ioet.com', 'testUser@ioet.com', False, False),
        ('testUser@ioet.com', 'testWrongUser@ioet.com', True, False),
        ('testUser@ioet.com', 'testWrongUser@ioet.com', False, False),
    ],
)
def test_if_is_toggle_enabled_for_user(
    current_user_email_mock,
    get_data_configuration_mock,
    from_connection_string_mock,
    user_email_enabled,
    currrent_user_email,
    is_toggle_enabled,
    expected_result,
):
    current_user_email_mock.return_value = currrent_user_email
    feature_toggle_manager = FeatureToggleManager("test-feature-toggle")
    feature_toggle_manager.get_data_configuration.return_value = (
        mock_feature_toggle_config_response(
            is_toggle_enabled, user_email_enabled
        )
    )

    assert (
        feature_toggle_manager.is_toggle_enabled_for_user() == expected_result
    )
