from enum import Enum
DB_NAME = "Data/puppet_database.db"
DEFAULT_ROLE = "animator"

FILE_CHANGE_DIC = {
    "D": "Deleted",
    "": "Unmodified",
    "M": "Modified",
    "T": "File Type Changed",
    "A": "Added",
    "R": "Renamed",
    "C": "Copied",
    "U": "Updated but Unmerged",
    "??": "New File/Folder added"
}


class RoleID(Enum):
    NONE = 0
    ADMIN = 1
    DEV = 2
    ANIMATOR = 3
    ADMIN_ANIM = 4


class CreateDir(Enum):
    ALREADY_EXIST = 1
    DIR_CREATED = 2
    JUST_DIR = 3

