from utils.query_builder import CosmosDBQueryBuilder


class TimeEntryQueryBuilder(CosmosDBQueryBuilder):
    def __init__(self):
        super().__init__()

    def add_sql_date_range_condition(self, dates: tuple = None):
        if dates and len(dates) == 2:
            start_date, end_date = dates
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
