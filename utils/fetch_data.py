from mysql.connector import connection

from typing import Union


def fetch_data(query: str, params: dict, as_dict: bool = False) -> list[Union[dict, tuple]]:
    con = connection.MySQLConnection(
        auth_plugin="mysql_native_password",
        **params  # extracts dict: {"database": "dbname", "host": "1.2.3.4", "user": "user": "password": "mypassword"}
    )

    cursor = con.cursor(dictionary=True) if as_dict else con.cursor()

    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    con.close()

    return result