from enum import Enum

class SupportedDatabase(Enum):
    POSTGRES = "POSTGRES"
    MYSQL = "MYSQL"


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