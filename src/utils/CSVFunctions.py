import csv
import pandas as pd

from NBAScrapper.src.utils import DataBase


def create_csv(csv_name: str, variables: list[str]):
    """Create a CSV file with variables"""
    with open('../csv/' + csv_name + '.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(variables)


def write_csv(csv_name: str, text: any):
    """Write lines in the CSV file"""
    with open('../csv/' + csv_name + '.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(text)


def create_csv_query(csv_name: str, variables: list[str], query: str):
    """Create a CSV file with variables and data with the query"""
    my_conn = DataBase.open_connection()
    my_conn.cursor.execute(query)
    query_result = my_conn.cursor.fetchall()
    DataBase.close_connection(my_conn)

    with open('../csv/' + csv_name + '.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(variables)
        writer.writerows(query_result)


def read_csv(csv_name: str):
    """Return the dataframe from CSV file"""
    return pd.read_csv('../csv/' + csv_name + '.csv', sep=",")
        