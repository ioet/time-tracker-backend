from utils.query_builder import CosmosDBQueryBuilder


class TimeEntryQueryBuilder(CosmosDBQueryBuilder):
    def __init__(self):
        super(TimeEntryQueryBuilder, self).__init__()

    def add_sql_date_range_condition(self, date_range: tuple = None):
        if date_range and len(date_range) == 2:
            start_date = date_range['start_date']
            end_date = date_range['end_date']
            condition = """
            ((c.start_date BETWEEN @start_date AND @end_date) OR
             (c.end_date BETWEEN @start_date AND @end_date))
            """
            self.where_conditions.append(condition)
            self.parameters.extend(
                [
                    {'name': '@start_date', 'value': start_date},
                    {'name': '@end_date', 'value': end_date},
                ]
            )
        return self

    def add_sql_interception_with_date_range_condition(
        self, start_date, end_date
    ):
        condition = """
        (((c.start_date BETWEEN @start_date AND @end_date)
          OR (c.end_date BETWEEN @start_date AND @end_date))
          OR ((@start_date BETWEEN c.start_date AND c.end_date)
          OR (@end_date BETWEEN c.start_date AND c.end_date)))
          AND c.start_date!= @end_date
          AND c.end_date!= @start_date
        """
        self.where_conditions.append(condition)
        self.parameters.extend(
            [
                {'name': '@start_date', 'value': start_date},
                {'name': '@end_date', 'value': end_date},
            ]
        )
        return self

    def add_sql_is_running_time_entry_condition(self):
        condition = "(NOT IS_DEFINED(c.end_date) OR c.end_date = null)"
        self.where_conditions.append(condition)
        return self

    def add_sql_ignore_id_condition(self, id: str = None):
        if id:
            self.where_conditions.append("c.id!=@ignore_id")
            self.parameters.append({'name': '@ignore_id', 'value': id})
        return self
