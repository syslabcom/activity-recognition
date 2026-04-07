#!/usr/bin/env python3
"""Publish GitHub Activity Digest output into docs/data."""

from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

TASK_SLUG = "github-activity-digest"
TASK_TITLE = "GitHub Activity Digest"
INDEX_VERSION = 1

ANSI_ESCAPE_PATTERN = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
REPOS_PROCESSED_PATTERN = re.compile(r"Found\s+(?P<count>\d+)\s+repositories")
ACTIVE_REPOS_PATTERN = re.compile(r"Activity found in\s+(?P<count>\d+)\s+repositories")


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Publish GitHub Activity Digest output into docs/data."
    )
    parser.add_argument("--config-file", required=True, help="Path to config.json")
    parser.add_argument(
        "--summary-file",
        required=True,
        help="Path to the generated summary markdown file",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Pages data directory, usually docs/data",
    )
    parser.add_argument(
        "--source-repository",
        required=True,
        help="Repository that owns the digest config and code",
    )
    parser.add_argument(
        "--source-config-path",
        required=True,
        help="Config path inside the source repository",
    )
    parser.add_argument(
        "--log-file",
        required=False,
        help="Optional workflow log file used to extract basic counts",
    )
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    """Load a JSON file into a dictionary."""
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    if not isinstance(data, dict):
        raise ValueError(f"Expected an object in {path}")

    return data


def load_optional_text(path: Path | None) -> str | None:
    """Read a text file if it exists and has non-empty content."""
    if path is None or not path.exists():
        return None

    content = path.read_text(encoding="utf-8").strip()
    return content or None


def strip_ansi_sequences(text: str) -> str:
    """Remove ANSI escape sequences from workflow log output."""
    return ANSI_ESCAPE_PATTERN.sub("", text)


def extract_last_count(pattern: re.Pattern[str], text: str) -> int | None:
    """Extract the last matching integer from the provided text."""
    matches = pattern.findall(text)
    if not matches:
        return None

    return int(matches[-1])


def parse_log_counts(log_text: str | None) -> tuple[int | None, int | None]:
    """Parse repository counts from the digest log output."""
    if not log_text:
        return None, None

    clean_log = strip_ansi_sequences(log_text)
    repos_processed = extract_last_count(REPOS_PROCESSED_PATTERN, clean_log)
    active_repos = extract_last_count(ACTIVE_REPOS_PATTERN, clean_log)
    return repos_processed, active_repos


def compute_period(days: int, now: datetime) -> dict[str, Any]:
    """Compute the reporting period used by the digest."""
    start = (now - timedelta(days=days)).replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )
    return {
        "days": days,
        "start": start.date().isoformat(),
        "end": now.date().isoformat(),
    }


def build_fallback_summary(period: dict[str, Any]) -> str:
    """Build a readable fallback summary when no markdown file was created."""
    return (
        "📊 WEEKLY SUMMARY\n"
        f"{period['start']} to {period['end']}\n\n"
        "No repository activity during this period.\n\n"
        "Automatically generated from 0 active repositories."
    )


def build_summary_excerpt(summary: str, limit: int = 180) -> str:
    """Build a single-line summary excerpt for the index file."""
    compact = " ".join(summary.split())
    if len(compact) <= limit:
        return compact

    return compact[: limit - 1].rstrip() + "…"


def iso_timestamp(now: datetime) -> str:
    """Return an ISO8601 UTC timestamp without microseconds."""
    return now.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def file_timestamp(now: datetime) -> str:
    """Return a filesystem-safe UTC timestamp."""
    return now.strftime("%Y-%m-%dT%H-%M-%SZ")


def relative_site_path(path: Path, site_root: Path) -> str:
    """Convert a local file path into a site-relative POSIX path."""
    return path.relative_to(site_root).as_posix()


def build_workflow_metadata() -> dict[str, Any]:
    """Build metadata for the workflow run that published the data."""
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


def load_index(index_path: Path) -> dict[str, Any]:
    """Load the existing site index or create a minimal default structure."""
    if index_path.exists():
        index_data = load_json(index_path)
    else:
        index_data = {"version": INDEX_VERSION, "generated_at": None, "tasks": []}

    tasks = index_data.get("tasks")
    if not isinstance(tasks, list):
        index_data["tasks"] = []

    index_data.setdefault("version", INDEX_VERSION)
    index_data.setdefault("generated_at", None)
    return index_data


def get_or_create_task(index_data: dict[str, Any]) -> dict[str, Any]:
    """Return the task entry for the digest, creating it when needed."""
    tasks = index_data.setdefault("tasks", [])
    if not isinstance(tasks, list):
        tasks = []
        index_data["tasks"] = tasks

    for task in tasks:
        if task.get("slug") == TASK_SLUG:
            return task

    task = {
        "slug": TASK_SLUG,
        "title": TASK_TITLE,
        "latest": {
            "status": "pending",
            "generated_at": None,
            "json_path": f"data/{TASK_SLUG}/latest.json",
            "markdown_path": f"data/{TASK_SLUG}/latest.md",
        },
        "runs": [],
    }
    tasks.append(task)
    return task


def write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write a JSON file with stable formatting."""
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    """Publish the digest output to the Pages data tree."""
    args = parse_arguments()

    config_path = Path(args.config_file)
    summary_path = Path(args.summary_file)
    log_path = Path(args.log_file) if args.log_file else None
    output_dir = Path(args.output_dir)
    site_root = output_dir.parent
    task_dir = output_dir / TASK_SLUG
    runs_dir = task_dir / "runs"

    output_dir.mkdir(parents=True, exist_ok=True)
    task_dir.mkdir(parents=True, exist_ok=True)
    runs_dir.mkdir(parents=True, exist_ok=True)

    config = load_json(config_path)
    now = datetime.now(timezone.utc)
    generated_at = iso_timestamp(now)
    run_stamp = file_timestamp(now)

    days = int(config.get("period", {}).get("days", 7))
    period = compute_period(days, now)

    summary_text = load_optional_text(summary_path)
    status = "success" if summary_text else "no_activity"
    if summary_text is None:
        summary_text = build_fallback_summary(period)

    log_text = load_optional_text(log_path)
    repos_processed, active_repos = parse_log_counts(log_text)

    latest_markdown_path = task_dir / "latest.md"
    latest_json_path = task_dir / "latest.json"
    run_markdown_path = runs_dir / f"{run_stamp}.md"
    run_json_path = runs_dir / f"{run_stamp}.json"

    latest_markdown_site_path = relative_site_path(latest_markdown_path, site_root)
    latest_json_site_path = relative_site_path(latest_json_path, site_root)
    run_markdown_site_path = relative_site_path(run_markdown_path, site_root)
    run_json_site_path = relative_site_path(run_json_path, site_root)

    workflow = build_workflow_metadata()

    payload = {
        "version": INDEX_VERSION,
        "task": {"slug": TASK_SLUG, "title": TASK_TITLE},
        "status": status,
        "generated_at": generated_at,
        "message": None,
        "period": period,
        "source": {
            "repository": args.source_repository,
            "config_path": args.source_config_path,
            "mode": config.get("mode"),
            "organization": config.get("source", {}).get("organization"),
            "user": config.get("source", {}).get("user"),
            "topics": config.get("source", {}).get("topics") or [],
            "repositories": config.get("source", {}).get("repositories") or [],
        },
        "filters": {
            "exclude_repos": config.get("filters", {}).get("excludeRepos") or [],
            "include_repos": config.get("filters", {}).get("includeRepos") or [],
            "only_public": config.get("filters", {}).get("onlyPublic", False),
            "only_private": config.get("filters", {}).get("onlyPrivate", False),
            "max_repos": config.get("filters", {}).get("maxRepos"),
        },
        "counts": {
            "repos_processed": repos_processed,
            "active_repos": active_repos,
        },
        "ai": {
            "provider": config.get("ai", {}).get("provider"),
            "model": config.get("ai", {}).get("model"),
            "language": config.get("output", {}).get("language"),
            "prompt_template": config.get("ai", {}).get("promptTemplate"),
        },
        "summary": summary_text,
        "artifacts": {
            "latest_json_path": latest_json_site_path,
            "latest_markdown_path": latest_markdown_site_path,
            "run_json_path": run_json_site_path,
            "run_markdown_path": run_markdown_site_path,
        },
        "workflow": workflow,
    }

    if status == "no_activity":
        payload["message"] = (
            "No markdown summary was created, so a fallback no-activity summary was published."
        )

    markdown_output = summary_text.rstrip() + "\n"
    run_markdown_path.write_text(markdown_output, encoding="utf-8")
    latest_markdown_path.write_text(markdown_output, encoding="utf-8")
    write_json(run_json_path, payload)
    write_json(latest_json_path, payload)

    index_path = output_dir / "index.json"
    index_data = load_index(index_path)
    task = get_or_create_task(index_data)

    latest_record = {
        "status": status,
        "generated_at": generated_at,
        "json_path": latest_json_site_path,
        "markdown_path": latest_markdown_site_path,
    }
    task["latest"] = latest_record
    task["title"] = TASK_TITLE

    existing_runs = task.get("runs")
    if not isinstance(existing_runs, list):
        existing_runs = []

    run_record = {
        "status": status,
        "generated_at": generated_at,
        "period": period,
        "counts": {
            "repos_processed": repos_processed,
            "active_repos": active_repos,
        },
        "json_path": run_json_site_path,
        "markdown_path": run_markdown_site_path,
        "workflow_url": workflow.get("url"),
        "summary_excerpt": build_summary_excerpt(summary_text),
    }

    task["runs"] = [
        run for run in existing_runs if run.get("json_path") != run_json_site_path
    ]
    task["runs"].insert(0, run_record)

    index_data["generated_at"] = generated_at
    write_json(index_path, index_data)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
