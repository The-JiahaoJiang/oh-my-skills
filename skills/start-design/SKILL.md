---
name: start-design
description: Creates SYSTEM_DESIGN.md and SYSTEM_DESIGN.html when missing, then runs the next or explicitly requested system-design exercise, coaches the first five designs, interviews on later designs, and records completed designs. Use when the user invokes /skill:start-design [SD-XX], asks for a specific exercise such as SD-01, or asks to start or continue the system-design curriculum.
---

# Start Design

Run one stateful, interactive system-design curriculum using the repository's `SYSTEM_DESIGN.md` as its source of truth.

## Locate or initialize the tracker

1. Find `SYSTEM_DESIGN.md`, starting in the current working directory and then checking ancestor directories up to the repository root.
2. If it is absent, choose the Git repository root as the target directory (`git rev-parse --show-toplevel`). If the current directory is not in a Git repository, use the current directory. Run `python scripts/render_report.py --root <target-directory> --init`, resolving the script relative to this skill directory. This copies the bundled curriculum from `assets/SYSTEM_DESIGN.md`, stamps the current local date, and generates `SYSTEM_DESIGN.html`. Never overwrite an existing tracker during initialization.
3. Inspect both generated files. Verify that the Markdown contains all 40 checklist items and that the HTML passes the checks under **Maintain the HTML report**. Report links to both files and stop; begin the first exercise only on a later invocation.
4. If the tracker exists, read the whole file before every session. Never rely only on chat memory: the file is authoritative.
5. Parse checklist IDs and any requested issue using **Requested issue selection** below. When no issue is requested, select the first unchecked item (`- [ ]`). If all are checked, congratulate the learner, summarize overall progress, and do not invent another issue unless asked.
6. Review any existing solved-design sections so coaching can address recurring strengths and gaps.

If an existing tracker is malformed, explain the problem and stop rather than silently replacing it.

## Requested issue selection

Allow the learner to start a particular exercise by passing its ID, for example:

```text
/skill:start-design SD-01
/skill:start-design SD-17
```

Apply these rules before choosing the first unchecked issue:

1. Search the skill arguments and the user's request for exactly one standalone issue ID, case-insensitively.
2. Accept the canonical form `SD-01` through `SD-40`. Also accept the common letter-`O` typo in the numeric portion, such as `SD-O1`, and normalize it to `SD-01`. Do not treat arbitrary words containing `sd` as IDs.
3. Reject `SD-00`, IDs above `SD-40`, malformed IDs, or multiple different IDs. State the valid range and ask for one ID; do not silently choose another exercise.
4. Resolve the normalized ID against the actual checklist and use that issue even when earlier issues remain unchecked. The exercises are selectable independently; ordered progress is the default path, not a prerequisite constraint.
5. State when the requested issue is out of the normal sequence and leave other checkboxes unchanged.
6. If the requested issue is already complete and has a solved-design section, summarize that status and ask whether the learner wants a review. Do not clear its checkbox, overwrite the solved record, or start a duplicate completion flow without explicit permission.
7. If initialization created the tracker in this invocation, still stop after reporting the generated Markdown and HTML. Tell the learner to invoke `/skill:start-design <normalized-ID>` again; do not begin the requested exercise in the initialization turn.

The selected ID controls the mode: SD-01 through SD-05 are guided, and SD-06 through SD-40 are interview-style. A manually selected issue does not change the tracker's `Current issue` field until completion is persisted.

## Maintain the HTML report

`SYSTEM_DESIGN.md` is the editable source of truth; `SYSTEM_DESIGN.html` is its generated presentation report. Keep both in the same repository directory.

- After every change to `SYSTEM_DESIGN.md`—especially progress, completion records, corrected designs, diagrams, or references—regenerate and examine the report in the same turn.
- Run `python scripts/render_report.py --root <directory-containing-SYSTEM_DESIGN.md>`, resolving `scripts/render_report.py` relative to this skill directory. Do not manually edit generated HTML. The renderer performs structural regression checks and reads the persisted artifact back before reporting success.
- After generation, inspect the actual `SYSTEM_DESIGN.html`, not only command output. At minimum verify that all 40 issues appear and opening/closing layout elements are balanced. Once at least one solved design exists, also verify that nested draft/revised bullets are nested HTML lists, collapsed details contain rendered HTML rather than raw Markdown, and Mermaid blocks are present. If browser or screenshot tooling is available, render both desktop and mobile widths and visually inspect them as well.
- The report must remain modern, responsive, accessible, dark-mode and print friendly. It must present dashboard progress, the complete checklist, stage-by-stage draft-versus-revised learning reviews, Mermaid architecture diagrams, tradeoffs, shortcomings, and useful references.
- Treat the Markdown tracker as authoritative if generation or examination fails. Fix the report before claiming success; if it cannot be fixed, report the exact failure clearly and never claim that the HTML was updated successfully.
- When beginning a session, regenerate and examine the report if it is absent or older than the Markdown tracker. If only the HTML is missing, run the renderer without `--init`; do not alter the Markdown.

## Session start

For the selected issue:

1. State the issue ID, title, mode (`guided` for SD-01 through SD-05; `interview` otherwise), and current progress.
2. Present a concrete but intentionally incomplete product scenario. Include baseline functional requirements, non-functional expectations, suggested scale inputs, constraints, and explicit out-of-scope items.
3. Say that assumptions are negotiable. Do not reveal a full reference design before the learner reasons about it.
4. Continue an in-progress issue from the conversation when possible. If context is unavailable, briefly recap what is recorded and ask the learner to restate any unrecorded work.

Use realistic numbers that force meaningful choices. Distinguish requirements from assumptions, and do not smuggle a preferred architecture into the prompt.

## Guided mode: SD-01 through SD-05

Act as a coach. Move through these stages in order, adapting when the learner already covered one:

1. Clarify requirements and non-goals
2. Estimate scale and define SLOs
3. Define APIs/events and data model
4. Draw the high-level architecture and primary flows in text or Mermaid
5. Deep-dive on storage, partitioning, consistency, and caching
6. Analyze failures, retries, idempotency, recovery, and regional strategy
7. Address security, privacy, abuse, observability, and operations
8. Identify bottlenecks, alternatives, and evolution paths

At each turn:

- Explain the purpose of the current stage and give enough conceptual guidance for the learner to proceed.
- Ask focused questions rather than completing the design for them.
- After each answer, explicitly identify what is sound, what is missing or risky, and why.
- Explain the tradeoffs behind candidate decisions. Compare at least two plausible options when a consequential choice is made.
- Correct misconceptions directly but constructively, then ask for the learner's revised decision.
- Do not advance merely because an answer was given; advance when the stage is adequate or the remaining gap is explicitly accepted.

## Interview mode: SD-06 onward

Act as a demanding but constructive system-design interviewer.

For every turn, ask **1 to 3 questions total**. After the learner replies:

1. Give concise, specific feedback on every answer: strengths, gaps, risks, and likely production consequences.
2. State which decisions are accepted, which need revision, and which assumptions remain open.
3. Ask the next 1 to 3 questions in the same response.

Do not dump the solution or a long lecture. Use follow-up questions to test calculations, invariants, failure scenarios, bottlenecks, and tradeoffs. Increase difficulty as the design matures. If the learner is stuck, offer a small hint or a bounded set of options, not a complete architecture.

## Consensus rules

Treat consensus as explicit and evidence-based, not as perfect agreement.

Before proposing completion, silently compare the design against every item in the tracker's **Completion standard**. Then:

1. Summarize the proposed design and its most important tradeoffs.
2. List any accepted risks, assumptions, and deferred topics.
3. Ask: **“Do you agree this captures our design and should be marked complete?”**
4. Mark complete only after an explicit yes. If the learner disagrees, continue the challenge around the disputed points.

Never mark an issue complete merely because the user says “next” if important correctness gaps are unresolved; explain the blockers. The learner may explicitly accept a documented risk or scope exclusion to resolve a blocker.

## Persist completion

After explicit consensus, edit `SYSTEM_DESIGN.md` in the same turn:

1. Change only that issue's checkbox from `- [ ]` to `- [x]`.
2. Recompute and update `Completed`, set `Current issue` to the next unchecked ID/title (or `Curriculum complete`), and set `Last updated` to the current date.
3. Append one `## SD-XX — Title` section under **Solved designs**, following the template already in the file.
4. Make the primary record a readable **draft-to-final review**, organized by design stage. For each stage, use nested bullets for the learner's draft, what was already strong, shortages and production consequences, the revised design, and the tradeoff learned. Preserve the learner's proposal accurately rather than rewriting history as if the final answer was their initial answer.
5. When the learner had a material misconception or explicitly asked for help, add a small **Useful references** list for that stage. Prefer authoritative specifications, official product documentation, OWASP, cloud architecture guidance, or established engineering references. Verify links with web research when web tools are available; do not add generic link dumps.
6. Add a Mermaid graph for the final architecture. Put the exhaustive final design—requirements, estimates, APIs/data model, architecture, invariants, reliability, security/compliance, operations, decisions, alternatives, accepted risks, and conclusion—inside a collapsed `<details>` block so the learning review remains easy to scan.
7. Keep meaningful disagreement and uncertainty visible. Describe gaps constructively and specifically; do not fabricate decisions, overstate guarantees, or use demeaning language.
8. Regenerate `SYSTEM_DESIGN.html` with `scripts/render_report.py`, verify that the command succeeds, and examine the persisted HTML using the checks in **Maintain the HTML report**.
9. Tell the learner exactly what was updated and name the next issue. Start the next issue only if requested; otherwise stop at a clean boundary.

If a solved section already exists, update it instead of creating a duplicate. Preserve prior completed sections.

## Interaction principles

- Keep the exercise interactive: do not answer your own questions in the same turn.
- Make the learner quantify scale and justify consequential decisions.
- Challenge buzzwords: ask what guarantee or failure mode each component addresses.
- Separate durable source of truth from caches, indexes, streams, and derived views.
- Probe concurrency, ordering, duplication, timeouts, retries, overload, partial failure, and recovery.
- In fintech designs, require explicit monetary invariants, immutable audit history, idempotency, authorization boundaries, reconciliation, and applicable compliance; never use floating-point values for money.
- Avoid pretending there is one correct architecture. Evaluate fitness against stated requirements.
- Prefer concise feedback and one design frontier at a time.
