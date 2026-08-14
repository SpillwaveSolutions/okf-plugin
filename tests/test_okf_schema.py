#!/usr/bin/env python3
"""Tests for the shared OKF concept schema pack."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
from okf_schema import SchemaRegistry, TRUTH_STATES, load_default_registry  # noqa: E402


def test_base_concept_required_is_only_type_and_title():
    base = json.loads((REPO / "schemas/okf-concepts/BaseConcept.schema.json").read_text())
    assert base["required"] == ["type", "title"]
    assert base["additionalProperties"] is True
    enum = set(base["properties"]["truth_state"]["enum"])
    assert enum == set(TRUTH_STATES)


def test_legacy_minimal_frontmatter_has_zero_errors():
    reg = load_default_registry()
    issues = reg.validate_frontmatter({"type": "Playbook", "title": "How to pack"})
    assert not any(i.severity == "error" for i in issues), issues


def test_missing_title_is_error():
    reg = load_default_registry()
    issues = reg.validate_frontmatter({"type": "Feature"})
    assert any(i.severity == "error" and "title" in i.message for i in issues)


def test_truth_state_union_accepts_dekc_and_pkc():
    reg = load_default_registry()
    for ts in ("current", "snapshot", "superseded", "archived", "historical", "proposed"):
        issues = reg.validate_frontmatter(
            {"type": "Feature", "title": "x", "truth_state": ts}
        )
        assert not any("truth_state" in i.message for i in issues), (ts, issues)
    issues = reg.validate_frontmatter(
        {"type": "Feature", "title": "x", "truth_state": "nope"}
    )
    assert any(i.severity == "warn" and "truth_state" in i.message for i in issues)


def test_bug_kind_warns_without_structural_link():
    reg = load_default_registry()
    issues = reg.validate_frontmatter(
        {"type": "TicketLink", "title": "crash", "kind": "bug"}
    )
    assert any(i.severity == "warn" and "kind=bug" in i.message for i in issues)
    issues = reg.validate_frontmatter(
        {
            "type": "TicketLink",
            "title": "crash",
            "kind": "bug",
            "links": [{"target": "/modules/auth.md", "rel": "affects"}],
        }
    )
    assert not any("kind=bug" in i.message for i in issues)


def test_sample_okf_has_zero_schema_errors():
    proc = subprocess.run(
        [sys.executable, str(REPO / "scripts/okf-graph.py"), "validate", "sample-okf"],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    out = json.loads(proc.stdout)
    assert out["error_count"] == 0, out["issues"]
    assert out["concept_count"] == 22


def test_schemas_subcommand_lists_base():
    proc = subprocess.run(
        [sys.executable, str(REPO / "scripts/okf-graph.py"), "schemas"],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    out = json.loads(proc.stdout)
    assert out["base_required"] == ["type", "title"]
    assert "TicketLink" in out["types"]
    assert "Project" in out["types"]
    assert "Epic" in out["types"]
    assert "Bug" in out["types"]
    assert "Branch" in out["types"]


def test_first_class_work_types_are_known():
    reg = load_default_registry()
    for t in ("Epic", "Story", "Task", "Subtask", "Bug", "Branch"):
        assert t in reg.known_types, t
        issues = reg.validate_frontmatter({"type": t, "title": "x"})
        assert not any(i.severity == "error" for i in issues), (t, issues)


def test_recommended_fields_are_warnings_not_errors():
    reg = load_default_registry()
    issues = reg.validate_frontmatter({"type": "DecisionRecord", "title": "Use Postgres"})
    assert any(i.severity == "warn" and "status" in i.message for i in issues)
    assert not any(i.severity == "error" for i in issues)
    issues = reg.validate_frontmatter(
        {"type": "DecisionRecord", "title": "Use Postgres", "status": "accepted"}
    )
    assert not any("status" in i.message for i in issues)
    issues = reg.validate_frontmatter({"type": "TicketLink", "title": "no id"})
    assert any(i.severity == "warn" and "worklog_id" in i.message for i in issues)
    assert not any(i.severity == "error" for i in issues)


def test_bug_type_warns_without_structural_link():
    reg = load_default_registry()
    issues = reg.validate_frontmatter({"type": "Bug", "title": "crash", "status": "open"})
    assert any(i.severity == "warn" and "Bug" in i.message for i in issues)
    issues = reg.validate_frontmatter(
        {
            "type": "Bug",
            "title": "crash",
            "status": "open",
            "links": [{"target": "/modules/auth.md", "rel": "affects"}],
        }
    )
    assert not any("should link" in i.message or "recommended link" in i.message for i in issues)


def test_strict_promotes_recommended_to_error():
    reg = load_default_registry()
    issues = reg.validate_frontmatter(
        {"type": "DecisionRecord", "title": "x"}, strict=True
    )
    assert any(i.severity == "error" and "status" in i.message for i in issues)




def test_mixed_fixture_validates():
    fixture = REPO / "tests/fixtures/mixed-second-brain"
    if not fixture.is_dir():
        return
    proc = subprocess.run(
        [sys.executable, str(REPO / "scripts/okf-graph.py"), "validate", str(fixture)],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    out = json.loads(proc.stdout)
    assert out["error_count"] == 0, out["issues"]


if __name__ == "__main__":
    tests = [v for k, v in globals().items() if k.startswith("test_")]
    failed = 0
    for fn in tests:
        try:
            fn()
            print(f"ok   {fn.__name__}")
        except Exception as exc:
            failed += 1
            print(f"FAIL {fn.__name__}: {exc}")
    raise SystemExit(1 if failed else 0)
