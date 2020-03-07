class SupervisorUniqueError(BaseException):
    pass


class SupervisorThreadLimit(BaseException):
    pass


class ConfigurationUpdateFailure(BaseException):
    pass


class ConfigurationBackupFailure(BaseException):
    pass
