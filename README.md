# activity-recognition

This repository publishes workflow-generated activity data for the Plone
organization.

## First published task

The initial workflow runs the `github-activity-digest` CLI from the upstream
repository at
[`abensur/github-activity-digest`](https://github.com/abensur/github-activity-digest).

It uses a local config and a local editable prompt template from this
repository, then publishes the result into `docs/data/`.

The workflow is configured with these digest settings:

- organization: `plone`
- only-public: `false`
- only-private: `false`

The published output is available in two forms:

- HTML via GitHub Pages from `docs/index.html`
- JSON for external clients under `docs/data/`

## Help wanted issue lists

This repository also publishes static lists of Plone issues that:

- are open issues
- are in the `plone` organization
- have the label `help wanted`
- also have one of these type labels:
  - `99 tag: good first issue- onboarding`
  - `41 lvl: easy - beginner-friendly but not trivial`
  - `42 lvl: moderate`
  - `43 lvl: complex`

The workflow runs hourly and writes:

- Markdown pages under `docs/issues/`
- JSON files under `docs/data/issues/`

The generated lists are sorted by last updated date, newest first.

To avoid accidental data loss, the workflow does not overwrite an existing
published file with an empty result set.

## Custom prompt

Edit these files to control the digest prompt and run settings:

- `digest/config.json`
- `digest/prompt-template-activity-recognition.txt`

During the workflow run, those files are copied into the checked-out digest
tool directory before the CLI is executed.

## Repository layout

```text
.github/workflows/github-activity-digest.yml
.github/workflows/help-wanted-issues.yml
digest/
  config.json
  prompt-template-activity-recognition.txt
docs/
  index.html
  assets/
  data/
  issues/
scripts/publish_github_activity_digest.py
scripts/publish_help_wanted_issues.py
```

## Required secrets

- `OPENAI_API_KEY`
  - Required because the current local digest config uses OpenAI.

For public repository data, the workflow uses the built-in GitHub Actions
`GITHUB_TOKEN`. You do not need to create a separate GitHub token secret for
the current public-only setup.

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
- `.../issues/good-first-onboarding/`
- `.../issues/lvl-easy/`
- `.../issues/lvl-moderate/`
- `.../issues/lvl-complex/`
- `.../data/issues/good-first-onboarding.json`
- `.../data/issues/lvl-easy.json`
- `.../data/issues/lvl-moderate.json`
- `.../data/issues/lvl-complex.json`

## Notes

- The workflow commits generated data back into this repository.
- Run history is kept in `docs/data/github-activity-digest/runs/`.
- The JSON contract is owned by this repository so external clients can rely
  on a stable structure even if the upstream digest tool evolves.
- The prompt file is local to this repository, so you can customize the summary
  style without modifying the upstream digest project.
