# Traceability

_The evidence chain: plan → item → ticket → code → release, forward and backward. Generated from `docs/.index/_graph.json`; do not edit._

### Cut the v0.3.0 release
`01KYZNSQQQDZD0J6XERYHJF98F` · status: todo
- targets: release/v0.3.0

### Tell agents to verify their worktree base before building
`01KYZNNMWG2ZHJV4YRKPJX0DZE` · status: done
- lands-in: pr/9
- targets: release/v0.3.0

### Clear ticket sync keys left pointing at the old repository
`01KYZNNMGDBGN01Z83896Q4J8H` · status: done
- lands-in: pr/9
- targets: release/v0.3.0

### Regenerate stale IA index so the doc gates stop warning
`01KYZNNM1XEWFFN01EE60THRXK` · status: done
- lands-in: pr/9
- targets: release/v0.3.0

### Release chore — bump to 0.3.0 across the four manifests and README
`01KYZFDBAZW0F3RCN8P9J1R29A` · status: done
- belongs-to: v0.3.0 — fix the plumbing, add the net
- lands-in: pr/8
- produced-by: [[Plan-v030-plumbing-and-tests]]

### Add graph subcommand and the two missing slash commands
`01KYZFDBAZ6G090EZ3FSS0FXS9` · status: done
- belongs-to: v0.3.0 — fix the plumbing, add the net
- lands-in: pr/8
- produced-by: [[Plan-v030-plumbing-and-tests]]

### Qualify intra-plugin paths with CLAUDE_PLUGIN_ROOT
`01KYZFDBAZ62YTTMN7SRGD2QKC` · status: done
- belongs-to: v0.3.0 — fix the plumbing, add the net
- lands-in: pr/8
- produced-by: [[Plan-v030-plumbing-and-tests]]

### Add tests/test_okf_graph.py and wire it into CI and pre-commit
`01KYZFDBAZ0T4W5TZYVXSBXADV` · status: done
- belongs-to: v0.3.0 — fix the plumbing, add the net
- lands-in: pr/8
- produced-by: [[Plan-v030-plumbing-and-tests]]

### v0.3.0 — fix the plumbing, add the net
`01KYZFDBAYGEG2FKWRADN46Z9W` · status: done
- lands-in: pr/8
- contains: Fix the no-op post-edit hook and curate fallback
- contains: Fix okf-graph.py block-sequence YAML, Mermaid IDs, and add validate --strict
- contains: Add tests/test_okf_graph.py and wire it into CI and pre-commit
- contains: Qualify intra-plugin paths with CLAUDE_PLUGIN_ROOT
- contains: Add graph subcommand and the two missing slash commands
- contains: Release chore — bump to 0.3.0 across the four manifests and README
- produced-by: [[Plan-v030-plumbing-and-tests]]

### Fix okf-graph.py block-sequence YAML, Mermaid IDs, and add validate --strict
`01KYZFDBAY2VPBHBNXW7E4ZKHF` · status: done
- belongs-to: v0.3.0 — fix the plumbing, add the net
- lands-in: pr/8
- produced-by: [[Plan-v030-plumbing-and-tests]]

### Fix the no-op post-edit hook and curate fallback
`01KYZFDBAY0AX03XQ6SAT6SXJW` · status: done
- belongs-to: v0.3.0 — fix the plumbing, add the net
- lands-in: pr/8
- produced-by: [[Plan-v030-plumbing-and-tests]]

### Local Substack→OKF integration test runner
`01KYW8WH356FYJ3PM9EFKB8BCW` · status: done
- targets: release/v0.3.0

### Pack progressive disclosure should be outbound-only by default
`01KYR4G11VPKJBWGJV1QD0H184` · status: done
- targets: release/v0.2.1

### Fix okf-graph pack/impact on large OKF bundles with dir links
`01KYR4792FJKSZW81SJ4F45HAC` · status: done
- targets: release/v0.2.1

### Fix red wiki Home links with missing guide and design docs
`01KYR36M2K9CB3ZMAMG0NFNKV1` · status: done
- targets: release/v0.2.1

### Publish docs to SpillwaveSolutions GitHub wiki
`01KYR201M64QHFBVGV3FZ1GS4F` · status: done
- targets: release/v0.2.1

### Move okf-plugin to SpillwaveSolutions org
`01KYR1W31GBAGDJEMY077HFM0J` · status: done
- targets: release/v0.2.1

### Publish public GitHub repo okf-plugin
`01KYQZ5FE1NZM2VB2E43MJMNCQ` · status: done
- belongs-to: OKF graph-eng plugin MVP v0.1
- targets: release/v0.1.0

### Ship dual-host README, CLAUDE.md, AGENTS.md
`01KYQZ5F4W0P0GWM6JHQBWFKGY` · status: done
- belongs-to: OKF graph-eng plugin MVP v0.1
- targets: release/v0.1.0

### Ship sample-okf self-describing dual graph
`01KYQZ5EVN14SMZW8KW60K42G8` · status: done
- belongs-to: OKF graph-eng plugin MVP v0.1
- targets: release/v0.1.0

### Ship GraphEngineer agent and slash commands
`01KYQZ5EJJJQNPT07017JQQWMM` · status: done
- belongs-to: OKF graph-eng plugin MVP v0.1
- targets: release/v0.1.0

### Ship seven OKF graph-eng skills
`01KYQZ5E9M9DDN8N84V2CZ5Q2Z` · status: done
- belongs-to: OKF graph-eng plugin MVP v0.1
- targets: release/v0.1.0

### OKF graph-eng plugin MVP v0.1
`01KYQZ5E4X4XZ1XZ39FC4SKWBN` · status: done
- contains: Ship seven OKF graph-eng skills
- contains: Ship GraphEngineer agent and slash commands
- contains: Ship sample-okf self-describing dual graph
- contains: Ship dual-host README, CLAUDE.md, AGENTS.md
- contains: Publish public GitHub repo okf-plugin

### Capture MVP v0.1 delivery as closed worklog history
`01KYQZ4PANSHKME2QNA8FZVVGC` · status: done
- belongs-to: Adopt WikiTicket SDD for okf-plugin
- produced-by: [[Plan-wiki-ticket-adoption]]

### Link sample-okf TicketLink concepts to real worklog ULIDs
`01KYQZ4PANS9D55RG19VMXGQ1V` · status: done
- belongs-to: Adopt WikiTicket SDD for okf-plugin
- targets: release/v0.2.0
- produced-by: [[Plan-wiki-ticket-adoption]]

### Optional Claude marketplace listing for okf-graph-eng
`01KYQZ4PANQFYAMMEBBHYPPG6P` · status: done
- belongs-to: Adopt WikiTicket SDD for okf-plugin
- references: [github#6](https://github.com/RichardHightower/okf-plugin/issues/6)
- targets: release/v0.2.0
- produced-by: [[Plan-wiki-ticket-adoption]]

### v0.2 — richer typed-edge conventions and TicketLink SLDC helpers
`01KYQZ4PANG2JE670X42GCZY6S` · status: done
- belongs-to: Adopt WikiTicket SDD for okf-plugin
- references: [github#5](https://github.com/RichardHightower/okf-plugin/issues/5)
- targets: release/v0.2.0
- produced-by: [[Plan-wiki-ticket-adoption]]

### v0.2 — GraphEngineer polish and progressive-disclosure defaults
`01KYQZ4PAN71X19C6ZZVM42ZS2` · status: done
- belongs-to: Adopt WikiTicket SDD for okf-plugin
- references: [github#4](https://github.com/RichardHightower/okf-plugin/issues/4)
- targets: release/v0.2.0
- produced-by: [[Plan-wiki-ticket-adoption]]

### Publish initial roadmap and plan to GitHub wiki
`01KYQZ4PAN6A8EX36M2ZRWMDAZ` · status: done
- belongs-to: Adopt WikiTicket SDD for okf-plugin
- references: [github#3](https://github.com/RichardHightower/okf-plugin/issues/3)
- targets: release/v0.1.1
- produced-by: [[Plan-wiki-ticket-adoption]]

### Sync open work items to GitHub Issues
`01KYQZ4PAN551JXFMH2GF82BXF` · status: done
- belongs-to: Adopt WikiTicket SDD for okf-plugin
- references: [github#2](https://github.com/RichardHightower/okf-plugin/issues/2)
- targets: release/v0.1.1
- produced-by: [[Plan-wiki-ticket-adoption]]

### Configure GitHub Issues and GitHub wiki in .work/config.yml
`01KYQZ4PAN1WHT2YGX667F3EX6` · status: done
- belongs-to: Adopt WikiTicket SDD for okf-plugin
- produced-by: [[Plan-wiki-ticket-adoption]]

### Adopt WikiTicket SDD for okf-plugin
`01KYQZ4PAMZCM9N56K8F3034F2` · status: done
- references: [github#1](https://github.com/RichardHightower/okf-plugin/issues/1)
- contains: Scaffold worklog tooling in okf-plugin
- contains: Configure GitHub Issues and GitHub wiki in .work/config.yml
- contains: Sync open work items to GitHub Issues
- contains: Publish initial roadmap and plan to GitHub wiki
- contains: v0.2 — GraphEngineer polish and progressive-disclosure defaults
- contains: v0.2 — richer typed-edge conventions and TicketLink SLDC helpers
- contains: Optional Claude marketplace listing for okf-graph-eng
- contains: Link sample-okf TicketLink concepts to real worklog ULIDs
- contains: Capture MVP v0.1 delivery as closed worklog history
- produced-by: [[Plan-wiki-ticket-adoption]]

### Scaffold worklog tooling in okf-plugin
`01KYQZ4PAMK1ND4XKH8A1VHMFN` · status: done
- belongs-to: Adopt WikiTicket SDD for okf-plugin
- produced-by: [[Plan-wiki-ticket-adoption]]

