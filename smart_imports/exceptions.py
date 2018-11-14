

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
    MESSAGE = 'config "{path}" has wrong format: {message}'


class ImporterError(SmartImportsError):
    MESSAGE = None


class NoImportFound(ImporterError):
    MESSAGE = 'can not find import rule for variable "{variable}"\n\n' \
              'module: "{module}"\n' \
              'file: {path}\n' \
              'lines: {lines}'


class RulesError(ImporterError):
    MESSAGE = None


class RuleAlreadyRegistered(RulesError):
    MESSAGE = 'rule "{rule}" has been registered already'


class RuleNotRegistered(RulesError):
    MESSAGE = 'rule "{rule}" has not registered'
