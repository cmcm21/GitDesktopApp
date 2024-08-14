from enum import Enum


class FileLockModel:
    class FileLockState(Enum):
        LOCK = 1
        NO_LOCK = 2

    file_path: str = ""
    file_state: FileLockState = FileLockState.NO_LOCK
