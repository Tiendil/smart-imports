
import enum


class SCOPE_TYPE(enum.Enum):
    NORMAL = 0
    CLASS = 1


class VARIABLE_STATE(enum.Enum):
    INITIALIZED = 0
    UNINITIALIZED = 1


class VARIABLE_USAGE_TYPE(enum.Enum):
    FULLY_DEFINED = 0
    PARTIALY_DEFINED = 1
    FULLY_UNDEFINED = 2


CONFIG_FILE_NAME = 'smart_imports.json'
