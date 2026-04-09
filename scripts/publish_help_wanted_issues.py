#!/usr/bin/env python3
"""Publish labeled Plone issue lists as Markdown and JSON."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen

API_ACCEPT = "application/vnd.github+json"
API_VERSION = "2022-11-28"
DEFAULT_ORG = "plone"
DEFAULT_STATE = "open"
INDEX_VERSION = 1
SUMMARY_CACHE_VERSION = 1
MAX_RESULTS = 1000
PER_PAGE = 100
TIMEOUT_SECONDS = 60
SUMMARY_STALE_AFTER_DAYS = 7
DEFAULT_SUMMARY_MODEL = "gpt-4o-mini"
DEFAULT_SUMMARY_MAX_OUTPUT_TOKENS = 450
DEFAULT_SUMMARY_GENERATIONS_PER_RUN = 20
OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
SAFE_PATH_PART_PATTERN = re.compile(r"[^A-Za-z0-9._-]+")


@dataclass(frozen=True)
class IssueListSpec:
    """Describe one published issue list."""

    slug: str
    title: str
    label: str


@dataclass(frozen=True)
class SummaryCandidate:
    """Describe one issue that needs summary generation or regeneration."""

    issue_key: str
    issue: dict[str, Any]
    cache_path: Path
    reason: str


ISSUE_LIST_SPECS = (
    IssueListSpec(
        slug="good-first-onboarding",
        title="Plone issue list — Good first issue onboarding",
        label="99 tag: good first issue",
    ),
    IssueListSpec(
        slug="lvl-easy",
        title="Plone issue list — Level: Easy",
        label="41 lvl: easy",
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

ISSUE_SUMMARY_SYSTEM_PROMPT = """You explain open-source GitHub issues to potential contributors.

Write concise, friendly Markdown for people who may be new to this code area and may not yet understand the type of work involved.

Rules:
- Be accurate and cautious.
- Do not invent missing requirements, implementation details, or certainty.
- If the issue discussion is ambiguous, outdated, or contains competing suggestions, say so plainly.
- Keep the language accessible and reduce jargon where possible.
- Make the likely expectations and first steps feel understandable and approachable.
"""


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


def parse_optional_iso_datetime(value: Any) -> datetime | None:
    """Parse an optional ISO8601 timestamp."""
    if not isinstance(value, str) or not value.strip():
        return None

    try:
        return parse_iso_datetime(value)
    except ValueError:
        return None


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


def load_json_file(path: Path) -> dict[str, Any] | None:
    """Load a JSON file when it exists and contains an object."""
    if not path.exists():
        return None

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None

    if not isinstance(payload, dict):
        return None

    return payload


def load_existing_json_status(path: Path) -> str | None:
    """Load the status field from an existing JSON file when possible."""
    payload = load_json_file(path)
    if payload is None:
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


def build_url_with_params(url: str, params: dict[str, Any]) -> str:
    """Return a URL with the provided query parameters applied."""
    split_url = urlsplit(url)
    existing_params = dict(parse_qsl(split_url.query, keep_blank_values=True))
    for key, value in params.items():
        existing_params[key] = str(value)

    return urlunsplit(
        (
            split_url.scheme,
            split_url.netloc,
            split_url.path,
            urlencode(existing_params),
            split_url.fragment,
        )
    )


def request_json(
    url: str,
    headers: dict[str, str],
    payload: dict[str, Any] | None = None,
) -> Any:
    """Perform an HTTP request and parse the JSON response."""
    request_headers = dict(headers)
    request_data = None
    if payload is not None:
        request_headers["Content-Type"] = "application/json"
        request_data = json.dumps(payload).encode("utf-8")

    request = Request(
        url,
        headers=request_headers,
        data=request_data,
        method="POST" if request_data is not None else "GET",
    )

    try:
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            return json.load(response)
    except HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Request failed with HTTP {error.code}: {body}") from error
    except URLError as error:
        raise RuntimeError(f"Request failed: {error.reason}") from error


def github_headers(token: str | None) -> dict[str, str]:
    """Build GitHub API request headers."""
    headers = {
        "Accept": API_ACCEPT,
        "User-Agent": "activity-recognition/issue-publisher",
        "X-GitHub-Api-Version": API_VERSION,
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    return headers


def github_request_json(
    url: str,
    token: str | None,
    params: dict[str, Any] | None = None,
) -> Any:
    """Perform a GitHub API request and return parsed JSON."""
    request_url = build_url_with_params(url, params or {})
    return request_json(request_url, github_headers(token))


def github_request_paginated_list(url: str, token: str | None) -> list[dict[str, Any]]:
    """Fetch all pages from a GitHub list endpoint."""
    items: list[dict[str, Any]] = []
    page = 1

    while True:
        payload = github_request_json(
            url,
            token,
            params={"per_page": PER_PAGE, "page": page},
        )
        if not isinstance(payload, list):
            raise RuntimeError("Unexpected GitHub API list response shape")

        page_items = [item for item in payload if isinstance(item, dict)]
        items.extend(page_items)

        if len(page_items) < PER_PAGE:
            break

        page += 1

    return items


def extract_repository_full_name(repository_url: str, api_url: str) -> str:
    """Extract the owner/repository name from a repository API URL."""
    prefix = f"{api_url.rstrip('/')}/repos/"
    if repository_url.startswith(prefix):
        return repository_url[len(prefix) :]

    parts = repository_url.rstrip("/").split("/")
    if len(parts) >= 2:
        return "/".join(parts[-2:])

    return repository_url


def issue_key(issue: dict[str, Any]) -> str:
    """Return a stable key for one issue."""
    repository = issue.get("repository_full_name") or "unknown/unknown"
    number = issue.get("number") or "unknown"
    return f"{repository}#{number}"


def safe_path_part(value: str) -> str:
    """Convert arbitrary text into a safe path fragment."""
    normalized = SAFE_PATH_PART_PATTERN.sub("_", value.strip())
    return normalized.strip("._") or "unknown"


def relative_site_path(path: Path, site_root: Path) -> str:
    """Convert a local path into a site-relative POSIX path."""
    return path.relative_to(site_root).as_posix()


def summary_cache_path(summary_root: Path, issue: dict[str, Any]) -> Path:
    """Return the cache path for one issue summary."""
    repository_full_name = str(issue.get("repository_full_name") or "unknown/unknown")
    if "/" in repository_full_name:
        owner, repository = repository_full_name.split("/", 1)
    else:
        owner, repository = "unknown", repository_full_name

    issue_number = str(issue.get("number") or "unknown")
    return (
        summary_root
        / safe_path_part(owner)
        / safe_path_part(repository)
        / f"{issue_number}.json"
    )


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
    search_url = f"{api_url.rstrip('/')}/search/issues"

    while True:
        payload = github_request_json(
            search_url,
            token,
            params={
                "q": query,
                "sort": "updated",
                "order": "desc",
                "per_page": PER_PAGE,
                "page": page,
            },
        )

        if not isinstance(payload, dict):
            raise RuntimeError("Unexpected GitHub API search response shape")

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

    issues.sort(key=lambda issue: issue.get("updated_at") or "", reverse=True)
    return issues[:total_count]


def fetch_issue_comments(comments_url: str, token: str | None) -> list[dict[str, Any]]:
    """Fetch all comments for one issue."""
    raw_comments = github_request_paginated_list(comments_url, token)
    comments = []

    for comment in raw_comments:
        user = comment.get("user") or {}
        comments.append(
            {
                "author": {
                    "login": user.get("login"),
                    "html_url": user.get("html_url"),
                },
                "created_at": comment.get("created_at"),
                "updated_at": comment.get("updated_at"),
                "body": comment.get("body") or "",
            }
        )

    return comments


def fetch_issue_detail(
    issue: dict[str, Any],
    api_url: str,
    token: str | None,
) -> dict[str, Any]:
    """Fetch the full issue description and all comments."""
    repository_full_name = issue.get("repository_full_name")
    issue_number = issue.get("number")
    if not repository_full_name or issue_number is None:
        raise RuntimeError("Issue is missing repository or number")

    detail_url = (
        f"{api_url.rstrip('/')}/repos/{repository_full_name}/issues/{issue_number}"
    )
    detail_payload = github_request_json(detail_url, token)
    if not isinstance(detail_payload, dict):
        raise RuntimeError("Unexpected GitHub issue detail response shape")

    comments_url = detail_payload.get("comments_url")
    comments = []
    if isinstance(comments_url, str) and comments_url:
        comments = fetch_issue_comments(comments_url, token)

    return {
        "body": detail_payload.get("body") or "",
        "comments": comments,
    }


def issue_summary_model() -> str:
    """Return the OpenAI model used for issue summaries."""
    return os.getenv("OPENAI_ISSUE_SUMMARY_MODEL", DEFAULT_SUMMARY_MODEL)


def issue_summary_max_output_tokens() -> int:
    """Return the max output token setting for issue summaries."""
    raw_value = os.getenv(
        "OPENAI_ISSUE_SUMMARY_MAX_OUTPUT_TOKENS",
        str(DEFAULT_SUMMARY_MAX_OUTPUT_TOKENS),
    )
    try:
        return max(100, int(raw_value))
    except ValueError:
        return DEFAULT_SUMMARY_MAX_OUTPUT_TOKENS


def issue_summary_generation_limit() -> int:
    """Return the per-run limit for newly generated issue summaries."""
    raw_value = os.getenv(
        "OPENAI_ISSUE_SUMMARY_LIMIT_PER_RUN",
        str(DEFAULT_SUMMARY_GENERATIONS_PER_RUN),
    )
    try:
        return max(0, int(raw_value))
    except ValueError:
        return DEFAULT_SUMMARY_GENERATIONS_PER_RUN


def build_issue_summary_prompt(
    issue: dict[str, Any],
    issue_detail: dict[str, Any],
) -> str:
    """Build the user prompt for one issue summary request."""
    prompt_payload = {
        "repository": issue.get("repository_full_name"),
        "issue_number": issue.get("number"),
        "title": issue.get("title"),
        "labels": issue.get("labels") or [],
        "state": issue.get("state"),
        "author": issue.get("author") or {},
        "assignees": issue.get("assignees") or [],
        "created_at": issue.get("created_at"),
        "updated_at": issue.get("updated_at"),
        "body": issue_detail.get("body") or "",
        "comments": issue_detail.get("comments") or [],
    }

    return (
        "Using the issue description and all comments below, write a short, "
        "contributor-friendly Markdown summary.\n\n"
        "Use exactly these sections:\n"
        "## What this issue is about\n"
        "## What needs to be done\n"
        "## Helpful background\n"
        "## Good first steps\n\n"
        "Additional rules:\n"
        "- Assume the reader may be new to this part of Plone.\n"
        "- Lower the entry barrier without hiding complexity.\n"
        "- Explain special terms briefly when needed.\n"
        "- Mention uncertainty if the issue discussion is incomplete or outdated.\n"
        "- Mention testing, documentation, review, or coordination expectations if they are visible.\n"
        "- Keep the summary concise, ideally under 220 words.\n\n"
        "Issue data:\n"
        f"{json.dumps(prompt_payload, indent=2, ensure_ascii=False)}"
    )


def extract_openai_output_text(payload: Any) -> str:
    """Extract the text result from an OpenAI Responses API payload."""
    if not isinstance(payload, dict):
        raise RuntimeError("Unexpected OpenAI response shape")

    output_text = payload.get("output_text")
    if isinstance(output_text, str) and output_text.strip():
        return output_text.strip()

    output = payload.get("output")
    if not isinstance(output, list):
        raise RuntimeError("OpenAI response did not contain an output list")

    parts: list[str] = []
    for item in output:
        if not isinstance(item, dict):
            continue

        content = item.get("content")
        if not isinstance(content, list):
            continue

        for block in content:
            if not isinstance(block, dict):
                continue

            if block.get("type") != "output_text":
                continue

            text = block.get("text")
            if isinstance(text, str) and text.strip():
                parts.append(text.strip())

    if not parts:
        raise RuntimeError("OpenAI response did not contain output text")

    return "\n\n".join(parts)


def generate_issue_summary_with_openai(
    api_key: str,
    model: str,
    max_output_tokens: int,
    issue: dict[str, Any],
    issue_detail: dict[str, Any],
) -> str:
    """Generate a contributor-friendly issue summary with OpenAI."""
    payload = {
        "model": model,
        "instructions": ISSUE_SUMMARY_SYSTEM_PROMPT,
        "input": build_issue_summary_prompt(issue, issue_detail),
        "max_output_tokens": max_output_tokens,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "User-Agent": "activity-recognition/issue-summary-publisher",
    }

    response_payload = request_json(OPENAI_RESPONSES_URL, headers, payload=payload)
    return extract_openai_output_text(response_payload).strip()


def build_summary_cache_payload(
    issue: dict[str, Any],
    summary_markdown: str,
    generated_at: str,
    model: str,
    workflow: dict[str, Any],
) -> dict[str, Any]:
    """Build the stored summary cache payload for one issue."""
    return {
        "version": SUMMARY_CACHE_VERSION,
        "status": "success",
        "generated_at": generated_at,
        "source_issue": {
            "id": issue.get("id"),
            "number": issue.get("number"),
            "title": issue.get("title"),
            "html_url": issue.get("html_url"),
            "repository_full_name": issue.get("repository_full_name"),
            "updated_at": issue.get("updated_at"),
            "labels": issue.get("labels") or [],
            "comments": issue.get("comments", 0),
        },
        "ai": {
            "provider": "openai",
            "model": model,
        },
        "summary_markdown": summary_markdown,
        "workflow": workflow,
    }


def build_summary_reference(
    cache_payload: dict[str, Any] | None,
    cache_path: Path,
    site_root: Path,
) -> dict[str, Any] | None:
    """Build the summary object embedded into the issue JSON output."""
    if not isinstance(cache_payload, dict):
        return None

    if cache_payload.get("status") != "success":
        return None

    summary_markdown = cache_payload.get("summary_markdown")
    if not isinstance(summary_markdown, str) or not summary_markdown.strip():
        return None

    source_issue = cache_payload.get("source_issue") or {}
    ai_config = cache_payload.get("ai") or {}

    return {
        "status": "available",
        "generated_at": cache_payload.get("generated_at"),
        "source_issue_updated_at": source_issue.get("updated_at"),
        "model": ai_config.get("model"),
        "summary_markdown": summary_markdown.strip(),
        "path": relative_site_path(cache_path, site_root),
    }


def summary_regeneration_reason(
    cache_payload: dict[str, Any] | None,
    issue: dict[str, Any],
    now: datetime,
) -> str | None:
    """Return why an issue summary should be generated or regenerated."""
    if cache_payload is None:
        return "missing"

    if cache_payload.get("status") != "success":
        return "invalid"

    summary_markdown = cache_payload.get("summary_markdown")
    if not isinstance(summary_markdown, str) or not summary_markdown.strip():
        return "invalid"

    generated_at = parse_optional_iso_datetime(cache_payload.get("generated_at"))
    source_issue = cache_payload.get("source_issue") or {}
    source_updated_at = parse_optional_iso_datetime(source_issue.get("updated_at"))
    current_issue_updated_at = parse_optional_iso_datetime(issue.get("updated_at"))

    if generated_at is None or source_updated_at is None:
        return "invalid"

    if current_issue_updated_at is None:
        return None

    if current_issue_updated_at <= source_updated_at:
        return None

    if now - generated_at < timedelta(days=SUMMARY_STALE_AFTER_DAYS):
        return None

    return "stale"


def enrich_issues_with_summaries(
    issues: list[dict[str, Any]],
    summary_index: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Attach available contributor summaries to each issue."""
    enriched_issues = []

    for issue in issues:
        enriched_issue = dict(issue)
        summary_reference = summary_index.get(issue_key(issue))
        if summary_reference is not None:
            enriched_issue["contributor_summary"] = summary_reference

        enriched_issues.append(enriched_issue)

    return enriched_issues


def prepare_summary_generation(
    issues_by_spec: dict[str, list[dict[str, Any]]],
    summary_root: Path,
    site_root: Path,
    now: datetime,
) -> tuple[dict[str, dict[str, Any]], list[SummaryCandidate]]:
    """Load existing summaries and identify issues that need summary generation."""
    summary_index: dict[str, dict[str, Any]] = {}
    summary_candidates: list[SummaryCandidate] = []
    unique_issues: dict[str, dict[str, Any]] = {}

    for issues in issues_by_spec.values():
        for issue in issues:
            unique_issues.setdefault(issue_key(issue), issue)

    for unique_issue_key, issue in unique_issues.items():
        cache_path = summary_cache_path(summary_root, issue)
        cache_payload = load_json_file(cache_path)
        summary_reference = build_summary_reference(
            cache_payload, cache_path, site_root
        )
        if summary_reference is not None:
            summary_index[unique_issue_key] = summary_reference

        reason = summary_regeneration_reason(cache_payload, issue, now)
        if reason is not None:
            summary_candidates.append(
                SummaryCandidate(
                    issue_key=unique_issue_key,
                    issue=issue,
                    cache_path=cache_path,
                    reason=reason,
                )
            )

    summary_candidates.sort(
        key=lambda candidate: candidate.issue.get("updated_at") or "",
        reverse=True,
    )
    return summary_index, summary_candidates


def generate_issue_summaries(
    summary_candidates: list[SummaryCandidate],
    summary_index: dict[str, dict[str, Any]],
    site_root: Path,
    api_url: str,
    github_token: str | None,
    workflow: dict[str, Any],
) -> None:
    """Generate or refresh issue summaries when needed."""
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("[info] OPENAI_API_KEY not set; skipping contributor summary generation.")
        return

    generation_limit = issue_summary_generation_limit()
    if generation_limit <= 0:
        print(
            "[info] Issue summary generation limit is 0; skipping contributor summary generation."
        )
        return

    selected_candidates = summary_candidates[:generation_limit]
    skipped_candidates = len(summary_candidates) - len(selected_candidates)
    if skipped_candidates > 0:
        print(
            f"[info] Limiting contributor summary generation to {generation_limit} "
            f"issues this run; {skipped_candidates} more remain queued."
        )

    model = issue_summary_model()
    max_output_tokens = issue_summary_max_output_tokens()

    for candidate in selected_candidates:
        issue = candidate.issue
        try:
            print(
                f"[info] Generating contributor summary for {candidate.issue_key} "
                f"({candidate.reason})"
            )
            issue_detail = fetch_issue_detail(issue, api_url, github_token)
            generated_at = iso_now()
            summary_markdown = generate_issue_summary_with_openai(
                api_key=openai_api_key,
                model=model,
                max_output_tokens=max_output_tokens,
                issue=issue,
                issue_detail=issue_detail,
            )
            cache_payload = build_summary_cache_payload(
                issue=issue,
                summary_markdown=summary_markdown,
                generated_at=generated_at,
                model=model,
                workflow=workflow,
            )
            write_json_atomic(candidate.cache_path, cache_payload)
            summary_reference = build_summary_reference(
                cache_payload,
                candidate.cache_path,
                site_root,
            )
            if summary_reference is not None:
                summary_index[candidate.issue_key] = summary_reference
        except Exception as error:  # noqa: BLE001 - keep publishing even if one summary fails
            print(
                f"[warn] Failed to generate contributor summary for "
                f"{candidate.issue_key}: {error}"
            )


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
    github_token = os.getenv("GITHUB_TOKEN")
    generated_at = iso_now()
    now = parse_iso_datetime(generated_at)
    workflow = build_workflow_metadata()
    markdown_dir = Path("docs/issues")
    json_dir = Path("docs/data/issues")
    site_root = Path("docs")
    summary_root = json_dir / "summaries"

    issues_by_spec: dict[str, list[dict[str, Any]]] = {}
    for spec in ISSUE_LIST_SPECS:
        issues_by_spec[spec.slug] = fetch_issues_for_spec(
            spec=spec,
            org=org,
            state=DEFAULT_STATE,
            api_url=api_url,
            token=github_token,
        )

    summary_index, summary_candidates = prepare_summary_generation(
        issues_by_spec=issues_by_spec,
        summary_root=summary_root,
        site_root=site_root,
        now=now,
    )

    generate_issue_summaries(
        summary_candidates=summary_candidates,
        summary_index=summary_index,
        site_root=site_root,
        api_url=api_url,
        github_token=github_token,
        workflow=workflow,
    )

    for spec in ISSUE_LIST_SPECS:
        enriched_issues = enrich_issues_with_summaries(
            issues=issues_by_spec[spec.slug],
            summary_index=summary_index,
        )
        publish_spec(
            spec=spec,
            issues=enriched_issues,
            generated_at=generated_at,
            org=org,
            markdown_dir=markdown_dir,
            json_dir=json_dir,
            workflow=workflow,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
