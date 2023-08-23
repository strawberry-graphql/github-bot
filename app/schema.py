from enum import Enum
from typing import Annotated

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
    def hello(self) -> str:
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
    release_info: ReleaseInfo | None = None
    release_card_url: str | None = None
    tweet: str | None = None
    repo: str | None = None


@strawberry.input
class AddOkToPreviewCommentInput:
    pr_number: int
    paths: list[str]
    repo: str | None = None


@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_ok_to_preview_comment(
        self,
        input_: Annotated[
            AddOkToPreviewCommentInput,
            strawberry.argument(name="input"),
        ],
    ) -> str:
        paths = [
            p.replace(".md", "").replace("docs/", "").replace("README", "")
            for p in input_.paths
        ]
        links = [
            f"https://strawberry.rocks/docs/pr/{input_.pr_number}/{path}"
            for path in paths
        ]

        comment = OK_TO_PREVIEW.format(links=links)

        add_or_edit_comment(
            input_.pr_number,
            comment,
            slug="ok-to-preview",
            repo=input_.repo,
        )

        return "ok"

    @strawberry.mutation
    def add_release_file_comment(
        self,
        input_: Annotated[
            AddReleaseFileCommentInput,
            strawberry.argument(name="input"),
        ],
    ) -> str:
        """Adds a comment about the release file to a PR."""
        status_to_template = {
            ReleaseFileStatus.MISSING: MISSING_RELEASE_FILE,
            ReleaseFileStatus.INVALID: INVALID_RELEASE_FILE,
            ReleaseFileStatus.OK: RELEASE_FILE_ADDED,
        }

        comment = status_to_template[input_.status]

        if input_.release_info:
            comment = comment.format(changelog_preview=input_.release_info.changelog)

        if input_.release_card_url:
            comment += (
                "\n---\nHere's the preview release card for "
                f"twitter:\n\n![]({input_.release_card_url})\n"
            )

        if input_.tweet:
            comment += f"\n\nHere's the tweet text: \n```\n{input_.tweet}\n```\n"

        add_or_edit_comment(
            input_.pr_number,
            comment,
            slug="release-file",
            repo=input_.repo,
        )
        update_labels(input_.pr_number, input_.release_info, repo=input_.repo)

        return "ok"


schema = strawberry.Schema(query=Query, mutation=Mutation)
