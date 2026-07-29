---
type: DecisionRecord
title: Use OKF for dual knowledge and agent graphs
description: Adopt OKF Markdown+YAML as the durable model for domain knowledge and harness graphs.
status: accepted
tags: [decision, adr]
timestamp: 2026-07-29T00:00:00Z
verified: true
---

# Use OKF for dual knowledge and agent graphs

## Context

Teams need a portable, Git-native graph for both knowledge and agent orchestration.

## Decision

Store both graphs in OKF concept files with typed frontmatter and absolute Markdown links.

## Consequences

- Reviewable diffs in PRs
- Deterministic CLI validation
- Progressive disclosure via subgraph extraction
