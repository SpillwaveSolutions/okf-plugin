---
type: DecisionRecord
title: Use Stripe for card processing
description: Charge cards via Stripe rather than a custom processor.
timestamp: 2026-08-13T00:00:00Z
status: accepted
verified: true
truth_state: current
wiki_key: adr-use-stripe
tags: [decision, adr]
links:
  - target: /features/checkout.md
    rel: decides
---

# Use Stripe

## Context

Need a PCI-compliant processor.

## Decision

Stripe.

## Consequences

Webhook + idempotency keys.
