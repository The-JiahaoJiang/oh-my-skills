# Oh My Skills

A collection of reusable [Pi](https://pi.dev) agent skills for structured engineering practice.

**[Explore the interactive project site →](https://the-jiahaojiang.github.io/oh-my-skills/)**

The site visualizes both learning workflows with architecture graphs, draft-to-revised examples, source-learning diagrams, and installation instructions. It is built and deployed to GitHub Pages by GitHub Actions on every relevant push to `main`.

## Included skills

### `start-design`

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

### `learn-project`

`learn-project` turns a source repository into an evidence-backed, function-level learning curriculum. It first maps the project's architecture, then guides the learner through concrete functions in an order that follows real initialization, request, control, and data flows.

Invoke it with one repository name or relative path beneath the current working directory:

```text
/skill:learn-project my-repository
```

#### Architecture analysis

When study artifacts are missing, the skill selectively inspects repository documentation, manifests, entry points, public APIs, module boundaries, tests, deployment files, and representative execution paths. It also researches authoritative external material about the project and its closest alternatives.

The analysis covers:

- project purpose, users, scope, and primary use cases;
- modules, responsibilities, dependencies, boundaries, and public interfaces;
- representative end-to-end request, data, and control flows;
- runtime, state ownership, concurrency, persistence, networking, and extension points;
- build, testing, packaging, deployment, and operational architecture;
- security boundaries, trust assumptions, failures, and error handling;
- strengths, weaknesses, tradeoffs, and comparisons with similar projects;
- a source-code map connecting claims to repository-relative files, symbols, and line ranges;
- analyzed revision, uncertainties, and repository/external references.

Architectural claims are grounded in source code or cited external evidence. Inferences are labeled rather than presented as verified facts.

#### Function-level learning plan

The generated curriculum selects exactly one concrete function or method per step. Each stable step records:

- a module and step ID such as `M01-S01`;
- the fully qualified function name where available;
- repository-relative source path and original line range;
- why the function matters and what should be learned;
- prerequisites and a link to the eventual session note.

The plan prioritizes functions that collectively explain the architecture, including initialization, core behavior, state and data flow, error paths, concurrency, performance, security, extensibility, and testing where relevant.

#### Interactive source-learning sessions

For each step, Pi reads the current function plus the callers, callees, types, tests, and configuration needed to explain it accurately. The session includes:

1. the function's architectural role, inputs, outputs, side effects, invariants, and collaborators;
2. simplified, sequentially numbered code that preserves important control flow, state changes, async boundaries, security checks, errors, and resource lifetime;
3. one open-ended question at a time about the most relevant correctness, performance, concurrency, security, recovery, or API tradeoffs;
4. feedback that identifies what the learner got right, omissions or misconceptions, and a recommended answer grounded in the code;
5. a durable session note containing the simplified function, questions, learner answers, feedback, takeaways, and optional experiments.

Progress is updated only after the session note is successfully written. The skill never modifies the repository's source code.

#### Generated study artifacts

The target repository receives:

- `ARCHITETURE.html` — standalone architecture report with diagrams, comparisons, source-code mapping, uncertainty notes, and references;
- `LEARNING_PLAN.md` — ordered function-level curriculum and progress tracker;
- `LEARNING_NOTES/<module>/<date>-<function>.md` — completed interactive session records.

`ARCHITETURE.html` retains the historical spelling used by this skill. Existing architecture and learning-plan files are preserved unless regeneration is explicitly requested.

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

Reload Pi and invoke either skill:

```text
/reload
/skill:start-design
/skill:learn-project my-repository
```

On the first `start-design` invocation, the skill initializes the Markdown and HTML reports. Invoke it again to begin SD-01 or resume the first incomplete exercise. `learn-project` creates missing architecture and learning-plan artifacts on its first invocation, then begins the function-level curriculum on a later invocation.
