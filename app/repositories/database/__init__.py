
from abc import abstractmethod
import typesense


class DB():
    @abstractmethod
    def __init__(self):
        pass


    @staticmethod
    def init_client(api_key, host='localhost', port='8108', protocol='http', timeout=2):
        client = typesense.Client({
            'nodes': [{
                'host': host,  
                'port': port,  
                'protocol': protocol 
            }],
            'api_key': api_key,
            'connection_timeout_seconds': timeout
        })
        return client