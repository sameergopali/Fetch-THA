from modules import PostgresClient
from modules import SqsClient
from modules import Processor
from dotenv import load_dotenv
import os
from loguru import logger


class App:
    '''
    Main application class to process messages from SQS and store them in PostgreSQL.
    '''

  
    def __init__(self,config):
        '''
        Initialize the App with the given configuration.

        :param config: Dictionary containing configuration parameters
        '''
        # Initialize to postgres client
        self.pg_client = PostgresClient(
            host=config['db_host'],
            port=config['db_port'],
            database=config['db_name'],
            user=config['db_user'],
            password=config['db_password'])
        
        self.pg_client.connect()

        # Initialize sqs client
        self.sqs_client = SqsClient(endpoint_url=config['sqs_endpoint_url'])
        self.sqs_client.connect()
        self.processor =  Processor()
        
        # Set logger level
        logger.level(config['log_level'])
        
        
    def run(self):
        '''
        Main loop to fetch, process, and store messages from the SQS queue.
        '''
        while True:
            try:
                # Fetch messages in batch size of 10 from SQS
                messages = self.sqs_client.fetch(config['sqs_queue_url'])
                logger.info('Fetched {} messages from SQS', len(messages))

                
                
                if not messages:
                    logger.info('No messages found in the queue')
                    break
                
                # Mask the field from the messages
                receipt_handles, error_handles, records =  self.processor.process_messages(messages)

                # Batch Insert records into db
                if records:
                    status = self.pg_client.insert_masked_records(records)
                    if not status:
                        logger.warning("Failed to insert records into the database")
                        continue
                    
                # Delete the message from the queue after processing
                if receipt_handles:
                    logger.info("Deleting processed messages from the SQS queue")
                    self.sqs_client.delete_message(config['sqs_queue_url'], receipt_handles)
                if error_handles:
                    logger.info("Deleting messages that is not correct format from the SQS queue")
                    self.sqs_client.delete_message(config['sqs_queue_url'], error_handles)
                    
                self.pg_client.commit()
                
            except Exception as err:
                self.pg_client.rollback()
                logger.error("An error occurred while processing messages: {}", err)

        # Disconnect from PostgreSQL
        self.pg_client.disconnect()
        # Disconnect from SQS
        self.sqs_client.disconnect()

if __name__ == "__main__":
    
    # Load db creditials from environment variables
    load_dotenv()
    
    # Next Steps: configuration could be abstracted and use config file
    config ={
        'db_host': os.getenv('DB_HOST'),
        'db_name': os.getenv('DB_NAME'),
        'db_user': os.getenv('DB_USER'),
        'db_password': os.getenv('DB_PASSWORD'),
        'db_port':os.getenv('DB_PORT'),
        'sqs_endpoint_url': 'http://localhost:4566',
        'sqs_queue_url': 'http://localhost:4566/000000000000/login-queue',
        'log_level':"INFO"
    }
    app = App(config)
    app.run()
