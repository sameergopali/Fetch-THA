import psycopg2
from psycopg2 import extras
from datetime import datetime
from loguru import logger

class PostgresClient:
    def __init__(self, host, database, user, password,port):
        
        '''
        Initialize the PostgresClient with the necessary connection details.

        :param host: The hostname of the PostgreSQL server
        :param database: The name of the database to connect to
        :param user: The username used to authenticate
        :param password: The password used to authenticate
        :param port: The port number on which the PostgreSQL server is listening
        '''
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
        self.port = port
        
    def connect(self):
        '''
        Establish a connection to the PostgreSQL database.
        '''
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port= self.port
            )
            logger.info("Connection to PostgreSQL DB successful")
        except Exception as err:
            logger.error("Error connecting to PostgreSQL DB: {}", err)

    def disconnect(self):
        '''
        Close the connection to the PostgreSQL database.
        '''
        if self.connection:
            self.connection.close()
            logger.info("PostgreSQL connection closed")

    def rollback(self):
        '''
        Rollback the transaction
        '''
        logger.info("Rolling back transaction")
        try:
            self.connection.rollback()
        except Exception as err:
            logger.error("Error while rollingback {}",err)
            
        
    def commit(self):
        '''
        Commit the transaction
        '''
        logger.info('Commiting transaction')
        try :
            self.connection.commit()
        except Exception as err:
            logger.error("Error while commiting transaction {}",err)

    def insert_masked_records(self, messages):
        '''
        Insert in batch a list of masked records into the user_logins table.
        Rolls back the transaction if an error occurs.

        :param messages: List of tuples containing masked record data
        :return: True if the insertion is successful, False otherwise
        '''
        
        insert_query = '''
            INSERT INTO user_logins (user_id, device_type, masked_ip, 
            masked_device_id, locale, app_version, create_date)
            VALUES %s;
            '''
        try:
            cursor = self.connection.cursor()
            extras.execute_values(cursor,insert_query, messages)
            logger.info("Data inserted successfully: {}", len(messages))
            return True
        except Exception as err:
            self.rollback()
            logger.error("Error inserting data: {}", err)
            return False
        finally:
            cursor.close()

