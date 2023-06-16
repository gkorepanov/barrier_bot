from typing import Optional
from llm_tools.tokens import TokenExpenses

class APIOverloadedError(TimeoutError):
    pass

class EmptyTranscriptionError(ValueError):
    pass

class PlaceholderMessageDeletedError(ValueError):
    pass

class TooManyTokensError(ValueError):
    pass

class FileIsTooBigError(ValueError):
    pass

class LanguageDetectionError(ValueError):
    pass
