from src.core.repositories.exceptions import RepositoryException


class BaseSQLAlRepositoryException(RepositoryException):
    """Base SQLAlchemyRepository exception"""


class SQLARepositoryConnectionError(BaseSQLAlRepositoryException):
    """Database connection error"""


class SQLARepositoryIntegrityError(BaseSQLAlRepositoryException):
    """Data integrity violation"""


class SQLARepositoryDataError(BaseSQLAlRepositoryException):
    """Error in data or its structure"""


class SQLARepositoryOperationalError(BaseSQLAlRepositoryException):
    """Database operation error"""


class SQLARepositoryTimeoutError(BaseSQLAlRepositoryException):
    """Query execution timeout"""


class SQLARepositoryQueryError(BaseSQLAlRepositoryException):
    """Error executing the database query"""


class SQLARepositoryInternalError(BaseSQLAlRepositoryException):
    """Internal error"""


class SQLARepositoryObjectNotFoundError(BaseSQLAlRepositoryException):
    """In case of object not found"""
