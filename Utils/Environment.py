from enum import Enum

DB_NAME = "Data/puppet_database.db"
DEFAULT_ROLE = "animator"
SEASON_USER = None


class ROLE_ID(Enum):
    ADMIN = 1
    DEV = 2
    ANIMATOR = 3
