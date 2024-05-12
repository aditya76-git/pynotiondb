import re
import csv


class MySQLQueryParser:

    INSERT_PATTERN = r"INSERT INTO ([\w\s]+) \(([^)]+)\) VALUES \(([^)]+)\)"
    SELECT_PATTERN = r"SELECT\s+(?P<columns>[a-zA-Z\*,\s]+)\s+FROM\s+(?P<table>\w+)(?:\s+WHERE\s+(?P<conditions>.+))?"
    UPDATE_PATTERN = r"UPDATE\s+(\w+)\s+SET\s+(.*?)\s+WHERE\s+(.*)"
    DELETE_PATTERN = r"DELETE\s+FROM\s+(\w+)\s+WHERE\s+(.*)"


    def __init__(self, statement):
        self.statement = statement

    @staticmethod
    def _process_string(input_string):
        # CSV reader with a single quote as the quote character
        csv_reader = csv.reader([input_string], quotechar="'", skipinitialspace=True)

        processed_values = next(csv_reader)

        processed_values = [value.strip() for value in processed_values if value.strip()]

        return processed_values

    def extract_insert_statement_info(self):
        match = re.match(self.INSERT_PATTERN, self.statement)

        if match:
            table_name = match.group(1)
            prop_string = match.group(2)
            values_string = match.group(3)

            properties = self._process_string(prop_string)
            values = self._process_string(values_string)

            data = []

            for index in range(len(properties)):
                data.append({
                    "property": properties[index],
                    "value": values[index]
                })

            if len(properties) > len(values):
                raise Exception("The number of properties specified in the INSERT statement is larger than the number of values. Please ensure that the number of properties matches the number of values to correctly assign each property a corresponding value.")

            elif len(values) > len(properties):
                raise Exception("The number of values provided in the INSERT statement is larger than the number of properties. Please ensure that the number of values matches the number of properties in order to correctly map each value to its corresponding property.")

            return {
                'table_name': table_name,
                'data': data
            }
        else:
            return None

    def extract_select_statement_info(self):
        select_pattern = re.compile(self.SELECT_PATTERN, re.IGNORECASE)
        match  = select_pattern.match(self.statement)

        if match:


          table_name = match.group('table')

          columns = match.group('columns').split(',')
          columns = [col.strip() for col in columns if col.strip() != '*']


          conditions_str = match.group('conditions')

          conditions = []
          if conditions_str:

              conditions_list = re.split(r'\s+(AND|OR)\s+', conditions_str)

              i = 0

              while i < len(conditions_list):
                  if conditions_list[i] == 'AND':
                      conditions.append(conditions_list[i])
                      i += 1
                  else:
                      key, operator, value = re.split(r'\s*(=|>|<)\s*', conditions_list[i])
                      key = key.strip()
                      operator = operator.strip()
                      value = value.strip().strip("'")
                      condition = {
                          "parameter": key,
                          "operator": operator,
                          "value": int(value) if value.isdigit() else value
                      }
                      conditions.append(condition)
                      i += 2



          outut =  {
              "table": table_name,
              "columns": columns if len(columns) != 0 else None,
              "conditions": conditions if len(conditions) != 0 else None,
          }


          return outut

        
        raise ValueError("Invalid SQL statement")

    def extract_update_statement_info(self):
        match = re.search(self.UPDATE_PATTERN, self.statement)
        
        if not match:
            return None

        table_name = match.group(1)
        set_values_str = match.group(2)
        where_clause = match.group(3)

        set_values = self.extract_set_values(set_values_str)

        output = {
            "table_name": table_name,
            "set_values": set_values,
            "where_clause": where_clause
        }
        return output

    def extract_delete_statement_info(self):
        match = re.search(self.DELETE_PATTERN, self.statement)
        
        if not match:
            return None

        table_name = match.group(1)
        where_clause = match.group(2)

        return {
            "table_name": table_name,
            "where_clause": where_clause
        }


    def extract_set_values(self, set_values_str):
        set_values = []
        pairs = set_values_str.split("AND")
        for pair in pairs:
            key_value = pair.split("=")
            if len(key_value) != 2:
                continue
            key = key_value[0].strip()
            value = key_value[1].strip().strip("'")
            set_values.append({"key": key, "value": int(value) if value.isdigit() else value})
        return set_values

    def parse(self):
        if re.match(self.INSERT_PATTERN, self.statement):
            return self.extract_insert_statement_info()

        if re.compile(self.SELECT_PATTERN, re.IGNORECASE).match(self.statement):
            return self.extract_select_statement_info()

        if re.search(self.UPDATE_PATTERN, self.statement):
            return self.extract_update_statement_info()

        if re.search(self.DELETE_PATTERN, self.statement):
            return self.extract_delete_statement_info()

        raise ValueError("Invalid SQL statement")

    def check_statement(self):

        if re.match(self.INSERT_PATTERN, self.statement):
            return True, "insert"

        if re.compile(self.SELECT_PATTERN, re.IGNORECASE).match(self.statement):
            return True, "select"

        if re.search(self.UPDATE_PATTERN, self.statement):
            return True, "update"

        if re.search(self.DELETE_PATTERN, self.statement):
            return True, "delete"

        return False, "unknown"