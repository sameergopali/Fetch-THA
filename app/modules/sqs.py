import boto3
from loguru import logger

class SqsClient:
    '''Client class to manage interactions with Amazon SQS.'''
    
    def __init__(self, endpoint_url,region_name='us-east-1'):
        '''
        Initialize the SqsClient with the necessary connection details.

        :param endpoint_url: The endpoint URL of the SQS service
        :param region_name: The region name for the SQS service, defaults to 'us-east-1'
        '''
        self.region_name = region_name
        self.sqs = None
        self.endpoint_url =  endpoint_url

    def connect(self):
        '''
        Establish a connection to the Amazon SQS service.
        '''
        try:
            self.sqs = boto3.client('sqs', endpoint_url = self.endpoint_url,region_name=self.region_name)
            logger.info('Connected to SQS')
        except Exception as err:
            logger.error('Error connecting to SQS: {}',err)

    def disconnect(self):
        '''
        Disconnect from the Amazon SQS service.
        '''
        self.sqs = None
        logger.info('Disconnected from SQS')

    def fetch(self, queue_url, max_messages=10):
        '''
        Fetch messages from the specified SQS queue.

        :param queue_url: The URL of the SQS queue
        :param max_messages: The maximum number of messages to retrieve, defaults to 10
        :return: A list of messages fetched from the queue
        '''

        try:
            response = self.sqs.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=max_messages, # Batch size
                VisibilityTimeout=30             # Visibility timeout for processing messages
            )
            messages = response.get('Messages', [])
            return messages
        except Exception as err:
            logger.error("Error fetching messages from SQS: {}",err)
            return []

    def delete_message(self,queue_url,receipt_handle):
        '''
        Delete messages from the specified SQS queue using their receipt handles.

        :param queue_url: The URL of the SQS queue
        :param receipt_handle: A list of receipt handles for the messages to be deleted
        '''
        try:
            self.sqs.delete_message_batch(
                QueueUrl=queue_url,
                Entries=receipt_handle
            )
            logger.info("Message deleted successfully: {}", len(receipt_handle))
        except Exception as err:
            logger.info("Error deleting message from SQS: {}",err)