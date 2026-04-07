const INDEX_PATH = './data/index.json';
const TASK_SLUG = 'github-activity-digest';

function toHref(path) {
  if (!path) {
    return '';
  }

  if (/^https?:\/\//.test(path)) {
    return path;
  }

  return `./${path.replace(/^\.\//, '')}`;
}

function formatDateTime(value) {
  if (!value) {
    return '—';
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat('en', {
    dateStyle: 'medium',
    timeStyle: 'short',
    timeZone: 'UTC'
  }).format(date);
}

function formatCount(value) {
  return typeof value === 'number' ? String(value) : '—';
}

function setEndpointLinks(latest) {
  const container = document.getElementById('endpoint-links');
  container.innerHTML = '';

  const links = [
    { label: 'Task index JSON', href: INDEX_PATH },
    { label: 'Latest JSON', href: latest?.artifacts?.latest_json_path },
    { label: 'Latest markdown', href: latest?.artifacts?.latest_markdown_path }
  ].filter((item) => item.href);

  for (const item of links) {
    const link = document.createElement('a');
    link.href = toHref(item.href);
    link.textContent = item.label;
    link.target = '_blank';
    link.rel = 'noreferrer';
    container.append(link);
  }
}

function setLatestMeta(latest) {
  const meta = document.getElementById('latest-meta');
  meta.innerHTML = '';

  const entries = [
    ['Status', latest?.status ?? 'pending'],
    ['Generated', formatDateTime(latest?.generated_at)],
    ['Period', latest?.period ? `${latest.period.start} → ${latest.period.end}` : '—'],
    ['Days', latest?.period?.days ?? '—'],
    ['Mode', latest?.source?.mode ?? '—'],
    ['Organization', latest?.source?.organization ?? '—'],
    ['Repositories processed', formatCount(latest?.counts?.repos_processed)],
    ['Active repositories', formatCount(latest?.counts?.active_repos)],
    ['AI provider', latest?.ai?.provider ?? '—'],
    ['AI model', latest?.ai?.model ?? '—']
  ];

  for (const [label, value] of entries) {
    const dt = document.createElement('dt');
    dt.textContent = label;

    const dd = document.createElement('dd');
    dd.textContent = String(value);

    meta.append(dt, dd);
  }
}

function setSummary(latest) {
  const summary = document.getElementById('summary-text');
  summary.textContent = latest?.summary || latest?.message || 'No published summary yet.';
}

function setStatusMessage(latest, runsCount) {
  const element = document.getElementById('status-message');
  const generatedAt = latest?.generated_at ? formatDateTime(latest.generated_at) : 'not yet published';
  element.textContent = `Status: ${latest?.status ?? 'pending'} · Latest run: ${generatedAt} · Archived runs: ${runsCount}`;
}

function setRunsList(task) {
  const list = document.getElementById('runs-list');
  list.innerHTML = '';

  const runs = task?.runs ?? [];
  if (runs.length === 0) {
    const item = document.createElement('li');
    item.className = 'muted';
    item.textContent = 'No archived runs have been published yet.';
    list.append(item);
    return;
  }

  for (const run of runs) {
    const item = document.createElement('li');
    item.className = 'run-item';

    const header = document.createElement('div');
    header.className = 'run-header';
    header.textContent = `${formatDateTime(run.generated_at)} · ${run.status}`;

    const details = document.createElement('p');
    details.className = 'muted';
    const counts = run.counts || {};
    details.textContent = `${run.period?.start ?? '—'} → ${run.period?.end ?? '—'} · ${formatCount(counts.repos_processed)} repos processed · ${formatCount(counts.active_repos)} active repos`;

    const excerpt = document.createElement('p');
    excerpt.textContent = run.summary_excerpt || 'No summary excerpt available.';

    const links = document.createElement('div');
    links.className = 'links';

    const linkData = [
      { label: 'JSON', href: run.json_path },
      { label: 'Markdown', href: run.markdown_path },
      { label: 'Workflow run', href: run.workflow_url }
    ].filter((entry) => entry.href);

    for (const entry of linkData) {
      const link = document.createElement('a');
      link.href = toHref(entry.href);
      link.textContent = entry.label;
      if (/^https?:\/\//.test(entry.href)) {
        link.target = '_blank';
        link.rel = 'noreferrer';
      }
      links.append(link);
    }

    item.append(header, details, excerpt, links);
    list.append(item);
  }
}

async function loadJson(path) {
  const response = await fetch(path, { headers: { Accept: 'application/json' } });
  if (!response.ok) {
    throw new Error(`Request failed with ${response.status}`);
  }
  return response.json();
}

async function main() {
  try {
    const indexData = await loadJson(INDEX_PATH);
    const task = (indexData.tasks || []).find((item) => item.slug === TASK_SLUG);

    if (!task) {
      throw new Error(`Task '${TASK_SLUG}' not found in index.json`);
    }

    const latestJsonPath = task.latest?.json_path || 'data/github-activity-digest/latest.json';
    const latest = await loadJson(toHref(latestJsonPath));

    setEndpointLinks(latest);
    setLatestMeta(latest);
    setSummary(latest);
    setStatusMessage(latest, task.runs?.length ?? 0);
    setRunsList(task);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    document.getElementById('status-message').textContent = `Failed to load published data: ${message}`;
    document.getElementById('summary-text').textContent = 'Published data is not available yet.';
    document.getElementById('runs-list').innerHTML = '<li class="muted">No run history available.</li>';
  }
}

document.addEventListener('DOMContentLoaded', () => {
  void main();
});
