from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field

class SQLAgentState(BaseModel):
    """State schema for the SQL Agent graph."""
    
    # Input state
    question: str
    db_connection_id: str
    prompt_id: str
    dialect: str
    
    # Context state
    db_scan: List[Dict[str, Any]] = Field(default_factory=list)
    few_shot_examples: Optional[List[Dict[str, Any]]] = None
    instructions: Optional[List[Dict[str, Any]]] = None
    business_metrics: Optional[List[Dict[str, Any]]] = None
    aliases: Optional[List[Dict[str, Any]]] = None
    
    # Processing state
    relevant_tables: List[Dict[str, Any]] = Field(default_factory=list)
    table_schemas: Dict[str, Any] = Field(default_factory=dict)
    relevant_columns: Dict[str, Any] = Field(default_factory=dict)
    
    # Output state
    generated_sql: Optional[str] = None
    execution_result: Optional[str] = None
    error: Optional[str] = None
    status: str = "PENDING"  # PENDING, VALID, INVALID
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=lambda: str(datetime.now()))
    completed_at: Optional[str] = None
    input_tokens_used: int = 0
    output_tokens_used: int = 0
    
    # Tracking
    iteration_count: int = 0
    max_iterations: int = 3
