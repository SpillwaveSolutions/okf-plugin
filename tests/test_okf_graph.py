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
