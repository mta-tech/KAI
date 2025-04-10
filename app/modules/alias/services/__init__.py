import logging
from datetime import datetime
from fastapi import HTTPException

from app.api.requests import (
    AliasRequest,
    UpdateAliasRequest,
)
from app.modules.alias.models import Alias
from app.modules.alias.repositories import AliasRepository

logger = logging.getLogger(__name__)


class AliasService:
    def __init__(self, storage):
        self.storage = storage
        self.repository = AliasRepository(self.storage)

    def create_alias(self, alias_request: AliasRequest) -> Alias:
        # Check if alias with the same name already exists
        existing_alias = self.repository.find_by_name(alias_request.name)
        if existing_alias:
            raise HTTPException(
                status_code=400,
                detail=f"Alias with name '{alias_request.name}' already exists",
            )

        alias = Alias(
            db_connection_id=alias_request.db_connection_id,
            name=alias_request.name,
            target_name=alias_request.target_name,
            target_type=alias_request.target_type,
            description=alias_request.description,
            metadata=alias_request.metadata,
        )
        return self.repository.insert(alias)

    def get_alias(self, alias_id: str) -> Alias:
        alias = self.repository.find_by_id(alias_id)
        if not alias:
            raise HTTPException(status_code=404, detail=f"Alias {alias_id} not found")
        return alias

    def get_alias_by_name(self, name: str, db_connection_id: str) -> Alias:
        """
        Get an alias by name using full-text search within the specified db_connection_id.
        
        This method uses full-text search to find aliases with names that match or are similar
        to the provided name, filtered by the specified db_connection_id.
        
        Args:
            name: The name or partial name of the alias to search for
            db_connection_id: The database connection ID to filter by
            
        Returns:
            The matched alias
            
        Raises:
            HTTPException: If no alias is found with the given name in the specified db_connection
        """
        alias = self.repository.find_by_name(name, db_connection_id)
        if not alias:
            raise HTTPException(
                status_code=404, detail=f"Alias with name '{name}' not found"
            )
        return alias

    def get_aliases(self, db_connection_id: str, target_type: str = None) -> list[Alias]:
        filter = {"db_connection_id": db_connection_id}
        if target_type:
            filter["target_type"] = target_type
        return self.repository.find_by(filter)

    def update_alias(self, alias_id: str, update_request: UpdateAliasRequest) -> Alias:
        alias = self.repository.find_by_id(alias_id)
        if not alias:
            raise HTTPException(status_code=404, detail=f"Alias {alias_id} not found")

        # If name is being updated, check if it conflicts with existing aliases
        if update_request.name and update_request.name != alias.name:
            existing_alias = self.repository.find_by_name(update_request.name)
            if existing_alias and existing_alias.id != alias_id:
                raise HTTPException(
                    status_code=400,
                    detail=f"Alias with name '{update_request.name}' already exists",
                )

        update_data = update_request.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.now().isoformat()

        for key, value in update_data.items():
            setattr(alias, key, value)

        self.repository.update(alias_id, alias)
        return alias

    def delete_alias(self, alias_id: str) -> Alias:
        alias = self.repository.find_by_id(alias_id)
        if not alias:
            raise HTTPException(status_code=404, detail=f"Alias {alias_id} not found")

        is_deleted = self.repository.delete_by_id(alias_id)

        if not is_deleted:
            raise HTTPException(
                status_code=500, detail=f"Failed to delete alias {alias_id}"
            )

        return Alias(**is_deleted.model_dump())
