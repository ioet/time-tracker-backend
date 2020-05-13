def add_project_name_to_time_entries(time_entries, projects):
    for time_entry in time_entries:
        for project in projects:
            if time_entry.project_id == project.id:
                setattr(time_entry, 'project_name', project.name)
