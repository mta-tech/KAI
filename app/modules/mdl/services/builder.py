"""MDL Builder service for constructing semantic layer manifests."""
from typing import Optional

from app.modules.mdl.models import (
    MDLManifest,
    MDLModel,
    MDLColumn,
    MDLRelationship,
    JoinType,
)
from app.modules.table_description.models import TableDescription


class MDLBuilder:
    """
    Builder service for constructing MDL manifests.

    Provides utilities to:
    - Convert TableDescriptions to MDL models
    - Infer relationships from foreign keys
    - Add/remove/modify models and relationships
    """

    @classmethod
    def from_table_descriptions(
        cls,
        db_connection_id: str,
        catalog: str,
        schema: str,
        table_descriptions: list[TableDescription],
        name: str | None = None,
        data_source: str | None = None,
    ) -> MDLManifest:
        """
        Build an MDL manifest from TableDescription objects.

        Args:
            db_connection_id: Database connection ID
            catalog: Database catalog name
            schema: Database schema name
            table_descriptions: List of table descriptions to convert
            name: Optional manifest name
            data_source: Optional data source type (postgresql, mysql, etc.)

        Returns:
            MDLManifest with models and inferred relationships
        """
        models = []
        relationships = []
        foreign_keys = []  # Track FK info for relationship building

        for table_desc in table_descriptions:
            model, fks = cls._table_description_to_model(table_desc)
            models.append(model)
            foreign_keys.extend(fks)

        # Build relationships from foreign keys
        for fk in foreign_keys:
            rel = cls._build_relationship_from_fk(fk)
            if rel:
                relationships.append(rel)

        return MDLManifest(
            db_connection_id=db_connection_id,
            name=name,
            catalog=catalog,
            schema=schema,
            data_source=data_source,
            models=models,
            relationships=relationships,
        )

    @classmethod
    def _table_description_to_model(
        cls, table_desc: TableDescription
    ) -> tuple[MDLModel, list[dict]]:
        """
        Convert a TableDescription to an MDLModel.

        Args:
            table_desc: TableDescription to convert

        Returns:
            Tuple of (MDLModel, list of foreign key info dicts)
        """
        columns = []
        primary_key = None
        foreign_keys = []

        for col_desc in table_desc.columns:
            column = MDLColumn(
                name=col_desc.name,
                type=col_desc.data_type,
                properties=(
                    {"description": col_desc.description}
                    if col_desc.description
                    else None
                ),
            )
            columns.append(column)

            if col_desc.is_primary_key:
                primary_key = col_desc.name

            if col_desc.foreign_key:
                foreign_keys.append({
                    "source_table": table_desc.table_name,
                    "source_column": col_desc.name,
                    "target_table": col_desc.foreign_key.reference_table,
                    "target_column": col_desc.foreign_key.field_name,
                })

        model = MDLModel(
            name=table_desc.table_name,
            columns=columns,
            primary_key=primary_key,
            properties=(
                {"description": table_desc.table_description}
                if table_desc.table_description
                else None
            ),
        )

        return model, foreign_keys

    @classmethod
    def _build_relationship_from_fk(cls, fk_info: dict) -> Optional[MDLRelationship]:
        """
        Build an MDLRelationship from foreign key info.

        Args:
            fk_info: Dict with source_table, source_column, target_table, target_column

        Returns:
            MDLRelationship or None if invalid
        """
        source_table = fk_info["source_table"]
        source_column = fk_info["source_column"]
        target_table = fk_info["target_table"]
        target_column = fk_info["target_column"]

        return MDLRelationship(
            name=f"{source_table}_{target_table}",
            models=[source_table, target_table],
            join_type=JoinType.MANY_TO_ONE,
            condition=f"{source_table}.{source_column} = {target_table}.{target_column}",
        )

    @classmethod
    def add_model(cls, manifest: MDLManifest, model: MDLModel) -> MDLManifest:
        """
        Add or replace a model in the manifest.

        Args:
            manifest: Existing manifest
            model: Model to add

        Returns:
            Updated manifest (new instance)
        """
        # Remove existing model with same name
        models = [m for m in manifest.models if m.name != model.name]
        models.append(model)

        return MDLManifest(
            id=manifest.id,
            db_connection_id=manifest.db_connection_id,
            name=manifest.name,
            catalog=manifest.catalog,
            schema_name=manifest.schema_name,
            data_source=manifest.data_source,
            models=models,
            relationships=manifest.relationships,
            metrics=manifest.metrics,
            views=manifest.views,
            enum_definitions=manifest.enum_definitions,
            version=manifest.version,
            metadata=manifest.metadata,
            created_at=manifest.created_at,
            updated_at=manifest.updated_at,
        )

    @classmethod
    def add_relationship(
        cls, manifest: MDLManifest, relationship: MDLRelationship
    ) -> MDLManifest:
        """
        Add or replace a relationship in the manifest.

        Args:
            manifest: Existing manifest
            relationship: Relationship to add

        Returns:
            Updated manifest (new instance)
        """
        # Remove existing relationship with same name
        relationships = [r for r in manifest.relationships if r.name != relationship.name]
        relationships.append(relationship)

        return MDLManifest(
            id=manifest.id,
            db_connection_id=manifest.db_connection_id,
            name=manifest.name,
            catalog=manifest.catalog,
            schema_name=manifest.schema_name,
            data_source=manifest.data_source,
            models=manifest.models,
            relationships=relationships,
            metrics=manifest.metrics,
            views=manifest.views,
            enum_definitions=manifest.enum_definitions,
            version=manifest.version,
            metadata=manifest.metadata,
            created_at=manifest.created_at,
            updated_at=manifest.updated_at,
        )

    @classmethod
    def remove_model(cls, manifest: MDLManifest, model_name: str) -> MDLManifest:
        """
        Remove a model from the manifest.

        Args:
            manifest: Existing manifest
            model_name: Name of model to remove

        Returns:
            Updated manifest (new instance)
        """
        models = [m for m in manifest.models if m.name != model_name]

        # Also remove relationships referencing this model
        relationships = [
            r for r in manifest.relationships if model_name not in r.models
        ]

        return MDLManifest(
            id=manifest.id,
            db_connection_id=manifest.db_connection_id,
            name=manifest.name,
            catalog=manifest.catalog,
            schema_name=manifest.schema_name,
            data_source=manifest.data_source,
            models=models,
            relationships=relationships,
            metrics=manifest.metrics,
            views=manifest.views,
            enum_definitions=manifest.enum_definitions,
            version=manifest.version,
            metadata=manifest.metadata,
            created_at=manifest.created_at,
            updated_at=manifest.updated_at,
        )

    @classmethod
    def remove_relationship(
        cls, manifest: MDLManifest, relationship_name: str
    ) -> MDLManifest:
        """
        Remove a relationship from the manifest.

        Args:
            manifest: Existing manifest
            relationship_name: Name of relationship to remove

        Returns:
            Updated manifest (new instance)
        """
        relationships = [
            r for r in manifest.relationships if r.name != relationship_name
        ]

        return MDLManifest(
            id=manifest.id,
            db_connection_id=manifest.db_connection_id,
            name=manifest.name,
            catalog=manifest.catalog,
            schema_name=manifest.schema_name,
            data_source=manifest.data_source,
            models=manifest.models,
            relationships=relationships,
            metrics=manifest.metrics,
            views=manifest.views,
            enum_definitions=manifest.enum_definitions,
            version=manifest.version,
            metadata=manifest.metadata,
            created_at=manifest.created_at,
            updated_at=manifest.updated_at,
        )

    @classmethod
    def infer_relationships(cls, manifest: MDLManifest) -> MDLManifest:
        """
        Infer relationships from column naming conventions.

        Looks for columns ending in _id that match other table names.
        Example: customer_id -> customers table

        Args:
            manifest: Manifest to analyze

        Returns:
            Updated manifest with inferred relationships
        """
        model_names = {m.name for m in manifest.models}
        model_primary_keys = {m.name: m.primary_key for m in manifest.models}
        existing_rel_conditions = {r.condition for r in manifest.relationships}

        new_relationships = list(manifest.relationships)

        for model in manifest.models:
            for column in model.columns:
                # Look for columns ending in _id
                if column.name.endswith("_id") and column.name != "id":
                    # Try to find matching table
                    potential_table_base = column.name[:-3]  # Remove _id suffix

                    # Try singular and plural forms
                    candidates = [
                        potential_table_base,
                        potential_table_base + "s",
                        potential_table_base + "es",
                        potential_table_base[:-1] + "ies" if potential_table_base.endswith("y") else None,
                    ]
                    candidates = [c for c in candidates if c]

                    for target_table in candidates:
                        if target_table in model_names and target_table != model.name:
                            # Determine target column (usually pk or id)
                            target_pk = model_primary_keys.get(target_table) or "id"

                            condition = f"{model.name}.{column.name} = {target_table}.{target_pk}"

                            # Don't add duplicate relationships
                            if condition not in existing_rel_conditions:
                                rel = MDLRelationship(
                                    name=f"{model.name}_{target_table}",
                                    models=[model.name, target_table],
                                    join_type=JoinType.MANY_TO_ONE,
                                    condition=condition,
                                )
                                new_relationships.append(rel)
                                existing_rel_conditions.add(condition)
                            break

        return MDLManifest(
            id=manifest.id,
            db_connection_id=manifest.db_connection_id,
            name=manifest.name,
            catalog=manifest.catalog,
            schema_name=manifest.schema_name,
            data_source=manifest.data_source,
            models=manifest.models,
            relationships=new_relationships,
            metrics=manifest.metrics,
            views=manifest.views,
            enum_definitions=manifest.enum_definitions,
            version=manifest.version,
            metadata=manifest.metadata,
            created_at=manifest.created_at,
            updated_at=manifest.updated_at,
        )
