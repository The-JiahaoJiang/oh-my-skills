# System Design Practice Tracker

This file is the source of truth for the `start-design` skill. Work from top to bottom. An unchecked item is pending; a checked item is complete only after the learner and coach explicitly reach consensus on a design.

## Progress

- **Current issue:** SD-01 — URL shortener
- **Completed:** 0 / 40
- **Mode:** Issues 1–5 are guided; issues 6–40 are interview-style
- **Last updated:** YYYY-MM-DD

## Checklist

### Foundations — guided designs

- [ ] **SD-01 — URL shortener:** Design short-link creation and low-latency redirection with custom aliases, expiration, analytics, and abuse prevention.
- [ ] **SD-02 — Distributed rate limiter:** Enforce per-user, per-IP, and per-API quotas across many gateway instances while handling bursts and partial failures.
- [ ] **SD-03 — Notification service:** Deliver email, SMS, push, and in-app notifications with preferences, retries, templates, scheduling, and deduplication.
- [ ] **SD-04 — Real-time chat:** Support direct and group chat, presence, multi-device synchronization, ordering, offline delivery, and media attachments.
- [ ] **SD-05 — News feed:** Build personalized fan-out, ranking, pagination, reactions, privacy controls, and celebrity-scale distribution.

### Classical distributed systems

- [ ] **SD-06 — Key-value store:** Design a durable distributed store with replication, partitioning, tunable consistency, rebalancing, and recovery.
- [ ] **SD-07 — Message broker:** Provide partitioned topics, consumer groups, retention, replay, backpressure, ordering, and delivery guarantees.
- [ ] **SD-08 — Search autocomplete:** Return low-latency ranked suggestions with freshness, typo tolerance, personalization, and abuse filtering.
- [ ] **SD-09 — Web crawler and indexer:** Crawl the web politely, deduplicate content, schedule recrawls, handle traps, and build a searchable index.
- [ ] **SD-10 — Object storage:** Store huge immutable blobs with multipart upload, metadata, replication, lifecycle policies, and integrity checks.
- [ ] **SD-11 — File synchronization:** Synchronize folders across devices with chunking, version history, conflicts, sharing, and offline edits.
- [ ] **SD-12 — Video streaming platform:** Handle upload, transcoding, global playback, adaptive bitrate, recommendations, rights, and hot content.
- [ ] **SD-13 — Content delivery network:** Route users to edge caches, invalidate content, shield origins, and survive regional failures.
- [ ] **SD-14 — Collaborative document editor:** Support concurrent edits, cursors, comments, history, permissions, and offline reconciliation.
- [ ] **SD-15 — Ride-hailing dispatch:** Match drivers and riders using live geospatial data, ETAs, surge pricing, and trip state transitions.
- [ ] **SD-16 — E-commerce marketplace:** Support catalog, search, carts, inventory, orders, promotions, sellers, and oversell prevention.
- [ ] **SD-17 — Ticket booking:** Allocate scarce seats under extreme contention with holds, waiting rooms, expiration, and fair purchase flows.
- [ ] **SD-18 — Food delivery:** Coordinate customers, restaurants, couriers, menus, order state, batching, ETAs, and substitutions.
- [ ] **SD-19 — Distributed job scheduler:** Run delayed, recurring, and dependency-based jobs with leases, retries, priorities, and idempotency.
- [ ] **SD-20 — Metrics and alerting platform:** Ingest high-cardinality time series, aggregate, retain, query, visualize, and alert reliably.
- [ ] **SD-21 — Log aggregation and search:** Collect, buffer, parse, index, retain, secure, and query logs from a large fleet.
- [ ] **SD-22 — API gateway:** Provide routing, authentication, rate limiting, transformations, observability, canaries, and multi-region resilience.
- [ ] **SD-23 — Identity and authorization:** Implement login, sessions, MFA, OAuth/OIDC, RBAC/ABAC, revocation, and audit trails.
- [ ] **SD-24 — Feature flag service:** Evaluate flags at low latency with targeting, staged rollouts, kill switches, consistency, and auditability.
- [ ] **SD-25 — Distributed cache:** Design sharding, replication, eviction, hot-key handling, stampede protection, and cache coherence.
- [ ] **SD-26 — Distributed coordination service:** Offer locks, leases, leader election, membership, fencing tokens, and failure-safe semantics.
- [ ] **SD-27 — Multi-region SaaS control plane:** Provision tenants, isolate data, enforce quotas, roll out configuration, and recover regions.
- [ ] **SD-28 — Social graph:** Store follows/friends, traverse neighborhoods, recommend connections, enforce privacy, and handle celebrity nodes.

### Fintech and financial infrastructure

- [ ] **SD-29 — Double-entry ledger:** Record immutable balanced postings with idempotency, account balances, corrections, auditability, and high concurrency.
- [ ] **SD-30 — Payment gateway:** Orchestrate card payments across processors with authorization, capture, refunds, retries, webhooks, and PCI boundaries.
- [ ] **SD-31 — Digital wallet:** Manage stored value, top-ups, holds, transfers, withdrawals, limits, account recovery, and ledger integration.
- [ ] **SD-32 — Bank transfer system:** Process ACH/SEPA-like transfers with cutoffs, returns, asynchronous states, idempotency, and beneficiary controls.
- [ ] **SD-33 — Fraud detection platform:** Score transactions in real time using rules and models, feature freshness, feedback loops, and explainability.
- [ ] **SD-34 — Reconciliation platform:** Compare internal ledgers with processor and bank statements, identify breaks, and manage auditable resolution.
- [ ] **SD-35 — Trading exchange:** Build an order gateway and price-time-priority matching engine with market data, risk checks, and deterministic recovery.
- [ ] **SD-36 — Market data distribution:** Ingest exchange feeds, normalize, sequence, aggregate, replay, and distribute low-latency quotes globally.
- [ ] **SD-37 — Pre-trade risk engine:** Enforce credit, position, price, and fat-finger limits synchronously while remaining available and auditable.
- [ ] **SD-38 — Clearing and settlement:** Net obligations, move cash and securities, manage settlement failures, finality, and end-of-day processing.
- [ ] **SD-39 — Subscription billing:** Handle plans, metering, invoices, proration, taxes, collections, dunning, credits, and revenue events.
- [ ] **SD-40 — AML transaction monitoring:** Screen customers and transactions, detect suspicious patterns, manage cases, preserve evidence, and file reports.

## Completion standard

A design reaches consensus only when it adequately covers:

1. Functional requirements and explicit non-goals
2. Scale estimates and service-level objectives
3. APIs/events and core data model
4. High-level architecture and main request/data flows
5. Correctness invariants and consistency choices
6. Partitioning, replication, caching, and hot-spot strategy where relevant
7. Failure handling, retries, idempotency, recovery, and disaster recovery
8. Security, privacy, abuse controls, and compliance where relevant
9. Observability, deployment, migration, and operational concerns
10. Bottlenecks, alternatives, and explicit tradeoffs

Not every category needs equal depth, but skipped categories must be consciously declared irrelevant or out of scope.

## Solved designs

When an issue is completed, append a section here using this exact structure. Preserve the learner's decisions; do not replace them with an idealized answer.

<!--
## SD-XX — Title

- **Completed:** YYYY-MM-DD
- **Learning mode:** Guided design or interview
- **Result:** One-sentence outcome

### Draft-to-final review

#### Stage N — Topic

- **Your draft:** Bullets preserving the learner's proposal
- **What was already strong:** Bullets identifying sound reasoning
- **Shortages found:** Specific gaps and their production consequences
- **Revised design:** Bullets recording the agreed corrections
- **Tradeoff learned:** Concise comparison of viable alternatives
- **Useful references:** Authoritative links when the draft had a material gap or the learner requested help

### Final architecture

```mermaid
flowchart LR
    A[Component] --- B[Component]
```

### Compact final-design reference

<details>
<summary>Expand the complete agreed design and operational record</summary>

- **Requirements and scope:**
- **Scale and SLOs:**
- **APIs and data model:**
- **Architecture and data flow:**
- **Correctness and consistency:**
- **Reliability and failure handling:**
- **Security and compliance:**
- **Observability and operations:**
- **Key decisions:**
- **Tradeoffs and alternatives rejected:**
- **Open risks / future improvements:**
- **Conclusion:**

</details>
-->
