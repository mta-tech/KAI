from configs import Config
from api.dto.dataherald.base_class import BaseSQLGeneration
from api.dto.dataherald.prompt import PromptID
from api.dto.dataherald.sql_generation import SQLGenerationExecute, SQLGenerationID, SQLGenerationPrompt
from .utils import mta_request
import json

class SQLGeneration():
    def __init__(self):
        self.api_host = Config().DataHeraldConf.HOST


    def create_sql_generation_for_prompt(self, data:BaseSQLGeneration, params:PromptID, es_sql:str = None):
        """Create SQL generation for a prompt."""
        
        url = f"{self.api_host}/prompts/{params.prompt_id}/sql-generations"

        # Add the SQL string to the dictionary
        data_dict = data.model_dump()
        if es_sql is not None:
            data_dict['sql'] = es_sql

        # Convert the modified dictionary to JSON
        data = json.dumps(data_dict)

        params = params.model_dump_json()

        response = mta_request(method="POST", url=url, data=data, params=params)
        
        return response


    def create_sql_generation(self, data:SQLGenerationPrompt):
        """Create SQL generation."""
        
        url = f"{self.api_host}/prompts/sql-generations"

        data = data.model_dump_json()

        response = mta_request(method="POST", url=url, data=data)
        
        return response


    def list_sql_generations(self):
        """List all SQL generations."""
        
        url = f"{self.api_host}/sql-generations"

        response = mta_request(method="GET", url=url)
        
        return response


    def get_sql_generations_from_prompt(self, params:PromptID):
        """Get SQL generations from a prompt."""
        
        url = f"{self.api_host}/sql-generations"

        params = params.model_dump_json()

        response = mta_request(method="GET", url=url, params=params)
        
        return response


    def get_sql_generation(self, params:SQLGenerationID):
        """Get a specific SQL generation."""
        
        url = f"{self.api_host}/sql-generations/{params.sql_generation_id}"
        
        params = params.model_dump_json()
        
        response = mta_request(method="GET", url=url, params=params) 
        
        return response
    

    def update_sql_generation(self, params:SQLGenerationID):
        """Update a SQL generation."""
        
        url = f"{self.api_host}/sql-generations/{params.sql_generation_id}"
        
        params = params.model_dump_json()
        
        response = mta_request(method="PUT", url=url, params=params) 
        
        return response


    def sql_generation_execute(self, data:SQLGenerationID, params:SQLGenerationExecute):
        """Execute a SQL generation."""
        
        url = f"{self.api_host}/sql-generations/{data.sql_generation_id}/execute"
        
        data = data.model_dump_json()

        params = params.model_dump_json()

        response = mta_request(method="GET", url=url, params=params) 
        
        return response


    def sql_generation_to_csv(self, params:SQLGenerationID):
        """Convert SQL generation to CSV."""
        
        url = f"{self.api_host}/sql-generations/{params.sql_generation_id}/csv-file"

        params = params.model_dump_json()

        response = mta_request(method="GET", url=url, params=params) 
        
        return response

