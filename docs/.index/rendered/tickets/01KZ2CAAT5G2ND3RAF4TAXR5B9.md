# v0.3.1 — correctness cleanup and traceability backfill

`01KZ2CAAT5G2ND3RAF4TAXR5B9` · epic/ops · **done**

Clear the defects found while fixing v0.3.0: logic that is dead, silent, or wrong without crashing, plus the public traceability gap left by the move to the SpillwaveSolutions org.

## Children

- [[Ticket-01KZ2CAAT56M9V49211G7NVBYV]] Escalate unverified medium-impact concepts in criticality_of — The unverified branch reassigns medium to itself, so a medium-impact concept
never escalates no matter its state. (done)
- [[Ticket-01KZ2CAAT5C7PGNP8QDXGJJB9E]] Report ambiguous concept lookups instead of guessing — Concept resolution accepts any path ending with the query, and returns
whichever match comes first in iteration order. (done)
- [[Ticket-01KZ2CAAT5JS108XWJ4T00B3V1]] Make merge_edges precedence match what it documents — The third clause of the precedence test is true for every frontmatter edge,
so the two clauses before it can never decide anything. (done)
- [[Ticket-01KZ2CAAT61CM8G0N25MPDEHRQ]] Correct the plan page published to the wiki — The adoption plan shows seven unchecked tasks that the work log records as
closed, and points at the pre-move repository. (done)
- [[Ticket-01KZ2CAAT64CERBRZMR7AJZ5XW]] Build the undirected adjacency once in subgraph — Subgraph walks the edge set twice to build one adjacency map, which is
harmless only because the result is deduped immediately after. (done)
- [[Ticket-01KZ2CAAT66ZFTBX9NQ7Z0AKKX]] Backfill external tickets for closed work — Every closed item lacks an external ticket: the originals live in the
pre-move repository and their keys were cleared in v0.3.0 because they
collided with this repo's pull request numbers. (done)
- [[Ticket-01KZ2CAAT6XQ5WCT70AS6QQNTY]] Flag links that point outside the bundle — A link resolving outside the bundle root is dropped before validation ever
sees it, so a mistyped path is invisible rather than broken. (done)
- [[Ticket-01KZ2CAAT6YNARXMA7HMNM1AZ1]] Curate the bundle wherever it is rooted — The post-edit hook filters on three hard-coded path fragments, so a bundle
rooted anywhere else is skipped entirely. (done)
- [[Ticket-01KZ2CAAT6Z9Q09MMFFWD7XH1R]] Skip dot-directories when loading a bundle — Bundle loading skips dot-files but walks dot-directories, so pointing it at a
repo root pulls the work log and other internal trees in as concepts. (done)

Progress: 9/9 done

## Related tickets

- [github #16](https://github.com/SpillwaveSolutions/okf-plugin/issues/16)
