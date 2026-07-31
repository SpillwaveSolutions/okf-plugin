#!/usr/bin/env python3
"""Local integration test: Substack archive → OKF graph → okf-graph.py checks.

Pulls articles from rickhigh.substack.com, classifies by type/subject, emits an
OKF v0.2 bundle under integration/ (gitignored), and verifies the plugin CLI.

Usage:
  python3 scripts/substack_okf.py run --limit 20
  python3 scripts/substack_okf.py fetch --limit 20
  python3 scripts/substack_okf.py classify
  python3 scripts/substack_okf.py emit
  python3 scripts/substack_okf.py verify
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = "https://rickhigh.substack.com"
DEFAULT_OUT = REPO_ROOT / "integration"
GRAPH_PY = REPO_ROOT / "scripts" / "okf-graph.py"

ARTICLE_TYPES = frozenset({"news", "tutorial", "guide", "one-off"})

SUBJECT_RULES: list[tuple[str, str]] = [
    (r"crewai", "crewai"),
    (r"agent\s*core|bedrock", "agentcore"),
    (r"claude agent sdk|agent sdk", "claude-agent-sdk"),
    (r"harness engineering|\bharness\b", "harness-engineering"),
    (r"wiki.?ticket|wicked ticket|worklog", "wiki-ticket"),
    (r"\bokf\b|graph engineering", "okf-graph"),
    (r"lang(?:chain|graph)|deepagents", "langchain"),
    (r"claude code|managed agents|\bskills\b|subagent", "claude-code"),
    (r"ai news", "ai-news"),
    (r"fail in production|production agent", "production-agents"),
    (r"law changes|agreements", "legal-ops"),
    (r"loop engineering|spec-driven|fishbowl", "loop-engineering"),
]

SUBJECT_TITLES: dict[str, str] = {
    "crewai": "CrewAI",
    "agentcore": "AWS Bedrock AgentCore",
    "claude-agent-sdk": "Claude Agent SDK",
    "harness-engineering": "Harness Engineering",
    "wiki-ticket": "Wiki Ticket / Worklog",
    "okf-graph": "OKF / Graph Engineering",
    "langchain": "LangChain / DeepAgents",
    "claude-code": "Claude Code",
    "ai-news": "AI News Roundups",
    "production-agents": "Production Agents",
    "legal-ops": "Legal / Agreements",
    "loop-engineering": "Loop Engineering / SDD",
    "general": "General",
}

TYPE_TITLES: dict[str, str] = {
    "news": "News / Newsletter",
    "tutorial": "Tutorials / Series",
    "guide": "Guides",
    "one-off": "One-off Essays",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def http_get(url: str) -> str:
    """Fetch URL text; prefer curl when urllib is blocked (Substack often 403s)."""
    try:
        import urllib.request

        req = urllib.request.Request(
            url,
            headers={"User-Agent": "okf-plugin-integration/0.1 (+local-test)"},
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception:
        r = subprocess.run(
            ["curl", "-sL", "-A", "okf-plugin-integration/0.1", url],
            capture_output=True,
            text=True,
            timeout=90,
        )
        if r.returncode != 0:
            raise RuntimeError(f"curl failed for {url}: {r.stderr or r.stdout}")
        return r.stdout


def yaml_quote(s: str) -> str:
    """Single-line YAML scalar safe for the simple okf-graph frontmatter parser."""
    s = (s or "").replace("\n", " ").replace("\r", " ").strip()
    s = s.replace('"', "'")
    return f'"{s}"'


def slugify(text: str) -> str:
    s = text.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s[:80] or "article"


def paths(out_root: Path) -> dict[str, Path]:
    base = out_root
    substack = base / "substack"
    return {
        "root": base,
        "substack": substack,
        "raw": substack / "raw",
        "archive": substack / "raw" / "archive.json",
        "feed": substack / "raw" / "feed.xml",
        "articles": substack / "articles.json",
        "taxonomy": substack / "taxonomy.json",
        "bundle": base / "substack-okf",
    }


# ---------------------------------------------------------------------------
# Classify
# ---------------------------------------------------------------------------


def classify_type(title: str, subtitle: str = "") -> str:
    t = f"{title} {subtitle}".lower()
    if re.search(r"ai news|volume\s+\d+|newsletter", t):
        return "news"
    if re.search(r"\bguide\b|complete guide|walkthrough|\bprimer\b", t):
        return "guide"
    if re.search(r"tutorial|hands.?on|from scratch|step.by.step|how to", t):
        return "tutorial"
    # Numbered / roman series common in this catalog
    if re.search(
        r"\b(crewai|agentcore|agent core)\b.*\b([ivxlc]+|\d+)\b"
        r"|\b([ivxlc]+|\d+)\b.*\b(crewai|agentcore|agent core)\b",
        t,
    ):
        return "tutorial"
    if re.search(r":\s*(the |your |stop |use |host |remembering|what )", t):
        return "tutorial"
    return "one-off"


def classify_subjects(title: str, subtitle: str = "") -> list[str]:
    t = f"{title} {subtitle}".lower()
    found: list[str] = []
    for pat, name in SUBJECT_RULES:
        if re.search(pat, t) and name not in found:
            found.append(name)
    return found or ["general"]


def apply_classification(article: dict[str, Any]) -> dict[str, Any]:
    title = str(article.get("title") or "")
    subtitle = str(article.get("subtitle") or "")
    article = dict(article)
    article["type"] = classify_type(title, subtitle)
    article["subjects"] = classify_subjects(title, subtitle)
    return article


# ---------------------------------------------------------------------------
# Fetch
# ---------------------------------------------------------------------------


def fetch_archive(source: str, limit: int) -> list[dict[str, Any]]:
    base = source.rstrip("/") + "/api/v1/archive"
    all_posts: list[dict[str, Any]] = []
    offset = 0
    page = 50
    while len(all_posts) < limit:
        url = f"{base}?sort=new&search=&offset={offset}&limit={page}"
        batch = json.loads(http_get(url))
        if not isinstance(batch, list) or not batch:
            break
        all_posts.extend(batch)
        offset += len(batch)
        if len(batch) < page:
            break
    return all_posts[:limit]


def normalize_post(raw: dict[str, Any], source: str) -> dict[str, Any]:
    slug = str(raw.get("slug") or slugify(str(raw.get("title") or "post")))
    url = str(raw.get("canonical_url") or f"{source.rstrip('/')}/p/{slug}")
    subtitle = (
        raw.get("subtitle")
        or raw.get("description")
        or raw.get("search_engine_description")
        or ""
    )
    # archive items often lack body; keep optional truncated fields if present
    excerpt = ""
    for key in ("description", "truncated_text", "subtitle"):
        val = raw.get(key)
        if isinstance(val, str) and val.strip():
            excerpt = val.strip()[:400]
            break
    return {
        "id": raw.get("id"),
        "slug": slug,
        "title": str(raw.get("title") or slug),
        "url": url,
        "post_date": str(raw.get("post_date") or utc_now()),
        "subtitle": str(subtitle or ""),
        "excerpt": excerpt,
    }


def cmd_fetch(out_root: Path, source: str, limit: int) -> int:
    p = paths(out_root)
    p["raw"].mkdir(parents=True, exist_ok=True)

    print(f"Fetching up to {limit} posts from {source} …")
    raw_posts = fetch_archive(source, limit)
    p["archive"].write_text(json.dumps(raw_posts, indent=2), encoding="utf-8")

    try:
        feed = http_get(source.rstrip("/") + "/feed")
        p["feed"].write_text(feed, encoding="utf-8")
    except Exception as exc:
        print(f"  (feed snapshot skipped: {exc})")

    articles = [apply_classification(normalize_post(r, source)) for r in raw_posts]
    payload = {
        "source": source,
        "fetched_at": utc_now(),
        "limit": limit,
        "count": len(articles),
        "articles": articles,
    }
    p["articles"].write_text(json.dumps(payload, indent=2), encoding="utf-8")

    tax = {
        "types": sorted(ARTICLE_TYPES),
        "subject_rules": [{"pattern": a, "subject": b} for a, b in SUBJECT_RULES],
        "applied": {
            "types": dict(Counter(a["type"] for a in articles)),
            "subjects": dict(Counter(s for a in articles for s in a["subjects"])),
        },
        "updated_at": utc_now(),
    }
    p["taxonomy"].write_text(json.dumps(tax, indent=2), encoding="utf-8")

    print(f"  wrote {p['archive']} ({len(raw_posts)} raw)")
    print(f"  wrote {p['articles']} ({len(articles)} classified)")
    print(f"  type histogram: {tax['applied']['types']}")
    print(f"  subject histogram: {tax['applied']['subjects']}")
    if len(articles) < limit:
        print(f"  note: only {len(articles)} posts available (requested {limit})")
    return 0 if articles else 1


def cmd_classify(out_root: Path) -> int:
    p = paths(out_root)
    if not p["articles"].is_file():
        print(f"missing {p['articles']}; run fetch first", file=sys.stderr)
        return 1
    data = json.loads(p["articles"].read_text(encoding="utf-8"))
    articles = [apply_classification(a) for a in data.get("articles") or []]
    data["articles"] = articles
    data["count"] = len(articles)
    data["classified_at"] = utc_now()
    p["articles"].write_text(json.dumps(data, indent=2), encoding="utf-8")

    tax = {
        "types": sorted(ARTICLE_TYPES),
        "subject_rules": [{"pattern": a, "subject": b} for a, b in SUBJECT_RULES],
        "applied": {
            "types": dict(Counter(a["type"] for a in articles)),
            "subjects": dict(Counter(s for a in articles for s in a["subjects"])),
        },
        "updated_at": utc_now(),
    }
    p["taxonomy"].write_text(json.dumps(tax, indent=2), encoding="utf-8")
    print(f"reclassified {len(articles)} articles")
    print(f"  types: {tax['applied']['types']}")
    print(f"  subjects: {tax['applied']['subjects']}")
    return 0


# ---------------------------------------------------------------------------
# Emit OKF bundle
# ---------------------------------------------------------------------------


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def article_path(slug: str) -> str:
    return f"knowledge/articles/{slug}.md"


def type_path(t: str) -> str:
    return f"knowledge/types/{t}.md"


def subject_path(s: str) -> str:
    return f"knowledge/subjects/{s}.md"


def emit_article(bundle: Path, art: dict[str, Any], ts: str) -> None:
    slug = art["slug"]
    atype = art["type"]
    subjects = art["subjects"]
    tags = ["article", atype] + list(subjects)
    tag_s = ", ".join(tags)
    subjects_s = ", ".join(subjects)
    ts_art = art.get("post_date") or ts
    if ts_art.endswith("+00:00"):
        ts_art = ts_art.replace("+00:00", "Z")
    if "T" not in ts_art:
        ts_art = ts_art + "T00:00:00Z"

    links_yaml = [
        f"  - target: /{type_path(atype)}",
        "    rel: related_to",
    ]
    for s in subjects:
        links_yaml.append(f"  - target: /{subject_path(s)}")
        links_yaml.append("    rel: related_to")

    desc = art.get("subtitle") or art.get("excerpt") or art["title"]
    body_related = [f"- [{TYPE_TITLES.get(atype, atype)}](/{type_path(atype)})"]
    for s in subjects:
        body_related.append(f"- [{SUBJECT_TITLES.get(s, s)}](/{subject_path(s)})")

    excerpt = art.get("excerpt") or art.get("subtitle") or ""
    content = f"""---
type: Reference
title: {yaml_quote(art['title'])}
description: {yaml_quote(str(desc)[:240])}
tags: [{tag_s}]
timestamp: {ts_art}
status: active
verified: false
generated: true
sources: [{art['url']}]
article_type: {atype}
subjects: [{subjects_s}]
links:
{chr(10).join(links_yaml)}
---

# {art['title']}

## Overview

{desc}

## Canonical URL

[{art['url']}]({art['url']})

## Classification

- **Type:** [{TYPE_TITLES.get(atype, atype)}](/{type_path(atype)})
- **Subjects:** {', '.join(f'[{SUBJECT_TITLES.get(s, s)}](/{subject_path(s)})' for s in subjects)}

## Excerpt

{excerpt or '_No excerpt in archive payload._'}

## Related

{chr(10).join(body_related)}
"""
    write(bundle / article_path(slug), content)


def emit_type_hub(bundle: Path, atype: str, members: list[dict[str, Any]], ts: str) -> None:
    title = TYPE_TITLES.get(atype, atype)
    links = "\n".join(
        f"- [{a['title']}](/{article_path(a['slug'])})" for a in members
    ) or "- _No articles in this type for the current sample._"
    content = f"""---
type: Reference
title: {yaml_quote(title)}
description: {yaml_quote(f'Article type hub: {title} ({len(members)} articles)')}
tags: [type-hub, {atype}]
timestamp: {ts}
status: active
verified: false
generated: true
---

# {title}

## Overview

Hub for articles classified as **{atype}** in the Substack → OKF integration sample.

## Articles ({len(members)})

{links}

## Related

- [Knowledge index](/knowledge/index.md)
- [Content librarian](/agents/content-librarian.md)
"""
    write(bundle / type_path(atype), content)


def emit_subject_hub(bundle: Path, subject: str, members: list[dict[str, Any]], ts: str) -> None:
    title = SUBJECT_TITLES.get(subject, subject)
    links = "\n".join(
        f"- [{a['title']}](/{article_path(a['slug'])})" for a in members
    ) or "- _No articles for this subject in the current sample._"
    content = f"""---
type: Reference
title: {yaml_quote(title)}
description: {yaml_quote(f'Subject hub: {title} ({len(members)} articles)')}
tags: [subject-hub, {subject}]
timestamp: {ts}
status: active
verified: false
generated: true
---

# {title}

## Overview

Subject hub for **{title}** articles from Hightower's AI Harness Engineering Substack.

## Articles ({len(members)})

{links}

## Related

- [Knowledge index](/knowledge/index.md)
- [Content librarian](/agents/content-librarian.md)
"""
    write(bundle / subject_path(subject), content)


def cmd_emit(out_root: Path) -> int:
    p = paths(out_root)
    if not p["articles"].is_file():
        print(f"missing {p['articles']}; run fetch first", file=sys.stderr)
        return 1

    data = json.loads(p["articles"].read_text(encoding="utf-8"))
    articles: list[dict[str, Any]] = data.get("articles") or []
    if not articles:
        print("no articles to emit", file=sys.stderr)
        return 1

    # Ensure classified
    articles = [apply_classification(a) for a in articles]
    data["articles"] = articles
    p["articles"].write_text(json.dumps(data, indent=2), encoding="utf-8")

    bundle = p["bundle"]
    if bundle.exists():
        # clean previous emit (bundle only)
        for md in bundle.rglob("*.md"):
            md.unlink()
    ts = utc_now()
    source = data.get("source") or DEFAULT_SOURCE

    by_type: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_subject: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for a in articles:
        by_type[a["type"]].append(a)
        for s in a["subjects"]:
            by_subject[s].append(a)

    # Articles
    for a in articles:
        emit_article(bundle, a, ts)

    # Type hubs (always emit all four so catalogs are stable)
    for t in sorted(ARTICLE_TYPES):
        emit_type_hub(bundle, t, by_type.get(t, []), ts)

    # Subject hubs
    for s in sorted(by_subject.keys()):
        emit_subject_hub(bundle, s, by_subject[s], ts)

    # Knowledge index
    type_links = "\n".join(
        f"- [{TYPE_TITLES[t]}](/{type_path(t)}) — {len(by_type.get(t, []))} articles"
        for t in sorted(ARTICLE_TYPES)
    )
    subject_links = "\n".join(
        f"- [{SUBJECT_TITLES.get(s, s)}](/{subject_path(s)}) — {len(by_subject[s])} articles"
        for s in sorted(by_subject.keys())
    )
    article_links = "\n".join(
        f"- [{a['title']}](/{article_path(a['slug'])})" for a in articles
    )
    write(
        bundle / "knowledge" / "index.md",
        f"""---
type: Index
title: Knowledge catalog
description: Articles, type hubs, and subject hubs from Substack integration sample.
timestamp: {ts}
tags: [index, knowledge]
---

# Knowledge catalog

Integration sample derived from [{source}]({source}).

## Types

{type_links}

## Subjects

{subject_links}

## Articles ({len(articles)})

{article_links}
""",
    )

    # Agents
    write(
        bundle / "agents" / "content-librarian.md",
        f"""---
type: AgentNode
title: Content Librarian
description: Classifies Substack articles into OKF type and subject hubs and keeps the graph consistent.
resource: agents/content-librarian.md
tags: [agent, integration]
timestamp: {ts}
status: active
verified: false
generated: true
links:
  - target: /workflows/curate-substack.md
    rel: implements
  - target: /knowledge/index.md
    rel: documents
---

# Content Librarian

## Overview

Agent role for the Substack → OKF integration pipeline: fetch archive metadata,
classify by type/subject, emit concept files, and validate the graph.

## Responsibilities

- Pull Substack archive metadata
- Apply deterministic type/subject taxonomy
- Author OKF Reference concepts with absolute links
- Run `okf-graph.py validate` before considering the bundle ready

## Inputs

- Substack archive API or cached `integration/substack/articles.json`

## Outputs

- OKF bundle under `integration/substack-okf/`
- Taxonomy audit JSON

## Routes to

- [Curate Substack workflow](/workflows/curate-substack.md)

## Related knowledge

- [Knowledge catalog](/knowledge/index.md)
""",
    )
    write(
        bundle / "agents" / "index.md",
        f"""---
type: Index
title: Agents
description: Harness agents for the Substack integration sample.
timestamp: {ts}
tags: [index, agents]
---

# Agents

- [Content Librarian](/agents/content-librarian.md)
""",
    )

    # Workflows
    write(
        bundle / "workflows" / "curate-substack.md",
        f"""---
type: Workflow
title: Curate Substack into OKF
description: Fetch, classify, emit, and validate Substack articles as an OKF graph.
tags: [workflow, harness, integration]
timestamp: {ts}
status: active
verified: false
generated: true
links:
  - target: /agents/content-librarian.md
    rel: routes_to
  - target: /knowledge/index.md
    rel: uses
---

# Curate Substack into OKF

## Overview

Local integration workflow exercised by `scripts/substack_okf.py`.

## Stages

1. **Fetch** — archive API → `integration/substack/raw/archive.json`
2. **Classify** — type + subject heuristics → `articles.json`
3. **Emit** — OKF concepts under `integration/substack-okf/`
4. **Validate** — `python3 scripts/okf-graph.py validate integration/substack-okf`

## Agent graph

- Entry: [Content Librarian](/agents/content-librarian.md)
- Knowledge: [catalog](/knowledge/index.md)

## Success criteria

- Requested article count classified
- Zero broken-link errors from `okf-graph.py validate`
- Subject hub impact/pack returns multi-node neighborhoods
""",
    )
    write(
        bundle / "workflows" / "index.md",
        f"""---
type: Index
title: Workflows
description: Harness workflows for the Substack integration sample.
timestamp: {ts}
tags: [index, workflows]
---

# Workflows

- [Curate Substack into OKF](/workflows/curate-substack.md)
""",
    )

    # Root index + log
    write(
        bundle / "index.md",
        f"""---
okf_version: "0.2"
title: Substack Integration OKF Bundle
description: Local integration sample — Hightower AI Harness Engineering articles as knowledge + harness graph.
timestamp: {ts}
tags: [okf, integration, substack]
generated: true
---

# Substack Integration OKF Bundle

Self-contained OKF graph built from **{len(articles)}** articles on [{source}]({source}).

## Dual purpose

1. **Knowledge graph** — articles organized by type and subject
2. **Agent graph** — content librarian + curate workflow for the pipeline

## Catalogs

- [Knowledge](/knowledge/index.md)
- [Agents](/agents/index.md)
- [Workflows](/workflows/index.md)

## Quick demos

- Impact: `python3 scripts/okf-graph.py impact integration/substack-okf knowledge/subjects/crewai.md`
- Pack: `python3 scripts/okf-graph.py pack integration/substack-okf knowledge/subjects/agentcore.md --hops 2`
- Validate: `python3 scripts/okf-graph.py validate integration/substack-okf`

## Change log

See [log.md](/log.md).
""",
    )
    write(
        bundle / "log.md",
        f"""# log

## {ts[:10]}

- Generated integration bundle from Substack archive ({len(articles)} articles) via `scripts/substack_okf.py`.
- Source: {source}
""",
    )

    print(f"emitted OKF bundle → {bundle}")
    print(f"  articles: {len(articles)}")
    print(f"  types: { {k: len(v) for k, v in by_type.items()} }")
    print(f"  subjects: { {k: len(v) for k, v in by_subject.items()} }")
    return 0


# ---------------------------------------------------------------------------
# Verify (integration asserts)
# ---------------------------------------------------------------------------


def run_graph(*args: str) -> tuple[int, dict[str, Any] | None, str]:
    cmd = [sys.executable, str(GRAPH_PY), *args]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO_ROOT))
    out = (r.stdout or "") + (r.stderr or "")
    data = None
    try:
        data = json.loads(r.stdout)
    except Exception:
        pass
    return r.returncode, data, out


def cmd_verify(out_root: Path, min_count: int = 1) -> int:
    p = paths(out_root)
    failures: list[str] = []

    if not p["articles"].is_file():
        print("FAIL: articles.json missing", file=sys.stderr)
        return 1
    data = json.loads(p["articles"].read_text(encoding="utf-8"))
    articles = data.get("articles") or []
    print(f"articles: {len(articles)} (min {min_count})")
    if len(articles) < min_count:
        failures.append(f"expected ≥{min_count} articles, got {len(articles)}")

    for a in articles:
        if a.get("type") not in ARTICLE_TYPES:
            failures.append(f"bad type for {a.get('slug')}: {a.get('type')}")
        if not a.get("subjects"):
            failures.append(f"no subjects for {a.get('slug')}")

    bundle = p["bundle"]
    if not bundle.is_dir() or not (bundle / "index.md").is_file():
        failures.append(f"bundle missing or incomplete: {bundle}")
        _print_result(failures, articles, None, None, None)
        return 1

    # Count article files
    art_files = list((bundle / "knowledge" / "articles").glob("*.md"))
    print(f"article concepts on disk: {len(art_files)}")
    if len(art_files) != len(articles):
        failures.append(f"article file count {len(art_files)} != json {len(articles)}")

    code, validate, raw = run_graph("validate", str(bundle))
    errors = (validate or {}).get("error_count", 99) if validate else 99
    print(f"validate: exit={code} error_count={errors} concepts={(validate or {}).get('concept_count')}")
    if code != 0 or errors:
        failures.append(f"validate failed: errors={errors}")
        if validate and validate.get("issues"):
            for iss in validate["issues"][:10]:
                if iss.get("severity") == "error":
                    print(f"  ERROR {iss.get('path')}: {iss.get('message')}")

    # Pick subject with most members for impact/pack
    by_subject: Counter[str] = Counter()
    for a in articles:
        for s in a.get("subjects") or []:
            by_subject[s] += 1
    # Prefer multi-article non-news hubs if available
    candidates = [s for s, n in by_subject.most_common() if n >= 2 and s != "ai-news"]
    if not candidates:
        candidates = [s for s, n in by_subject.most_common() if n >= 1]
    hub = candidates[0] if candidates else None
    impact = pack = None
    if hub:
        hub_rel = subject_path(hub)
        code_i, impact, _ = run_graph("impact", str(bundle), hub_rel)
        # Articles link to hub (inbound on hub); hub links to articles (outbound)
        inbound = (impact or {}).get("inbound") or []
        outbound = (impact or {}).get("outbound") or []
        article_hits = [
            x
            for x in inbound + outbound
            if str(x.get("id", "")).startswith("knowledge/articles/")
        ]
        print(
            f"impact on {hub_rel}: inbound={len(inbound)} outbound={len(outbound)} "
            f"article_hits={len(article_hits)}"
        )
        if code_i != 0 or not article_hits:
            failures.append(f"impact on {hub} did not return article neighbors")

        code_p, pack, _ = run_graph("pack", str(bundle), hub_rel, "--hops", "2", "--max-nodes", "30")
        included = (pack or {}).get("included") or []
        print(f"pack on {hub_rel}: included={len(included)} exit={code_p}")
        if code_p != 0 or len(included) < 2:
            failures.append(f"pack on {hub} expected ≥2 nodes, got {len(included)}")
    else:
        failures.append("no subject hub available for impact/pack")

    code_o, orphans, _ = run_graph("orphans", str(bundle))
    oc = (orphans or {}).get("count", "?")
    print(f"orphans: {oc}")

    _print_result(failures, articles, validate, impact, pack)
    return 1 if failures else 0


def _print_result(
    failures: list[str],
    articles: list[dict[str, Any]],
    validate: dict[str, Any] | None,
    impact: dict[str, Any] | None,
    pack: dict[str, Any] | None,
) -> None:
    print()
    print("=" * 60)
    if failures:
        print("INTEGRATION TEST: FAIL")
        for f in failures:
            print(f"  - {f}")
    else:
        print("INTEGRATION TEST: PASS")
    print("=" * 60)
    print(f"articles classified: {len(articles)}")
    print(f"types: {dict(Counter(a['type'] for a in articles))}")
    print(f"subjects: {dict(Counter(s for a in articles for s in a['subjects']))}")
    if validate:
        print(
            f"bundle concepts={validate.get('concept_count')} "
            f"edges={validate.get('edge_count')} errors={validate.get('error_count')}"
        )
    if impact:
        print(
            f"impact target={impact.get('target', {}).get('id')} "
            f"inbound={impact.get('stats', {}).get('inbound_count')} "
            f"outbound={impact.get('stats', {}).get('outbound_count')}"
        )
    if pack:
        print(f"pack root={pack.get('root')} included={len(pack.get('included') or [])}")
    print()
    print("Sample classifications:")
    for a in articles[:8]:
        print(f"  [{a['type']:8}] {','.join(a['subjects']):36} | {a['title'][:60]}")
    if len(articles) > 8:
        print(f"  … and {len(articles) - 8} more")


def cmd_run(out_root: Path, source: str, limit: int) -> int:
    if cmd_fetch(out_root, source, limit) != 0:
        return 1
    if cmd_emit(out_root) != 0:
        return 1
    # min_count: accept fewer if source has fewer posts, but prefer limit
    p = paths(out_root)
    data = json.loads(p["articles"].read_text(encoding="utf-8"))
    available = len(data.get("articles") or [])
    min_count = min(limit, available) if available else limit
    return cmd_verify(out_root, min_count=min_count)


def main() -> int:
    ap = argparse.ArgumentParser(description="Substack → OKF local integration test")
    ap.add_argument(
        "command",
        choices=["run", "fetch", "classify", "emit", "verify"],
        help="Pipeline stage (run = fetch+emit+verify)",
    )
    ap.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Max articles to fetch (default 20)",
    )
    ap.add_argument(
        "--source",
        default=DEFAULT_SOURCE,
        help=f"Substack publication base URL (default {DEFAULT_SOURCE})",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help=f"Output root (default {DEFAULT_OUT})",
    )
    args = ap.parse_args()
    out = args.out.resolve()

    if args.command == "fetch":
        return cmd_fetch(out, args.source, args.limit)
    if args.command == "classify":
        return cmd_classify(out)
    if args.command == "emit":
        return cmd_emit(out)
    if args.command == "verify":
        return cmd_verify(out, min_count=1)
    if args.command == "run":
        return cmd_run(out, args.source, args.limit)
    return 1


if __name__ == "__main__":
    sys.exit(main())
