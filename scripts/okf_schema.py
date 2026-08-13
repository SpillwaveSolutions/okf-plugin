#!/usr/bin/env python3
"""Shared OKF concept-schema loader and subset validator.

Stdlib only. Soft by default: missing recommended fields and unknown types
are warnings. Required on BaseConcept v1 is type + title only.

Domain plugins call:

    from okf_schema import SchemaRegistry, discover_schema_dirs

    reg = SchemaRegistry()
    for d in discover_schema_dirs(extra=args.schema_dirs):
        reg.load_dir(d)
    issues = reg.validate_frontmatter(fm)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

CORE_SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schemas" / "okf-concepts"

TRUTH_STATES = frozenset(
    {
        "current",
        "snapshot",
        "superseded",
        "archived",  # PKC / SAC
        "historical",
        "proposed",  # DEKC
    }
)

BUG_RECOMMENDED_RELS = frozenset(
    {"affects", "reproduces_in", "fixed_in", "lands_in", "implements"}
)


@dataclass
class Issue:
    severity: str  # error | warn | info
    message: str
    path: str = ""
    type: str = ""

    def as_dict(self) -> dict[str, str]:
        d = {"severity": self.severity, "message": self.message}
        if self.path:
            d["path"] = self.path
        if self.type:
            d["type"] = self.type
        return d


class SchemaRegistry:
    def __init__(self) -> None:
        self.schemas: dict[str, dict[str, Any]] = {}
        self.base: dict[str, Any] | None = None
        self.dirs: list[Path] = []
        self.known_types: set[str] = set()
        self.catalog_ownership: dict[str, list[str]] = {}

    def load_dir(self, directory: Path) -> int:
        directory = directory.resolve()
        if not directory.is_dir():
            return 0
        if directory in self.dirs:
            return 0
        self.dirs.append(directory)
        loaded = 0
        registry = directory / "registry.json"
        if registry.is_file():
            try:
                doc = json.loads(registry.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                doc = {}
            for name in doc.get("concepts") or []:
                self.known_types.add(str(name))
            owners = doc.get("catalog_ownership") or {}
            if isinstance(owners, dict):
                for plugin, catalogs in owners.items():
                    self.catalog_ownership.setdefault(str(plugin), [])
                    for c in catalogs or []:
                        if c not in self.catalog_ownership[str(plugin)]:
                            self.catalog_ownership[str(plugin)].append(c)
        for path in sorted(directory.glob("*.schema.json")):
            try:
                schema = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            stem = path.name[: -len(".schema.json")]
            self.schemas[stem] = schema
            self.known_types.add(stem)
            loaded += 1
            if stem == "BaseConcept":
                self.base = schema
        return loaded

    def schema_for(self, type_name: str) -> dict[str, Any] | None:
        if type_name in self.schemas:
            return self.schemas[type_name]
        if type_name == "Dataset":
            return self.schemas.get("Table")
        return None

    def validate_frontmatter(
        self,
        fm: dict[str, Any],
        *,
        path: str = "",
        strict: bool = False,
    ) -> list[Issue]:
        issues: list[Issue] = []
        type_name = str(fm.get("type") or "")
        title = fm.get("title")
        if not type_name:
            issues.append(Issue("error", "missing required `type`", path))
        if title in (None, ""):
            issues.append(Issue("error", "missing required `title`", path, type_name))

        schema = self.schema_for(type_name) if type_name else None
        if type_name and schema is None:
            if type_name not in ("", "Unknown", "Index", "Catalog"):
                issues.append(
                    Issue(
                        "info",
                        f"unknown type `{type_name}` — falling back to BaseConcept",
                        path,
                        type_name,
                    )
                )
            schema = self.base

        if schema:
            issues.extend(_check_schema(fm, schema, path=path, type_name=type_name, strict=strict))

        ts = fm.get("truth_state")
        if ts and ts not in TRUTH_STATES:
            issues.append(
                Issue("warn", f"unusual truth_state `{ts}`", path, type_name)
            )

        if type_name == "TicketLink" and fm.get("kind") == "bug":
            issues.extend(_check_bug_refinement(fm, path=path))

        return issues


def _type_ok(value: Any, schema_type: Any) -> bool:
    if isinstance(schema_type, list):
        return any(_type_ok(value, t) for t in schema_type)
    if schema_type == "string":
        return isinstance(value, str)
    if schema_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if schema_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if schema_type == "boolean":
        return isinstance(value, bool)
    if schema_type == "array":
        return isinstance(value, list)
    if schema_type == "object":
        return isinstance(value, dict)
    return True


def _check_schema(
    fm: dict[str, Any],
    schema: dict[str, Any],
    *,
    path: str,
    type_name: str,
    strict: bool,
) -> list[Issue]:
    issues: list[Issue] = []
    required = schema.get("required") or []
    props = schema.get("properties") or {}
    for key in required:
        if fm.get(key) in (None, ""):
            # type+title already reported; extra required would be domain-local
            if key in ("type", "title"):
                continue
            sev = "error" if strict else "warn"
            issues.append(Issue(sev, f"missing required `{key}`", path, type_name))
    for key, value in fm.items():
        if key not in props:
            continue
        p = props[key]
        if "const" in p and value != p["const"]:
            issues.append(
                Issue("warn", f"`{key}` must be {p['const']!r}, got {value!r}", path, type_name)
            )
        if "enum" in p and value not in p["enum"] and value != "":
            # soft: unknown enum is a warning so old files keep working
            issues.append(
                Issue(
                    "warn",
                    f"`{key}` value {value!r} not in enum {p['enum']}",
                    path,
                    type_name,
                )
            )
        if "type" in p and not _type_ok(value, p["type"]):
            issues.append(
                Issue("warn", f"`{key}` wrong type for {p['type']}", path, type_name)
            )
        if p.get("type") == "array" and isinstance(value, list):
            item = p.get("items") or {}
            if item.get("type") == "object":
                for i, el in enumerate(value):
                    if not isinstance(el, dict):
                        issues.append(
                            Issue("error", f"`{key}[{i}]` must be object", path, type_name)
                        )
                        continue
                    for rk in item.get("required") or []:
                        if rk not in el:
                            issues.append(
                                Issue(
                                    "error",
                                    f"`{key}[{i}]` missing `{rk}`",
                                    path,
                                    type_name,
                                )
                            )
    return issues


def _check_bug_refinement(fm: dict[str, Any], *, path: str) -> list[Issue]:
    links = fm.get("links") or []
    rels = set()
    if isinstance(links, list):
        for link in links:
            if isinstance(link, dict) and link.get("rel"):
                rels.add(str(link["rel"]))
    if rels & BUG_RECOMMENDED_RELS:
        return []
    if fm.get("branch"):
        return []
    return [
        Issue(
            "warn",
            "kind=bug should link to a Module/Package/Release/CodeChange "
            f"(rels {sorted(BUG_RECOMMENDED_RELS)}) or set `branch`",
            path,
            "TicketLink",
        )
    ]


def discover_schema_dirs(*, extra: list[Path] | None = None, start: Path | None = None) -> list[Path]:
    """Find schema packs: core okf-plugin first, then sibling checkouts, then extras."""
    found: list[Path] = []
    seen: set[Path] = set()

    def _add(p: Path) -> None:
        p = p.resolve()
        if p.is_dir() and p not in seen:
            seen.add(p)
            found.append(p)

    _add(CORE_SCHEMA_DIR)
    env = os.environ.get("OKF_SCHEMA_DIRS", "")
    for part in env.split(os.pathsep):
        if part.strip():
            _add(Path(part.strip()))

    roots: list[Path] = []
    if start:
        roots.append(start.resolve())
    here = Path(__file__).resolve().parent.parent
    roots.append(here.parent)  # .../repos
    for root in roots:
        for name in (
            "okf-plugin",
            "project-knowledge-capture",
            "system-architecture-capture",
            "data-engineering-knowledge-capture",
            "okf-agent-graph",
        ):
            _add(root / name / "schemas" / "okf-concepts")
            _add(root / name / "schemas")

    for p in extra or []:
        _add(p)
    return found


def load_default_registry(*, extra: list[Path] | None = None, start: Path | None = None) -> SchemaRegistry:
    reg = SchemaRegistry()
    for d in discover_schema_dirs(extra=extra, start=start):
        reg.load_dir(d)
    return reg


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="OKF shared concept schemas")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list", help="List known types from merged registries")
    p_val = sub.add_parser("validate-fm", help="Validate a JSON frontmatter object from stdin")
    p_val.add_argument("--strict", action="store_true")
    args = parser.parse_args(argv)

    reg = load_default_registry()
    if args.cmd == "list":
        print(
            json.dumps(
                {
                    "dirs": [str(d) for d in reg.dirs],
                    "types": sorted(reg.known_types),
                    "catalog_ownership": reg.catalog_ownership,
                    "base_required": (reg.base or {}).get("required"),
                },
                indent=2,
            )
        )
        return 0
    if args.cmd == "validate-fm":
        fm = json.load(sys.stdin)
        issues = reg.validate_frontmatter(fm, strict=args.strict)
        print(json.dumps([i.as_dict() for i in issues], indent=2))
        errors = sum(1 for i in issues if i.severity == "error")
        return 1 if errors else 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
