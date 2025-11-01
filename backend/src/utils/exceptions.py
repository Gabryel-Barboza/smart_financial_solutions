"""Classe para definição de novas exceções da aplicação"""


class WrongFileTypeError(Exception):
    """Raised when the received file is incompatible with the service being used."""

    def __init__(self, msg: str = None):
        self.msg = (
            msg
            or 'Wrong file type received! Please, check the compatible file types and try again...'
        )
        super().__init__(self.msg)


class MaxFileSizeException(Exception):
    """Raised when a file has exceeded the maximum size defined."""

    def __init__(self, msg: str = None):
        self.msg = (
            msg or 'Max file size exceeded! Please, try again with a smaller file.'
        )


class ModelNotFoundException(Exception):
    """Raised when no llm was instantiated before using agents or the model provided was not found."""

    def __init__(self, msg: str = None):
        self.msg = (
            msg or 'No llm found, instantiate a model first with the available methods.'
        )
        super().__init__(self.msg)


class ModelResponseValidationException(Exception):
    """Raised when the agent response could not be validated with the output schema."""

    def __init__(self, msg: str = None):
        self.msg = (
            msg or 'Agent failed to generate a response correctly, please try again.'
        )


class ExecutorNotFoundException(Exception):
    """Raised when no agent executor was instantiated before using agents."""

    def __init__(self, msg: str = None):
        self.msg = (
            msg
            or 'No agent found, initialize the agent first with initialize_agent method.'
        )
        super().__init__(self.msg)


class APIKeyNotFoundException(Exception):
    """Raised when no API key for the desired chat model was found."""

    def __init__(self, msg: str = None):
        self.msg = (
            msg
            or 'Your API key for the desired agent is missing, please export a key as an environment variable.'
        )
        super().__init__(self.msg)


class DatabaseFailedException(Exception):
    """Raised when a database interaction has failed."""

    def __init__(self, msg: str = None):
        self.msg = msg or 'An internal error occurred, please try again.'
        super().__init__(self.msg)


class VectorStoreConnectionException(Exception):
    """Raised when no connection for the vector store was found."""

    def __init__(self, msg: str = None):
        self.msg = msg or 'No connection found for the vector store, aborting operation'
        super().__init__(self.msg)


class SessionNotFoundException(Exception):
    """Raised when the user tries to use a service without a registered session."""

    def __init__(self, msg: str = None):
        self.msg = (
            msg
            or 'Current session not found for the specified ID, please add an API key first.'
        )
        super().__init__(self.msg)


class InvalidEmailTypeException(Exception):
    """Raised when a string is validated as false for email patterns."""

    def __init__(self, msg: str = None):
        self.msg = msg or 'Invalid email received, please try again with a valid email.'
        super().__init__(self.msg)
