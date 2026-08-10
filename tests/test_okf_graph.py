#!/usr/bin/env python3
"""Tests for scripts/okf-graph.py — the graph engine.

Plain asserts, no framework. Run: python3 tests/test_okf_graph.py [-q]

Kept deliberately small: it exists to catch the defects that shipped in v0.2.0
(silently-dropped block-sequence YAML, colliding Mermaid node IDs) and to stop
sample-okf and the four version manifests from drifting.
"""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "okf-graph.py"


def load_graph_module():
    """Import okf-graph.py by path.

    The sys.modules registration is load-bearing: without it the @dataclass
    decorators raise AttributeError on Python 3.13, because dataclasses looks
    the class's module up in sys.modules and gets None.
    """
    spec = importlib.util.spec_from_file_location("okf_graph", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["okf_graph"] = mod
    spec.loader.exec_module(mod)
    return mod


g = load_graph_module()


def test_frontmatter_inline_list():
    meta = g.parse_frontmatter("---\ntitle: X\ntags: [alpha, beta]\n---\nbody\n")
    assert meta["tags"] == ["alpha", "beta"], meta
    assert meta["title"] == "X", meta


def test_frontmatter_block_sequence():
    """Standard YAML block sequences must parse. Regression: these silently
    became '' and were then coerced to [] by the isinstance guard."""
    meta = g.parse_frontmatter(
        "---\ntitle: X\ntags:\n  - alpha\n  - beta\nstatus: draft\n---\nbody\n"
    )
    assert meta["tags"] == ["alpha", "beta"], f"block-seq tags dropped: {meta}"
    # the key after the list must still parse
    assert meta["status"] == "draft", meta


def test_frontmatter_block_sequence_then_links():
    meta = g.parse_frontmatter(
        "---\ntitle: X\ntags:\n  - a\nlinks:\n  - rel: uses\n    target: /b.md\n---\n"
    )
    assert meta["tags"] == ["a"], meta
    assert meta["links"] == [{"rel": "uses", "target": "/b.md"}], meta


def test_frontmatter_booleans_survive():
    meta = g.parse_frontmatter("---\nverified: true\ndraft: false\n---\n")
    assert meta["verified"] is True, meta
    assert meta["draft"] is False, meta


def test_normalize_target():
    with tempfile.TemporaryDirectory() as td:
        bundle = Path(td) / "bundle"
        (bundle / "sub").mkdir(parents=True)
        (bundle / "index.md").write_text("---\n---\n")
        (bundle / "sub" / "index.md").write_text("---\n---\n")
        (bundle / "sub" / "page.md").write_text("---\n---\n")
        src = bundle / "sub" / "page.md"

        assert g._normalize_target("/sub/page.md", src, bundle) == "sub/page.md"
        # a directory link resolves to its index.md
        assert g._normalize_target("/sub", src, bundle) == "sub/index.md"
        # off-bundle and external targets are not edges
        assert g._normalize_target("../../elsewhere.md", src, bundle) is None
        assert g._normalize_target("https://example.com", src, bundle) is None


def test_merge_edges_frontmatter_wins():
    md = [g.TypedEdge(target="a.md", rel="links_to", source="markdown")]
    fm = [g.TypedEdge(target="a.md", rel="uses", source="frontmatter")]
    merged = {e.target: e for e in g.merge_edges(md, fm)}
    assert merged["a.md"].rel == "uses", merged


def test_merge_edges_keeps_markdown_only_targets():
    """Frontmatter overrides its own targets and nothing else. Markdown edges
    are only ever `links_to`, so frontmatter is always at least as specific —
    the precedence is unconditional, not a comparison of rels."""
    md = [
        g.TypedEdge(target="a.md", rel="links_to", source="markdown"),
        g.TypedEdge(target="b.md", rel="links_to", source="markdown"),
    ]
    fm = [
        g.TypedEdge(target="a.md", rel="depends_on", source="frontmatter"),
        g.TypedEdge(target="c.md", rel="routes_to", source="frontmatter"),
    ]
    merged = {e.target: e for e in g.merge_edges(md, fm)}
    assert set(merged) == {"a.md", "b.md", "c.md"}, merged
    assert merged["a.md"].rel == "depends_on", merged
    assert merged["b.md"].rel == "links_to" and merged["b.md"].source == "markdown", merged
    assert merged["c.md"].source == "frontmatter", merged
    # one edge per target, no duplicates
    assert len(g.merge_edges(md, fm)) == 3


def _concept(rel: str = "x.md", **kw):
    return g.Concept(path=Path(rel), rel=rel, **kw)


def test_criticality_escalates_unverified_medium():
    """Unverified escalates one level: medium→high, high→critical. Regression:
    the medium arm assigned the variable to itself, so the tier was decorative."""
    assert g.criticality_of(_concept(type="Dataset", verified=True)) == "medium"
    assert g.criticality_of(_concept(type="Dataset", verified=False)) == "high"
    assert g.criticality_of(_concept(type="Workflow", verified=True)) == "high"
    assert g.criticality_of(_concept(type="Workflow", verified=False)) == "critical"
    # low never escalates, verified or not
    assert g.criticality_of(_concept(type="Reference", verified=False)) == "low"


def test_criticality_ordering_survives_escalation():
    """enrich_nodes is the only consumer that ranks on criticality; the
    escalated value must stay inside its {critical,high,medium,low} order map."""
    concepts = {
        "w.md": _concept(rel="w.md", title="Flow", type="Workflow", verified=False),
        "d.md": _concept(rel="d.md", title="Data", type="Dataset", verified=False),
        "r.md": _concept(rel="r.md", title="Ref", type="Reference", verified=True),
    }
    items = [{"id": r, "depth": 1} for r in ("r.md", "d.md", "w.md")]
    ranked = g.enrich_nodes(concepts, items)
    assert [x["id"] for x in ranked] == ["w.md", "d.md", "r.md"], ranked
    assert [x["criticality"] for x in ranked] == ["critical", "high", "low"], ranked


def test_mermaid_ids_are_unique_per_path():
    """Regression: IDs were derived from Path(...).stem, so every index.md in
    the bundle collapsed into a single node."""
    a = g.mermaid_id("agents/index.md")
    b = g.mermaid_id("workflows/index.md")
    assert a != b, f"index.md collision: {a} == {b}"
    # IDs must be Mermaid-safe: identifier chars only, never leading digit
    for rel in ("agents/index.md", "2024/notes.md", "a b/c.d.md"):
        mid = g.mermaid_id(rel)
        assert mid.replace("_", "").isalnum(), mid
        assert not mid[0].isdigit(), mid
    # and stable across calls
    assert g.mermaid_id("agents/index.md") == a


def test_resolve_concept_reports_ambiguity():
    """A suffix or stem query matching two concepts must report both instead of
    answering about whichever one iteration happened to reach first."""
    concepts = {
        "a/page.md": _concept(rel="a/page.md", title="A page"),
        "b/page.md": _concept(rel="b/page.md", title="B page"),
        "a/only.md": _concept(rel="a/only.md", title="Only"),
    }
    # exact path is unambiguous by construction
    assert g.resolve_concept(concepts, "a/page.md")[0] == "a/page.md"
    assert g.resolve_concept(concepts, "/a/page.md")[0] == "a/page.md"
    # title and unambiguous suffix still resolve
    assert g.resolve_concept(concepts, "Only")[0] == "a/only.md"
    assert g.resolve_concept(concepts, "only.md")[0] == "a/only.md"
    # ambiguous suffix and ambiguous stem both report their candidates
    for q in ("page.md", "page"):
        match, candidates = g.resolve_concept(concepts, q)
        assert match is None, f"{q} guessed {match}"
        assert candidates == ["a/page.md", "b/page.md"], candidates
    assert g.resolve_concept(concepts, "nope.md") == (None, [])


def test_load_bundle_skips_dot_directories():
    """Pointed at a repo root, load_bundle must not pull .work/ or .git/ in as
    concepts. Regression: only dot-*files* were skipped, not dot-*dirs*."""
    with tempfile.TemporaryDirectory() as td:
        bundle = Path(td) / "b"
        (bundle / ".work").mkdir(parents=True)
        (bundle / "docs").mkdir()
        (bundle / "index.md").write_text("---\ntitle: Root\n---\n")
        (bundle / ".work" / "notes.md").write_text("---\ntitle: Hidden\n---\n")
        (bundle / ".hidden.md").write_text("---\ntitle: Dotfile\n---\n")
        (bundle / "docs" / "real.md").write_text("---\ntitle: Real\n---\n")
        assert set(g.load_bundle(bundle)) == {"index.md", "docs/real.md"}


def run_script(*args) -> tuple[int, dict]:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), *args], capture_output=True, text=True, cwd=REPO
    )
    try:
        return proc.returncode, json.loads(proc.stdout)
    except json.JSONDecodeError:
        raise AssertionError(f"non-JSON stdout from {args}: {proc.stdout!r} {proc.stderr!r}")


def test_sample_bundle_validates():
    code, out = run_script("validate", "sample-okf")
    assert code == 0, out
    assert out["error_count"] == 0, out["issues"]
    # drift tripwire: sample-okf is the plugin's worked example, and the skills
    # quote these numbers. A surprise change here means an unreviewed edit.
    assert out["concept_count"] == 22, out["concept_count"]
    assert out["edge_count"] == 83, out["edge_count"]


def test_pack_mermaid_has_no_collapsed_nodes():
    code, out = run_script("pack", "sample-okf", "agents/graph-engineer.md", "--hops", "2")
    assert code == 0, out
    ids = {g.mermaid_id(e["from"]) for e in out["edges"]} | {
        g.mermaid_id(e["to"]) for e in out["edges"]
    }
    # one Mermaid ID per distinct concept path, no merging
    paths = {e["from"] for e in out["edges"]} | {e["to"] for e in out["edges"]}
    assert len(ids) == len(paths), f"{len(paths)} paths collapsed into {len(ids)} ids"
    assert "```mermaid" in out["markdown"]


def run_script_raw(*args) -> tuple[int, str]:
    """For subcommands that print an artifact rather than JSON."""
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), *args], capture_output=True, text=True, cwd=REPO
    )
    return proc.returncode, proc.stdout


def test_graph_mermaid_is_a_fenced_block():
    code, out = run_script_raw("graph", "sample-okf")
    assert code == 0, out
    assert out.startswith("```mermaid\ngraph LR\n"), out[:80]
    assert out.rstrip().endswith("```"), out[-80:]
    # every concept in the bundle gets a node line, orphans included
    _, doc = run_script("graph", "sample-okf", "--format", "json")
    for n in doc["nodes"]:
        assert g.mermaid_id(n["id"]) in out, f"{n['id']} missing from mermaid"


def test_graph_json_shape():
    code, out = run_script("graph", "sample-okf", "--format", "json")
    assert code == 0, out
    assert out["focus"] is None and out["hops"] is None, out
    assert out["nodes"] and out["edges"], out
    for n in out["nodes"]:
        assert set(n) == {"id", "title", "type", "verified"}, n
    ids = {n["id"] for n in out["nodes"]}
    for e in out["edges"]:
        assert set(e) == {"from", "to", "rel"}, e
        # no dangling endpoints: broken links belong to validate, not the graph
        assert e["from"] in ids and e["to"] in ids, e


def test_graph_focus_narrows_the_node_set():
    _, whole = run_script("graph", "sample-okf", "--format", "json")
    _, near = run_script(
        "graph", "sample-okf", "--format", "json", "--focus", "agents/graph-engineer.md",
        "--hops", "1",
    )
    assert near["focus"] == "agents/graph-engineer.md", near["focus"]
    whole_ids = {n["id"] for n in whole["nodes"]}
    near_ids = {n["id"] for n in near["nodes"]}
    assert near_ids < whole_ids, f"focus did not narrow: {len(near_ids)}/{len(whole_ids)}"
    assert "agents/graph-engineer.md" in near_ids
    # more hops reach at least as far
    _, far = run_script(
        "graph", "sample-okf", "--format", "json", "--focus", "agents/graph-engineer.md",
        "--hops", "3",
    )
    assert near_ids <= {n["id"] for n in far["nodes"]}


def test_graph_focus_unknown_concept_errors():
    code, out = run_script("graph", "sample-okf", "--format", "json", "--focus", "no/such.md")
    assert code == 1, out
    assert "error" in out, out


def test_graph_html_is_self_contained():
    code, out = run_script_raw("graph", "sample-okf", "--format", "html")
    assert code == 0, out[:200]
    assert out.startswith("<!doctype html>"), out[:40]
    assert "</html>" in out
    # no network: a CSP-locked viewer or an offline file must render fully
    assert "http://" not in out and "https://" not in out, "external reference in html"
    for tag in ("<script", "src=", "@import", "url("):
        assert tag not in out, f"external/executable resource in html: {tag}"
    assert '<pre class="mermaid">' in out and "graph LR" in out
    # the node table carries the same concepts as the JSON view
    _, doc = run_script("graph", "sample-okf", "--format", "json")
    for n in doc["nodes"]:
        assert f"<code>{n['id']}</code>" in out, f"{n['id']} missing from html table"


def test_ambiguous_concept_is_a_cli_error():
    """impact/pack must refuse an ambiguous query rather than silently answer
    about the wrong concept."""
    with tempfile.TemporaryDirectory() as td:
        bundle = Path(td) / "b"
        (bundle / "a").mkdir(parents=True)
        (bundle / "b").mkdir()
        (bundle / "index.md").write_text("---\ntitle: Root\n---\n[a](/a/page.md) [b](/b/page.md)\n")
        (bundle / "a" / "page.md").write_text("---\ntitle: A\ntype: Reference\n---\n")
        (bundle / "b" / "page.md").write_text("---\ntitle: B\ntype: Reference\n---\n")
        for cmd in ("impact", "backlinks", "subgraph", "pack"):
            code, out = run_script(cmd, str(bundle), "page.md")
            assert code == 1, (cmd, out)
            assert "error" in out, (cmd, out)
            assert out.get("candidates") == ["a/page.md", "b/page.md"], (cmd, out)
        # the unambiguous full path still works
        code, _ = run_script("impact", str(bundle), "a/page.md")
        assert code == 0


def test_validate_reports_off_bundle_links():
    """A typo'd ../../ link is not an edge, but it must not vanish either —
    validate reports it as a warning so --strict gates it in CI."""
    with tempfile.TemporaryDirectory() as td:
        bundle = Path(td) / "b"
        (bundle / "sub").mkdir(parents=True)
        (bundle / "index.md").write_text("---\ntitle: Root\n---\n[p](/sub/page.md)\n")
        (bundle / "sub" / "page.md").write_text(
            "---\ntitle: P\ntype: Reference\nlinks:\n  - rel: uses\n    target: ../../other.md\n"
            "---\n[typo](../../elsewhere.md)\n"
        )
        code, out = run_script("validate", str(bundle))
        flagged = [i for i in out["issues"] if "outside bundle" in i["message"]]
        assert len(flagged) == 2, out["issues"]
        assert {i["severity"] for i in flagged} == {"warn"}, flagged
        assert {i["path"] for i in flagged} == {"sub/page.md"}, flagged
        assert any("elsewhere.md" in i["message"] for i in flagged), flagged
        assert any("other.md" in i["message"] for i in flagged), flagged
        # default exit stays 0 — the skills and okf-curate.sh depend on it
        assert code == 0 and out["error_count"] == 0, out
        strict, _ = run_script("validate", str(bundle), "--strict")
        assert strict == 1


def test_root_index_and_log_have_their_links_validated():
    """The root index.md/log.md exemption is for type and title only. It used
    to `continue` past the whole loop body, so the bundle's entry point — its
    most linked-from file — was the one place a broken link went unreported."""
    with tempfile.TemporaryDirectory() as td:
        bundle = Path(td) / "b"
        (bundle / "sub").mkdir(parents=True)
        # no title on any of these: the metadata exemption must survive
        (bundle / "index.md").write_text("[gone](/missing.md)\n[out](../../escape.md)\n")
        (bundle / "log.md").write_text("[gone too](/absent.md)\n")
        (bundle / "sub" / "index.md").write_text("---\ntype: Index\n---\n")
        (bundle / "sub" / "log.md").write_text("---\ntype: Reference\n---\n")
        code, out = run_script("validate", str(bundle))
        broken = {(i["path"], i["message"]) for i in out["issues"]
                  if "broken link" in i["message"]}
        assert ("index.md", "broken link → missing.md") in broken, out["issues"]
        assert ("log.md", "broken link → absent.md") in broken, out["issues"]
        assert code == 1 and out["error_count"] == 2, out
        assert any(i["path"] == "index.md" and "outside bundle" in i["message"]
                   for i in out["issues"]), out["issues"]
        # …while the exemption they actually needed still holds, at any depth
        titles = {i["path"] for i in out["issues"] if "missing title" in i["message"]}
        assert titles == {"sub/log.md"}, titles  # only the root log.md is structural


def test_subgraph_neighbourhood_is_symmetric():
    """subgraph walks the graph undirected: if B is in A's 1-hop set then A is
    in B's. Locks the behaviour of the (formerly two-pass) adjacency build."""
    _, a = run_script("subgraph", "sample-okf", "agents/graph-engineer.md", "--hops", "1")
    neighbours = [n["id"] for n in a["nodes"] if n["id"] != a["root"]]
    assert neighbours, a
    for nid in neighbours:
        _, b = run_script("subgraph", "sample-okf", nid, "--hops", "1")
        assert a["root"] in [n["id"] for n in b["nodes"]], (nid, b["nodes"])


def test_strict_validate_flags_warnings():
    """--strict turns warn into a non-zero exit so CI can gate on it; the
    default stays lenient because the skills depend on exit 0."""
    with tempfile.TemporaryDirectory() as td:
        bundle = Path(td) / "b"
        bundle.mkdir()
        (bundle / "index.md").write_text("---\ntitle: Root\nokf_version: 0.2\n---\n")
        # missing type and title -> warn, not error
        (bundle / "loose.md").write_text("---\ndescription: no type here\n---\n")
        lenient = subprocess.run(
            [sys.executable, str(SCRIPT), "validate", str(bundle)],
            capture_output=True, text=True,
        )
        strict = subprocess.run(
            [sys.executable, str(SCRIPT), "validate", str(bundle), "--strict"],
            capture_output=True, text=True,
        )
        assert lenient.returncode == 0, lenient.stdout
        assert strict.returncode == 1, strict.stdout


def test_version_is_consistent_across_manifests():
    """The version lives in four manifests and has drifted before."""
    manifests = {
        ".claude-plugin/plugin.json": ("version",),
        "marketplace.json": ("plugins", 0, "version"),
        ".claude-plugin/marketplace.json": ("plugins", 0, "version"),
        ".grok-plugin/marketplace.json": ("plugins", 0, "version"),
    }
    found = {}
    for rel, path in manifests.items():
        f = REPO / rel
        if not f.exists():
            continue
        node = json.loads(f.read_text())
        for key in path:
            node = node[key]
        found[rel] = node
    assert len(set(found.values())) == 1, f"version drift: {found}"


def test_pre_commit_keeps_the_local_gates():
    """hooks/pre-commit is vendored — `worklog init` rewrites it wholesale on
    every upgrade, and doing so silently deleted both of these lines going
    0.18.0 -> 0.22.2 (01KZD84S62B5TWKQSX4XV9848M). There is no extension point
    to move them to, so the loss cannot be prevented; this makes it loud.

    CI runs this file directly, not through the hook, so this assert still
    fires in the very case where the hook itself has been clobbered."""
    hook = REPO / "hooks" / "pre-commit"
    if not hook.exists():
        return
    body = hook.read_text()
    for suite in ("tests/test_okf_graph.py", "tests/test_okf_curate.sh"):
        assert suite in body, (
            f"{suite} is not gated in hooks/pre-commit — a worklog upgrade "
            "likely overwrote the file. Restore the okf-plugin local gates block."
        )


def test_link_re_accepts_bracketed_labels():
    """A bracketed label must still yield an edge.

    Regression: `[^\\]]+` stopped at the first `]`, so `[[AREA]](/p.md)` matched
    nothing. That produced no edge rather than a broken one, and validate only
    reports broken edges — so the missing backlink was invisible. Bracketed
    titles are routine in exported wiki content (`[AREA]`, `[DEPRECATED]`)."""
    cases = [
        ("- [[AREA NAME]](/requirements/area-name.md)", "/requirements/area-name.md"),
        ("- [Title [DEPRECATED]](/x/y.md)", "/x/y.md"),
        ("- [nested [a] and [b]](/z.md)", "/z.md"),
    ]
    for line, target in cases:
        found = g.LINK_RE.findall(line)
        assert found, f"no match for {line!r}"
        assert found[0][1] == target, found


def test_link_re_is_a_superset_of_the_plain_form():
    """Everything the previous pattern matched must still match.

    The two easy ways to get this wrong, both of which shipped in drafts of the
    fix: an escape-aware branch swallows a label ending in a backslash, and `*`
    instead of `+` starts matching the empty label."""
    prior = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    for line in [
        "- [Plain](/a/b.md)",
        r"- [ends with backslash \](/c.md)",
        r"- [C:\dir\](/x.md)",
        "- [a](b) and [c](d)",
        "text with ] stray and [ok](/p.md)",
    ]:
        assert {t for _l, t in prior.findall(line)} <= {t for _l, t in g.LINK_RE.findall(line)}, line

    # Empty label: unmatched before, and must stay unmatched.
    assert not g.LINK_RE.findall("- [](/empty.md)")


def test_released_in_is_a_known_rel():
    """The release axis needs a vocabulary entry.

    A bundle modelling releases previously emitted one `non-standard rel` info
    per edge, which is one per shipped work item — enough noise to make filtering
    validate output a habit, which is how a real warning gets missed. The repo
    already models releases on the worklog side (`milestone` -> `targets
    release/*` in bin/ia_graph.py); this gives bundles a way to say the same
    thing."""
    assert "released_in" in g.KNOWN_RELS

    # The list is duplicated in prose; drift here is the failure mode.
    for rel in (
        "skills/okf-author/references/typed-edges.md",
        "skills/okf-author/SKILL.md",
        "agents/graph-engineer.md",
    ):
        f = REPO / rel
        if f.exists():
            assert "released_in" in f.read_text(), f"{rel} missing released_in"


def test_known_rels_covers_ager_vocabulary():
    """KNOWN_RELS must be a superset of AGER's declared typed-edge vocabulary.

    Source: okf-agent-graph's docs/AGER_SPEC.md, "## Typed edges (AGER
    additions)" section (same 31 rels also tabulated in
    skills/ager-author/references/typed-edges.md). okf-plugin cannot import
    the sibling plugin, so its vocabulary is pinned here as a literal
    constant. A real AGER bundle previously produced 15 'non-standard rel'
    info lines, of which 13 were false positives from rels this allow-list
    didn't know about yet — noise that buried 2 genuine typos. Without this
    guard, a future AGER spec addition silently regresses back into that
    noise instead of failing a test."""
    AGER_VOCAB = frozenset(
        {
            "routes_to",
            "delegates_to",
            "spawns",
            "judges",
            "aggregates_from",
            "fans_out_to",
            "fans_in_from",
            "handoffs_to",
            "guards",
            "reads_from",
            "writes_to",
            "appends_to",
            "records_to",
            "models_with",
            "isolates_context",
            "uses",
            "blocks",
            "budgets",
            "controlled_by",
            "retries_with",
            "compensates_with",
            "on_failure",
            "triggered_by",
            "derived_from",
            "output_of",
            "retrieves_from",
            "rate_limited_by",
            "binds_secret",
            "depends_on",
            "implements",
            "related_to",
        }
    )
    assert len(AGER_VOCAB) == 31, f"AGER vocab drifted from spec: {len(AGER_VOCAB)}"
    missing = AGER_VOCAB - g.KNOWN_RELS
    assert not missing, f"KNOWN_RELS is missing AGER relations: {sorted(missing)}"


def main() -> int:
    quiet = "-q" in sys.argv
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failures = []
    for t in tests:
        try:
            t()
            if not quiet:
                print(f"ok   {t.__name__}")
        except AssertionError as e:
            failures.append((t.__name__, e))
            print(f"FAIL {t.__name__}: {e}", file=sys.stderr)
        except Exception as e:  # noqa: BLE001 - report, don't mask
            failures.append((t.__name__, e))
            print(f"ERROR {t.__name__}: {type(e).__name__}: {e}", file=sys.stderr)
    if not quiet or failures:
        print(f"\n{len(tests) - len(failures)}/{len(tests)} passed", file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
