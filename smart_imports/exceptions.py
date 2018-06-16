

class SmartImportsError(Exception):
    MESSAGE = None

    def __init__(self, **kwargs):
        super(SmartImportsError, self).__init__(self.MESSAGE.format(**kwargs))
        self.arguments = kwargs


class ConfigError(SmartImportsError):
    MESSAGE = None


class ConfigNotFound(ConfigError):
    MESSAGE = 'config "{path}" does not exists'


class ConfigHasWrongFormat(ConfigError):
    MESSAGE = 'config "{path}" not in JSON format'
