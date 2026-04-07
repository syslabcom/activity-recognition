# activity-recognition

This repository publishes workflow-generated activity data for the Plone
organization.

## First published task

The initial workflow uses the documented GitHub Action integration:
[`abensur/github-activity-digest@v1`](https://github.com/abensur/github-activity-digest).

It runs in organization mode for `plone`, publishes the result into
`docs/data/`, and keeps a stable JSON contract for external consumers.

The workflow is configured with these digest settings:

- organization: `plone`
- user: `pilz`
- only-public: `false`
- only-private: `false`

Note: in the upstream action, `user` is only actively used for `user` mode.
This repository still records `pilz` in the published metadata so the output
mirrors your chosen source context.

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

- `OPENAI_API_KEY`
  - Required because the workflow uses the digest action with OpenAI.

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

## Notes

- The workflow commits generated data back into this repository.
- Run history is kept in `docs/data/github-activity-digest/runs/`.
- The JSON contract is owned by this repository so external clients can rely
  on a stable structure even if the upstream digest tool evolves.
- The workflow now follows the upstream README more closely by using the
  documented `uses: abensur/github-activity-digest@v1` pattern.
