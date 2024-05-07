import requests
from .exceptions import NotionAPIError
from .mysql_query_parser import MySQLQueryParser

class NOTION_API:

    SEARCH = "https://api.notion.com/v1/search"
    PAGES = "https://api.notion.com/v1/pages"
    DATABASES = "https://api.notion.com/v1/databases/{}"


    def __init__(self, token, databaseId):
        self.token = token
        self.databaseId = databaseId
        self.DEFAULT_NOTION_VERSION = "2022-06-28"
        self.AUTHORIZATION = "Bearer " + self.token
        self.headers = {
            "Authorization": self.AUTHORIZATION,
            "Content-Type": "application/json",
            "Notion-Version": self.DEFAULT_NOTION_VERSION
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def request_helper(self, url, method = "GET", payload=None):
        response = self.session.request(method, url, json = payload)
        response = self.get_json(response)
        response.raise_for_status()
        return response

    def get_json(self, response):
        if response.status_code >= 400:
            try:
                error_info = response.json()
                error_message = error_info.get("message", "Unknown Notion API Error")
                error_code = error_info.get("code", "Unknown Code")

            except Exception:
                error_message = "Unable to parse"
                error_code = "Unknown Code"

            raise NotionAPIError(f"Notion API Error ({response.status_code}): {error_message} ({error_code})")

        else:
            return response

    def construct_payload_for_pages_creation(self, properties_data):

        json_data = {
            "parent": {
                "database_id": self.databaseId
            },
            "properties": {}
        }

        for data in properties_data['data']:
            json_data["properties"][data.get('property')] = {
                "title" if data.get('name') == "title" else "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": str(data.get('value')),
                        },
                        "plain_text": str(data.get('value')),
                    }
                ]
            }

        return json_data





    def get_table_header_info(self):

        response = self.request_helper(url = self.DATABASES.format(self.databaseId), method = "GET")

        database_info = response.json()
        properties = database_info.get("properties", {})

        data = {}

        for property_name, property_info in properties.items():

            data[property_name] = {
                "id": property_info.get("id", ""),
                "name": property_info.get("type", ""),
                "type": property_info.get("name", "")
            }

        return data

    def get_table_header(self):
        table_data = self.get_table_header_info()
        return tuple(table_data.keys())

    def get_all_database_info(self, cursor = None, page_size = 20):
        payload = {
            'filter': {
                'value': 'database',
                'property': 'object',
            },
            'page_size' : int(page_size)
        }

        if cursor:
            payload["start_cursor"] = cursor

        response = self.request_helper(url = self.SEARCH, method = "POST", payload = payload)

        data = {
            "results" : []
        }

        dbs_info = response.json()
        results = dbs_info.get("results", {})


        for result in results:
            data['results'].append({
                "id" : result.get('id'),
                "created_by" : result.get('created_by'),
                "last_edited_by" : result.get('last_edited_by'),
                "last_edited_time" : result.get('last_edited_time'),
                "title" : result.get('title')[0].get('plain_text') if len(result.get('title')) >= 1 else None,
                "description" : result.get('description')[0].get('plain_text') if len(result.get('description')) >= 1 else None,
                'properties' : list(result.get('properties').keys())
            })

        data['has_more'] = dbs_info.get('has_more')
        data['next_cursor'] = dbs_info.get('next_cursor')
        data['previous_cursor'] = dbs_info.get('previous_cursor')


        return data

    def get_all_database(self):
        dbs = self.get_all_database_info()
        databases = [db.get('title') for db in dbs.get('results')]

        return tuple(databases)

    @staticmethod
    def __add_name_and_id_to_parsed_data(parsed_data, table_header):

        for item in parsed_data['data']:

            if item.get('property') in table_header:
                item['name'] = table_header[item.get('property')]["name"]
                item['id'] = table_header[item.get('property')]["id"]

        return parsed_data

    @staticmethod
    def __generate_query(sql, val = None):

        if val is not None:
            query = sql.replace("%s", "'%s'")
            query = sql % val

        else:
            query = sql

        return query

    def insert(self, query):

        table_header = self.get_table_header_info()

        parsed_data = MySQLQueryParser(query).parse()

        parsed_data = self.__add_name_and_id_to_parsed_data(parsed_data, table_header)

        payload = self.construct_payload_for_pages_creation(parsed_data)

        response = self.request_helper(self.PAGES, method = "POST", payload = payload)

    def insert_many(self, sql, val):

        table_header = self.get_table_header_info()

        for row in val:
            query = self.__generate_query(sql, row)

            parsed_data = MySQLQueryParser(query).parse()
            parsed_data = self.__add_name_and_id_to_parsed_data(parsed_data, table_header)
            payload = self.construct_payload_for_pages_creation(parsed_data)
            response = self.request_helper(self.PAGES, method = "POST", payload = payload)


    def execute(self, sql, val = None):

        if val is not None and type(val) == list:
            query = sql
            to_execute_many = True

        else:
            query = self.__generate_query(sql, val)
            to_execute_many = False

        parser = MySQLQueryParser(query)

        can_continue, to_do = parser.check_statement()

        if can_continue:

            if to_do == "insert":


                self.insert_many(sql, val) if to_execute_many else self.insert(query)

            else:
                raise ValueError(f"Unsupported operation")

        else:
            raise ValueError("Invalid SQL statement or type of statement not implemented")