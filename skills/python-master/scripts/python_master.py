#!/usr/bin/env python3
"""Create, validate, inspect, and launch the Python Master notebook."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import webbrowser
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlencode, urljoin, urlparse, urlunparse

NOTEBOOK_NAME = "PYTHON_MASTER.ipynb"
PROGRESS_NAME = "PYTHON_MASTER_PROGRESS.json"
NOTEBOOK_SCHEMA_VERSION = 2
PROGRESS_SCHEMA_VERSION = 1
CURRICULUM_SCHEMA_VERSION = 1
GUIDED_EXAMPLES_SCHEMA_VERSION = 1
SKILL_ROOT = Path(__file__).resolve().parent.parent
CURRICULUM_PATH = SKILL_ROOT / "assets" / "curriculum.json"
GUIDED_EXAMPLES_PATH = SKILL_ROOT / "assets" / "guided_examples.json"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def load_curriculum() -> dict[str, Any]:
    curriculum = read_json(CURRICULUM_PATH)
    sections = curriculum.get("sections", [])
    ids = [section.get("id") for section in sections]
    if curriculum.get("schemaVersion") != CURRICULUM_SCHEMA_VERSION or not sections:
        raise ValueError("Curriculum is missing or has an unsupported schema")
    if len(ids) != len(set(ids)) or any(not valid_section_id(value) for value in ids):
        raise ValueError("Curriculum contains duplicate or malformed section IDs")
    return curriculum


def load_guided_examples(section_ids: list[str]) -> dict[str, dict[str, Any]]:
    document = read_json(GUIDED_EXAMPLES_PATH)
    examples = document.get("examples", {})
    if document.get("schemaVersion") != GUIDED_EXAMPLES_SCHEMA_VERSION or not isinstance(examples, dict):
        raise ValueError("Guided examples are missing or have an unsupported schema")
    if set(examples) != set(section_ids):
        raise ValueError("Guided examples must contain exactly one entry for every curriculum section")
    for section_id, example in examples.items():
        if not isinstance(example, dict) or not example.get("title") or not example.get("code"):
            raise ValueError(f"Guided example {section_id} is incomplete")
        guidance = example.get("guidance")
        if not isinstance(guidance, list) or len(guidance) < 2 or not all(isinstance(item, str) and item for item in guidance):
            raise ValueError(f"Guided example {section_id} needs at least two guidance prompts")
    return examples


def valid_section_id(value: object) -> bool:
    if not isinstance(value, str) or len(value) != 5 or not value.startswith("PM-"):
        return False
    return value[3:].isdigit() and 1 <= int(value[3:]) <= 99


def markdown_cell(cell_id: str, source: str) -> dict[str, Any]:
    return {
        "cell_type": "markdown",
        "id": cell_id,
        "metadata": {},
        "source": source.splitlines(keepends=True),
    }


def code_cell(cell_id: str, source: str) -> dict[str, Any]:
    return {
        "cell_type": "code",
        "execution_count": None,
        "id": cell_id,
        "metadata": {},
        "outputs": [],
        "source": source.splitlines(keepends=True),
    }


def setup_source(section_ids: list[str]) -> str:
    ids_literal = repr(section_ids)
    return f'''from __future__ import annotations

import json
from pathlib import Path
from time import perf_counter

NOTEBOOK_ROOT = Path.cwd()
PROGRESS_PATH = NOTEBOOK_ROOT / "{PROGRESS_NAME}"
SECTION_IDS = {ids_literal}


def _read_progress():
    if not PROGRESS_PATH.exists():
        return {{"schemaVersion": 1, "completed": [], "current": SECTION_IDS[0]}}
    return json.loads(PROGRESS_PATH.read_text(encoding="utf-8"))


def _write_progress(progress):
    temporary = PROGRESS_PATH.with_suffix(PROGRESS_PATH.suffix + ".tmp")
    temporary.write_text(json.dumps(progress, indent=2) + "\\n", encoding="utf-8")
    temporary.replace(PROGRESS_PATH)


def progress():
    state = _read_progress()
    completed = [section for section in state.get("completed", []) if section in SECTION_IDS]
    remaining = [section for section in SECTION_IDS if section not in completed]
    print(f"Completed: {{len(completed)}} / {{len(SECTION_IDS)}}")
    print(f"Next: {{remaining[0] if remaining else 'Curriculum complete'}}")
    return state


def mark_complete(section_id):
    if section_id not in SECTION_IDS:
        raise ValueError(f"Unknown section: {{section_id}}")
    state = _read_progress()
    completed = [section for section in state.get("completed", []) if section in SECTION_IDS]
    if section_id not in completed:
        completed.append(section_id)
    remaining = [section for section in SECTION_IDS if section not in completed]
    state.update({{"schemaVersion": 1, "completed": completed, "current": remaining[0] if remaining else None}})
    _write_progress(state)
    print(f"Marked {{section_id}} complete. Progress: {{len(completed)}} / {{len(SECTION_IDS)}}")
    print(f"Next: {{remaining[0] if remaining else 'Curriculum complete'}}")
    return state

progress()
'''


def guided_cells(section: dict[str, Any], example: dict[str, Any]) -> list[dict[str, Any]]:
    section_id = section["id"]
    anchor = section_anchor(section_id)
    guidance = "\n".join(f"{index}. {item}" for index, item in enumerate(example["guidance"], 1))
    concepts = ", ".join(f"`{item}`" for item in section["concepts"])
    pitfalls = "\n".join(f"- Probe **{item}** by changing one input or line." for item in section["pitfalls"])
    walkthrough = f'''### Guided walkthrough — {example["title"]}

**Mental model:** Connect the example to {concepts}.

**Before running**

{guidance}

1. Predict every printed value, exception, state transition, and side effect.
2. Identify which behavior is a Python language guarantee and which may be CPython-specific.

**After running**

- Explain any difference between prediction and output.
- Change one factor at a time and rerun; do not modify the lab scaffold yet.
- Add a Markdown cell recording the invariant, API consequence, or performance implication.

**Pitfall probes**

{pitfalls}
'''
    return [
        markdown_cell(f"{anchor}-guidance", walkthrough),
        code_cell(f"{anchor}-example", example["code"]),
    ]


def build_notebook(curriculum: dict[str, Any], examples: dict[str, dict[str, Any]]) -> dict[str, Any]:
    sections = curriculum["sections"]
    section_ids = [section["id"] for section in sections]
    track_counts: dict[str, int] = {}
    for section in sections:
        track_counts[section["track"]] = track_counts.get(section["track"], 0) + 1

    index_lines = [
        '<a id="python-master-home"></a>\n',
        "# Python Mastery Lab\n",
        "\n",
        "A persistent, executable curriculum for mastering Python's language model, data structures, API design, concurrency, networking, and performance. Read, predict, run, modify, measure, and explain—do not merely execute the completion cell.\n",
        "\n",
        "## Learning contract\n",
        "\n",
        "1. Run **Notebook setup** once per kernel.\n",
        "2. Read the guided mental model and predict the runnable example before executing it.\n",
        "3. Explain the output, run the pitfall probes, then complete the open lab and mastery challenge.\n",
        "4. Add tests and record observations; run `mark_complete(\"PM-XX\")` only when you can explain the relevant invariants and pitfalls.\n",
        f"5. Progress is stored beside this notebook in `{PROGRESS_NAME}`.\n",
        "\n",
        "## Curriculum map\n",
        "\n",
    ]
    for track, count in track_counts.items():
        index_lines.append(f"- **{track}:** {count} sections\n")
    index_lines.append("\n")
    for section in sections:
        anchor = section_anchor(section["id"])
        index_lines.append(f"- [{section['id']} — {section['title']}](#{anchor})\n")

    cells: list[dict[str, Any]] = [
        markdown_cell("python-master-home", "".join(index_lines)),
        markdown_cell(
            "python-master-setup-heading",
            '<a id="python-master-setup"></a>\n## Notebook setup\n\nRun this cell after opening or restarting the kernel. It provides durable progress helpers using only the standard library.\n',
        ),
        code_cell("python-master-setup", setup_source(section_ids)),
    ]

    for section in sections:
        section_id = section["id"]
        anchor = section_anchor(section_id)
        concepts = "\n".join(f"- {item}" for item in section["concepts"])
        pitfalls = "\n".join(f"- {item}" for item in section["pitfalls"])
        lesson = f'''<a id="{anchor}"></a>
## {section_id} — {section["title"]}

**Track:** {section["track"]}

**Why it matters:** {section["why"]}

### Language features and invariants

{concepts}

### Pitfalls to be able to explain

{pitfalls}

### Authoritative reference

- [Python documentation]({section["docs"]})
'''
        lab = f'''# {section_id} lab
#
# Goal: {section["lab"]}
#
# 1. Write your prediction in a Markdown cell before executing.
# 2. Build the smallest experiment that can falsify the prediction.
# 3. Add assertions, edge cases, and measurements where relevant.
# 4. Explain the result and its API or production consequence.

# Replace this scaffold with your experiment.
def experiment():
    raise NotImplementedError("Implement the {section_id} lab")
'''
        challenge = f'''### {section_id} mastery challenge

{section["challenge"]}

**Evidence required before completion**

- executable implementation rather than pseudocode;
- tests for normal, boundary, and failure behavior;
- a written explanation of the governing language feature or invariant;
- measurements for performance claims;
- explicit trade-offs and remaining limitations.
'''
        completion = f'''# Run only after the lab and mastery challenge satisfy the evidence checklist.
mark_complete("{section_id}")
'''
        cells.extend(
            [
                markdown_cell(anchor, lesson),
                *guided_cells(section, examples[section_id]),
                code_cell(f"{anchor}-lab", lab),
                markdown_cell(f"{anchor}-challenge", challenge),
                code_cell(f"{anchor}-complete", completion),
            ]
        )

    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": f"{sys.version_info.major}.{sys.version_info.minor}"},
            "python_master": {
                "schemaVersion": NOTEBOOK_SCHEMA_VERSION,
                "createdAt": date.today().isoformat(),
                "sectionIds": section_ids,
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def section_anchor(section_id: str) -> str:
    return f"python-master-{section_id.lower()}"


def initial_progress(section_ids: list[str]) -> dict[str, Any]:
    return {
        "schemaVersion": PROGRESS_SCHEMA_VERSION,
        "completed": [],
        "current": section_ids[0],
        "updatedAt": date.today().isoformat(),
    }


def initialize(root: Path) -> tuple[Path, Path]:
    root.mkdir(parents=True, exist_ok=True)
    notebook_path = root / NOTEBOOK_NAME
    progress_path = root / PROGRESS_NAME
    if notebook_path.exists():
        raise FileExistsError(f"Refusing to overwrite existing {notebook_path}")
    curriculum = load_curriculum()
    section_ids = [section["id"] for section in curriculum["sections"]]
    examples = load_guided_examples(section_ids)
    write_json(notebook_path, build_notebook(curriculum, examples))
    if not progress_path.exists():
        write_json(progress_path, initial_progress(section_ids))
    validate(root)
    return notebook_path, progress_path


def upgrade(root: Path) -> tuple[Path, Path | None]:
    notebook_path = root / NOTEBOOK_NAME
    if not notebook_path.is_file():
        raise FileNotFoundError(f"Missing {notebook_path}")
    notebook = read_json(notebook_path)
    metadata = notebook.get("metadata", {}).get("python_master", {})
    version = metadata.get("schemaVersion")
    if version == NOTEBOOK_SCHEMA_VERSION:
        validate(root)
        return notebook_path, None
    if version != 1:
        raise ValueError(f"Cannot upgrade notebook schema {version!r}")

    curriculum = load_curriculum()
    sections = curriculum["sections"]
    section_ids = [section["id"] for section in sections]
    if metadata.get("sectionIds") != section_ids:
        raise ValueError("Cannot upgrade a notebook whose curriculum IDs were changed")
    examples = load_guided_examples(section_ids)
    cells = notebook.get("cells")
    if not isinstance(cells, list):
        raise ValueError("Notebook cells are malformed")
    existing_ids = {cell.get("id") for cell in cells if isinstance(cell, dict)}
    missing_headings = [section_anchor(section_id) for section_id in section_ids if section_anchor(section_id) not in existing_ids]
    if missing_headings:
        raise ValueError(f"Cannot upgrade; section headings are missing: {', '.join(missing_headings)}")
    enriched: list[dict[str, Any]] = []
    section_by_anchor = {section_anchor(section["id"]): section for section in sections}
    for cell in cells:
        enriched.append(cell)
        if not isinstance(cell, dict):
            continue
        anchor = cell.get("id")
        section = section_by_anchor.get(anchor)
        if section is None:
            continue
        guidance_id = f"{anchor}-guidance"
        example_id = f"{anchor}-example"
        if guidance_id not in existing_ids and example_id not in existing_ids:
            enriched.extend(guided_cells(section, examples[section["id"]]))
        elif guidance_id not in existing_ids or example_id not in existing_ids:
            raise ValueError(f"Section {section['id']} has a partial guided-example upgrade")

    backup = notebook_path.with_name(f"{NOTEBOOK_NAME}.v1.bak")
    suffix = 2
    while backup.exists():
        backup = notebook_path.with_name(f"{NOTEBOOK_NAME}.v1.bak.{suffix}")
        suffix += 1
    shutil.copy2(notebook_path, backup)
    metadata["schemaVersion"] = NOTEBOOK_SCHEMA_VERSION
    metadata["upgradedAt"] = date.today().isoformat()
    notebook["metadata"]["python_master"] = metadata
    notebook["cells"] = enriched
    write_json(notebook_path, notebook)
    validate(root)
    return notebook_path, backup


def validate(root: Path) -> tuple[dict[str, Any], dict[str, Any], list[str]]:
    notebook_path = root / NOTEBOOK_NAME
    progress_path = root / PROGRESS_NAME
    if not notebook_path.is_file():
        raise FileNotFoundError(f"Missing {notebook_path}")
    notebook = read_json(notebook_path)
    metadata = notebook.get("metadata", {}).get("python_master", {})
    section_ids = metadata.get("sectionIds", [])
    curriculum_ids = [section["id"] for section in load_curriculum()["sections"]]
    if notebook.get("nbformat") != 4:
        raise ValueError("Notebook is not notebook format 4")
    version = metadata.get("schemaVersion")
    if version == 1:
        raise ValueError("Notebook schema 1 has goals only; run --upgrade to add guided examples without replacing learner work")
    if version != NOTEBOOK_SCHEMA_VERSION:
        raise ValueError("Notebook is not a supported Python Master plan")
    if section_ids != curriculum_ids:
        raise ValueError("Notebook curriculum IDs do not match the bundled curriculum")
    anchors = {
        cell.get("id")
        for cell in notebook.get("cells", [])
        if isinstance(cell, dict) and cell.get("cell_type") == "markdown"
    }
    required = []
    for section_id in section_ids:
        anchor = section_anchor(section_id)
        required.extend((anchor, f"{anchor}-guidance"))
    missing = [cell_id for cell_id in required if cell_id not in anchors]
    code_ids = {cell.get("id") for cell in notebook.get("cells", []) if isinstance(cell, dict) and cell.get("cell_type") == "code"}
    missing.extend(f"{section_anchor(section_id)}-example" for section_id in section_ids if f"{section_anchor(section_id)}-example" not in code_ids)
    if missing:
        raise ValueError(f"Notebook is missing required learning cells: {', '.join(missing)}")
    if progress_path.exists():
        progress = read_json(progress_path)
    else:
        progress = initial_progress(section_ids)
        write_json(progress_path, progress)
    if progress.get("schemaVersion") != PROGRESS_SCHEMA_VERSION:
        raise ValueError("Progress has an unsupported schema")
    completed = progress.get("completed", [])
    if not isinstance(completed, list) or any(item not in section_ids for item in completed):
        raise ValueError("Progress contains unknown section IDs")
    return notebook, progress, section_ids


def choose_section(root: Path, requested: str | None) -> tuple[str | None, dict[str, Any], list[str]]:
    _, progress, section_ids = validate(root)
    if requested:
        requested = requested.upper()
        if requested not in section_ids:
            raise ValueError(f"Unknown section {requested}; valid range is {section_ids[0]} through {section_ids[-1]}")
        selected: str | None = requested
    else:
        completed = set(progress.get("completed", []))
        selected = next((section_id for section_id in section_ids if section_id not in completed), None)
    progress["current"] = selected
    progress["updatedAt"] = date.today().isoformat()
    write_json(root / PROGRESS_NAME, progress)
    return selected, progress, section_ids


def jupyter_executable() -> str:
    executable = shutil.which("jupyter")
    if not executable:
        raise RuntimeError(
            "Jupyter is not installed. Install it with `python -m pip install jupyterlab notebook` and retry."
        )
    return executable


def list_servers(jupyter: str) -> list[dict[str, Any]]:
    commands = ([jupyter, "server", "list", "--jsonlist"], [jupyter, "notebook", "list", "--jsonlist"])
    for command in commands:
        result = subprocess.run(command, capture_output=True, text=True, timeout=15, check=False)
        if result.returncode != 0 or not result.stdout.strip():
            continue
        try:
            value = json.loads(result.stdout)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
            if isinstance(value, dict):
                return [value]
        except json.JSONDecodeError:
            servers = []
            for line in result.stdout.splitlines():
                try:
                    item = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(item, dict):
                    servers.append(item)
            if servers:
                return servers
    return []


def canonical_root(server: dict[str, Any]) -> Path | None:
    value = server.get("root_dir") or server.get("notebook_dir")
    if not value:
        return None
    try:
        return Path(value).resolve()
    except OSError:
        return None


def server_url(server: dict[str, Any], frontend: str, selected: str | None) -> str:
    base = server.get("url")
    if not isinstance(base, str) or not base:
        raise RuntimeError("Jupyter did not report a usable server URL")
    route = "tree" if frontend == "notebook" else "lab/tree"
    target = urljoin(base.rstrip("/") + "/", f"{route}/{quote(NOTEBOOK_NAME)}")
    parsed = urlparse(target)
    query = dict()
    if parsed.query:
        for pair in parsed.query.split("&"):
            key, _, value = pair.partition("=")
            query[key] = value
    token = server.get("token")
    if token:
        query["token"] = str(token)
    fragment = section_anchor(selected) if selected else "python-master-home"
    return urlunparse(parsed._replace(query=urlencode(query), fragment=fragment))


def launch(root: Path, selected: str | None) -> tuple[str, int | None, str]:
    jupyter = jupyter_executable()
    frontend = "notebook"
    probe = subprocess.run([jupyter, "notebook", "--version"], capture_output=True, text=True, timeout=15, check=False)
    if probe.returncode != 0:
        frontend = "lab"
        probe = subprocess.run([jupyter, "lab", "--version"], capture_output=True, text=True, timeout=15, check=False)
        if probe.returncode != 0:
            raise RuntimeError("Install a Jupyter frontend with `python -m pip install jupyterlab notebook`")

    existing = [server for server in list_servers(jupyter) if canonical_root(server) == root]
    process: subprocess.Popen[bytes] | None = None
    server = existing[0] if existing else None
    if server is None:
        command = [jupyter, frontend, "--no-browser", f"--notebook-dir={root}"]
        options: dict[str, Any] = {"cwd": root, "stdin": subprocess.DEVNULL, "stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
        if os.name == "nt":
            options["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
        else:
            options["start_new_session"] = True
        process = subprocess.Popen(command, **options)
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError(f"Jupyter exited during startup with status {process.returncode}")
            matches = [item for item in list_servers(jupyter) if canonical_root(item) == root]
            if matches:
                server = matches[-1]
                break
            time.sleep(0.5)
    if server is None:
        if process and process.poll() is None:
            process.terminate()
        raise RuntimeError("Timed out waiting for Jupyter to start")
    url = server_url(server, frontend, selected)
    if not webbrowser.open(url, new=2):
        print("Browser could not be opened automatically; open the URL printed below.", file=sys.stderr)
    return url, process.pid if process else None, frontend


def status(root: Path) -> None:
    _, progress, section_ids = validate(root)
    completed = [section for section in progress.get("completed", []) if section in section_ids]
    remaining = [section for section in section_ids if section not in completed]
    print(f"NOTEBOOK={root / NOTEBOOK_NAME}")
    print(f"PROGRESS={len(completed)}/{len(section_ids)}")
    print(f"NEXT={remaining[0] if remaining else 'COMPLETE'}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Directory that owns notebook and progress")
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--init", action="store_true", help="Create the notebook without overwriting one")
    action.add_argument("--launch", action="store_true", help="Open the notebook at the selected/next section")
    action.add_argument("--status", action="store_true", help="Validate and print progress")
    action.add_argument("--upgrade", action="store_true", help="Add guided examples to a schema-1 notebook without replacing learner cells")
    parser.add_argument("--section", help="Explicit section such as PM-19")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.expanduser().resolve()
    try:
        if args.init:
            notebook, progress = initialize(root)
            print(f"CREATED_NOTEBOOK={notebook}")
            print(f"CREATED_PROGRESS={progress}")
        elif args.status:
            status(root)
        elif args.upgrade:
            notebook, backup = upgrade(root)
            print(f"UPGRADED_NOTEBOOK={notebook}")
            print(f"BACKUP={backup if backup else 'NOT_NEEDED'}")
        else:
            selected, progress, section_ids = choose_section(root, args.section)
            if selected is None:
                print(f"CURRICULUM_COMPLETE={len(section_ids)}/{len(section_ids)}")
                selected = section_ids[-1]
            url, pid, frontend = launch(root, selected)
            section = next(item for item in load_curriculum()["sections"] if item["id"] == selected)
            print(f"SECTION={selected}")
            print(f"TITLE={section['title']}")
            print(f"FRONTEND={frontend}")
            if pid:
                print(f"SERVER_PID={pid}")
            print(f"URL={url}")
            print("The URL includes the section anchor. If the frontend restores an old workspace position, use the notebook link for the printed section ID.")
        return 0
    except (FileNotFoundError, FileExistsError, ValueError, RuntimeError, OSError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
