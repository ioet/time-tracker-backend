from typing import List
from utils.repository import convert_list_to_tuple_string


class CosmosDBQueryBuilder:
    query: str

    def __init__(self):
        super().__init__()
        self.query = ""
        self.parameters = []
        self.select_conditions = []
        self.where_conditions = []
        self.limit = None
        self.offset = None

    def add_select_conditions(self, column: List[str] = None):
        column = column if column else ["*"]
        self.select_conditions.extend(column)
        return self

    def add_sql_in_condition(
        self, attribute: str = None, ids_list: List[str] = None
    ):
        if ids_list and attribute and len(ids_list) > 0:
            ids_values = convert_list_to_tuple_string(ids_list)
            self.where_conditions.append(f"c.{attribute} IN {ids_values}")
        return self

    def add_sql_where_equal_condition(self, data: dict = None):
        if data:
            for k, v in data.items():
                condition = f"c.{k} = @{k}"
                self.where_conditions.append(condition)
                self.parameters.append({'name': f'@{k}', 'value': v})
        return self

    def add_sql_visibility_condition(self, visible_only: bool):
        if visible_only:
            self.where_conditions.append('NOT IS_DEFINED(c.deleted)')
        return self

    def add_sql_limit_condition(self, limit):
        if limit and isinstance(limit, int):
            self.limit = limit
        return self

    def add_sql_offset_condition(self, offset):
        if offset and isinstance(offset, int):
            self.offset = offset
        return self

    def build_select(self):
        if len(self.select_conditions) < 1:
            self.select_conditions.append("*")
        return ",".join(self.select_conditions)

    def build_where(self):
        if len(self.where_conditions) > 0:
            return "WHERE " + " AND ".join(self.where_conditions)
        else:
            return ""

    def build_offset(self):
        if self.offset:
            self.parameters.append({'name': '@offset', 'value': self.offset})
            return "OFFSET @offset"
        else:
            return ""

    def build_limit(self):
        if self.limit:
            self.parameters.append({'name': '@limit', 'value': self.limit})
            return "LIMIT @limit"
        else:
            return ""

    def build(self):
        self.query = """
        SELECT {select_conditions} FROM c
        {where_conditions}
        {offset_condition}
        {limit_condition}
        """.format(
            select_conditions=self.build_select(),
            where_conditions=self.build_where(),
            offset_condition=self.build_offset(),
            limit_condition=self.build_limit(),
        )
        return self

    def get_query(self):
        return self.query

    def get_parameters(self):
        return self.parameters
