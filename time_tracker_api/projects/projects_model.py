from time_tracker_api.errors \
    import MissingResource, InvalidInput, InvalidMatch


class InMemoryProjectDAO(object):
    def __init__(self):
        self.counter = 0
        self.projects = []

    def get_all(self):
        return self.projects

    def get(self, id):
        for project in self.projects:
            if project.get('id') == id:
                return project
        raise MissingResource("Project '%s' not found" % id)

    def create(self, project):
        self.counter += 1
        project['id'] = str(self.counter)
        self.projects.append(project)
        return project

    def update(self, id, data):
        project = self.get(id)
        if project:
            project.update(data)
            return project
        else:
            raise MissingResource("Project '%s' not found" % id)

    def delete(self, id):
        if id:
            project = self.get(id)
            self.projects.remove(project)

    def flush(self):
        self.projects.clear()

    def search(self, search_criteria):
        matching_projects = self.select_matching_projects(search_criteria)

        if len(matching_projects) > 0:
            return matching_projects
        else:
            raise InvalidMatch("No project matched the specified criteria")

    def select_matching_projects(self, user_search_criteria):
        search_criteria = {k: v for k, v
                           in user_search_criteria.items()
                           if v is not None}

        def matches_search_string(search_str, project):
            return search_str in project['comments'] or \
                   search_str in project['short_name']

        if not search_criteria:
            raise InvalidInput("No search criteria specified")

        search_str = search_criteria.get('search_string')
        if search_str:
            matching_projects = [p for p
                                 in self.projects
                                 if matches_search_string(search_str, p)]
        else:
            matching_projects = self.projects

        is_active = search_criteria.get('active')
        if is_active is not None:
            matching_projects = [p for p
                                 in matching_projects
                                 if p['active'] is is_active]

        return matching_projects


# Instances
# TODO Create an strategy to create other types of DAO
project_dao = InMemoryProjectDAO()
