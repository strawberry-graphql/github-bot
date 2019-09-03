from enum import Enum

import strawberry


@strawberry.enum
class ChangeType(Enum):
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"


@strawberry.input
class ReleaseInfo:
    change_type: ChangeType
    changelog: str
