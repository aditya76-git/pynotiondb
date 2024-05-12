import requests
from .exceptions import NotionAPIError
from .mysql_query_parser import MySQLQueryParser


class NOTION_API:

    SEARCH = "https://api.notion.com/v1/search"
    PAGES = "https://api.notion.com/v1/pages"
    UPDATE_PAGE = "https://api.notion.com/v1/pages/{}"
    DATABASES = "https://api.notion.com/v1/databases/{}"
    QUERY_DATABASE = "https://api.notion.com/v1/databases/{}/query"
    DEFAULT_PAGE_SIZE_FOR_SELECT_STATEMENTS = 20

    CONDITION_MAPPING = {
        "=" : "equals",
        ">" : "greater_than",
        "<" : "less_than",
        "<=" : "less_than_or_equal_to",
        ">=" : "greater_than_or_equal_to",
        "==" : "equals",
    }

  

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
        # response.raise_for_status()
        response = self.get_json(response)
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

            if data.get('name') == "number":

                json_data["properties"][data.get('property')] = {
                     "number": int(data.get('value'))
                }

            elif data.get('name') in ['title', 'rich_text']:
              
                json_data["properties"][data.get('property')] = {
                    data.get('name') : [
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
    def __add_name_and_id_to_parsed_data_for_insert_statements(parsed_data, table_header):

        for item in parsed_data['data']:

            if item.get('property') in table_header:
                item['name'] = table_header[item.get('property')]["name"]
                item['id'] = table_header[item.get('property')]["id"]

        return parsed_data


    @staticmethod
    def __add_name_and_id_to_parsed_data_for_select_statements(parsed_data, table_header):
        for condition in parsed_data.get('conditions', []):
            parameter = condition.get('parameter')
            if parameter in table_header:
                condition['name'] = table_header[parameter]["name"]
                condition['id'] = table_header[parameter]["id"]
        return parsed_data


    @staticmethod
    def __add_name_and_id_to_parsed_data_for_update_statements(parsed_data, table_header):
        set_values = parsed_data.get('set_values', [])
        updated_set_values = []

        for set_value in set_values:
            key = set_value.pop('key', None)

            if key and key in table_header:
                set_value.update({
                    'property': key,  # Changing 'key' to 'property'
                    'name': table_header[key]["name"],
                    'id': table_header[key]["id"]
                })

            updated_set_values.append(set_value)

       #Doing this so that using this we can later call construct payload function         
        return {
            "table_name": parsed_data.get('table_name'),
            "data": updated_set_values,
            "where_clause": parsed_data.get('where_clause')
        }



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

        parsed_data = self.__add_name_and_id_to_parsed_data_for_insert_statements(parsed_data, table_header)

        payload = self.construct_payload_for_pages_creation(parsed_data)

        response = self.request_helper(self.PAGES, method = "POST", payload = payload)

    def insert_many(self, sql, val):

        table_header = self.get_table_header_info()

        for row in val:
            query = self.__generate_query(sql, row)

            parsed_data = MySQLQueryParser(query).parse()
            parsed_data = self.__add_name_and_id_to_parsed_data_for_insert_statements(parsed_data, table_header)
            payload = self.construct_payload_for_pages_creation(parsed_data)
            response = self.request_helper(self.PAGES, method = "POST", payload = payload)

    def select(self, query):

        table_header = self.get_table_header_info()
        parsed_data = MySQLQueryParser(query).parse()

        #We will need to add title, rich_text or number acc to the type of the property in the parsed_data which is parsed from the SELECT statement
        #We only need to add name and id if there are condition in the statement

        if parsed_data.get('conditions') is not None:

            parsed_data = self.__add_name_and_id_to_parsed_data_for_select_statements(parsed_data, table_header)



        #If * is in the query that means it needs to have all the table headers so we need to use get_table_header()
        property_names = parsed_data.get('columns', None) if parsed_data.get('columns') else self.get_table_header()

        results = {
            "data": [],
            "next_cursor": "",
            "previous_cursor": None,
            "has_more": "",
        }

        page_size_dict = []

        if parsed_data.get('conditions') is not None:
            page_size_dict = [
                condition for condition in parsed_data.get('conditions', []) if condition.get('parameter') == 'page_size' and condition is not None
            ]


        payload = {
            "page_size": page_size_dict[0].get('value') if len(page_size_dict) > 0 else self.DEFAULT_PAGE_SIZE_FOR_SELECT_STATEMENTS,
            "filter" : {
                "and" : []
            }
        }

        all_conditions_except_page_size = parsed_data.get('conditions')
        
        if len(page_size_dict) > 0:
            
            all_conditions_except_page_size = [condition for condition in parsed_data.get('conditions', []) if condition.get('parameter') != "page_size"]


        if all_conditions_except_page_size is not None:

            for condition in all_conditions_except_page_size:
              
                filter = {
                    "property": condition.get('parameter'), 
                    condition.get('name') : {
                        self.CONDITION_MAPPING.get(condition.get('operator')): condition.get('value')
                    }
                }
                payload["filter"]['and'].append(filter)



        response = self.request_helper(self.QUERY_DATABASE.format(self.databaseId), method = "POST", payload = payload).json()


        for entry in response["results"]:

            properties = entry["properties"]

            single_dict = {}


            for prop_name in property_names:
                prop_data = properties.get(prop_name, {})
                prop_type = prop_data.get("type", None)

                prop_value = None

                if prop_type and prop_type in prop_data:
                  
                    try:
                        if prop_type in ["title", "rich_text"]:
                            prop_value = prop_data[prop_type][0].get("plain_text", "")

                        elif prop_type == "number":
                            prop_value = prop_data.get("number", None)

                        else:
                            prop_value = None

                    except:
                        prop_value = None


                single_dict[prop_name.lower()] = prop_value
                single_dict["id"] = entry["id"]
                single_dict["created_time"] = entry["created_time"]
                single_dict["last_edited_time"] = entry["last_edited_time"]

            # Check if any of the properties in the single_dict is empty
            if any(value for value in single_dict.values()):
                results["data"].append(single_dict)

        results["next_cursor"] = response.get("next_cursor", None)
        results["has_more"] = response.get("has_more", False)

        return results

    def update(self, query):
        table_header = self.get_table_header_info()

        parsed_data = MySQLQueryParser(query).parse()

        parsed_data = self.__add_name_and_id_to_parsed_data_for_update_statements(parsed_data, table_header)

        select_statement_response = self.select("SELECT * from TEMP WHERE {}".format(parsed_data.get('where_clause')))

        if not len(select_statement_response['data']) >= 0:
            raise ValueError("No Data Found")

        for entry in select_statement_response['data']:

            payload = self.construct_payload_for_pages_creation(parsed_data)

            #We don't want "parent" key in the payload
            payload.pop('parent')

            response = self.request_helper(url = self.UPDATE_PAGE.format(entry['id']), method = "PATCH", payload = payload)

      


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

            elif to_do == "select":
              
                return self.select(query)

            elif to_do == "update":

                self.update(query)

            else:
                raise ValueError(f"Unsupported operation")

        else:
            raise ValueError("Invalid SQL statement or type of statement not implemented")