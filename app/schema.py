from enum import Enum
from typing import List, Optional

import strawberry

from .github import add_or_edit_comment, update_labels
from .release import ReleaseInfo
from .templates import (
    INVALID_RELEASE_FILE,
    MISSING_RELEASE_FILE,
    OK_TO_PREVIEW,
    RELEASE_FILE_ADDED,
)


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
    release_info: Optional[ReleaseInfo] = None
    release_card_url: Optional[str] = None


@strawberry.input
class AddOkToPreviewCommentInput:
    pr_number: int
    paths: List[str]


@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_ok_to_preview_comment(self, input: AddOkToPreviewCommentInput) -> str:
        paths = [
            p.replace(".md", "").replace("docs/", "").replace("README", "")
            for p in input.paths
        ]
        links = [
            f"https://strawberry.rocks/docs/pr/{input.pr_number}/{path}"
            for path in paths
        ]

        comment = OK_TO_PREVIEW.format(links=links)

        add_or_edit_comment(input.pr_number, comment, slug="ok-to-preview")

        return "ok"

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

        if input.release_card_url:
            comment += f"\nHere's the preview release card for twitter: ![]({input.release_card_url})"

        add_or_edit_comment(input.pr_number, comment, slug="release-file")
        update_labels(input.pr_number, input.release_info)

        return "ok"


schema = strawberry.Schema(query=Query, mutation=Mutation)
