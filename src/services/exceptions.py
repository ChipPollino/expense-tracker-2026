class EmailAlreadyRegisteredError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class InvalidOldPasswordError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class EmptyUpdateError(Exception):
    pass

class SettingsNotFoundError(Exception):
    pass