from typing import List, Optional
from pydantic import BaseModel
from configs import Config


class BaseSSHSettings(BaseModel):
    host: str
    username: str
    password: str
    port: int = 22
    private_key_password: str


class BaseFileStorage(BaseModel):
    name: str
    access_key_id: str
    secret_access_key: str
    region: str
    bucket: str


class BaseDatabaseConnection(BaseModel):
    alias: str
    use_ssh: Optional[bool] = False
    connection_uri: str
    schemas: Optional[list[str]] = []
    path_to_credentials_file: Optional[str] = None
    llm_api_key: Optional[str] = None
    ssh_settings: Optional[BaseSSHSettings] = None
    file_storage: Optional[BaseFileStorage] = None
    metadata: Optional[dict] = {}


class BaseForeignKey(BaseModel):
    field_name: str
    reference_table: str


class BaseColumn(BaseModel):
    name: str
    description: Optional[str] = None
    is_primary_key: bool
    data_type: str 
    low_cardinality: Optional[bool] = True
    categories: Optional[list] = None
    foreign_key: Optional[BaseForeignKey] = None


class BaseTableDescription(BaseModel):
    description: str
    columns: List[BaseColumn]
    metadata: Optional[dict]


class BaseLLMConfig(BaseModel):
    llm_name: Optional[str] = Config().DataHeraldConf.LLM_NAME
    api_base: Optional[str] = None


class BasePrompt(BaseModel):
    text: str
    db_connection_id: str
    schemas: Optional[List[str]] = []
    metadata: Optional[dict] = {}


class BaseInstruction(BaseModel):
    db_connection_id: str
    instruction: str
    metadata: Optional[dict] = {}


class BaseGoldenSQL(BaseModel):
    db_connection_id: str
    prompt_text: str
    sql: str
    metadata: Optional[dict] = {}


class BaseSQLGeneration(BaseModel):
    finetuning_id: Optional[str] = ""
    low_latency_mode: Optional[bool] = False
    llm_config: BaseLLMConfig
    evaluate: Optional[bool] = False
    metadata: Optional[dict] = {}


class BaseNLGeneration(BaseModel):
    llm_config: BaseLLMConfig
    max_rows: Optional[int] = 100
    metadata: Optional[dict] = {}