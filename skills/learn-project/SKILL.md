---
name: learn-project
description: Analyze a source repository beneath the current workspace, centrally store its architecture report, learning plan, identity metadata, and session notes under the workspace repository, and run an interactive function-level source-learning curriculum with feedback and progress tracking. Use when the user invokes /skill:learn-project with a repository path or asks to study and track a project's architecture and source code.
---

# Learn Project

Treat the skill argument as the name or relative path of one source repository beneath the current workspace repository.

## Safety and path resolution

1. Require exactly one repository argument. If it is missing, ask for it and stop.
2. Resolve the current Git repository root and call it `WORKSPACE`. If the current directory is not inside a Git repository, explain that centralized, syncable study state requires a workspace repository and stop.
3. Resolve the argument against the current working directory and call the result `REPO`. Reject a path that resolves outside `WORKSPACE`, equals `WORKSPACE`, does not exist, or is not a directory.
4. Keep all generated study state in `WORKSPACE`, never in `REPO`. The target repository is read-only: do not create, update, move, or delete source files or study artifacts inside it.
5. Never write to a nested target repository's Git metadata. Respect ignored/generated/vendor directories. Start with repository metadata and manifests, then inspect source selectively. Do not bulk-read dependencies, build output, minified files, generated files, binaries, or secrets. Never reproduce secret values in study material.
6. Use workspace-relative paths for synchronized metadata and links whenever possible. Never persist machine-specific absolute paths.

## Central study layout and project correlation

Store every project's learning material beneath this workspace-owned root:

```text
WORKSPACE/PROJECT_LEARNING/
├── projects.json
└── <project-key>/
    ├── PROJECT.json
    ├── ARCHITETURE.html
    ├── LEARNING_PLAN.md
    └── LEARNING_NOTES/
        └── <module-slug>/YYYY-MM-DD-<function-slug>.md
```

`ARCHITETURE.html` retains its historical spelling. Call the project directory `STUDY_ROOT`. All checks, reads, writes, progress updates, and note creation must use `STUDY_ROOT`; never fall back to similarly named files in `REPO`.

### Stable project identity

Correlate central files to the source project with both a human-readable key and synchronized metadata:

1. Derive `projectName` from the target Git root's directory name. If the target is not a Git repository, use `REPO`'s directory name.
2. Convert `projectName` to a lowercase filesystem-safe slug. Preserve letters and numbers, collapse other runs to one hyphen, and trim hyphens. Use `project` if the result is empty.
3. Read the target's `origin` fetch URL when available. Normalize HTTPS, `ssh://`, and SCP-like `user@host:path` forms to one credential-free identity, `https://<lowercase-host>/<repository-path>`, so SSH and HTTPS clones of the same project correlate. Remove userinfo, tokens, default ports, duplicate slashes, a trailing `.git`, and a trailing slash. Retain a non-default port. Treat local/file remotes as unavailable rather than persisting machine-specific paths. Never persist secrets from a remote URL.
4. Build the identity seed from the sanitized canonical remote URL when available; otherwise use the normalized POSIX-style path from `WORKSPACE` to `REPO`.
5. Compute the first eight lowercase hexadecimal characters of SHA-256 over the UTF-8 identity seed. Set `projectKey` to `<project-slug>--<hash8>`, for example `redis--3a71c9e2`. The readable prefix identifies the project; the hash prevents collisions between forks or same-named directories.
6. Before creating a key, read `PROJECT_LEARNING/projects.json`. Reuse an existing entry when its sanitized remote matches, or—when no remote exists—its repository-relative path matches. This keeps identity stable when the display name changes. Never silently merge two different remotes.
7. Set `STUDY_ROOT` to `WORKSPACE/PROJECT_LEARNING/<projectKey>`.

Create `STUDY_ROOT/PROJECT.json` with this portable shape:

```json
{
  "schemaVersion": 1,
  "projectKey": "redis--3a71c9e2",
  "projectName": "redis",
  "repository": {
    "workspaceRelativePath": "sources/redis",
    "remote": "https://github.com/redis/redis"
  },
  "artifacts": {
    "architecture": "ARCHITETURE.html",
    "learningPlan": "LEARNING_PLAN.md",
    "notes": "LEARNING_NOTES"
  },
  "createdAt": "YYYY-MM-DD",
  "updatedAt": "YYYY-MM-DD"
}
```

Use `null` for an unavailable remote. Preserve `createdAt`; update `updatedAt` only when this skill changes project study state. Maintain `PROJECT_LEARNING/projects.json` as a sorted registry using this shape:

```json
{
  "schemaVersion": 1,
  "projects": [
    {
      "projectKey": "redis--3a71c9e2",
      "projectName": "redis",
      "repository": {
        "workspaceRelativePath": "sources/redis",
        "remote": "https://github.com/redis/redis"
      },
      "manifest": "PROJECT_LEARNING/redis--3a71c9e2/PROJECT.json"
    }
  ]
}
```

Sort entries by `projectKey`. Write valid UTF-8 JSON with stable two-space indentation and a trailing newline. Update the registry and manifest together; do not leave one pointing to a missing directory.

Validate correlation on every invocation:

- the registry entry, directory name, and manifest `projectKey` must agree;
- the manifest's workspace-relative source path must resolve to `REPO` without escaping `WORKSPACE`;
- a stored remote mismatch is an identity conflict, not an automatic update;
- if a repository moved inside the workspace but the sanitized remote still matches, update only its workspace-relative path;
- if neither path nor remote identifies an existing entry, create a new project key rather than reusing another project's notes.

Use the local date. Make note slugs filesystem-safe. If overloaded or duplicate function names would collide, add a short class, namespace, or file qualifier to `function-slug`.

### Legacy target-repository artifacts

At startup, check `REPO` for legacy `ARCHITETURE.html`, `LEARNING_PLAN.md`, or `LEARNING_NOTES/` created by older versions of this skill.

- Never continue updating those target-local files.
- If `STUDY_ROOT` has no corresponding artifacts, offer to migrate them. With user approval, copy them into `STUDY_ROOT`, rewrite only note links needed for the central layout, validate the copy, and then ask separately before deleting the originals.
- If central and legacy artifacts both exist, keep the central copy authoritative and report the legacy files; do not merge or overwrite automatically.
- Never delete target-local artifacts without explicit confirmation, even after a successful migration.

## Initial inspection

After validating `PROJECT.json` and the central registry, check independently whether `STUDY_ROOT/ARCHITETURE.html` and `STUDY_ROOT/LEARNING_PLAN.md` exist.

Also inspect, in this order:

1. repository tree, README and contributor documentation;
2. package/build/workspace manifests and lockfiles;
3. entry points, public APIs, configuration, and module boundaries;
4. tests, examples, benchmarks, deployment files, and important cross-cutting code;
5. git metadata when available, only as needed to understand active components.

Detect the primary languages and use appropriate symbol/search tools available in the environment. Trace representative execution paths rather than reading files indiscriminately. Every architectural claim should be grounded in source code or a cited external source; label inferences as inferences.

## Missing-file workflow

If either required file is missing from `STUDY_ROOT`, perform architecture research before creating the missing central file(s). Create or validate the project manifest and registry first.

### Research

Search the web for authoritative material about the repository and its closest alternatives. Prefer:

- the project's official documentation and website;
- upstream repository documentation, design documents, release notes, and maintainer discussions;
- primary documentation for important frameworks/protocols;
- credible benchmarks or technical comparisons whose versions and methodology are stated.

Use multiple focused searches when comparison, internals, and use cases need different evidence. Distinguish verified facts from reasoned assessments. Do not invent benchmark results. Record source titles, URLs, and access date in the HTML.

### Generate `ARCHITETURE.html`

Create a standalone, readable HTML5 document that works locally without a server or remote JavaScript. Inline CSS is allowed. Escape source-derived text before embedding it. Include:

1. project purpose, scope, primary users, and primary use cases;
2. a high-level architectural overview and representative end-to-end request/data/control flows;
3. module partitioning, responsibilities, dependencies, boundaries, and important public interfaces;
4. runtime model, state/data ownership, concurrency model, persistence, networking, and extension points where applicable;
5. build, test, packaging, deployment, and operational architecture where applicable;
6. security boundaries, trust assumptions, and failure/error-handling strategy;
7. notable strengths and exactly how implementation/design choices produce them;
8. notable weaknesses, trade-offs, and the technical or organizational factors that contribute to them;
9. a fair comparison table with a small set of genuinely similar projects, including where this project is or is not a good fit;
10. a “Source-code map” linking claims to `REPO`-relative file paths and symbols, with original line ranges when reliably available; because the HTML lives outside `REPO`, display source paths as repository-relative text and compute any clickable local `href` relative from `STUDY_ROOT` to the source file;
11. project identity from `PROJECT.json` (`projectName`, `projectKey`, workspace-relative repository path, and sanitized remote), plus uncertainty/version notes: analyzed revision or commit (if available), current date, and areas not verified;
12. references with clickable URLs, titles, access dates, and a distinction between repository evidence and external evidence.

Use diagrams where useful. Prefer inline SVG or semantic HTML/CSS; include text explanations so diagrams are not the only representation. Do not use Mermaid unless it is bundled and works offline.

If `STUDY_ROOT/ARCHITETURE.html` already exists, preserve it. Read it as an input when making a missing learning plan. Only replace it when the user explicitly requests regeneration. If it is missing, generate it in `STUDY_ROOT` even when the plan already exists, and then report material inconsistencies without silently rewriting the plan.

### Generate `LEARNING_PLAN.md`

Base the curriculum on the architecture analysis and actual source tree. If the HTML exists, read it first. Create the plan only if missing unless the user explicitly requests regeneration.

The plan must contain:

- `projectName`, `projectKey`, sanitized remote when available, and the workspace-relative path from `WORKSPACE` to `REPO`;
- analyzed revision/commit and date;
- learning goals and suggested prerequisites;
- a module-by-module order that follows real execution/data flows and respects dependencies;
- a `Progress Summary` with total, completed, and next step;
- step-level Markdown checkboxes with stable IDs such as `M01-S01`;
- exactly one concrete source function/method per step;
- for every step: module, function's fully qualified name where possible, repository-relative file and original line range, why it matters, prerequisites, and learning focus;
- coverage of initialization, core behavior, error paths, state/data flow, concurrency, performance, security, extensibility, and testing when relevant;
- a `Session note:` field that is initially blank and later points to the generated record.

Use this parseable shape for every step:

```markdown
- [ ] **M01-S01 — `qualified.functionName`**
  - Source: `path/to/file.ext:L10-L42`
  - Why: ...
  - Prerequisites: ...
  - Focus: ...
  - Session note:
```

Keep every `Source:` value relative to `REPO`, because it identifies source code. Keep every populated `Session note:` value relative to `STUDY_ROOT` (for example `LEARNING_NOTES/core/2026-07-21-dispatch.md`), because it identifies centralized learning state. Never prefix source paths with machine-specific absolute directories.

Choose functions that collectively teach the architecture, not merely the longest functions. Keep the plan practical. If no conventional function exists for an important declarative module, choose the nearest executable loader, parser, adapter, build task, or test helper and state why.

After creating or regenerating both `ARCHITETURE.html` and `LEARNING_PLAN.md` in the current invocation, stop before the learning-step workflow. In that response, output only two clickable Markdown links—one to each generated file—and nothing else. Do not summarize, identify the first unchecked step, ask a question, or invite the user to continue. The user can start the learning-step workflow in a later invocation.

Use this response shape, with both central artifact paths resolved relative to the current working directory:

```markdown
[ARCHITETURE.html](relative/path/to/PROJECT_LEARNING/<project-key>/ARCHITETURE.html)
[LEARNING_PLAN.md](relative/path/to/PROJECT_LEARNING/<project-key>/LEARNING_PLAN.md)
```

If only one missing study file was created, report its link and the preserved companion file's link, but still do not begin the learning-step workflow or ask questions in that same response.

## Existing-file and progress workflow

When both central files exist:

1. Validate `PROJECT.json` and its `projects.json` registry entry, then read both study files and validate their `REPO`-relative source references against the current source revision.
2. Read existing `STUDY_ROOT/LEARNING_NOTES` records as needed.
3. Determine completion from checked boxes plus valid `Session note` links. Do not mark a step complete merely because its box is checked if its record is absent; report the inconsistency.
4. Recompute the `Progress Summary` if stale.
5. Choose the first unchecked step whose prerequisites are complete. If source moved, locate the symbol and repair only its source reference in the plan, noting the drift.
6. If all steps are complete, report completion and suggest review or plan refresh; do not invent another step.
7. Otherwise, begin the next step. If the user explicitly names a step, use that step if it exists and explain any unmet prerequisites.

## Learning-step workflow

### 1. Inspect and simplify the assigned function

Read the current implementation and enough callers, callees, types, tests, and configuration to explain its role accurately. Cite the original repository-relative source location and revision.

Display:

- module and stable step ID;
- fully qualified function name and original source location;
- its role in the architecture;
- inputs, outputs, side effects, invariants, and important collaborators;
- a simplified version of the function.

The simplified version must preserve the signature concept, control-flow structure, state transitions, synchronization/async boundaries, security checks, error paths, and resource lifetime that matter. Remove logging boilerplate, repetitive conversion, framework ceremony, and trivial details. Do not remove a detail that changes the lesson.

If the original is already short, show it with only minimal normalization. Otherwise show pedagogical pseudocode or reduced source and label it clearly as non-production/non-compilable when applicable. Add visible sequential line numbers to every displayed simplified-code line (for example `01 | ...`). These are pedagogical line numbers, not original source line numbers.

### 2. Ask questions one at a time

Ask at most 10 open-ended questions over the entire learning step, but present exactly one question per turn. Never display a list or preview of upcoming questions. Number questions sequentially so they can be recorded later.

Do not provide multiple-choice options, hints that reveal the answer, or the recommended answer before the user replies. Tailor the sequence to the function and, where useful, adapt later questions to the user's earlier answers. Across the step, cover the most relevant of:

- control/data flow and invariants;
- performance and complexity;
- concurrency, ordering, cancellation, and resource safety;
- security and trust boundaries;
- error handling and recovery;
- API/design trade-offs, testability, and observability.

Do not force irrelevant categories. Ask only the first question, then stop and wait for the reply.

### 3. Evaluate each reply, then continue

After each user reply:

- briefly restate or accurately summarize the user's answer;
- say what is correct;
- identify omissions or misconceptions constructively;
- provide the recommended answer and reasoning, grounded in the code;
- cite simplified line numbers and original source symbols/locations where useful.

Do not penalize wording differences. After giving feedback and the recommended answer, ask exactly one next question in the same response and wait again. Continue this feedback-then-one-question cycle until the planned questions are complete or 10 questions have been asked.

Maintain an internal question ledger with one entry per asked question: question number, answer status, feedback status, and whether another question follows. Before asking question N+1, confirm that feedback for question N has already been shown to the user.

If the user does not answer the current question, ask only that question again or clarify it; do not advance. If the user explicitly chooses to skip it, record the answer as `Skipped`, still provide the recommended answer and reasoning, and proceed to exactly one next question when one remains.

### Final-answer feedback checkpoint

The final question follows the same feedback contract as every earlier question. It is not a signal to skip directly to persistence.

In the response to the final answer, perform these actions in this exact order:

1. label the section `Feedback on question N (final)`;
2. summarize the learner's answer;
3. state what is correct;
4. identify omissions or misconceptions constructively;
5. provide the recommended answer and reasoning grounded in simplified line numbers and original source where useful;
6. state that the question round is complete;
7. only then create the session record and update progress, without asking another question.

Do not call file-writing tools, announce completion, mark a checkbox, or move directly to takeaways before the final feedback and recommended answer have been displayed. A skipped final question still requires a clearly labeled recommended answer. Before persistence, verify from the question ledger that every asked question has an answer or explicit `Skipped` status **and** displayed feedback. If final feedback was omitted, provide it immediately and defer persistence until afterward. If conversation context is insufficient to reconstruct the final answer accurately, ask the learner to restate it rather than fabricating feedback.

### 4. Record the session

After all feedback—including the explicitly displayed final-answer feedback—is complete, create the module-level session markdown file under `STUDY_ROOT/LEARNING_NOTES/<module-slug>/`. Never create it under `REPO`, and never use the session note as a substitute for showing final feedback in the conversation. It must include:

- date, analyzed revision, step ID, module, function, and original source location;
- architectural context and learning objectives;
- the exact simplified function shown, with its pedagogical line numbers;
- every question;
- the user's answer (verbatim when practical; otherwise clearly marked as a faithful summary);
- feedback and the recommended answer;
- key takeaways and optional follow-up experiments/tests.

If the target filename already exists, do not overwrite it. Add a numeric suffix or update the existing record only with explicit user permission.

### 5. Update progress last

Only after the session record is successfully written:

1. change that step from `[ ]` to `[x]` in `STUDY_ROOT/LEARNING_PLAN.md`;
2. set its `Session note:` to the note path relative to `STUDY_ROOT`;
3. recompute total/completed/remaining and `Next step` in `Progress Summary`;
4. preserve stable IDs and unrelated user edits;
5. report the completed step, note path, progress count, and next eligible step.

Never mark progress complete before recording the user's answers and feedback. Final-answer feedback must have been shown in the conversation before this update begins. Do not start the next quiz in the same response unless the user asks to continue.
