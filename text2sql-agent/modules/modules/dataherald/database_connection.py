from api.dto.dataherald.base_class import BaseDatabaseConnection
from api.dto.dataherald.database_connection import DBConnectionID
from configs import Config
from .utils import mta_request


class DBConnection():
    def __init__(self):
        self.api_host = Config().DataHeraldConf.HOST

    def list_database_connections(self):                                                                                                                                                                                                                                                                                                                                                                                                                                                                             
        """ List all database connections available. """
        
        url = f"{self.api_host}/database-connections"
        
        response = mta_request(method="GET", url=url)
        
        return response


    def create_database_connection(self, data:BaseDatabaseConnection):
        """ Adds a new connection to a database using the provided alias and connection URI. """

        url = f"{self.api_host}/database-connections"
        
        data = data.model_dump_json()
        
        response = mta_request(method="POST", url=url, data=data)

        return response


    def update_database_connection(self, data:BaseDatabaseConnection, param:DBConnectionID):
        """ Update a database connection identified by the given ID. """
        
        url = f"{self.api_host}/database-connections/{param.db_connection_id}"
        
        data = data.model_dump_json()

        response = mta_request(method="PUT", url=url, data=data)
        
        return response
