from configs import Config
from api.dto.dataherald.base_class import BaseTableDescription
from api.dto.dataherald.table_description import TableDescriptionScan, TableDescriptionID, TableDescriptionList
from .utils import mta_request
import json

class TableDescription():
    def __init__(self):
        self.api_host = Config().DataHeraldConf.HOST

    def scan_tables(self, data:TableDescriptionScan):
        """ Scans and synchronizes table descriptions with the provided database connection. """
        
        url = f"{self.api_host}/table-descriptions/sync-schemas"

        data = data.model_dump_json()
        
        response = mta_request(method="POST", url=url, data=data)
        
        return response


    def refresh_table_description(self, data:TableDescriptionID):
        """ Refreshes the descriptions of tables associated with the provided database connection. """
        
        url = f"{self.api_host}/table-descriptions/refresh"
        
        data = data.model_dump_json()

        response = mta_request(method="POST", url=url, data=data)

        return response
    
    
    def get_table_description(self, params:TableDescriptionID):
        """ Retrieves the description of a table with the specified ID. """

        url = f"{self.api_host}/table-descriptions/{params.table_decription_id}"
        
        params = params.model_dump_json()
        
        response = mta_request(method="GET", url=url, params=params)

        return response


    def update_table_description(self, data:BaseTableDescription, params:TableDescriptionID):
        """ Updates the description of a table with the specified ID. """

        url = f"{self.api_host}//table-descriptions/{params.table_decription_id}"

        data = data.model_dump_json()

        params = params.model_dump_json()

        response = mta_request(method="PUT", url=url, data=data, params=params)
        
        return response


    def list_table_description(self, params:TableDescriptionList):
        """ Lists the description of a specific table associated with the provided database connection. """
        
        url = f"{self.api_host}/table-descriptions"
        
        response = mta_request(method="GET", url=url, params=params)

        return response