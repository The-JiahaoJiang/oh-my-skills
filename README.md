# Oh My Skills

A collection of reusable [Pi](https://pi.dev) agent skills for structured engineering practice.

## Included skill: `start-design`

`start-design` runs a stateful, interactive system-design curriculum with 40 exercises covering foundational services, distributed systems, platform infrastructure, and fintech systems.

The skill is designed to reveal *why* a design changes—not just present a polished reference architecture. It records the learner's initial draft, identifies knowledge shortages and production risks, and preserves the revised design reached through coaching or interview feedback.

### Learning modes

- **SD-01 through SD-05 — Guided:** Pi explains the purpose of each design stage, provides bounded guidance, evaluates the learner's answer, and asks for revisions where needed.
- **SD-06 through SD-40 — Interview:** Pi acts as a demanding but constructive interviewer, asking 1–3 focused questions per turn and probing calculations, invariants, bottlenecks, failures, and tradeoffs.

A design is marked complete only after the learner and Pi explicitly agree that it adequately covers the completion standard.

### What each exercise covers

Depending on the problem, the discussion works through:

1. functional requirements and non-goals;
2. capacity estimates, latency targets, availability, RPO, and RTO;
3. APIs, events, and data models;
4. high-level architecture and request/data flows;
5. consistency, partitioning, replication, caching, and hot spots;
6. retries, idempotency, partial failures, recovery, and regional strategy;
7. security, privacy, abuse prevention, and compliance;
8. observability, deployment, migration, bottlenecks, and evolution paths.

### Draft-to-final learning review

For every completed exercise, the skill records a stage-by-stage review containing:

- **Your draft:** The learner's original proposal, preserved accurately.
- **What was already strong:** Correct decisions and sound reasoning.
- **Shortages found:** Missing knowledge, unsafe assumptions, and likely production consequences.
- **Revised design:** The corrected design agreed upon after discussion.
- **Tradeoff learned:** A comparison of plausible alternatives and why one fits the stated requirements.
- **Useful references:** Related specifications and authoritative documentation when a material knowledge gap is found or the learner requests help.

References favor primary sources such as RFCs, official database and cloud documentation, OWASP guidance, and established SRE material rather than generic link collections.

Example review structure:

```markdown
#### Stage 3 — API, data model, and idempotency

- **Your draft:** Use a distributed lock to prevent duplicate records.
- **What was already strong:** Correctly identified concurrent creation as a correctness risk.
- **Shortages found:** A lock can expire or split during a partition and is not the final uniqueness boundary.
- **Revised design:** Enforce uniqueness with an atomic database constraint and persist the idempotency result in the same transaction.
- **Tradeoff learned:** Database constraints simplify correctness but constrain data placement and transaction boundaries.
- **Useful references:** Links to the relevant database and HTTP idempotency documentation.
```

### Persistent Markdown and HTML reports

On first use, the skill creates these files in the working repository:

- `SYSTEM_DESIGN.md` — editable source of truth containing progress, the 40-item checklist, and completed draft-to-final reviews.
- `SYSTEM_DESIGN.html` — generated responsive report with progress dashboards, completed reviews, Mermaid architecture diagrams, references, dark mode, and print styling.

The Markdown file remains authoritative. The HTML report is regenerated and structurally validated whenever progress changes. Existing trackers are never overwritten during initialization.

### Curriculum topics

The 40 exercises include:

- URL shortener, distributed rate limiter, notifications, chat, and news feed;
- key-value stores, message brokers, search, object storage, CDN, collaboration, and scheduling;
- API gateways, identity, feature flags, distributed caches, coordination, and multi-region SaaS;
- ledgers, payments, wallets, bank transfers, fraud detection, reconciliation, trading, settlement, billing, and AML monitoring.

## Requirements

- [Pi coding agent](https://pi.dev)
- Python 3
- Python [`markdown`](https://python-markdown.github.io/) package for HTML generation

Install the renderer dependency:

```bash
python -m pip install markdown
```

## Install

Install directly from GitHub:

```bash
pi install git:github.com/The-JiahaoJiang/oh-my-skills
```

Or install from a local checkout:

```bash
pi install /path/to/oh-my-skills
```

Alternatively, copy `skills/start-design` into `~/.pi/agent/skills/`.

Reload Pi and start or continue the curriculum:

```text
/reload
/skill:start-design
```

On the first invocation, the skill initializes the Markdown and HTML reports. Invoke it again to begin SD-01 or resume the first incomplete exercise.
