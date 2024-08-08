from app.storage.typesense import TypeSenseDB


class ColumnDescriptionSchema:
    def __init__(self):
        self.collection_schema = {
            "name": "column_description",
            "enable_nested_fields": True,
            "fields": [
                {"name": "id", "type": "string"},
                {"name": "table_description_id", "type": "string"},
                {"name": "name", "type": "string"},
                {"name": "description", "type": "string"},
                {"name": "is_primary_key", "type": "bool"},
                {"name": "data_type", "type": "string"},
                {"name": "is_low_cardinality", "type": "bool"},
                {"name": "categories", "type": "string[]", "optional": True},
                {"name": "examples", "type": "object"},
                {"name": "foreign_key", "type": "object", "optional": True}, # foreign_key": { "field_name": "string", "reference_table": "string"}
                {"name": "metadata", "type": "object", "optional": True},
                {"name": "created_at", "type": "string"},
            ],
        }
        TypeSenseDB.create_collection(self.collection_schema)
