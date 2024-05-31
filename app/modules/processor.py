import json 
from datetime import datetime
import hashlib
from loguru import logger



class Processor:
    """Processor class to handle masking and processing of message data."""

    def __init__(self, masked_fields=['user_id','ip']):
        """
        Initialize the Processor with fields to be masked.
        
        :param masked_fields: List of field names to be masked, defaults to ["user_id", "ip"]
        """
        self.masked_fields = masked_fields
    
    def __mask(self,data):
        """
        Mask the specified fields in the data dictionary.
        The fields are masked using sha256 hashing algorithm. But there are 
        options of encryption, base64 encoding, that can making masking reversible. 


        :param data: The data dictionary containing fields to be masked
        """
        for field in self.masked_fields:
            if field in data:
                data[field] = self.__hash(data[field])
    
    def __hash(self,data):
        '''
        Hash the data using the SHA-256 algorithm.

        :param data: The data to be hashed
        :return: The hashed data as a hexadecimal string
        '''
        hashed_data = hashlib.sha256(data.encode()).hexdigest()
        return hashed_data
    
    def __encrpt(self,data):
        '''
        Todo
        Implement method to encrypt data
        '''
        pass
    
    def __encode(self,data):
        '''
        Todo
        Encode data using base64 encoding or other encoding algorithms
        '''
        pass
        
    def process_messages(self,messages):
        '''
        Process a list of messages by masking specific fields and preparing 
        records for insertion.Use hashing to mask out the user_id and ip 
        field.The requried field are validated through try catch block.
        
        Next Steps: 
        Proper validation of fields and data could be abstractd and could 
        be introduced in the next steps.
        
        
        :param messages: List of messages to be processed
        :return: A tuple containing the receipt handles for deletion and the processed records
        '''
        receipt_handles= []
        records =[ ]
        error_handles= []
        try:
            print("Processing mesages",len(messages))
            for idx, message in enumerate(messages):
                try:
                    data = json.loads(message['Body'])
                    self.__mask(data)
                    record = (
                                data['user_id'], 
                                data['device_type'], 
                                data['ip'], 
                                data["device_id"], 
                                data["locale"], 
                                data["app_version"].replace(".", ""),  # Removing periods from app version
                                str(datetime.today().isoformat()))
                          
                    receipt_handles.append({"Id":str(idx),"ReceiptHandle":message['ReceiptHandle']})
                    records.append(record)
                except KeyError as kerr:
                    logger.error("KeyError: {} at index: {}, message: {}", kerr, idx, message)
                    error_handles.append({"Id":str(idx),"ReceiptHandle":message['ReceiptHandle']})
                except Exception as err:
                    logger.error("Processing error: {} at index: {}, message: {}", err, idx, message)
                    
            return receipt_handles, error_handles,records
        except Exception as err:
            logger.error("Error handling message: {}", err)