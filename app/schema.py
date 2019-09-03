import typing
from enum import Enum

import strawberry

from .github import add_or_edit_comment, update_labels
from .release import ReleaseInfo
from .templates import INVALID_RELEASE_FILE, MISSING_RELEASE_FILE, RELEASE_FILE_ADDED


@strawberry.type
class Query:
    @strawberry.field
    def hello(self, info) -> str:
        return "Hello 🍓"


@strawberry.enum
class ReleaseFileStatus(Enum):
    MISSING = "missing"
    INVALID = "invalid"
    OK = "ok"


@strawberry.input
class AddReleaseFileCommentInput:
    pr_number: int
    status: ReleaseFileStatus
    release_info: typing.Optional[ReleaseInfo] = None


@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_release_file_comment(self, input: AddReleaseFileCommentInput) -> str:
        """Adds a comment about the release file to a PR."""

        status_to_template = {
            ReleaseFileStatus.MISSING: MISSING_RELEASE_FILE,
            ReleaseFileStatus.INVALID: INVALID_RELEASE_FILE,
            ReleaseFileStatus.OK: RELEASE_FILE_ADDED,
        }

        comment = status_to_template[input.status]

        if input.release_info:
            comment = comment.format(changelog_preview=input.release_info.changelog)

        add_or_edit_comment(input.pr_number, comment)
        update_labels(input.pr_number, input.release_info)

        return "ok"


schema = strawberry.Schema(query=Query, mutation=Mutation)
