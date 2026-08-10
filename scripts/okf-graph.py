#!/usr/bin/env python3
"""Lightweight OKF graph utilities when okfcli is unavailable.

Usage:
  okf-graph.py impact <bundle> <concept-path>
  okf-graph.py backlinks <bundle> <concept-path>
  okf-graph.py subgraph <bundle> <concept-path> [--hops N]
  okf-graph.py pack <bundle> <concept-path> [--hops N] [--max-nodes N]
  okf-graph.py edges <bundle> [--from PATH] [--rel REL]
  okf-graph.py graph <bundle> [--format mermaid|json|html] [--focus PATH] [--hops N]
  okf-graph.py validate <bundle> [--strict]
  okf-graph.py orphans <bundle>
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
# The label alternation keeps `[^\]]` — the entirety of the previous pattern's
# label language — and *adds* balanced `[...]` pairs, tried first. Keeping the
# old branch is what makes this a superset: a label may legitimately end in a
# backslash (`[a\](/c.md)`), which an escape-aware branch alone would swallow.
# The quantifier is `+`, not `*`, so an empty label stays unmatched as before.
LINK_RE = re.compile(r"\[((?:\[[^\[\]]*\]|[^\]])+)\]\(([^)]+)\)")

# Common typed-edge relations (non-breaking; Markdown links remain canonical)
KNOWN_RELS = frozenset(
    {
        "depends_on",
        "routes_to",
        "implements",
        "documents",
        "uses",
        "owns",
        "supersedes",
        "related_to",
        "tracks",
        "maps_to",
        "released_in",
        # okf-agent-graph (AGER) typed-edge vocabulary — AGER_SPEC.md
        # "## Typed edges (AGER additions)". 5 of AGER's 31 rels already
        # overlap the set above (depends_on, implements, related_to,
        # routes_to, uses); these are the other 26. Kept in sync by
        # test_known_rels_covers_ager_vocabulary in tests/test_okf_graph.py.
        "aggregates_from",
        "appends_to",
        "binds_secret",
        "blocks",
        "budgets",
        "compensates_with",
        "controlled_by",
        "delegates_to",
        "derived_from",
        "fans_in_from",
        "fans_out_to",
        "guards",
        "handoffs_to",
        "isolates_context",
        "judges",
        "models_with",
        "on_failure",
        "output_of",
        "rate_limited_by",
        "reads_from",
        "records_to",
        "retries_with",
        "retrieves_from",
        "spawns",
        "triggered_by",
        "writes_to",
    }
)

HIGH_IMPACT_TYPES = frozenset({"AgentNode", "Workflow", "Harness", "SharedState"})
MEDIUM_IMPACT_TYPES = frozenset({"Dataset", "Table", "Metric", "API", "ToolCapability"})


@dataclass
class TypedEdge:
    target: str
    rel: str = "links_to"
    source: str = "markdown"  # markdown | frontmatter


@dataclass
class Concept:
    path: Path
    rel: str
    title: str = ""
    type: str = ""
    status: str = ""
    verified: bool = False
    tags: list[str] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)
    outbound: list[str] = field(default_factory=list)
    edges: list[TypedEdge] = field(default_factory=list)
    # raw link targets that resolved outside the bundle — not edges, but
    # validate reports them instead of letting a typo'd ../../ disappear
    off_bundle: list[str] = field(default_factory=list)


def parse_frontmatter(text: str) -> dict[str, Any]:
    """Parse simple YAML frontmatter including optional typed `links:` lists."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    block = m.group(1)
    meta: dict[str, Any] = {}
    links: list[dict[str, str]] = []
    in_links = False
    current: dict[str, str] | None = None
    # key whose value may turn out to be a block sequence (`tags:` then `- a`)
    pending_list_key: str | None = None

    for raw in block.splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # typed links list
        if re.match(r"^links:\s*$", stripped):
            in_links = True
            current = None
            pending_list_key = None
            continue
        if in_links:
            item = re.match(r"^-\s+(.*)$", stripped)
            if item:
                if current:
                    links.append(current)
                current = {}
                rest = item.group(1)
                if ":" in rest and not rest.startswith("{"):
                    k, _, v = rest.partition(":")
                    current[k.strip()] = v.strip().strip('"').strip("'")
                continue
            if current is not None and re.match(r"^[A-Za-z0-9_]+:", stripped) and not stripped.startswith("-"):
                # continuation fields of list item (indented key: val)
                if line[:1] in (" ", "\t") or (len(line) - len(line.lstrip()) > 0):
                    k, _, v = stripped.partition(":")
                    current[k.strip()] = v.strip().strip('"').strip("'")
                    continue
            # left the links block
            if current:
                links.append(current)
                current = None
            in_links = False
            # fall through to parse this line as normal key

        # block-sequence items belonging to the previous bare `key:`
        if pending_list_key is not None:
            item = re.match(r"^-\s+(.*)$", stripped)
            if item:
                if not isinstance(meta.get(pending_list_key), list):
                    meta[pending_list_key] = []
                meta[pending_list_key].append(item.group(1).strip().strip('"').strip("'"))
                continue
            # no list materialized; the bare key keeps its empty-string value
            pending_list_key = None

        if ":" not in stripped:
            continue
        key, _, val = stripped.partition(":")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if not val:
            # may be followed by a block sequence; stays "" if nothing follows
            pending_list_key = key
            meta[key] = ""
            continue
        if val.lower() in ("true", "false"):
            meta[key] = val.lower() == "true"
        elif val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            meta[key] = (
                [x.strip().strip('"').strip("'") for x in inner.split(",") if x.strip()] if inner else []
            )
        else:
            meta[key] = val

    if current:
        links.append(current)
    if links:
        meta["links"] = links
    return meta


def mermaid_id(rel: str) -> str:
    """Mermaid-safe node id from the *full* relative path.

    Deriving ids from the stem collapses every `index.md` in the bundle into
    one node (sample-okf has seven), and merges `agents/foo.md` with
    `docs/foo.md`.
    """
    ident = re.sub(r"[^A-Za-z0-9_]", "_", rel)
    first = ident[:1]
    return ident if first.isalpha() or first == "_" else "n" + ident


def render_mermaid(edges: list[dict[str, str]], concepts: dict[str, "Concept"]) -> list[str]:
    """`graph LR` body: labelled nodes, then typed edges. Shared by pack and graph."""
    lines = ["graph LR"]
    seen: set[str] = set()
    for e in edges:
        for rel in (e["from"], e["to"]):
            if rel in seen:
                continue
            seen.add(rel)
            c = concepts.get(rel)
            label = (c.title if c else Path(rel).stem).replace('"', "'")
            lines.append(f'  {mermaid_id(rel)}["{label}"]')
    for e in edges:
        a, b = mermaid_id(e["from"]), mermaid_id(e["to"])
        label = e["rel"] if e["rel"] != "links_to" else ""
        lines.append(f"  {a} -->|{label}| {b}" if label else f"  {a} --> {b}")
    return lines


def _normalize_target(
    target: str, source: Path, bundle: Path, off_bundle: list[str] | None = None
) -> str | None:
    """Bundle-relative path for a link target, or None when it is not an edge.

    A target that resolves *outside* the bundle is still worth knowing about
    (usually a typo'd `../../`), so pass `off_bundle` to collect those raw
    targets; `validate` reports them. Everything else — external URLs,
    anchors, non-Markdown files — is silently not an edge, as before.
    """
    t = target.split("#")[0].strip()
    if not t or t.startswith("http") or t.startswith("mailto:"):
        return None
    if t.startswith("/"):
        cand = (bundle / t.lstrip("/")).resolve()
    else:
        cand = (source.parent / t).resolve()
    # Directory links (e.g. /companies/ or companies) → index.md when present
    if cand.is_dir():
        idx = cand / "index.md"
        if idx.is_file():
            cand = idx
    elif not cand.suffix and not cand.exists():
        # path without .md that isn't a file yet — try as dir/index or .md
        as_md = Path(str(cand) + ".md")
        as_idx = cand / "index.md"
        if as_idx.is_file():
            cand = as_idx
        elif as_md.is_file():
            cand = as_md
    try:
        rel = cand.relative_to(bundle.resolve()).as_posix()
    except ValueError:
        if off_bundle is not None and t not in off_bundle:
            off_bundle.append(t)
        return None
    if cand.suffix == ".md" or cand.exists() or rel.endswith(".md"):
        return rel
    return None


def extract_markdown_links(
    text: str, source: Path, bundle: Path, off_bundle: list[str] | None = None
) -> list[TypedEdge]:
    edges: list[TypedEdge] = []
    seen: set[tuple[str, str]] = set()
    for _label, target in LINK_RE.findall(text):
        rel_path = _normalize_target(target, source, bundle, off_bundle)
        if not rel_path:
            continue
        key = (rel_path, "links_to")
        if key in seen:
            continue
        seen.add(key)
        edges.append(TypedEdge(target=rel_path, rel="links_to", source="markdown"))
    return edges


def extract_frontmatter_links(
    meta: dict[str, Any], source: Path, bundle: Path, off_bundle: list[str] | None = None
) -> list[TypedEdge]:
    edges: list[TypedEdge] = []
    for item in meta.get("links") or []:
        if not isinstance(item, dict):
            continue
        target = item.get("target") or item.get("to") or item.get("href") or ""
        rel = (item.get("rel") or item.get("type") or "related_to").strip()
        if rel not in KNOWN_RELS:
            rel = rel or "related_to"
        rel_path = _normalize_target(str(target), source, bundle, off_bundle)
        if not rel_path:
            continue
        edges.append(TypedEdge(target=rel_path, rel=rel, source="frontmatter"))
    return edges


def merge_edges(md_edges: list[TypedEdge], fm_edges: list[TypedEdge]) -> list[TypedEdge]:
    """Frontmatter typed edges enrich/override plain markdown for the same target.

    Unconditional by design: `extract_markdown_links` only ever emits
    `links_to`, so a frontmatter edge is always at least as specific as the
    markdown edge it replaces. The old three-clause guard read like a
    comparison of rels but could not decide anything — every clause was true
    for every frontmatter edge.
    """
    by_target: dict[str, TypedEdge] = {}
    for e in md_edges:
        by_target[e.target] = e
    for e in fm_edges:
        by_target[e.target] = e
    return list(by_target.values())


def load_bundle(bundle: Path) -> dict[str, Concept]:
    concepts: dict[str, Concept] = {}
    for path in sorted(bundle.rglob("*.md")):
        parts = path.relative_to(bundle).parts
        # skip dotfiles *and* dot-directories: pointed at a repo root, .work/,
        # .git/ and .claude/ are not concepts. Relative parts only — the
        # bundle itself may legitimately live under a dot-directory.
        if any(p.startswith(".") for p in parts):
            continue
        rel = path.relative_to(bundle).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        meta = parse_frontmatter(text)
        off_bundle: list[str] = []
        md_edges = extract_markdown_links(text, path, bundle, off_bundle)
        fm_edges = extract_frontmatter_links(meta, path, bundle, off_bundle)
        edges = merge_edges(md_edges, fm_edges)
        c = Concept(
            path=path,
            rel=rel,
            title=str(meta.get("title") or path.stem),
            type=str(meta.get("type") or ("Index" if path.name == "index.md" else "Unknown")),
            status=str(meta.get("status") or ""),
            verified=bool(meta.get("verified", False)),
            tags=list(meta.get("tags") or []) if isinstance(meta.get("tags"), list) else [],
            meta=meta,
            outbound=[e.target for e in edges],
            edges=edges,
            off_bundle=off_bundle,
        )
        concepts[rel] = c
    # Drop outbound edges that do not resolve to loaded concepts (broken links
    # remain detectable via validate, which re-reads edges from disk metadata).
    # Keep edge objects for validate; filter adjacency for graph traversal only.
    for c in concepts.values():
        c.outbound = [t for t in c.outbound if t in concepts]
    return concepts


def build_inbound(concepts: dict[str, Concept]) -> dict[str, list[str]]:
    inbound: dict[str, list[str]] = defaultdict(list)
    for rel, c in concepts.items():
        for tgt in c.outbound:
            if tgt in concepts:
                inbound[tgt].append(rel)
    return inbound


def resolve_concept(concepts: dict[str, Concept], query: str) -> tuple[str | None, list[str]]:
    """Resolve a concept query to a bundle-relative path.

    Returns `(match, candidates)`. Tiers, most specific first: exact path,
    then stem or title, then path suffix. A tier matching more than one
    concept is *ambiguous* — `(None, candidates)` — because answering with
    whichever key `dict` iteration reached first means `impact` and `pack`
    can silently report on the wrong concept.
    """
    q = query.strip().lstrip("/")
    if q in concepts:
        return q, [q]
    q_lower = q.lower()
    named = [
        rel
        for rel, c in concepts.items()
        if Path(rel).stem.lower() == q_lower or c.title.lower() == q_lower
    ]
    suffix = [rel for rel in concepts if rel.endswith(q) or rel.endswith(q + ".md")]
    for tier in (named, suffix):
        if len(tier) == 1:
            return tier[0], tier
        if tier:
            return None, sorted(tier)
    return None, []


def resolve_or_error(concepts: dict[str, Concept], query: str) -> str | None:
    """resolve_concept for the cmd_* layer: prints the JSON error on failure.

    Every caller already answers a falsy return with `return 1`, so ambiguity
    rides the same path as not-found rather than inventing a second one.
    """
    match, candidates = resolve_concept(concepts, query)
    if match:
        return match
    if candidates:
        print(json.dumps({"error": f"ambiguous concept: {query}", "candidates": candidates}))
    else:
        print(json.dumps({"error": f"concept not found: {query}"}))
    return None


def bfs_closure(start: str, edges: dict[str, list[str]], hops: int | None = None) -> list[dict[str, Any]]:
    seen = {start}
    q: deque[tuple[str, int]] = deque([(start, 0)])
    out: list[dict[str, Any]] = []
    while q:
        node, depth = q.popleft()
        if node != start:
            out.append({"id": node, "depth": depth})
        if hops is not None and depth >= hops:
            continue
        for nxt in edges.get(node, []):
            if nxt not in seen:
                seen.add(nxt)
                q.append((nxt, depth + 1))
    return out


ESCALATE = {"medium": "high", "high": "critical"}


def criticality_of(c: Concept) -> str:
    """Impact tier, escalated one level while the concept is unverified.

    medium → high, high → critical. `low` never escalates: an unverified
    Reference is not news.
    """
    criticality = "low"
    if c.type in HIGH_IMPACT_TYPES:
        criticality = "high"
    elif c.type in MEDIUM_IMPACT_TYPES:
        criticality = "medium"
    if not c.verified:
        criticality = ESCALATE.get(criticality, criticality)
    return criticality


def enrich_nodes(concepts: dict[str, Concept], items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for item in items:
        c = concepts.get(item["id"])
        if c is None:
            continue
        result.append(
            {
                **item,
                "title": c.title,
                "type": c.type,
                "status": c.status,
                "verified": c.verified,
                "criticality": criticality_of(c),
            }
        )
    order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    result.sort(key=lambda x: (order.get(x["criticality"], 9), x["depth"], x["title"]))
    return result


def edge_index(concepts: dict[str, Concept]) -> list[dict[str, str]]:
    out = []
    for rel, c in concepts.items():
        for e in c.edges:
            out.append({"from": rel, "to": e.target, "rel": e.rel, "source": e.source})
    return out


def cmd_impact(bundle: Path, concept: str) -> int:
    concepts = load_bundle(bundle)
    inbound_map = build_inbound(concepts)
    outbound_map = {k: v.outbound for k, v in concepts.items()}
    target = resolve_or_error(concepts, concept)
    if not target:
        return 1
    inbound = enrich_nodes(concepts, bfs_closure(target, inbound_map))
    outbound = enrich_nodes(concepts, bfs_closure(target, outbound_map))
    # direct typed edges from/to target
    direct_out = [
        {"to": e.target, "rel": e.rel, "source": e.source}
        for e in concepts[target].edges
        if e.target in concepts
    ]
    direct_in = []
    for rel, c in concepts.items():
        for e in c.edges:
            if e.target == target:
                direct_in.append({"from": rel, "rel": e.rel, "source": e.source})
    payload = {
        "target": {
            "id": target,
            "title": concepts[target].title,
            "type": concepts[target].type,
            "verified": concepts[target].verified,
            "status": concepts[target].status,
        },
        "inbound": inbound,
        "outbound": outbound,
        "direct_edges": {"inbound": direct_in, "outbound": direct_out},
        "suggested_order": [x["id"] for x in inbound],
        "stats": {
            "inbound_count": len(inbound),
            "outbound_count": len(outbound),
            "total_concepts": len(concepts),
            "typed_edge_count": sum(1 for e in concepts[target].edges if e.rel != "links_to"),
        },
    }
    print(json.dumps(payload, indent=2))
    return 0


def cmd_backlinks(bundle: Path, concept: str) -> int:
    concepts = load_bundle(bundle)
    inbound_map = build_inbound(concepts)
    target = resolve_or_error(concepts, concept)
    if not target:
        return 1
    bl = []
    for i in inbound_map.get(target, []):
        rels = [e.rel for e in concepts[i].edges if e.target == target]
        bl.append(
            {
                "id": i,
                "title": concepts[i].title,
                "type": concepts[i].type,
                "rels": rels or ["links_to"],
            }
        )
    print(json.dumps({"target": target, "backlinks": bl}, indent=2))
    return 0


def cmd_subgraph(bundle: Path, concept: str, hops: int) -> int:
    concepts = load_bundle(bundle)
    target = resolve_or_error(concepts, concept)
    if not target:
        return 1
    # One pass: inbound is the mirror of outbound, so walking build_inbound()
    # afterwards only re-added the same pairs for sorted(set(...)) to dedup.
    undirected: dict[str, list[str]] = defaultdict(list)
    for k, c in concepts.items():
        for o in c.outbound:
            undirected[k].append(o)
            undirected[o].append(k)
    undirected = {k: sorted(set(v)) for k, v in undirected.items()}
    nodes = [target] + [x["id"] for x in bfs_closure(target, undirected, hops=hops)]
    node_set = set(nodes)
    edges = []
    for n in nodes:
        for e in concepts[n].edges:
            if e.target in node_set:
                edges.append({"from": n, "to": e.target, "rel": e.rel, "source": e.source})
    print(
        json.dumps(
            {
                "root": target,
                "hops": hops,
                "nodes": [
                    {
                        "id": n,
                        "title": concepts[n].title,
                        "type": concepts[n].type,
                        "verified": concepts[n].verified,
                        "criticality": criticality_of(concepts[n]),
                    }
                    for n in nodes
                ],
                "edges": edges,
            },
            indent=2,
        )
    )
    return 0


def cmd_pack(bundle: Path, concept: str, hops: int, max_nodes: int, undirected: bool = False) -> int:
    """Progressive disclosure context pack — default 2 hops, outbound-only BFS.

    Outbound-only keeps packs inside a theme (e.g. group → members) instead of
    flooding through hub catalogs that link everything. Pass undirected=True
    for neighborhood exploration.
    """
    concepts = load_bundle(bundle)
    outbound_map = {k: list(v.outbound) for k, v in concepts.items()}
    target = resolve_or_error(concepts, concept)
    if not target:
        return 1

    if undirected:
        graph: dict[str, list[str]] = defaultdict(list)
        for k, outs in outbound_map.items():
            for o in outs:
                if o in concepts:
                    graph[k].append(o)
                    graph[o].append(k)
        graph = {k: sorted(set(v)) for k, v in graph.items()}
    else:
        graph = {k: [o for o in outs if o in concepts] for k, outs in outbound_map.items()}

    neighborhood = [target] + [
        x["id"] for x in bfs_closure(target, graph, hops=hops) if x["id"] in concepts
    ]

    def score(nid: str) -> tuple:
        c = concepts.get(nid)
        if c is None:
            return (9, 9, 9, nid)
        # prefer verified high-impact, keep root first
        return (
            0 if nid == target else 1,
            0 if c.verified else 1,
            0 if c.type in HIGH_IMPACT_TYPES else 1,
            c.title.lower(),
        )

    ranked = sorted((n for n in neighborhood if n in concepts), key=score)
    included = ranked[: max(1, max_nodes)]
    excluded = [n for n in ranked if n not in included]
    node_set = set(included)
    edges = []
    for n in included:
        for e in concepts[n].edges:
            if e.target in node_set:
                edges.append({"from": n, "to": e.target, "rel": e.rel})

    # read order: root, then high-impact, then by title
    read_order = sorted(
        included,
        key=lambda n: (
            0 if n == target else 1,
            0 if concepts[n].type in HIGH_IMPACT_TYPES else 1,
            0 if concepts[n].type == "SharedState" else 1,
            concepts[n].title.lower(),
        ),
    )

    lines = [
        f"# Context pack: {concepts[target].title}",
        f"Hops: {hops} | Nodes: {len(included)}/{len(neighborhood)} | "
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}",
        "",
        "## Entry",
        f"- `{target}` — {concepts[target].type} — {concepts[target].meta.get('description', '')}",
        "",
        "## Included concepts (read order)",
    ]
    for i, n in enumerate(read_order, 1):
        c = concepts[n]
        flag = ""
        if not c.verified and c.type in HIGH_IMPACT_TYPES:
            flag = " ⚠ unverified high-impact"
        lines.append(f"{i}. **{c.title}** (`{n}`) — {c.type}{flag}")

    lines += ["", "## Graph (Mermaid)", "```mermaid"]
    lines += render_mermaid(edges, concepts)
    lines.append("```")

    if excluded:
        lines += ["", "## Excluded (available on request)"]
        for n in excluded[:15]:
            lines.append(f"- {concepts[n].title} (`{n}`)")
        if len(excluded) > 15:
            lines.append(f"- … and {len(excluded) - 15} more")

    pack_md = "\n".join(lines) + "\n"
    payload = {
        "root": target,
        "hops": hops,
        "max_nodes": max_nodes,
        "included": read_order,
        "excluded": excluded,
        "edges": edges,
        "markdown": pack_md,
    }
    print(json.dumps(payload, indent=2))
    return 0


def cmd_edges(bundle: Path, from_path: str | None, rel_filter: str | None) -> int:
    concepts = load_bundle(bundle)
    edges = edge_index(concepts)
    if from_path:
        resolved = resolve_or_error(concepts, from_path)
        if not resolved:
            return 1
        edges = [e for e in edges if e["from"] == resolved]
    if rel_filter:
        edges = [e for e in edges if e["rel"] == rel_filter]
    typed = sum(1 for e in edges if e["rel"] != "links_to")
    print(json.dumps({"edges": edges, "count": len(edges), "typed_count": typed}, indent=2))
    return 0


def render_html(
    nodes: list[str],
    edges: list[dict[str, str]],
    concepts: dict[str, Concept],
    caption: str,
    mermaid: list[str],
) -> str:
    """Self-contained page: Mermaid source plus node/edge tables.

    No CDN, no JS, no network fetches — the file must open from disk and from
    a locked-down viewer. Renderers that understand `pre.mermaid` draw the
    diagram; everywhere else the tables carry the same information.
    """
    e = html.escape
    diagram = e("\n".join(mermaid))
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    node_rows = "\n".join(
        f"<tr><td>{e(concepts[n].title)}</td><td><code>{e(n)}</code></td>"
        f"<td>{e(concepts[n].type)}</td><td>{'yes' if concepts[n].verified else 'no'}</td></tr>"
        for n in nodes
    )
    edge_rows = "\n".join(
        f"<tr><td><code>{e(x['from'])}</code></td><td>{e(x['rel'])}</td>"
        f"<td><code>{e(x['to'])}</code></td></tr>"
        for x in edges
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>OKF graph — {e(caption)}</title>
<style>
  body {{ font-family: system-ui, sans-serif; margin: 2rem auto; max-width: 60rem;
         padding: 0 1rem; line-height: 1.5; }}
  h1 {{ margin-bottom: 0.2rem; }}
  .meta {{ color: #666; font-size: 0.9rem; margin-bottom: 1.5rem; }}
  pre {{ background: #f6f6f6; padding: 1rem; overflow-x: auto; border-radius: 4px; }}
  table {{ border-collapse: collapse; width: 100%; margin-bottom: 2rem; }}
  th, td {{ border-bottom: 1px solid #ddd; padding: 0.4rem 0.6rem;
            text-align: left; vertical-align: top; }}
  th {{ background: #f0f0f0; }}
  code {{ font-size: 0.85em; }}
  @media (prefers-color-scheme: dark) {{
    body {{ background: #16181c; color: #e6e6e6; }}
    .meta {{ color: #9aa0a6; }}
    pre {{ background: #22252a; }}
    th {{ background: #22252a; }}
    th, td {{ border-bottom-color: #383c42; }}
  }}
</style>
</head>
<body>
<h1>OKF graph</h1>
<p class="meta">{e(caption)} · {len(nodes)} concepts · {len(edges)} edges ·
generated {stamp}</p>

<h2>Diagram</h2>
<pre class="mermaid">{diagram}</pre>

<h2>Concepts</h2>
<table>
<thead><tr><th>Title</th><th>Path</th><th>Type</th><th>Verified</th></tr></thead>
<tbody>
{node_rows}
</tbody>
</table>

<h2>Edges</h2>
<table>
<thead><tr><th>From</th><th>Rel</th><th>To</th></tr></thead>
<tbody>
{edge_rows}
</tbody>
</table>
</body>
</html>
"""


def cmd_graph(bundle: Path, fmt: str, focus: str | None, hops: int) -> int:
    """Whole-bundle or focused graph view.

    `json` prints JSON like every other subcommand; `mermaid` and `html` print
    the raw artifact. Unlike `pack` — whose JSON envelope carries included /
    excluded / edges *alongside* its `markdown` byproduct — a rendered graph is
    the only product here, so wrapping it would force every caller through
    `jq -r` before it could be pasted into a doc or written to a file. `--format
    json` already covers the machine-readable case.
    """
    concepts = load_bundle(bundle)
    root: str | None = None
    nodes = sorted(concepts)

    if focus:
        root = resolve_or_error(concepts, focus)
        if not root:
            return 1
        undirected: dict[str, list[str]] = defaultdict(list)
        for k, c in concepts.items():
            for o in c.outbound:
                undirected[k].append(o)
                undirected[o].append(k)
        neighbors = {k: sorted(set(v)) for k, v in undirected.items()}
        nodes = [root] + [x["id"] for x in bfs_closure(root, neighbors, hops=hops)]

    node_set = set(nodes)
    edges = [e for e in edge_index(concepts) if e["from"] in node_set and e["to"] in node_set]

    if fmt == "json":
        print(
            json.dumps(
                {
                    "bundle": str(bundle),
                    "focus": root,
                    "hops": hops if root else None,
                    "nodes": [
                        {
                            "id": n,
                            "title": concepts[n].title,
                            "type": concepts[n].type,
                            "verified": concepts[n].verified,
                        }
                        for n in nodes
                    ],
                    "edges": [
                        {"from": e["from"], "to": e["to"], "rel": e["rel"]} for e in edges
                    ],
                },
                indent=2,
            )
        )
        return 0

    lines = render_mermaid(edges, concepts)
    # render_mermaid only declares nodes it sees on an edge; isolated concepts
    # would otherwise disappear from the diagram but stay in the JSON view.
    linked = {e["from"] for e in edges} | {e["to"] for e in edges}
    for n in nodes:
        if n not in linked:
            label = concepts[n].title.replace('"', "'")
            lines.append(f'  {mermaid_id(n)}["{label}"]')

    caption = f"{root} @ {hops} hops" if root else f"{bundle.name} (whole bundle)"
    if fmt == "html":
        print(render_html(nodes, edges, concepts, caption, lines), end="")
    else:
        print("```mermaid")
        print("\n".join(lines))
        print("```")
    return 0


def cmd_validate(bundle: Path, strict: bool = False) -> int:
    concepts = load_bundle(bundle)
    issues: list[dict[str, str]] = []
    if not (bundle / "index.md").exists():
        issues.append({"severity": "error", "message": "missing root index.md"})
    for rel, c in concepts.items():
        # Structural files carry no type/title of their own: any index.md (its
        # type is assigned on load) and the bundle's root log.md. Only those two
        # checks are excused -- their LINKS are validated like anyone else's.
        structural = c.path.name == "index.md" or rel == "log.md"
        if not structural:
            if c.type in ("", "Unknown"):
                issues.append({"severity": "warn", "path": rel, "message": "missing or unknown type"})
            if not c.meta.get("title"):
                issues.append({"severity": "warn", "path": rel, "message": "missing title"})
        # warn, not error: the default exit code must stay 0 for the skills
        # and okf-curate.sh; --strict gates these in CI.
        for t in c.off_bundle:
            issues.append(
                {"severity": "warn", "path": rel, "message": f"link outside bundle → {t}"}
            )
        for e in c.edges:
            if e.target not in concepts:
                issues.append({"severity": "error", "path": rel, "message": f"broken link → {e.target}"})
            if e.source == "frontmatter" and e.rel not in KNOWN_RELS and e.rel != "links_to":
                issues.append(
                    {
                        "severity": "info",
                        "path": rel,
                        "message": f"non-standard rel '{e.rel}' (allowed but uncommon)",
                    }
                )
        # TicketLink hygiene
        if c.type == "TicketLink":
            if not c.meta.get("external_id") and not c.meta.get("worklog_id"):
                issues.append(
                    {
                        "severity": "warn",
                        "path": rel,
                        "message": "TicketLink missing external_id/worklog_id",
                    }
                )
    inbound = build_inbound(concepts)
    orphans = [
        rel
        for rel, c in concepts.items()
        if rel not in ("index.md", "log.md")
        and c.path.name != "index.md"
        and not inbound.get(rel)
        and not c.outbound
    ]
    for o in orphans:
        issues.append({"severity": "info", "path": o, "message": "orphan (no inbound or outbound links)"})
    for rel, c in concepts.items():
        if c.type in HIGH_IMPACT_TYPES and not c.verified:
            issues.append(
                {
                    "severity": "warn",
                    "path": rel,
                    "message": f"unverified high-impact {c.type}",
                }
            )
    errors = sum(1 for i in issues if i["severity"] == "error")
    warnings = sum(1 for i in issues if i["severity"] == "warn")
    print(
        json.dumps(
            {
                "bundle": str(bundle),
                "concept_count": len(concepts),
                "edge_count": sum(len(c.edges) for c in concepts.values()),
                "issues": issues,
                "error_count": errors,
                "warn_count": warnings,
                "strict": strict,
            },
            indent=2,
        )
    )
    # Default stays lenient: the skills call validate and expect 0 on warnings.
    # --strict is for CI, which needs warnings to actually gate.
    return 1 if errors or (strict and warnings) else 0


def cmd_orphans(bundle: Path) -> int:
    concepts = load_bundle(bundle)
    inbound = build_inbound(concepts)
    orphans = []
    for rel, c in concepts.items():
        if rel in ("index.md", "log.md") or c.path.name == "index.md":
            continue
        if not inbound.get(rel) and not c.outbound:
            orphans.append({"id": rel, "title": c.title, "type": c.type})
    print(json.dumps({"orphans": orphans, "count": len(orphans)}, indent=2))
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="OKF graph utilities (okfcli fallback)")
    sub = p.add_subparsers(dest="cmd", required=True)

    for name in ("impact", "backlinks"):
        s = sub.add_parser(name)
        s.add_argument("bundle")
        s.add_argument("concept")

    s = sub.add_parser("subgraph")
    s.add_argument("bundle")
    s.add_argument("concept")
    s.add_argument("--hops", type=int, default=2)

    s = sub.add_parser("pack", help="Progressive disclosure context pack (default 2 hops, outbound)")
    s.add_argument("bundle")
    s.add_argument("concept")
    s.add_argument("--hops", type=int, default=2)
    s.add_argument("--max-nodes", type=int, default=20)
    s.add_argument(
        "--undirected",
        action="store_true",
        help="Explore both inbound and outbound neighbors (can flood via hub indexes)",
    )

    s = sub.add_parser("edges", help="List edges (optional typed rel filter)")
    s.add_argument("bundle")
    s.add_argument("--from", dest="from_path", default=None)
    s.add_argument("--rel", dest="rel_filter", default=None)

    s = sub.add_parser("graph", help="Render the bundle (or a focused neighborhood)")
    s.add_argument("bundle")
    s.add_argument("--format", dest="fmt", choices=("mermaid", "json", "html"), default="mermaid")
    s.add_argument("--focus", default=None, help="Scope to this concept's neighborhood")
    s.add_argument("--hops", type=int, default=2, help="Neighborhood radius for --focus")

    s = sub.add_parser("validate")
    s.add_argument("bundle")
    s.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero on warnings too (for CI gates)",
    )

    s = sub.add_parser("orphans")
    s.add_argument("bundle")

    args = p.parse_args()
    bundle = Path(args.bundle).resolve()
    if not bundle.is_dir():
        print(json.dumps({"error": f"bundle not found: {bundle}"}))
        return 1

    if args.cmd == "impact":
        return cmd_impact(bundle, args.concept)
    if args.cmd == "backlinks":
        return cmd_backlinks(bundle, args.concept)
    if args.cmd == "subgraph":
        return cmd_subgraph(bundle, args.concept, args.hops)
    if args.cmd == "pack":
        return cmd_pack(bundle, args.concept, args.hops, args.max_nodes, undirected=args.undirected)
    if args.cmd == "edges":
        return cmd_edges(bundle, args.from_path, args.rel_filter)
    if args.cmd == "graph":
        return cmd_graph(bundle, args.fmt, args.focus, args.hops)
    if args.cmd == "validate":
        return cmd_validate(bundle, strict=args.strict)
    if args.cmd == "orphans":
        return cmd_orphans(bundle)
    return 1


if __name__ == "__main__":
    sys.exit(main())
