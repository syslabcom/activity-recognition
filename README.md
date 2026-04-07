# activity-recognition

This repository publishes workflow-generated activity data for the Plone
organization.

## First published task

The initial workflow runs
[`plone/github-activity-digest`](https://github.com/plone/github-activity-digest)
with the tested `config.json` from that repository, then publishes the
result into `docs/data/`.

The published output is available in two forms:

- HTML via GitHub Pages from `docs/index.html`
- JSON for external clients under `docs/data/`

## Repository layout

```text
.github/workflows/github-activity-digest.yml
docs/
  index.html
  assets/
  data/
scripts/publish_github_activity_digest.py
```

## Required secrets

- `ACTIVITY_SOURCE_GITHUB_TOKEN`
  - Recommended token for the digest run itself.
  - Use a token with `read:org` and, if needed, `repo` so the workflow can
    inspect the target Plone repositories.
- `OPENAI_API_KEY`
  - Required by the current tested digest config.
- `ANTHROPIC_API_KEY`
  - Optional fallback if the upstream config is changed to Anthropic later.
- `DIGEST_REPOSITORY_TOKEN`
  - Optional.
  - Only needed if `plone/github-activity-digest` is private or the default
    workflow token cannot read it.

If `ACTIVITY_SOURCE_GITHUB_TOKEN` is not set, the workflow falls back to the
repository `GITHUB_TOKEN`, which is usually only sufficient for public data.

## GitHub Pages setup

Enable Pages in the repository settings with:

- **Source:** Deploy from a branch
- **Branch:** `main`
- **Folder:** `/docs`

Once enabled, the site will serve both the HTML overview and the raw JSON
files from the same published tree.

## Published endpoints

After the first successful run, expect these paths in Pages:

- `.../data/index.json`
- `.../data/github-activity-digest/latest.json`
- `.../data/github-activity-digest/latest.md`

## Notes

- The workflow commits generated data back into this repository.
- Run history is kept in `docs/data/github-activity-digest/runs/`.
- The JSON contract is owned by this repository so external clients can rely
  on a stable structure even if the upstream digest tool evolves.
