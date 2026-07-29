#!/usr/bin/env python3
"""Lightweight OKF graph utilities when okfcli is unavailable.

Usage:
  okf-graph.py impact <bundle> <concept-path>
  okf-graph.py backlinks <bundle> <concept-path>
  okf-graph.py subgraph <bundle> <concept-path> [--hops N]
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
from pathlib import Path
from typing import Any

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
YAML_SIMPLE_RE = re.compile(r"^([A-Za-z0-9_]+):\s*(.+)$", re.MULTILINE)


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


def parse_frontmatter(text: str) -> dict[str, Any]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    block = m.group(1)
    meta: dict[str, Any] = {}
    for line in block.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # simple key: value (no nested YAML parsing)
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if val.lower() in ("true", "false"):
            meta[key] = val.lower() == "true"
        elif val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            meta[key] = [x.strip().strip('"').strip("'") for x in inner.split(",") if x.strip()] if inner else []
        else:
            meta[key] = val
    return meta


def extract_links(text: str, source: Path, bundle: Path) -> list[str]:
    # drop frontmatter for link scan of body, but also allow links in frontmatter resource fields
    links: list[str] = []
    for _label, target in LINK_RE.findall(text):
        t = target.split("#")[0].strip()
        if not t or t.startswith("http") or t.startswith("mailto:"):
            continue
        if t.startswith("/"):
            cand = (bundle / t.lstrip("/")).resolve()
        else:
            cand = (source.parent / t).resolve()
        try:
            rel = cand.relative_to(bundle.resolve()).as_posix()
        except ValueError:
            continue
        if cand.suffix == ".md" or cand.exists():
            links.append(rel)
    return links


def load_bundle(bundle: Path) -> dict[str, Concept]:
    concepts: dict[str, Concept] = {}
    for path in sorted(bundle.rglob("*.md")):
        if path.name.startswith("."):
            continue
        rel = path.relative_to(bundle).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        meta = parse_frontmatter(text)
        c = Concept(
            path=path,
            rel=rel,
            title=str(meta.get("title") or path.stem),
            type=str(meta.get("type") or ("Index" if path.name == "index.md" else "Unknown")),
            status=str(meta.get("status") or ""),
            verified=bool(meta.get("verified", False)),
            tags=list(meta.get("tags") or []) if isinstance(meta.get("tags"), list) else [],
            meta=meta,
            outbound=extract_links(text, path, bundle),
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
    # try by stem / title
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


def cmd_impact(bundle: Path, concept: str) -> int:
    concepts = load_bundle(bundle)
    inbound_map = build_inbound(concepts)
    outbound_map = {k: v.outbound for k, v in concepts.items()}
    target = resolve_concept(concepts, concept)
    if not target:
        print(json.dumps({"error": f"concept not found: {concept}"}))
        return 1
    inbound = bfs_closure(target, inbound_map)
    outbound = bfs_closure(target, outbound_map)

    def enrich(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        result = []
        for item in items:
            c = concepts[item["id"]]
            criticality = "low"
            if c.type in ("AgentNode", "Workflow", "Harness", "SharedState"):
                criticality = "high"
            elif c.type in ("Dataset", "Table", "Metric", "API"):
                criticality = "medium"
            if not c.verified and criticality != "low":
                criticality = "critical" if criticality == "high" else criticality
            result.append(
                {
                    **item,
                    "title": c.title,
                    "type": c.type,
                    "status": c.status,
                    "verified": c.verified,
                    "criticality": criticality,
                }
            )
        order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        result.sort(key=lambda x: (order.get(x["criticality"], 9), x["depth"], x["title"]))
        return result

    payload = {
        "target": {
            "id": target,
            "title": concepts[target].title,
            "type": concepts[target].type,
            "verified": concepts[target].verified,
            "status": concepts[target].status,
        },
        "inbound": enrich(inbound),
        "outbound": enrich(outbound),
        "suggested_order": [x["id"] for x in enrich(inbound)],
        "stats": {
            "inbound_count": len(inbound),
            "outbound_count": len(outbound),
            "total_concepts": len(concepts),
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
    bl = [{"id": i, "title": concepts[i].title, "type": concepts[i].type} for i in inbound_map.get(target, [])]
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
    # undirected neighborhood
    undirected: dict[str, list[str]] = defaultdict(list)
    for k, outs in outbound_map.items():
        for o in outs:
            undirected[k].append(o)
            undirected[o].append(k)
    for k, ins in inbound_map.items():
        for i in ins:
            undirected[k].append(i)
            undirected[i].append(k)
    # dedupe lists
    undirected = {k: sorted(set(v)) for k, v in undirected.items()}
    nodes = [target] + [x["id"] for x in bfs_closure(target, undirected, hops=hops)]
    edges = []
    node_set = set(nodes)
    for n in nodes:
        for o in concepts[n].outbound:
            if o in node_set:
                edges.append({"from": n, "to": o})
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
                    }
                    for n in nodes
                ],
                "edges": edges,
            },
            indent=2,
        )
    )
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
        for o in c.outbound:
            if o not in concepts:
                issues.append({"severity": "error", "path": rel, "message": f"broken link → {o}"})
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
    errors = sum(1 for i in issues if i["severity"] == "error")
    print(json.dumps({"bundle": str(bundle), "concept_count": len(concepts), "issues": issues, "error_count": errors}, indent=2))
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
    if args.cmd == "validate":
        return cmd_validate(bundle)
    if args.cmd == "orphans":
        return cmd_orphans(bundle)
    return 1


if __name__ == "__main__":
    sys.exit(main())
