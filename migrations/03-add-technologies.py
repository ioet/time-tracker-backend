def up():
    from commons.data_access_layer.cosmos_db import cosmos_helper
    import azure.cosmos.exceptions as exceptions
    from . import app

    app.logger.info("Creating technology container...")

    try:
        app.logger.info('- Technologies')
        from time_tracker_api.technologies.technologies_model import (
            container_definition as technologies_definition,
        )

        cosmos_helper.create_container(technologies_definition)

    except exceptions.CosmosResourceExistsError as e:
        app.logger.warning(
            "Unexpected error while creating initial database schema: %s"
            % e.message
        )

    app.logger.info("Done!")


def down():
    print("Not implemented!")
