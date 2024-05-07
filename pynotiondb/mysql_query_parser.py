import re
import csv

class MySQLQueryParser:

    INSERT_PATTERN = r"INSERT INTO ([\w\s]+) \(([^)]+)\) VALUES \(([^)]+)\)"

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

    def parse(self):
        if re.match(self.INSERT_PATTERN, self.statement):
            return self.extract_insert_statement_info()

    def check_statement(self):

        if re.match(self.INSERT_PATTERN, self.statement):
            return True, "insert"

        return False, "unknown"