def up():
    from commons.data_access_layer.cosmos_db import cosmos_helper
    import azure.cosmos.exceptions as exceptions
    from commons.data_access_layer.events_model import container_definition as event_definition
    from . import app

    app.logger.info("Creating container events...")

    try:
        app.logger.info('- Event')
        cosmos_helper.create_container(event_definition)
    except exceptions.CosmosResourceExistsError as e:
        app.logger.warning("Unexpected error while creating container for events: %s" % e.message)

    app.logger.info("Done!")


def down():
    print("Not implemented!")
