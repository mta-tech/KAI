from api.dto.dataherald.base_class import BaseInstruction
from api.dto.dataherald.instruction import InstructionList, InstructionID
from configs import Config
from .utils import mta_request


class Instruction():
    def __init__(self):
        self.api_host = Config().DataHeraldConf.HOST
    

    def list_instructions(self, params:InstructionList):
        """List all instructions."""

        url = f"{self.api_host}/instructions"

        params = params.model_dump_json()

        response = mta_request(method="GET", url=url, params=params)
        
        return response


    def create_instruction(self, data:BaseInstruction):
        """Create a new instruction."""

        url = f"{self.api_host}/instructions"

        data = data.model_dump_json()

        response = mta_request(method="POST", url=url, data=data)

        return response


    def update_instruction(self, data:BaseInstruction, params:InstructionID):
        """Update an existing instruction."""

        url = f"{self.api_host}/instructions/{params.instruction_id}"

        data = data.model_dump_json()
        
        params = params.model_dump_json()

        response = mta_request(method="PUT", url=url, data=data, params=params) 
        
        return response
    

    def delete_instruction(self, params:InstructionID):
        """Delete an instruction."""

        url = f"{self.api_host}/instructions/{params.instruction_id}"

        params = params.model_dump_json()

        response = mta_request(method="DELETE", url=url, params=params) 
        
        return response