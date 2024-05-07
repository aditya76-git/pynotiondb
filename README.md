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

<!-- <img src="https://i.imgur.com/y3L6XfN.png" align="right" /> -->

# pynotiondb

`pynotiondb` is a Python package that provides a convenient way to interact with Notion databases using SQL-style syntax.

## 📋Details

- ➕ [Insert Statement](#insert)

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

To utilize this package, you'll initially need to create a database or table within Notion. Customize the table headers to align with your requirements; for instance, if you're managing customer data, you'd include headers such as "Name" and "Address" as needed.

When adding a new table header in the database, ensure to select "Text" from the Type dropdown menu. This selection ensures that the data is stored as text, which is compatible with the package's functionality for retrieving rows. Avoid selecting any other options from the dropdown menu.

As of now, the `pynotiondb` package only supports INSERT statements. It does not offer functionalities to create tables or add table headers directly from the package itself. Therefore, users must manually create the tables with appropriate headers in Notion before using the package.

Additional statements will be implemented in future updates of the package.

## 🚀Initialization

```python3
from pynotiondb import NOTION_API
mydb = NOTION_API("API_SECRET", "DATABASE_ID")
```

## <a id="insert"></a>➡️ Insert Statement

To insert a new row to the table

```python3
sql = "INSERT INTO customers (name, address) VALUES (%s, %s)"
val = ("John", "Highway 21")
mydb.execute(sql, val)
```

## <a id="insert"></a>➡️ Insert Statement v2

To insert multiple rows to the table

```python3
sql = "INSERT INTO customers (name, address) VALUES (%s, %s)"
val = [
    ("John", "Highway 21"),
    ("Lilly", "Road 99"),
    ]
mydb.execute(sql, val)
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
