from configs import Config
from api.dto.dataherald.base_class import BaseGoldenSQL
from api.dto.dataherald.golden_sql import GoldenSQLID, GoldenSQLList
from .utils import mta_request


class GoldenSQL():
    def __init__(self):
        self.api_host = Config().DataHeraldConf.HOST
    

    def list_golden_sqls(self, params:GoldenSQLList):
        """ List all golden SQLs available. """
        
        url = f"{self.api_host}/golden-sqls"

        params = params.model_dump_json()

        response = mta_request(method="GET", url=url, params=params)
        
        return response


    def create_golden_sql(self, data:BaseGoldenSQL):
        """ Adds a new golden SQL. """

        url = f"{self.api_host}/golden-sqls"

        data = data.model_dump_json()

        response = mta_request(method="POST", url=url, data=data)

        return response


    def update_golden_sql(self, data:BaseGoldenSQL, params:GoldenSQLID):
        """ Update a golden SQL identified by the given ID. """

        url = f"{self.api_host}/golden-sqls/{params.instruction_id}"

        data = data.model_dump_json()
        
        params = params.model_dump_json()

        response = mta_request(method="PUT", url=url, data=data, params=params) 
        
        return response
    

    def delete_golden_sql(self, params:GoldenSQLID):
        """ Delete a golden SQL identified by the given ID. """

        url = f"{self.api_host}/golden-sqls/{params.instruction_id}"

        params = params.model_dump_json()

        response = mta_request(method="DELETE", url=url, params=params) 
        
        return response