# TODO : check if we can improve this by using the overwritten __add__ method
def add_customer_name_to_projects(projects, customers):
    for project in projects:
        for customer in customers:
            if project.customer_id == customer.id:
                setattr(project, 'customer_name', customer.name)


def add_project_name_to_time_entries(time_entries, projects):
    for time_entry in time_entries:
        for project in projects:
            if time_entry.project_id == project.id:
                setattr(time_entry, 'project_name', project.name)
