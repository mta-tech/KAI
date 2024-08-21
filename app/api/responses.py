from app.modules.database_connection.models import DatabaseConnection
from app.modules.table_description.models import TableDescription


class DatabaseConnectionResponse(DatabaseConnection):
    pass


class TableDescriptionResponse(TableDescription):
    pass
