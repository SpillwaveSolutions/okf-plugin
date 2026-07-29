#!/usr/bin/env python3
"""Lightweight OKF graph utilities when okfcli is unavailable.

Usage:
  okf-graph.py impact <bundle> <concept-path>
  okf-graph.py backlinks <bundle> <concept-path>
  okf-graph.py subgraph <bundle> <concept-path> [--hops N]
  okf-graph.py pack <bundle> <concept-path> [--hops N] [--max-nodes N]
  okf-graph.py edges <bundle> [--from PATH] [--rel REL]
  okf-graph.py validate <bundle>
  okf-graph.py orphans <bundle>
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

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

    for raw in block.splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # typed links list
        if re.match(r"^links:\s*$", stripped):
            in_links = True
            current = None
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

        if ":" not in stripped:
            continue
        key, _, val = stripped.partition(":")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
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


def _normalize_target(target: str, source: Path, bundle: Path) -> str | None:
    t = target.split("#")[0].strip()
    if not t or t.startswith("http") or t.startswith("mailto:"):
        return None
    if t.startswith("/"):
        cand = (bundle / t.lstrip("/")).resolve()
    else:
        cand = (source.parent / t).resolve()
    try:
        rel = cand.relative_to(bundle.resolve()).as_posix()
    except ValueError:
        return None
    if cand.suffix == ".md" or cand.exists() or rel.endswith(".md"):
        return rel
    return None


def extract_markdown_links(text: str, source: Path, bundle: Path) -> list[TypedEdge]:
    edges: list[TypedEdge] = []
    seen: set[tuple[str, str]] = set()
    for _label, target in LINK_RE.findall(text):
        rel_path = _normalize_target(target, source, bundle)
        if not rel_path:
            continue
        key = (rel_path, "links_to")
        if key in seen:
            continue
        seen.add(key)
        edges.append(TypedEdge(target=rel_path, rel="links_to", source="markdown"))
    return edges


def extract_frontmatter_links(meta: dict[str, Any], source: Path, bundle: Path) -> list[TypedEdge]:
    edges: list[TypedEdge] = []
    for item in meta.get("links") or []:
        if not isinstance(item, dict):
            continue
        target = item.get("target") or item.get("to") or item.get("href") or ""
        rel = (item.get("rel") or item.get("type") or "related_to").strip()
        if rel not in KNOWN_RELS:
            rel = rel or "related_to"
        rel_path = _normalize_target(str(target), source, bundle)
        if not rel_path:
            continue
        edges.append(TypedEdge(target=rel_path, rel=rel, source="frontmatter"))
    return edges


def merge_edges(md_edges: list[TypedEdge], fm_edges: list[TypedEdge]) -> list[TypedEdge]:
    """Frontmatter typed edges enrich/override plain markdown for the same target."""
    by_target: dict[str, TypedEdge] = {}
    for e in md_edges:
        by_target[e.target] = e
    for e in fm_edges:
        # typed rel wins over generic links_to
        prev = by_target.get(e.target)
        if prev is None or prev.rel == "links_to" or e.source == "frontmatter":
            by_target[e.target] = e
    return list(by_target.values())


def load_bundle(bundle: Path) -> dict[str, Concept]:
    concepts: dict[str, Concept] = {}
    for path in sorted(bundle.rglob("*.md")):
        if path.name.startswith("."):
            continue
        rel = path.relative_to(bundle).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        meta = parse_frontmatter(text)
        md_edges = extract_markdown_links(text, path, bundle)
        fm_edges = extract_frontmatter_links(meta, path, bundle)
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
        )
        concepts[rel] = c
    return concepts


def build_inbound(concepts: dict[str, Concept]) -> dict[str, list[str]]:
    inbound: dict[str, list[str]] = defaultdict(list)
    for rel, c in concepts.items():
        for tgt in c.outbound:
            if tgt in concepts:
                inbound[tgt].append(rel)
    return inbound


def resolve_concept(concepts: dict[str, Concept], query: str) -> str | None:
    q = query.strip().lstrip("/")
    if q in concepts:
        return q
    q_lower = q.lower()
    for rel, c in concepts.items():
        if Path(rel).stem.lower() == q_lower or c.title.lower() == q_lower:
            return rel
        if rel.endswith(q) or rel.endswith(q + ".md"):
            return rel
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


def criticality_of(c: Concept) -> str:
    criticality = "low"
    if c.type in HIGH_IMPACT_TYPES:
        criticality = "high"
    elif c.type in MEDIUM_IMPACT_TYPES:
        criticality = "medium"
    if not c.verified and criticality != "low":
        criticality = "critical" if criticality == "high" else criticality
    return criticality


def enrich_nodes(concepts: dict[str, Concept], items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for item in items:
        c = concepts[item["id"]]
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
    target = resolve_concept(concepts, concept)
    if not target:
        print(json.dumps({"error": f"concept not found: {concept}"}))
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
    target = resolve_concept(concepts, concept)
    if not target:
        print(json.dumps({"error": f"concept not found: {concept}"}))
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
    inbound_map = build_inbound(concepts)
    outbound_map = {k: v.outbound for k, v in concepts.items()}
    target = resolve_concept(concepts, concept)
    if not target:
        print(json.dumps({"error": f"concept not found: {concept}"}))
        return 1
    undirected: dict[str, list[str]] = defaultdict(list)
    for k, outs in outbound_map.items():
        for o in outs:
            undirected[k].append(o)
            undirected[o].append(k)
    for k, ins in inbound_map.items():
        for i in ins:
            undirected[k].append(i)
            undirected[i].append(k)
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


def cmd_pack(bundle: Path, concept: str, hops: int, max_nodes: int) -> int:
    """Progressive disclosure context pack — default 2 hops, trust-aware trim."""
    concepts = load_bundle(bundle)
    # reuse subgraph logic via internal call pattern
    inbound_map = build_inbound(concepts)
    outbound_map = {k: v.outbound for k, v in concepts.items()}
    target = resolve_concept(concepts, concept)
    if not target:
        print(json.dumps({"error": f"concept not found: {concept}"}))
        return 1

    undirected: dict[str, list[str]] = defaultdict(list)
    for k, outs in outbound_map.items():
        for o in outs:
            undirected[k].append(o)
            undirected[o].append(k)
    undirected = {k: sorted(set(v)) for k, v in undirected.items()}
    neighborhood = [target] + [x["id"] for x in bfs_closure(target, undirected, hops=hops)]

    def score(nid: str) -> tuple:
        c = concepts[nid]
        # prefer verified high-impact, keep root first
        return (
            0 if nid == target else 1,
            0 if c.verified else 1,
            0 if c.type in HIGH_IMPACT_TYPES else 1,
            c.title.lower(),
        )

    ranked = sorted(neighborhood, key=score)
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

    lines += ["", "## Graph (Mermaid)", "```mermaid", "graph LR"]
    for e in edges:
        a = Path(e["from"]).stem.replace("-", "_")
        b = Path(e["to"]).stem.replace("-", "_")
        label = e["rel"] if e["rel"] != "links_to" else ""
        if label:
            lines.append(f"  {a} -->|{label}| {b}")
        else:
            lines.append(f"  {a} --> {b}")
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
        resolved = resolve_concept(concepts, from_path)
        if not resolved:
            print(json.dumps({"error": f"concept not found: {from_path}"}))
            return 1
        edges = [e for e in edges if e["from"] == resolved]
    if rel_filter:
        edges = [e for e in edges if e["rel"] == rel_filter]
    typed = sum(1 for e in edges if e["rel"] != "links_to")
    print(json.dumps({"edges": edges, "count": len(edges), "typed_count": typed}, indent=2))
    return 0


def cmd_validate(bundle: Path) -> int:
    concepts = load_bundle(bundle)
    issues: list[dict[str, str]] = []
    if not (bundle / "index.md").exists():
        issues.append({"severity": "error", "message": "missing root index.md"})
    for rel, c in concepts.items():
        if rel in ("index.md", "log.md"):
            continue
        if c.type in ("", "Unknown") and c.path.name != "index.md":
            issues.append({"severity": "warn", "path": rel, "message": "missing or unknown type"})
        if not c.meta.get("title") and c.path.name != "index.md":
            issues.append({"severity": "warn", "path": rel, "message": "missing title"})
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
    print(
        json.dumps(
            {
                "bundle": str(bundle),
                "concept_count": len(concepts),
                "edge_count": sum(len(c.edges) for c in concepts.values()),
                "issues": issues,
                "error_count": errors,
            },
            indent=2,
        )
    )
    return 1 if errors else 0


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

    s = sub.add_parser("pack", help="Progressive disclosure context pack (default 2 hops)")
    s.add_argument("bundle")
    s.add_argument("concept")
    s.add_argument("--hops", type=int, default=2)
    s.add_argument("--max-nodes", type=int, default=20)

    s = sub.add_parser("edges", help="List edges (optional typed rel filter)")
    s.add_argument("bundle")
    s.add_argument("--from", dest="from_path", default=None)
    s.add_argument("--rel", dest="rel_filter", default=None)

    for name in ("validate", "orphans"):
        s = sub.add_parser(name)
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
        return cmd_pack(bundle, args.concept, args.hops, args.max_nodes)
    if args.cmd == "edges":
        return cmd_edges(bundle, args.from_path, args.rel_filter)
    if args.cmd == "validate":
        return cmd_validate(bundle)
    if args.cmd == "orphans":
        return cmd_orphans(bundle)
    return 1


if __name__ == "__main__":
    sys.exit(main())
