from functools import wraps
import re


def add_custom_attribute(attr, dao):
    """
    Decorator to add an custom attribute in model, based on entity's id
    :param (attr) attribute: name of the new attribute
    :param (dao) dao: related entity to the model
    """

    def decorator_for_single_item(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_dao = dao()
            entity_model = func(*args, **kwargs)
            attribute_id = f"{attr}_id"

            if entity_model and attribute_id in entity_model.__dict__:
                value_id = entity_model.__dict__[attribute_id]
                if value_id:
                    related_entity = current_dao.get(value_id)
                    setattr(entity_model, attr, related_entity)

            return entity_model

        return wrapper

    return decorator_for_single_item


def add_custom_attribute_in_list(attr, dao):
    """
    Decorator to add an custom attribute in model_list, based on entity's id
    :param (attr) attribute: name of the new attribute
    :param (dao) dao: related entity to the model
    """

    def decorator_for_list_item(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_dao = dao()
            entity_model_list = func(*args, **kwargs)
            attribute_id = f"{attr}_id"

            related_entity_list = current_dao.get_all()
            related_entities_ids_dict = {x.id: x for x in related_entity_list}

            for entity_model in entity_model_list:
                value_id = entity_model.__dict__[attribute_id]
                setattr(
                    entity_model, attr, related_entities_ids_dict.get(value_id)
                )

            return entity_model_list

        return wrapper

    return decorator_for_list_item


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


def add_project_info_to_time_entries(time_entries, projects):
    """
    Add project info in time-entry model, based on project_id of the
    time_entry
    :param (list) time_entries: time_entries retrieved from time-entry repository
    :param (list) projects: projects retrieved from project repository

    TODO : check if we can improve this by using the overwritten __add__ method
    """
    for time_entry in time_entries:
        for project in projects:
            if time_entry.project_id == project.id:
                name = (
                    project.name + " (archived)"
                    if project.is_deleted()
                    else project.name
                )
                setattr(time_entry, 'project_name', name)
                setattr(time_entry, 'customer_id', project.customer_id)
                setattr(time_entry, 'customer_name', project.customer_name)


def add_activity_name_to_time_entries(time_entries, activities):
    for time_entry in time_entries:
        for activity in activities:
            if time_entry.activity_id == activity.id:
                name = (
                    activity.name + " (archived)"
                    if activity.is_deleted()
                    else activity.name
                )
                setattr(time_entry, 'activity_name', name)


def add_user_email_to_time_entries(time_entries, users):
    for time_entry in time_entries:
        for user in users:
            if time_entry.owner_id == user.id:
                setattr(time_entry, 'owner_email', user.email)


def create_in_condition(
    data_object: list, attr_to_filter: str = "", first_attr: str = "c.id"
):
    """
    Function to create a custom query string from a list of objects or a list of strings.
    :param data_object: List of objects or a list of strings
    :param attr_to_filter: Attribute to retrieve the value of the objects (Only in case it is a list of objects)
    :param first_attr: First attribute to build the condition
    :return: Custom condition string
    """
    attr_filter = re.sub('[^a-zA-Z_$0-9]', '', attr_to_filter)
    object_id = (
        [str(i) for i in data_object]
        if type(data_object[0]) == str
        else [str(eval(f"object.{attr_filter}")) for object in data_object]
    )
    ids = (
        str(tuple(object_id)).replace(",", "")
        if len(object_id) == 1
        else str(tuple(object_id))
    )
    return "{} IN {}".format(first_attr, ids)


def create_custom_query_from_str(
    data: str, first_attr, delimiter: str = ","
) -> str:
    """
    Function to create a string condition for url parameters (Example: data?values=value1,value2 or data?values=*)
    :param data: String to build the query
    :param first_attr: First attribute to build the condition
    :param delimiter: String delimiter
    :return: Custom condition string
    """
    data = data.split(delimiter)
    if len(data) > 1:
        query_str = create_in_condition(data, first_attr=first_attr)
    else:
        query_str = "{} = '{}'".format(first_attr, data[0])
    return query_str


def create_list_from_str(data: str, delimiter: str = ",") -> list:
    return [id for id in data.split(delimiter)] if data else []
