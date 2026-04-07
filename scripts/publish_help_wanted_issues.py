#!/usr/bin/env python3
"""Publish labeled Plone issue lists as Markdown and JSON."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API_ACCEPT = "application/vnd.github+json"
API_VERSION = "2022-11-28"
DEFAULT_ORG = "plone"
DEFAULT_STATE = "open"
INDEX_VERSION = 1
MAX_RESULTS = 1000
PER_PAGE = 100
TIMEOUT_SECONDS = 60


@dataclass(frozen=True)
class IssueListSpec:
    """Describe one published issue list."""

    slug: str
    title: str
    label: str


ISSUE_LIST_SPECS = (
    IssueListSpec(
        slug="good-first-onboarding",
        title="Plone issue list — Good first issue onboarding",
        label="99 tag: good first issue",  # or in volto: First Contribution
    ),
    IssueListSpec(
        slug="lvl-easy",
        title="Plone issue list — Level: Easy",
        label="41 lvl: easy",  # - beginner-friendly but not trivial
    ),
    IssueListSpec(
        slug="lvl-moderate",
        title="Plone issue list — Level: Moderate",
        label="42 lvl: moderate",
    ),
    IssueListSpec(
        slug="lvl-complex",
        title="Plone issue list — Level: Complex",
        label="43 lvl: complex",
    ),
)


def iso_now() -> str:
    """Return the current UTC timestamp in ISO8601 format."""
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def parse_iso_datetime(value: str) -> datetime:
    """Parse a GitHub ISO8601 timestamp."""
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def format_display_datetime(value: str) -> str:
    """Format a GitHub ISO8601 timestamp for Markdown output."""
    parsed = parse_iso_datetime(value)
    return parsed.strftime("%Y-%m-%d %H:%M UTC")


def markdown_escape(value: str) -> str:
    """Escape Markdown table-sensitive characters."""
    return (
        value.replace("\\", "\\\\")
        .replace("|", "\\|")
        .replace("\n", " ")
        .replace("[", "\\[")
        .replace("]", "\\]")
    )


def yaml_quoted(value: str) -> str:
    """Quote a string safely for YAML front matter."""
    return json.dumps(value, ensure_ascii=False)


def file_has_content(path: Path) -> bool:
    """Return whether a file exists and is non-empty after stripping."""
    return path.exists() and bool(path.read_text(encoding="utf-8").strip())


def write_text_atomic(path: Path, content: str) -> None:
    """Write text content atomically."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    temporary_path.write_text(content, encoding="utf-8")
    temporary_path.replace(path)


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    """Write JSON content atomically."""
    write_text_atomic(
        path,
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
    )


def load_existing_json_status(path: Path) -> str | None:
    """Load the status field from an existing JSON file when possible."""
    if not path.exists():
        return None

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None

    if not isinstance(payload, dict):
        return None

    status = payload.get("status")
    return status if isinstance(status, str) else None


def build_workflow_metadata() -> dict[str, Any]:
    """Build metadata about the workflow run."""
    repository = os.getenv("GITHUB_REPOSITORY")
    run_id = os.getenv("GITHUB_RUN_ID")
    server_url = os.getenv("GITHUB_SERVER_URL", "https://github.com")

    url = None
    if repository and run_id:
        url = f"{server_url}/{repository}/actions/runs/{run_id}"

    return {
        "repository": repository,
        "run_id": run_id,
        "run_number": os.getenv("GITHUB_RUN_NUMBER"),
        "attempt": os.getenv("GITHUB_RUN_ATTEMPT"),
        "url": url,
        "sha": os.getenv("GITHUB_SHA"),
    }


def github_request_json(
    api_url: str,
    params: dict[str, Any],
    token: str | None,
) -> dict[str, Any]:
    """Perform a GitHub API request and return the parsed JSON object."""
    query_string = urlencode(params)
    url = f"{api_url.rstrip('/')}/search/issues?{query_string}"
    headers = {
        "Accept": API_ACCEPT,
        "User-Agent": "activity-recognition/issue-publisher",
        "X-GitHub-Api-Version": API_VERSION,
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = Request(url, headers=headers)

    try:
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            payload = json.load(response)
    except HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"GitHub API request failed with HTTP {error.code}: {body}"
        ) from error
    except URLError as error:
        raise RuntimeError(f"GitHub API request failed: {error.reason}") from error

    if not isinstance(payload, dict):
        raise RuntimeError("Unexpected GitHub API response shape")

    return payload


def extract_repository_full_name(repository_url: str, api_url: str) -> str:
    """Extract the owner/repository name from a repository API URL."""
    prefix = f"{api_url.rstrip('/')}/repos/"
    if repository_url.startswith(prefix):
        return repository_url[len(prefix) :]

    parts = repository_url.rstrip("/").split("/")
    if len(parts) >= 2:
        return "/".join(parts[-2:])

    return repository_url


def normalize_issue(raw_issue: dict[str, Any], api_url: str) -> dict[str, Any]:
    """Normalize a GitHub search result item into a stable JSON shape."""
    labels = []
    for label in raw_issue.get("labels", []):
        if isinstance(label, dict) and label.get("name"):
            labels.append(label["name"])

    user = raw_issue.get("user") or {}
    assignees = []
    for assignee in raw_issue.get("assignees", []):
        if isinstance(assignee, dict) and assignee.get("login"):
            assignees.append(assignee["login"])

    repository_url = raw_issue.get("repository_url", "")
    repository_full_name = extract_repository_full_name(repository_url, api_url)

    return {
        "id": raw_issue.get("id"),
        "number": raw_issue.get("number"),
        "title": raw_issue.get("title", ""),
        "html_url": raw_issue.get("html_url", ""),
        "repository_full_name": repository_full_name,
        "repository_url": repository_url,
        "state": raw_issue.get("state"),
        "created_at": raw_issue.get("created_at"),
        "updated_at": raw_issue.get("updated_at"),
        "comments": raw_issue.get("comments", 0),
        "author": {
            "login": user.get("login"),
            "html_url": user.get("html_url"),
        },
        "assignees": assignees,
        "labels": labels,
    }


def fetch_issues_for_spec(
    spec: IssueListSpec,
    org: str,
    state: str,
    api_url: str,
    token: str | None,
) -> list[dict[str, Any]]:
    """Fetch all issues for a label spec, sorted by last update."""
    query = f'org:{org} is:issue is:{state} label:"{spec.label}"'

    issues: list[dict[str, Any]] = []
    page = 1
    total_count = None

    while True:
        payload = github_request_json(
            api_url=api_url,
            params={
                "q": query,
                "sort": "updated",
                "order": "desc",
                "per_page": PER_PAGE,
                "page": page,
            },
            token=token,
        )

        if total_count is None:
            reported_total = int(payload.get("total_count", 0))
            total_count = min(reported_total, MAX_RESULTS)
            if reported_total > MAX_RESULTS:
                print(
                    f"[warn] Query for {spec.slug} returned more than "
                    f"{MAX_RESULTS} issues; results will be truncated."
                )

        items = payload.get("items", [])
        if not isinstance(items, list):
            raise RuntimeError("Unexpected GitHub API search item list shape")

        page_issues = [
            normalize_issue(item, api_url)
            for item in items
            if isinstance(item, dict) and "pull_request" not in item
        ]
        issues.extend(page_issues)

        if len(issues) >= total_count or len(items) < PER_PAGE:
            break

        page += 1

    issues.sort(key=lambda issue: issue["updated_at"] or "", reverse=True)
    return issues[:total_count]


def build_front_matter(
    spec: IssueListSpec,
    generated_at: str,
    org: str,
    issue_count: int,
) -> str:
    """Build Jekyll front matter for a Markdown list page."""
    lines = [
        "---",
        f"title: {yaml_quoted(spec.title)}",
        f"permalink: {yaml_quoted(f'/issues/{spec.slug}/')}",
        f"generated_at: {yaml_quoted(generated_at)}",
        f"organization: {yaml_quoted(org)}",
        f"issue_count: {issue_count}",
        "required_labels:",
        f"  - {yaml_quoted(spec.label)}",
        "---",
        "",
    ]
    return "\n".join(lines)


def build_markdown_content(
    spec: IssueListSpec,
    issues: list[dict[str, Any]],
    generated_at: str,
    org: str,
) -> str:
    """Build the Markdown page content for a non-empty issue list."""
    lines = [
        build_front_matter(spec, generated_at, org, len(issues)),
        f"# {spec.title}",
        "",
        f"Generated: `{generated_at}`  ",
        f"Organization: `{org}`  ",
        f"Required label: `{spec.label}`  ",
        f"Issue count: `{len(issues)}`",
        "",
        "Sorted by last updated date, newest first.",
        "",
        "| Updated | Repository | Issue | Author | Labels |",
        "| --- | --- | --- | --- | --- |",
    ]

    for issue in issues:
        title = markdown_escape(issue["title"])
        issue_reference = f"#{issue['number']} {title}"
        issue_link = f"[{issue_reference}]({issue['html_url']})"
        repository = f"`{markdown_escape(issue['repository_full_name'])}`"
        author_login = issue.get("author", {}).get("login") or "unknown"
        author = f"`{markdown_escape(author_login)}`"
        labels = ", ".join(
            f"`{markdown_escape(label)}`" for label in issue.get("labels", [])
        )
        lines.append(
            "| "
            f"{format_display_datetime(issue['updated_at'])} | "
            f"{repository} | "
            f"{issue_link} | "
            f"{author} | "
            f"{labels} |"
        )

    lines.append("")
    return "\n".join(lines)


def build_empty_markdown_content(
    spec: IssueListSpec,
    generated_at: str,
    org: str,
) -> str:
    """Build a placeholder Markdown page for an initial empty result."""
    lines = [
        build_front_matter(spec, generated_at, org, 0),
        f"# {spec.title}",
        "",
        f"Generated: `{generated_at}`  ",
        f"Organization: `{org}`  ",
        f"Required label: `{spec.label}`  ",
        "Issue count: `0`",
        "",
        "No matching open issues were found at generation time.",
        "",
        "If a future query unexpectedly returns no issues while a published file "
        "already exists, the workflow safeguard keeps the previous non-empty "
        "published version instead of overwriting it.",
        "",
    ]
    return "\n".join(lines)


def build_json_payload(
    spec: IssueListSpec,
    issues: list[dict[str, Any]],
    generated_at: str,
    org: str,
    workflow: dict[str, Any],
    status: str,
    message: str | None,
) -> dict[str, Any]:
    """Build the JSON payload for one issue list."""
    return {
        "version": INDEX_VERSION,
        "status": status,
        "generated_at": generated_at,
        "organization": org,
        "state": DEFAULT_STATE,
        "slug": spec.slug,
        "title": spec.title,
        "required_labels": [spec.label],
        "issue_count": len(issues),
        "issues": issues,
        "message": message,
        "workflow": workflow,
    }


def publish_spec(
    spec: IssueListSpec,
    issues: list[dict[str, Any]],
    generated_at: str,
    org: str,
    markdown_dir: Path,
    json_dir: Path,
    workflow: dict[str, Any],
) -> None:
    """Publish Markdown and JSON outputs for one label spec."""
    markdown_path = markdown_dir / f"{spec.slug}.md"
    json_path = json_dir / f"{spec.slug}.json"
    existing_json_status = load_existing_json_status(json_path)

    if issues:
        markdown_content = build_markdown_content(spec, issues, generated_at, org)
        json_payload = build_json_payload(
            spec=spec,
            issues=issues,
            generated_at=generated_at,
            org=org,
            workflow=workflow,
            status="success",
            message=None,
        )
        write_text_atomic(markdown_path, markdown_content)
        write_json_atomic(json_path, json_payload)
        print(f"[info] Published {len(issues)} issues for {spec.slug}")
        return

    if existing_json_status == "pending":
        markdown_content = build_empty_markdown_content(spec, generated_at, org)
        json_payload = build_json_payload(
            spec=spec,
            issues=[],
            generated_at=generated_at,
            org=org,
            workflow=workflow,
            status="empty_initial",
            message="No matching open issues were found at generation time.",
        )
        write_text_atomic(markdown_path, markdown_content)
        write_json_atomic(json_path, json_payload)
        print(f"[info] Replaced pending placeholder with empty result for {spec.slug}")
        return

    if file_has_content(markdown_path) or file_has_content(json_path):
        print(
            f"[warn] Query for {spec.slug} returned no issues. "
            "Keeping the previous published files unchanged."
        )
        return

    markdown_content = build_empty_markdown_content(spec, generated_at, org)
    json_payload = build_json_payload(
        spec=spec,
        issues=[],
        generated_at=generated_at,
        org=org,
        workflow=workflow,
        status="empty_initial",
        message="No matching open issues were found at generation time.",
    )
    write_text_atomic(markdown_path, markdown_content)
    write_json_atomic(json_path, json_payload)
    print(f"[info] Published initial empty placeholder for {spec.slug}")


def main() -> int:
    """Publish all labeled issue lists."""
    org = os.getenv("PLONE_ISSUE_ORG", DEFAULT_ORG)
    api_url = os.getenv("GITHUB_API_URL", "https://api.github.com")
    token = os.getenv("GITHUB_TOKEN")
    generated_at = iso_now()
    workflow = build_workflow_metadata()
    markdown_dir = Path("docs/issues")
    json_dir = Path("docs/data/issues")

    for spec in ISSUE_LIST_SPECS:
        issues = fetch_issues_for_spec(
            spec=spec,
            org=org,
            state=DEFAULT_STATE,
            api_url=api_url,
            token=token,
        )
        publish_spec(
            spec=spec,
            issues=issues,
            generated_at=generated_at,
            org=org,
            markdown_dir=markdown_dir,
            json_dir=json_dir,
            workflow=workflow,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
