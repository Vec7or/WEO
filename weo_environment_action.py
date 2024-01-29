from enum import Enum


class WEOEnvironmentAction(Enum):
    CREATE = 'create'
    REMOVE = 'remove'
    EXPORT = 'export'
    IMPORT = 'import'
