const DIGEST_INDEX_PATH = 'data/index.json';
const DIGEST_LATEST_PATH = 'data/github-activity-digest/latest.json';
const TASK_SLUG = 'github-activity-digest';
const ISSUE_LISTS = [
  {
    slug: 'good-first-onboarding',
    title: 'Good first issue onboarding',
    jsonPath: 'data/issues/good-first-onboarding.json'
  },
  {
    slug: 'lvl-easy',
    title: 'Level: Easy',
    jsonPath: 'data/issues/lvl-easy.json'
  },
  {
    slug: 'lvl-moderate',
    title: 'Level: Moderate',
    jsonPath: 'data/issues/lvl-moderate.json'
  },
  {
    slug: 'lvl-complex',
    title: 'Level: Complex',
    jsonPath: 'data/issues/lvl-complex.json'
  }
];

function toHref(path) {
  if (!path) {
    return '';
  }

  if (/^https?:\/\//.test(path)) {
    return path;
  }

  return `./${path.replace(/^\.\//, '')}`;
}

function withCacheBuster(path) {
  const url = new URL(toHref(path), window.location.href);
  url.searchParams.set('_', String(Date.now()));
  return url.toString();
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

function toTimestamp(value) {
  const timestamp = Date.parse(value || '');
  return Number.isNaN(timestamp) ? 0 : timestamp;
}

function escapeHtml(value) {
  return String(value).replace(/[&<>'"]/g, (character) => {
    switch (character) {
      case '&':
        return '&amp;';
      case '<':
        return '&lt;';
      case '>':
        return '&gt;';
      case '"':
        return '&quot;';
      case '\'':
        return '&#39;';
      default:
        return character;
    }
  });
}

function sanitizeUrl(url) {
  const trimmed = String(url || '').trim();
  if (!trimmed) {
    return '';
  }

  if (/^(https?:|mailto:)/i.test(trimmed) || /^(\/|\.\/|\.\.\/|#)/.test(trimmed)) {
    return trimmed;
  }

  return '';
}

function renderInlineMarkdown(text) {
  const placeholders = [];
  const store = (html) => {
    const token = `\u0000${placeholders.length}\u0000`;
    placeholders.push(html);
    return token;
  };

  let result = escapeHtml(text);

  result = result.replace(/`([^`]+)`/g, (_match, code) => {
    return store(`<code>${code}</code>`);
  });

  result = result.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (_match, label, href) => {
    const safeHref = sanitizeUrl(href.replace(/^<|>$/g, ''));
    if (!safeHref) {
      return label;
    }

    return store(
      `<a href="${escapeHtml(safeHref)}" target="_blank" rel="noreferrer">${label}</a>`
    );
  });

  result = result.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  result = result.replace(/__([^_]+)__/g, '<strong>$1</strong>');
  result = result.replace(/\*([^*]+)\*/g, '<em>$1</em>');
  result = result.replace(/_([^_]+)_/g, '<em>$1</em>');

  const restored = result.replace(/\u0000(\d+)\u0000/g, (_match, index) => placeholders[Number(index)]);
  return restored.replace(/\n/g, '<br>');
}

function unwrapOuterMarkdownFence(markdown) {
  const source = String(markdown || '').trim();
  const fencedMatch = source.match(/^```(?:markdown|md)?\s*\n([\s\S]*?)\n```$/i);
  if (fencedMatch) {
    return fencedMatch[1].trim();
  }

  return source;
}

function renderMarkdown(markdown) {
  const source = unwrapOuterMarkdownFence(String(markdown || '').replace(/\r\n?/g, '\n'));
  if (!source) {
    return '<p>No published summary yet.</p>';
  }

  const lines = source.split('\n');
  const blocks = [];
  let index = 0;

  const isBlank = (line) => !line.trim();
  const isListItem = (line) => /^\s*([-*+] |\d+\. )/.test(line);

  while (index < lines.length) {
    const line = lines[index];

    if (isBlank(line)) {
      index += 1;
      continue;
    }

    if (/^```/.test(line.trim())) {
      const codeLines = [];
      index += 1;
      while (index < lines.length && !/^```/.test(lines[index].trim())) {
        codeLines.push(lines[index]);
        index += 1;
      }
      if (index < lines.length) {
        index += 1;
      }
      blocks.push(`${renderInlineMarkdown(escapeHtml(codeLines.join('\n')))}`);
      continue;
    }

    const headingMatch = line.match(/^(#{1,6})\s+(.*)$/);
    if (headingMatch) {
      const level = headingMatch[1].length;
      blocks.push(`<h${level}>${renderInlineMarkdown(headingMatch[2].trim())}</h${level}>`);
      index += 1;
      continue;
    }

    if (/^---+$/.test(line.trim()) || /^\*\*\*+$/.test(line.trim())) {
      blocks.push('<hr>');
      index += 1;
      continue;
    }

    if (/^>\s?/.test(line)) {
      const quoteLines = [];
      while (index < lines.length && /^>\s?/.test(lines[index])) {
        quoteLines.push(lines[index].replace(/^>\s?/, ''));
        index += 1;
      }
      blocks.push(`<blockquote>${renderMarkdown(quoteLines.join('\n'))}</blockquote>`);
      continue;
    }

    if (isListItem(line)) {
      const ordered = /^\s*\d+\. /.test(line);
      const tag = ordered ? 'ol' : 'ul';
      const items = [];

      while (index < lines.length && isListItem(lines[index])) {
        const itemText = lines[index].replace(/^\s*(?:[-*+] |\d+\. )/, '');
        items.push(`<li>${renderInlineMarkdown(itemText.trim())}</li>`);
        index += 1;
      }

      blocks.push(`<${tag}>${items.join('')}</${tag}>`);
      continue;
    }

    const paragraphLines = [];
    while (
      index < lines.length &&
      !isBlank(lines[index]) &&
      !/^```/.test(lines[index].trim()) &&
      !/^(#{1,6})\s+/.test(lines[index]) &&
      !/^>\s?/.test(lines[index]) &&
      !isListItem(lines[index]) &&
      !/^---+$/.test(lines[index].trim()) &&
      !/^\*\*\*+$/.test(lines[index].trim())
    ) {
      paragraphLines.push(lines[index].trim());
      index += 1;
    }

    blocks.push(`<p>${renderInlineMarkdown(paragraphLines.join('\n'))}</p>`);
  }

  return blocks.join('\n');
}

function issueCountLabel(count) {
  if (typeof count !== 'number') {
    return '— issues';
  }

  return `${count} ${count === 1 ? 'issue' : 'issues'}`;
}

function buildSummaryExcerpt(text, limit = 180) {
  const compact = String(text || '').replace(/\s+/g, ' ').trim();
  if (!compact) {
    return 'No summary excerpt available.';
  }

  if (compact.length <= limit) {
    return compact;
  }

  return `${compact.slice(0, limit - 1).trimEnd()}…`;
}

function buildRunRecordFromLatest(latest) {
  return {
    status: latest?.status ?? 'pending',
    generated_at: latest?.generated_at ?? null,
    period: latest?.period ?? null,
    counts: {
      repos_processed: latest?.counts?.repos_processed ?? null,
      active_repos: latest?.counts?.active_repos ?? null
    },
    json_path: latest?.artifacts?.run_json_path || latest?.artifacts?.latest_json_path || null,
    markdown_path: latest?.artifacts?.run_markdown_path || latest?.artifacts?.latest_markdown_path || null,
    workflow_url: latest?.workflow?.url || null,
    summary_excerpt: buildSummaryExcerpt(latest?.summary || latest?.message)
  };
}

function mergeLatestIntoTask(task, latest) {
  const baseTask = task && typeof task === 'object' ? { ...task } : { slug: TASK_SLUG, title: 'GitHub Activity Digest' };
  const latestRecord = {
    status: latest?.status ?? baseTask.latest?.status ?? 'pending',
    generated_at: latest?.generated_at ?? baseTask.latest?.generated_at ?? null,
    json_path: latest?.artifacts?.latest_json_path || baseTask.latest?.json_path || DIGEST_LATEST_PATH,
    markdown_path: latest?.artifacts?.latest_markdown_path || baseTask.latest?.markdown_path || null
  };

  const latestRun = buildRunRecordFromLatest(latest);
  const existingRuns = Array.isArray(baseTask.runs) ? [...baseTask.runs] : [];
  const mergedRuns = existingRuns.filter((run) => {
    if (!latestRun.generated_at) {
      return true;
    }

    if (run?.json_path && latestRun.json_path && run.json_path === latestRun.json_path) {
      return false;
    }

    return run?.generated_at !== latestRun.generated_at;
  });

  if (latestRun.generated_at || latestRun.json_path) {
    mergedRuns.unshift(latestRun);
  }

  mergedRuns.sort((left, right) => toTimestamp(right?.generated_at) - toTimestamp(left?.generated_at));

  return {
    ...baseTask,
    latest: latestRecord,
    runs: mergedRuns
  };
}

function createLink(label, href, external = false) {
  const link = document.createElement('a');
  link.href = external ? href : toHref(href);
  link.textContent = label;
  if (external) {
    link.target = '_blank';
    link.rel = 'noreferrer';
  }
  return link;
}

function setEndpointLinks(latest) {
  const container = document.getElementById('endpoint-links');
  container.innerHTML = '';

  const links = [
    { label: 'Task index JSON', href: DIGEST_INDEX_PATH, external: false },
    { label: 'Latest JSON', href: latest?.artifacts?.latest_json_path, external: false },
    { label: 'Latest markdown', href: latest?.artifacts?.latest_markdown_path, external: false }
  ].filter((item) => item.href);

  for (const item of links) {
    container.append(createLink(item.label, item.href, item.external));
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

function setSummary(summaryMarkdown, latest) {
  const summary = document.getElementById('summary-text');
  const source = summaryMarkdown || latest?.summary || latest?.message || 'No published summary yet.';
  summary.innerHTML = renderMarkdown(source);
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
      { label: 'JSON', href: run.json_path, external: false },
      { label: 'Markdown', href: run.markdown_path, external: false },
      { label: 'Workflow run', href: run.workflow_url, external: true }
    ].filter((entry) => entry.href);

    for (const entry of linkData) {
      links.append(createLink(entry.label, entry.href, entry.external));
    }

    item.append(header, details, excerpt, links);
    list.append(item);
  }
}

function renderIssueCards(issuePayloads) {
  const container = document.getElementById('issue-list-grid');
  container.innerHTML = '';

  for (const entry of issuePayloads) {
    const { spec, data, error } = entry;
    const card = document.createElement('article');
    card.className = 'issue-card';

    const header = document.createElement('div');
    header.className = 'issue-card-header';

    const headerText = document.createElement('div');
    const title = document.createElement('h3');
    title.textContent = spec.title;

    const label = document.createElement('p');
    label.className = 'issue-label muted';
    label.textContent = data?.required_labels?.[0] || 'Issue label';

    headerText.append(title, label);

    const count = document.createElement('span');
    count.className = 'issue-count';
    count.textContent = issueCountLabel(data?.issue_count);

    header.append(headerText, count);

    const body = document.createElement('div');
    body.className = 'issue-card-body';

    if (error) {
      const message = document.createElement('p');
      message.className = 'muted';
      message.textContent = `Failed to load this issue list: ${error}`;
      body.append(message);
    } else if (!data || !Array.isArray(data.issues) || data.issues.length === 0) {
      const message = document.createElement('p');
      message.className = 'muted';
      message.textContent = data?.message || 'No matching issues are currently published.';
      body.append(message);
    } else {
      const list = document.createElement('ul');
      list.className = 'issue-items';

      for (const issue of data.issues) {
        const item = document.createElement('li');
        item.className = 'issue-item';

        const link = document.createElement('a');
        link.className = 'issue-link';
        link.href = issue.html_url;
        link.target = '_blank';
        link.rel = 'noreferrer';
        link.textContent = `#${issue.number} ${issue.title}`;

        const meta = document.createElement('p');
        meta.className = 'issue-meta muted';
        const repository = issue.repository_full_name || 'unknown repository';
        const author = issue.author?.login ? ` · by ${issue.author.login}` : '';
        meta.textContent = `${repository} · updated ${formatDateTime(issue.updated_at)}${author}`;

        item.append(link, meta);

        const contributorSummary = issue.contributor_summary;
        if (contributorSummary?.summary_markdown) {
          const summary = document.createElement('div');
          summary.className = 'issue-summary markdown-content';
          summary.innerHTML = renderMarkdown(contributorSummary.summary_markdown);
          item.append(summary);
        }

        list.append(item);
      }

      body.append(list);
    }

    const footer = document.createElement('div');
    footer.className = 'issue-card-footer';

    const updated = document.createElement('span');
    updated.className = 'muted';
    updated.textContent = `Published: ${formatDateTime(data?.generated_at)}`;

    const links = document.createElement('div');
    links.className = 'links';
    links.append(createLink('JSON', spec.jsonPath, false));
    if (data?.workflow?.url) {
      links.append(createLink('Workflow run', data.workflow.url, true));
    }

    footer.append(updated, links);
    card.append(header, body, footer);
    container.append(card);
  }
}

async function loadJson(path) {
  const response = await fetch(withCacheBuster(path), {
    cache: 'no-store',
    headers: { Accept: 'application/json' }
  });

  if (!response.ok) {
    throw new Error(`Request failed with ${response.status}`);
  }

  return response.json();
}

async function loadText(path) {
  const response = await fetch(withCacheBuster(path), {
    cache: 'no-store',
    headers: { Accept: 'text/plain,text/markdown;q=0.9,*/*;q=0.8' }
  });

  if (!response.ok) {
    throw new Error(`Request failed with ${response.status}`);
  }

  return response.text();
}

async function loadIssuePayloads() {
  const results = await Promise.all(
    ISSUE_LISTS.map(async (spec) => {
      try {
        const data = await loadJson(spec.jsonPath);
        return { spec, data, error: null };
      } catch (error) {
        return {
          spec,
          data: null,
          error: error instanceof Error ? error.message : String(error)
        };
      }
    })
  );

  renderIssueCards(results);
}

async function main() {
  await loadIssuePayloads();

  try {
    const [latest, indexData] = await Promise.all([
      loadJson(DIGEST_LATEST_PATH),
      loadJson(DIGEST_INDEX_PATH)
    ]);

    let summaryMarkdown = latest?.summary || latest?.message || 'No published summary yet.';
    const latestMarkdownPath = latest?.artifacts?.latest_markdown_path;

    if (latestMarkdownPath) {
      try {
        const latestMarkdown = await loadText(latestMarkdownPath);
        if (latestMarkdown.trim()) {
          summaryMarkdown = latestMarkdown.trim();
        }
      } catch (_error) {
        // Keep JSON summary fallback if the markdown artifact is unavailable.
      }
    }

    const taskFromIndex = (indexData.tasks || []).find((item) => item.slug === TASK_SLUG);
    const task = mergeLatestIntoTask(taskFromIndex, latest);

    setSummary(summaryMarkdown, latest);
    setEndpointLinks(latest);
    setLatestMeta(latest);
    setStatusMessage(latest, task.runs?.length ?? 0);
    setRunsList(task);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    document.getElementById('status-message').textContent = `Failed to load digest data: ${message}`;
    document.getElementById('summary-text').innerHTML = renderMarkdown('Published digest data is not available yet.');
    document.getElementById('runs-list').innerHTML = '<li class="muted">No run history available.</li>';
    document.getElementById('latest-meta').innerHTML = '';
  }
}

document.addEventListener('DOMContentLoaded', () => {
  void main();
});
