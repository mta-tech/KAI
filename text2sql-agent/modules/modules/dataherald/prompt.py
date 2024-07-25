from configs import Config
from api.dto.dataherald.base_class import BasePrompt
from api.dto.dataherald.database_connection import DBConnectionID
from api.dto.dataherald.prompt import PromptID
from .utils import mta_request

class Prompt():
    def __init__(self):
        self.api_host = Config().DataHeraldConf.HOST


    def list_prompts(self, params:DBConnectionID):
        """ Lists all prompts associated with the provided database connection. """

        url = f"{self.api_host}/prompts"

        params = params.model_dump_json()

        response = mta_request(method="GET", url=url, params=params)
        
        return response
    

    def create_prompt(self, data:BasePrompt):
        """ Creates a new prompt with the provided data. """

        url = f"{self.api_host}/prompts"

        data = data.model_dump_json()

        response = mta_request(method="POST", url=url, data=data)

        return response
    

    def get_prompt(self, params:PromptID):
        """ Retrieves the prompt with the specified ID. """

        url = f"{self.api_host}/prompts/{params.prompt_id}"

        params = params.model_dump_json()

        response = mta_request(method="GET", url=url, params=params)
        
        return response


    def update_prompt(self, params:PromptID):
        """ Updates the prompt with the specified ID. """

        url = f"{self.api_host}/prompts/{params.prompt_id}"

        params = params.model_dump_json()

        response = mta_request(method="PUT", url=url, params=params)
        
        return response
