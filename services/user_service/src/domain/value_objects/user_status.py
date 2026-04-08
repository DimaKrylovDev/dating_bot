import enum


class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    BANNED = "banned"
    DELETED = "deleted"
