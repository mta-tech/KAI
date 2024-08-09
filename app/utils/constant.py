from enum import Enum


class SupportedDatabase(Enum):
    POSTGRES = "POSTGRES"


class TableDescriptionStatus(Enum):
    NOT_SCANNED = "NOT_SCANNED"
    SYNCHRONIZING = "SYNCHRONIZING"
    DEPRECATED = "DEPRECATED"
    SCANNED = "SCANNED"
    FAILED = "FAILED"


class SQLGenerationStatus(Enum):
    NONE = "NONE"
    VALID = "VALID"
    INVALID = "INVALID"
