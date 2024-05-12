<h1 align="center">pynotiondb</h1>
<p align="center">
    <img src="https://i.imgur.com/Vv7q65D.png" alt="pynotiondb">
</p>

<h4 align="center">
A Python wrapper for interacting with Notion databases using SQL-style syntax</h4>

<div style="text-align:center;">
  <a href="https://github.com/aditya76-git">aditya76-git</a> /
  <a href="https://github.com/aditya76-git/pynotiondb">pynotiondb</a>
</div>

<br />

# pynotiondb

`pynotiondb` is a Python package that provides a convenient way to interact with Notion databases using SQL-style syntax.

## 📋Details

- ➕ [Insert Statement](#insert)
  - [Single-Row Insertion](#single-row-insertion)
  - [Multiple-Row Insertion](#multiple-row-insertion)
- 🔎 [Select Statement](#select)
  - [Default Retrieval with All Columns](#default-retrieval-with-all-columns)
  - [Retrieval with Specified Columns](#retrieval-with-specified-columns)
  - [Retrieval with Specified Columns and Custom Page Size](#retrieval-with-specified-columns-and-custom-page-size)
  - [Applying Conditions](#applying-conditions)
  - [Applying Conditions (2)](#applying-conditions-2)
- ⚡ [Update Statement](#update)
  - [Updating a row](#updating-a-row)
- ⚡ [Delete Statement](#delete)
  - [Deleting a row](#single-row-deletion)

## ⚙️Installation

Open your terminal or command prompt and enter the following command:

```bash
pip install git+https://github.com/aditya76-git/pynotiondb@main
```

> **Note:** To use this package you need to have a Active Notion Account

## 🚀Pre-requisites

Before using this package, you'll need to set up a few things in your Notion workspace:

1. **Create an Integration in Notion**: Begin by creating a new integration in Notion’s integrations dashboard: [https://www.notion.com/my-integrations](https://www.notion.com/my-integrations).
   <br/>
   [DOCS](https://developers.notion.com/docs/create-a-notion-integration)

2. **Obtain Your API Secret**: API requests require an API secret to be successfully authenticated. Visit the `Secrets` tab to get your integration’s API secret

3. **Get the Database ID**: Retrieve the database ID from the URL of your Notion database.

> For example, in the URL `https://www.notion.so/f30ed4836a234308a63f7b76f71b098c?v=f9adf71ce9924344bf01e072150436cb`, `f30ed4836a234308a63f7b76f71b098c` is the database ID

4. **Connect the Integration to the Database**: Connect your database to the integration by clicking on the three dots menu, navigating to the connections tab, and selecting your integration from the available options.

## 📌 Note

- To utilize this package, you'll initially need to create a database or table within Notion. Customize the table headers to align with your requirements; for instance, if you're managing customer data, you'd include headers such as "Name" and "Address" as needed.

- When adding a new table header in the database, ensure to select "Text" or Number from the Type dropdown menu. This selection ensures that the data is stored as text or as number, which is compatible with the package's functionality for retrieving rows. Avoid selecting any other options from the dropdown menu.

- As of now, the `pynotiondb` package only supports `INSERT` and `SELECT` statements. It does not offer functionalities to create tables or add table headers directly from the package itself. Therefore, users must manually create the tables with appropriate headers in Notion before using the package.

- Even if you mistakenly input an incorrect table name while executing SQL statements, the query will still execute successfully due to the databaseId being used when you do `mydb = NOTION_API("API_SECRET", "DATABASE_ID")`.

- Additional statements will be implemented in future updates of the package.

## 📷 Notion Database View

<p align="center">
    <img src="https://i.imgur.com/VQbD1ky.png" alt="Notion Database Web View">
</p>

## 🚀Initialization

```python3
from pynotiondb import NOTION_API
mydb = NOTION_API("API_SECRET", "DATABASE_ID")
```

## <a id="insert"></a>➕ `INSERT` Statement

#### <a id="single-row-insertion"></a>➡️ Single-Row Insertion

To insert a single row into the table:

```python3
sql = "INSERT INTO customers (name, address) VALUES (%s, %s)"
val = ("John", "Highway 21")
mydb.execute(sql, val)
```

#### <a id="multiple-row-insertion"></a>➡️ Multiple-Row Insertion

To insert a single row into the table:

```python3
sql = "INSERT INTO customers (name, address) VALUES (%s, %s)"
val = [
    ("John", "Highway 21"),
    ("Lilly", "Road 99"),
]
mydb.execute(sql, val)

```

## <a id="select"></a>🔎 `SELECT` Statement

#### <a id="default-retrieval-with-all-columns"></a>➡️ Default Retrieval with All Columns

To fetch data from the database with all columns and a default page size of 20:

```python3
sql = "SELECT * FROM customers"
data = mydb.execute(sql)
```

- This query retrieves all rows and columns from the customers table.
- The default page size is set to 20 rows.

- Returned data includes all columns such as `name`, `address`, and `salary`.

```json
{
  "data": [
    {
      "address": "Highway 21",
      "salary": 1000,
      "name": "John"
    },
    {
      "address": "Highway 21",
      "salary": 2000,
      "name": "John"
    }
  ],
  "next_cursor": null,
  "previous_cursor": null,
  "has_more": false
}
```

#### <a id="retrieval-with-specified-columns"></a>➡️ Retrieval with Specified Columns

To fetch data with specific columns:

```python3
sql = "SELECT name, address FROM customers"
data = mydb.execute(sql)

```

- This query retrieves only the `name` and `address` columns from the customers table.

- The default page size is set to 20 rows.

```json
{
  "data": [
    {
      "address": "Highway 21",
      "name": "John"
    },
    {
      "address": "Highway 21",
      "name": "John"
    }
  ],
  "next_cursor": null,
  "previous_cursor": null,
  "has_more": false
}
```

#### <a id="retrieval-with-specified-columns-and-custom-page-size"></a>➡️ Retrieval with Specified Columns and Custom Page Size

To fetch data with specific columns:

```python3
sql = "SELECT name, address FROM customers WHERE page_size = 1"
data = mydb.execute(sql)
```

```python3
sql = "SELECT * FROM customers WHERE page_size = 1"
data = mydb.execute(sql)
```

- This query retrieves only the `name` and `address` columns from the customers table.
- Adding `*` will select all the colums

- The page_size parameter allows customization of the number of rows returned per page.

```json
{
  "data": [
    {
      "name": "John",
      "address": "Highway 21"
    }
  ],
  "next_cursor": "7184fff3-8859-45a1-863b-ab5c0d403a45",
  "previous_cursor": null,
  "has_more": true
}
```

#### <a id="applying-conditions"></a>➡️ Applying Conditions

To apply conditions for data retrieval, such as filtering based on numeric values:

```python3
sql = "SELECT * FROM customers WHERE salary > 1000"
data = mydb.execute(sql)

```

- This query retrieves all columns from the customers table where the `salary` is greater than 1000.

- Only numeric columns can be used for numerical comparisons.

- Make sure the property you are applying conditions for has a Number type in the Notion Database

```json
{
  "data": [
    {
      "address": "Highway 21",
      "salary": 1291029102910219,
      "name": "John"
    },
    {
      "address": "Some Road",
      "salary": 10000000,
      "name": "Aditya"
    }
  ],
  "next_cursor": null,
  "previous_cursor": null,
  "has_more": false
}
```

#### <a id="applying-conditions-2"></a>➡️ Applying Conditions (2)

To apply conditions for data retrieval, such as filtering based on numeric values:

```python3
sql = "SELECT * FROM customers WHERE salary > 1000 AND name = 'John' and page_size = 10"
data = mydb.execute(sql)

```

- This query retrieves all columns from the customers table where the `salary` is greater than 1000 and name which is John and page_size of 10.

- Only numeric columns can be used for numerical comparisons.

- Make sure the property you are applying conditions for has a Number type in the Notion Database

```json
{
  "data": [
    {
      "address": "Highway 21",
      "salary": 1291029102910219,
      "name": "John"
    },
    {
      "address": "Some Road",
      "salary": 10000000,
      "name": "Aditya"
    }
  ],
  "next_cursor": null,
  "previous_cursor": null,
  "has_more": false
}
```

## <a id="update"></a>⚡ `UPDATE` Statement

#### <a id="updating-a-row"></a>➡️ Updating a Row

To update a single row into the table:

```python3
sql = "UPDATE customers SET salary = 20000 WHERE name = Rachel Adams"
sql = "UPDATE customers SET salary = 20000 WHERE name = 'Rachel Adams'"
mydb.execute(sql)
```

- This query will update the salary to 20000 for the row with the name 'Rachel Adams'.
- Using single quotes around the name is recommended, especially if the value contains spaces or special characters.

## <a id="delete"></a>➕ `DELETE` Statement

#### <a id="single-row-deletion"></a>➡️ Single-Row Deletion

To delete a single row into the table:

```python3
sql = "DELETE FROM customers WHERE salary < 110"
mydb.execute(sql)
```

## 🌟 Show Your Support

- If you find this project useful or interesting, please consider giving it a star on GitHub. It's a simple way to show your support and help others discover the project.

![Github Stars](https://img.shields.io/github/stars/aditya76-git/pynotiondb?style=social "Github Stars")

## 👨‍💻Developement

Thank you for your interest in contributing to this project! There are several ways you can get involved:

- **Opening Issues**: If you encounter a bug, have a feature request, or want to suggest an improvement, please open an issue. We appreciate your feedback!
- **Cloning the Project**: To work on the project locally, you can clone the repository by running:

```bash
git clone https://github.com/aditya76-git/pynotiondb.git
```

- **Sending Pull Requests**: If you'd like to contribute directly to the codebase, you can fork the repository, make your changes, and then send a pull request. We welcome your contributions!

## 💻Authors

- Copyright © 2024 - [aditya76-git](https://github.com/aditya76-git) / [pynotiondb](https://github.com/aditya76-git/pynotiondb)
