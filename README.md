# Oh My Skills

A small collection of reusable [Pi](https://pi.dev) agent skills.

## Included skill

### `start-design`

Runs an interactive 40-exercise system-design curriculum. The first five exercises are guided; the remaining exercises use an interview format. Progress and completed designs are persisted in the working repository.

On first use, the skill creates:

- `SYSTEM_DESIGG.md` — editable curriculum and source of truth
- `SYSTEM_DESIGG.html` — generated responsive progress report

> `SYSTEM_DESIGG` is the intentional artifact name used by this skill.

## Install

From this repository:

```bash
pi install /path/to/oh-my-skills
```

Or copy `skills/start-design` into `~/.pi/agent/skills/`.

Reload Pi, then run:

```text
/skill:start-design
```

The HTML renderer requires Python 3 and the `markdown` package:

```bash
python -m pip install markdown
```
