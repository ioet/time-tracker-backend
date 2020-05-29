import re


def add_customer_name_to_projects(projects, customers):
    """
    Add attribute customer_name in project model, based on customer_id of the
    project
    :param (list) projects: projects retrieved from project repository
    :param (list) customers: customers retrieved from customer repository

    TODO : check if we can improve this by using the overwritten __add__ method
    """
    for project in projects:
        for customer in customers:
            if project.customer_id == customer.id:
                setattr(project, 'customer_name', customer.name)


def add_project_name_to_time_entries(time_entries, projects):
    """
    Add attribute project_name in time-entry model, based on project_id of the
    time_entry
    :param (list) time_entries: time_entries retrieved from time-entry repository
    :param (list) projects: projects retrieved from project repository

    TODO : check if we can improve this by using the overwritten __add__ method
    """
    for time_entry in time_entries:
        for project in projects:
            if time_entry.project_id == project.id:
                setattr(time_entry, 'project_name', project.name)


def create_in_condition(data_object, attr_to_filter, first_attr="c.id"):
    attr_filter = re.sub('[^a-zA-Z_$0-9]', '', attr_to_filter)
    object_id = [str(eval(f"object.{attr_filter}")) for object in data_object]
    ids = (
        str(tuple(object_id)).replace(",", "")
        if len(object_id) == 1
        else str(tuple(object_id))
    )
    return "{} IN {}".format(first_attr, ids)
