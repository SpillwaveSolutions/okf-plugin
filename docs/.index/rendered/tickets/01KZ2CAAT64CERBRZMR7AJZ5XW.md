# Build the undirected adjacency once in subgraph

`01KZ2CAAT64CERBRZMR7AJZ5XW` · task/ops · **done**

Subgraph walks the edge set twice to build one adjacency map, which is
harmless only because the result is deduped immediately after.

## Hierarchy

- epic: [[Ticket-01KZ2CAAT5G2ND3RAF4TAXR5B9]] v0.3.1 — correctness cleanup and traceability backfill — Clear the defects found while fixing v0.3.0: logic that is dead, silent, or wrong without crashing, plus the public traceability gap left by the move to the SpillwaveSolutions org.

## Linked PRs

- [[PR-29]]

## Release

- [[Release-v0.3.1]]

## Related tickets

- [github #19](https://github.com/SpillwaveSolutions/okf-plugin/issues/19)
