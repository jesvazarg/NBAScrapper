import mysql.connector
import time

from mysql import connector
from mysql.connector import cursor, errorcode

from NBAScrapper.src.utils import Log

RECONNECTION_WAITING_TIME = 60  # Seconds
RECONNECTION_ATTEMPTS = 5
USER = 'admin'
PASSWORD = 'nba-pred-tfg'
HOST = 'nba.cjpc8inv461q.eu-west-3.rds.amazonaws.com'
DB_PROD_NAME = "nba"
DB_TEST_NAME = "test"


class Connection:
    cnx: connector = mysql.connector
    cursor: cursor = mysql.connector.cursor


def get_db_name():
    """Choose the database: PROD or TEST"""
    # return DB_TEST_NAME
    return DB_PROD_NAME


def open_connection() -> Connection:
    """Open the connection with the database"""
    is_error = True  # Start true to execute first time
    attempts = 0
    connect = Connection()

    while is_error is True:
        try:
            connect.cnx = mysql.connector.connect(user=USER, password=PASSWORD, host=HOST, database=get_db_name())
            connect.cursor = connect.cnx.cursor(buffered=True)
            is_error = False
        except mysql.connector.Error as error:
            is_error = True
            Log.log_error("connection_error", str(error))
            if attempts < RECONNECTION_ATTEMPTS:
                attempts += 1
                reconnection_waiting_time()
                pass
            else:
                raise

    return connect


def execute(connection: Connection, query: str, data: tuple = None):
    """Execute the query operation with the data requirements.
    data is optional """
    my_cursor = connection.cursor
    is_error = True  # Start true to execute first time
    attempts = 0

    while is_error is True:
        try:
            if data is None:
                my_cursor.execute(query)
            else:
                my_cursor.execute(query, data)
            is_error = False
        except mysql.connector.Error as error:
            is_error = True
            Log.log_error("connection_error", str(error) + "\n\tQUERY: " + query + "\n\tDATA: " + str(data))
            if attempts < RECONNECTION_ATTEMPTS:
                attempts += 1
                reconnection_waiting_time()
                pass
            else:
                if error.errno == errorcode.CR_SERVER_LOST:
                    Log.log_error("connection_error", "Trying reconnecting with the database")
                    connection.reconnect(attempts=RECONNECTION_ATTEMPTS, delay=RECONNECTION_WAITING_TIME)
                raise


def commit(connect: Connection):
    """Do a commit with the changes into database"""
    is_error = True  # Start true to execute first time
    attempts = 0

    while is_error is True:
        try:
            connect.cnx.commit()
            is_error = False
        except mysql.connector.Error as error:
            is_error = True
            Log.log_error("connection_error", str(error))
            if attempts < RECONNECTION_ATTEMPTS:
                attempts += 1
                reconnection_waiting_time()
                pass
            else:
                raise


def close_connection(connect: Connection):
    """Close the connection with the database"""
    is_error = True  # Start true to execute first time
    attempts = 0

    while is_error is True:
        try:
            connect.cursor.close()
            connect.cnx.close()
            is_error = False
        except mysql.connector.Error as error:
            is_error = True
            Log.log_error("connection_error", str(error))
            if attempts < RECONNECTION_ATTEMPTS:
                attempts += 1
                reconnection_waiting_time()
                pass
            else:
                raise


def reconnection_waiting_time():
    """Set a waiting time to reconnect with the database"""
    time.sleep(RECONNECTION_WAITING_TIME)
