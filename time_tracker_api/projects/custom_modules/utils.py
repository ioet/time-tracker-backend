# TODO this must be refactored to be used from the utils module ↓
# Also check if we can change this using the overwritten __add__ method


def add_customer_name_to_projects(projects, customers):
    for project in projects:
        for customer in customers:
            if project.customer_id == customer.id:
                setattr(project, 'customer_name', customer.name)
