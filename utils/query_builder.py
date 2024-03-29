from typing import List

from utils.enums.status import Status
from utils.repository import convert_list_to_tuple_string
from enum import Enum


class Order(Enum):
    DESC = 'DESC'
    ASC = 'ASC'


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
        self.order_by = None

    def add_select_conditions(self, columns: List[str] = None):
        columns = columns if columns else ["*"]
        self.select_conditions.extend(columns)
        return self

    def add_sql_in_condition(
        self, attribute: str = None, ids_list: List[str] = None
    ):
        if ids_list and attribute and len(ids_list) > 0:
            ids_values = convert_list_to_tuple_string(ids_list)
            self.where_conditions.append(f"c.{attribute} IN {ids_values}")
        return self

    def add_sql_active_condition(self, status_value: str):
        if status_value:
            not_defined_condition = ''
            condition_operand = ''
            if status_value == Status.ACTIVE.value:
                not_defined_condition = 'NOT IS_DEFINED(c.status)'
                condition_operand = ' OR '

            defined_condition = (
                f"(IS_DEFINED(c.status) AND c.status = '{status_value}')"
            )
            condition = (
                not_defined_condition + condition_operand + defined_condition
            )
            self.where_conditions.append(condition)
        return self

    def add_sql_date_range_condition(self, date_range: dict = None):
        if date_range:
            start_date = date_range.get('start_date')
            end_date = date_range.get('end_date')
            if start_date and end_date:
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
        if limit:
            self.limit = limit
        return self

    def add_sql_offset_condition(self, offset):
        if offset != None:
            self.offset = offset
        return self

    def add_sql_order_by_condition(self, attribute: str, order: Order):
        self.order_by = (attribute, order.name)
        return self

    def add_sql_not_in_condition(
        self, attribute: str = None, ids_list: List[str] = None
    ):
        if ids_list and attribute and len(ids_list) > 0:
            ids_values = convert_list_to_tuple_string(ids_list)
            self.where_conditions.append(f"c.{attribute} NOT IN {ids_values}")
        return self

    def __build_select(self):
        if len(self.select_conditions) < 1:
            self.select_conditions.append("*")
        return ",".join(self.select_conditions)

    def __build_where(self):
        if len(self.where_conditions) > 0:
            return "WHERE " + " AND ".join(self.where_conditions)
        else:
            return ""

    def __build_offset(self):
        if self.offset != None:
            self.parameters.append({'name': '@offset', 'value': self.offset})
            return "OFFSET @offset"
        else:
            return ""

    def __build_limit(self):
        if self.limit != None:
            self.parameters.append({'name': '@limit', 'value': self.limit})
            return "LIMIT @limit"
        else:
            return ""

    def __build_order_by(self):
        if self.order_by:
            attribute, order = self.order_by
            return f"ORDER BY c.{attribute} {order}"
        else:
            return ""

    def build(self):
        self.query = """
        SELECT {select_conditions} FROM c
        {where_conditions}
        {order_by_condition}
        {offset_condition}
        {limit_condition}
        """.format(
            select_conditions=self.__build_select(),
            where_conditions=self.__build_where(),
            order_by_condition=self.__build_order_by(),
            offset_condition=self.__build_offset(),
            limit_condition=self.__build_limit(),
        )
        return self

    def get_query(self):
        return self.query

    def get_parameters(self):
        return self.parameters
