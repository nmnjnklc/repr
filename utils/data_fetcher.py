from mysql.connector import connection

from typing import Union


def fetch_data(
    query: str,
    params: dict,
    as_dict: bool = False
) -> list[Union[dict, tuple]]:

    con = connection.MySQLConnection(
        **params
        # unpacks params dict, example:
        # {"database": "dbname", "host": "1.2.3.4", "user": "username", "password": "password", "auth_plugin": "mysql_native_password"}
    )

    cursor = con.cursor(dictionary=as_dict)

    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    con.close()

    return result
