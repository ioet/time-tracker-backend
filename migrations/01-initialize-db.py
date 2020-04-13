def up():
    from commons.data_access_layer.cosmos_db import cosmos_helper
    import azure.cosmos.exceptions as exceptions
    from . import app

    app.logger.info("Creating TimeTracker initial containers...")

    try:
        app.logger.info('- Project')
        from time_tracker_api.projects.projects_model import container_definition as project_definition
        cosmos_helper.create_container(project_definition)

        app.logger.info('- Project type')
        from time_tracker_api.project_types.project_types_model import container_definition as project_type_definition
        cosmos_helper.create_container(project_type_definition)

        app.logger.info('- Activity')
        from time_tracker_api.activities.activities_model import container_definition as activity_definition
        cosmos_helper.create_container(activity_definition)

        app.logger.info('- Customer')
        from time_tracker_api.customers.customers_model import container_definition as customer_definition
        cosmos_helper.create_container(customer_definition)

        app.logger.info('- Time entry')
        from time_tracker_api.time_entries.time_entries_model import container_definition as time_entry_definition
        cosmos_helper.create_container(time_entry_definition)
    except exceptions.CosmosResourceExistsError as e:
        app.logger.warning("Unexpected error while creating initial database schema: %s" % e.message)

    app.logger.info("Done!")


def down():
    print("Not implemented!")
