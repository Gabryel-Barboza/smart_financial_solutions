"""Classe para definição de novas exceções da aplicação"""


class WrongFileTypeError(Exception):
    """Raised when the received file is incompatible with the service being used."""

    def __init__(self, msg: str = None):
        self.msg = (
            msg
            or 'Wrong file type received! Please, check the compatible file types and try again...'
        )


class ModelNotFoundException(Exception):
    """Raised when no llm was instantiated before using agents or the model provided was not found."""

    def __init__(self, msg: str = None):
        self.msg = (
            msg or 'No llm found, instantiate a model first with the available methods.'
        )


class ExecutorNotFoundException(Exception):
    """Raised when no agent executor was instantiated before using agents."""

    def __init__(self, msg: str = None):
        self.msg = (
            msg
            or 'No agent found, initialize the agent first with initialize_agent method.'
        )


class APIKeyNotFoundException(Exception):
    """Raised when no API key for the desired chat model was found."""

    def __init__(self, msg: str = None):
        self.msg = (
            msg
            or 'Your API key for the desired agent is missing, please export a key as an environment variable.'
        )


class DatabaseFailedException(Exception):
    """Raised when a database interaction has failed."""

    def __init__(self, msg: str = None):
        self.msg = msg or 'An internal error occurred, please try again.'
