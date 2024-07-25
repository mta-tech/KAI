from configs import Config

from api.dto.dataherald.base_class import BaseNLGeneration
from api.dto.dataherald.nl_generation import NLGenerationFromSQL, NLGenerationFromPrompt, NLGenerationID
from api.dto.dataherald.prompt import PromptID
from api.dto.dataherald.sql_generation import SQLGenerationID

from .utils import mta_request


class NLGeneration():
    def __init__(self):
        self.api_host = Config().DataHeraldConf.HOST


    def create_nl_generation(self, data:BaseNLGeneration, params:SQLGenerationID):
        """Create a NL generation."""

        url = f"{self.api_host}/sql-generations/{params.sql_generation_id}/nl-generations"
        
        data = data.model_dump_json()

        params = params.model_dump_json()
        
        response = mta_request(method="POST", url=url, data=data, params=params)
        
        return response

    
    def create_sql_nl_generation(self, data:NLGenerationFromSQL, params:PromptID):
        """Create a SQL NL generation."""

        url = f"{self.api_host}/prompts/{params.prompt_id}/sql-generations/nl-generations"
        
        data = data.model_dump_json()

        params = params.model_dump_json()

        response = mta_request(method="POST", url=url, data=data, params=params)

        return response
    

    def create_prompt_sql_nl_generation(self, data:NLGenerationFromPrompt):
        """Create a prompt SQL NL generation."""

        url = f"{self.api_host}/prompts/sql-generations/nl-generations"
        
        data = data.model_dump_json()

        response = mta_request(method="POST", url=url, data=data)
        
        return response


    def list_nl_generations(self, params:SQLGenerationID):
        """List all NL generations."""

        url = f"{self.api_host}/nl-generations"

        params = params.model_dump_json()

        response = mta_request(method="GET", url=url, params=params)

        return response


    def get_nl_generation(self, params:NLGenerationID):
        """Get a specific NL generation."""
        
        url = f"{self.api_host}/nl-generations/{params.nl_generation_id}"

        params = params.model_dump_json()

        response = mta_request(method="GET", url=url, params=params)

        return response
    

    def update_nl_generation(self, params:NLGenerationID):
        """Update a NL generation."""
        
        url = f"{self.api_host}/nl-generations/{params.nl_generation_id}"

        params = params.model_dump_json()

        response = mta_request(method="PUT", url=url, params=params)

        return response