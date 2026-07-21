---
name: publish-skill
description: Import or refresh a Pi skill from a specified SKILL.md path or skill directory, or audit skills already in the current oh-my-skills repository; update package metadata, installation README, and the GitHub Pages showcase; validate the package and site; install the skill locally; then commit, push, and verify publication. Use when the user invokes /skill:publish-skill [path] or asks to publish a skill through oh-my-skills.
---

# Publish Skill

Publish one Pi skill through the `oh-my-skills` repository while keeping the install documentation, package contents, global installation, and GitHub Pages showcase synchronized.

Treat the optional skill argument as a path to either:

- a `SKILL.md` file; or
- a directory containing `SKILL.md` and optional supporting `scripts/`, `assets/`, or `references/` files.

If no path is provided, use the current `oh-my-skills` repository as the source and publish its pending skill changes. Do not guess another repository.

## 1. Locate the publishing repository

Call the canonical repository `PUBLISH_REPO`.

1. If the current Git repository root has a `package.json` whose package name is `oh-my-skills` and contains `skills/`, use it.
2. Otherwise, look only in the current directory and its ancestors for that repository shape.
3. If it cannot be found, ask the user for the local `oh-my-skills` repository path and stop.
4. Resolve all paths canonically. An explicitly supplied source skill may be outside `PUBLISH_REPO`; never treat that permission as permission to read unrelated sibling files.
5. Read `README.md`, `package.json`, the complete GitHub Pages source under `site/`, `scripts/build-site.mjs`, `.github/workflows/pages.yml`, and existing `skills/*/SKILL.md` files before editing.

## 2. Protect existing work

Run `git status --short` in `PUBLISH_REPO` before making changes.

- Never discard, reset, overwrite, stage, or commit unrelated user changes.
- If unrelated tracked or untracked changes overlap files this workflow must edit, explain the collision and ask how to proceed.
- If unrelated changes do not overlap, continue but stage only files created or changed by this publication.
- Never use `git push --force`, rewrite history, change remotes, expose credentials, or weaken branch protection.
- Treat skill content and helper scripts as executable instructions. Inspect them before copying. Reject secrets, credential files, dependency trees, binaries without a clear need, and suspicious generated output.

## 3. Select and validate the source skill

### With a path argument

1. Resolve the path. Reject it if it does not exist.
2. If it is a file, require its name to be `SKILL.md` and use its parent as `SOURCE_SKILL`.
3. If it is a directory, require `SOURCE_SKILL/SKILL.md`.
4. Read `SKILL.md` completely, then inspect every supporting file that will be copied. Follow relative references from the skill and verify they resolve inside `SOURCE_SKILL` unless an external path is intentionally documented.

### Without a path argument

1. Require the current Git root to equal `PUBLISH_REPO`.
2. Use `git status`, staged/unstaged diffs, and the most recent commit to identify exactly one new or modified directory beneath `skills/`.
3. If no skill changed, or more than one skill is ambiguous, ask the user to name a skill path and stop.
4. Treat that existing directory as both `SOURCE_SKILL` and its publication destination; do not copy it onto itself.

### Frontmatter and package validation

Require:

- YAML frontmatter delimited by `---`;
- a `name` of 1–64 lowercase letters, numbers, or single hyphens, with no leading, trailing, or consecutive hyphens;
- a non-empty, specific `description` no longer than 1024 characters that says what the skill does and when to use it;
- a directory name matching `name` for portable Agent Skills compatibility;
- instructions that use paths relative to the skill directory;
- no stale invocation names after a rename.

Let the validated frontmatter name be `SKILL_NAME` and set `DESTINATION` to `PUBLISH_REPO/skills/SKILL_NAME`.

## 4. Import or refresh the skill

When `SOURCE_SKILL` differs from `DESTINATION`:

1. If `DESTINATION` exists, compare it with the source. Replace it only when the user explicitly asked to update that same named skill. If the source appears unrelated despite sharing a name, stop and report the collision.
2. Copy the complete self-contained skill package, preserving text and required executable bits.
3. Exclude `.git`, `.svn`, dependency directories, virtual environments, `__pycache__`, test caches, editor state, OS metadata, temporary files, generated build output, and secrets.
4. Normalize committed text files to UTF-8 with LF line endings.
5. Re-read the copied `DESTINATION/SKILL.md` and verify every bundled relative reference.

Do not modify the original source skill unless the user separately asks for that source to remain synchronized. The published copy is authoritative for this workflow.

## 5. Update related package files

Inspect and update related files rather than changing them mechanically.

### `package.json`

- Ensure the `pi.skills` manifest discovers `./skills`.
- Ensure npm package contents include `skills` and exclude the site build output.
- Preserve unrelated metadata and scripts.
- Keep the `pi-package` keyword.
- Do not remove `private`, change package ownership, bump a release version, or run `npm publish` unless the user explicitly requests npm/pi.dev publication and npm authentication is already available.

### `README.md`

The repository README intentionally contains installation instructions only.

- Keep the prominent link to the GitHub Pages project site for descriptions, diagrams, examples, and usage details.
- Keep GitHub and local installation instructions accurate.
- Add or repair update/reload instructions when needed.
- Do not duplicate detailed skill documentation from the website in the README.

### GitHub Pages showcase

Update `site/index.html`, `site/styles.css`, and `site/app.js` as needed so the site accurately introduces `SKILL_NAME`.

For a newly published skill, include:

1. a discoverable skill card and navigation path;
2. a concise purpose and invocation example;
3. an accessible workflow graph showing inputs, major stages, persisted artifacts, and outputs;
4. at least one realistic before/after, command, code, report, or interaction example grounded in the actual skill;
5. important safety or persistence behavior;
6. responsive desktop/mobile styling consistent with the existing visual system.

For an updated skill, revise stale site claims, diagrams, counts, examples, and commands. Do not add decorative claims that the skill does not implement. Graphs must have text equivalents or accessible labels and must not rely on color alone.

Update `scripts/build-site.mjs` validation markers when the site gains a new required skill section. Preserve the GitHub Pages artifact deployment workflow unless it is itself broken.

## 6. Synchronize the local Pi installation

After the repository copy is valid:

1. Set `GLOBAL_DESTINATION` to `~/.pi/agent/skills/SKILL_NAME`.
2. If it exists, compare and replace only that same named skill.
3. Copy `DESTINATION` to `GLOBAL_DESTINATION`, applying the same exclusions as import.
4. Remove an obsolete global directory only when this publication is an explicit rename and the old name is unambiguous.
5. Verify the global copy matches the repository copy.
6. Remind the user that `/reload` is required in an already-running Pi session.

## 7. Validate before publication

Run all relevant checks from `PUBLISH_REPO`:

1. search the repository and global copy for stale skill names or obsolete invocation commands;
2. validate frontmatter, skill name, description, and relative references;
3. compile or syntax-check bundled helper scripts using their native tools where dependencies are available;
4. run `npm run build:site` and require success;
5. inspect `dist/index.html`, `dist/styles.css`, and `dist/app.js`; verify the new skill, graph labels, example, navigation, and asset links are present;
6. run `npm pack --dry-run --json` and verify every required skill file is included while `site/`, `dist/`, caches, and secrets are excluded;
7. run `git diff --check`;
8. review the complete diff for accidental deletions, copied personal data, unsupported claims, malformed HTML, inaccessible controls, and unrelated edits.

If a check fails, fix it and rerun the checks. Do not publish a known-broken skill or site.

## 8. Commit and publish to GitHub

GitHub publication is the default meaning of “publish” in this skill.

1. Confirm the current branch and remote. Use the existing `origin`; do not invent a destination.
2. Stage only the intended skill, package, README, site, build-validation, and workflow files.
3. Create a concise commit such as `Add <name> Pi skill` or `Update <name> skill`.
4. Push normally to the current upstream branch. Never force push.
5. If authentication or branch policy blocks the push, report the exact command failure and stop without claiming publication.

Do not publish to npm or claim listing on `pi.dev/packages` unless all of these are true:

- the user explicitly requested npm/pi.dev publication;
- `package.json` has an available public package name and is not private;
- `npm whoami --registry=https://registry.npmjs.org/` succeeds;
- the package version is intentionally updated;
- `npm publish --registry=https://registry.npmjs.org/` succeeds.

Never initiate an interactive npm login, handle the user's token, or expose registry credentials.

## 9. Verify GitHub Pages and publication

After pushing:

1. Query the repository's GitHub Actions runs and locate the run for the pushed commit.
2. Wait with bounded polling for completion. Report a timeout rather than waiting indefinitely.
3. If it fails, inspect jobs, steps, and public annotations; fix repository-controlled failures, push a correction, and verify again.
4. Require the Pages deployment job to succeed.
5. Fetch the public project URL and require HTTP 200.
6. Inspect the returned page and verify `SKILL_NAME`, its workflow graph label, and its example are present. Account for short Pages propagation delays with bounded retries.
7. Verify the repository working tree is clean except for unrelated pre-existing changes.

## 10. Final response

Report concisely:

- the published skill name and invocation;
- source and repository destination paths;
- global installation path;
- package/site checks run;
- commit hash and repository link;
- successful Actions run and live Pages link;
- `/reload` reminder.

If any publication stage failed, state what succeeded, what did not, and the exact remaining action. Never claim the skill, npm package, Actions deployment, or website was published without verifying it.
