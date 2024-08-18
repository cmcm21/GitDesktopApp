from enum import Enum

class GitProtocolErrorCode(Enum):
    SETUP_FAILED = "SETUP FAILED"
    CONNECTION_FAILED = "CONNECTION FAILED"
    INSTALLATION_FAILED = "INSTALLATION FAILED"
    GENERATE_KEY_FAILED = "GENERATE SSH KEY FAILED"

class GitProtocolException(Exception):
    def __init__(self, message: str, error_code=None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code

    def __str__(self):
        if self.error_code:
            return f"[Error : {str(self.error_code)}] : {self.message}"
        return self.message