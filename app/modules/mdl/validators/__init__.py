"""MDL validation utilities."""
import json
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError


class MDLValidator:
    """Validate MDL manifests against JSON Schema."""

    _schema: dict | None = None
    _schema_path = Path(__file__).parent.parent / "schema" / "mdl.schema.json"

    @classmethod
    def get_schema(cls) -> dict:
        """Load and cache the MDL JSON schema."""
        if cls._schema is None:
            with open(cls._schema_path) as f:
                cls._schema = json.load(f)
        return cls._schema

    @classmethod
    def validate(cls, manifest: dict) -> tuple[bool, list[str]]:
        """
        Validate MDL manifest against schema.

        Args:
            manifest: MDL manifest dictionary to validate.

        Returns:
            Tuple of (is_valid, list_of_error_messages).
        """
        schema = cls.get_schema()
        validator = Draft202012Validator(schema)
        errors = list(validator.iter_errors(manifest))

        if errors:
            error_messages = [
                f"{'.'.join(str(p) for p in e.path) or 'root'}: {e.message}"
                for e in errors
            ]
            return False, error_messages

        return True, []

    @classmethod
    def validate_or_raise(cls, manifest: dict) -> None:
        """
        Validate and raise ValidationError if invalid.

        Args:
            manifest: MDL manifest dictionary to validate.

        Raises:
            ValidationError: If the manifest is invalid.
        """
        is_valid, errors = cls.validate(manifest)
        if not is_valid:
            raise ValidationError(f"MDL validation failed: {errors}")
