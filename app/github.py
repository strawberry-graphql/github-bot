import typing

import httpx

from .config import GITHUB_TOKEN
from .release import ReleaseInfo

SIGNATURE_TEMPLATE = "<!-- action-check: {slug} -->"
API_BASE = "https://api.github.com"


def has_signature(comment: dict, slug: str) -> bool:
    return (
        comment["user"]["login"] in ["github-actions[bot]", "botberry"]
        and SIGNATURE_TEMPLATE.format(slug) in comment["body"]
    )


def get_comments_link(pr_number: int) -> str:
    url = f"/repos/strawberry-graphql/strawberry/issues/{pr_number}/comments"

    return API_BASE + url


def get_labels_link(pr_number: int) -> str:
    url = f"/repos/strawberry-graphql/strawberry/issues/{pr_number}/labels"

    return API_BASE + url


def get_comments(pr_number: int) -> typing.List[dict]:
    comments_link = get_comments_link(pr_number)

    response = httpx.get(comments_link)

    return response.json()


def get_labels(pr_number) -> typing.List[dict]:
    labels_link = get_labels_link(pr_number)

    response = httpx.get(labels_link)

    return response.json()


def add_or_edit_comment(pr_number: int, comment: str, slug: str):
    current_comments = get_comments(pr_number)

    previous_comment = next(
        (comment for comment in current_comments if has_signature(comment, slug)),
        None,
    )

    method = httpx.patch if previous_comment else httpx.post
    url = previous_comment["url"] if previous_comment else get_comments_link(pr_number)

    response = method(
        url,
        headers={"Authorization": f"token {GITHUB_TOKEN}"},
        json={"body": comment + SIGNATURE_TEMPLATE.format(slug)},
    )

    response.raise_for_status()


def update_labels(pr_number: int, release_info: typing.Optional[ReleaseInfo]):
    labels_to_add = {"bot:has-release-file"}
    labels_to_remove: typing.Set[str] = set()

    new_release_label = None

    if release_info is None or release_info.change_type is None:
        labels_to_remove = labels_to_add
        labels_to_add = set()
    else:
        new_release_label = f"bot:release-type-{release_info.change_type.value}"
        labels_to_add.add(new_release_label)

    labels_url = get_labels_link(pr_number)
    current_labels = get_labels(pr_number)

    current_labels_url_by_name = {
        label["name"]: label["url"] for label in current_labels
    }

    current_labels = set(current_labels_url_by_name.keys())

    release_labels_to_remove = [
        label
        for label in current_labels
        if label.startswith("bot:release-type-") and label != new_release_label
    ]
    labels_to_remove.update(release_labels_to_remove)

    if not current_labels.issuperset(labels_to_add):
        response = httpx.post(
            labels_url,
            headers={"Authorization": f"token {GITHUB_TOKEN}"},
            json={"labels": list(labels_to_add)},
        )

        response.raise_for_status()

    if current_labels.issuperset(labels_to_remove):
        for label in labels_to_remove:
            response = httpx.delete(
                current_labels_url_by_name[label],
                headers={"Authorization": f"token {GITHUB_TOKEN}"},
            )

            response.raise_for_status()
