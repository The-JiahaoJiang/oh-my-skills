#!/usr/bin/env python3
"""Render SYSTEM_DESIGG.md as a modern, self-contained HTML report."""

from __future__ import annotations

import argparse
import html
import re
from datetime import date, datetime
from pathlib import Path

try:
    import markdown
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Missing dependency: install Python package 'markdown'.") from exc


def find_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "SYSTEM_DESIGG.md").exists():
            return candidate
    raise SystemExit("Could not find SYSTEM_DESIGG.md in the current directory or its ancestors.")


def extract(pattern: str, source: str, default: str) -> str:
    match = re.search(pattern, source, re.MULTILINE)
    return match.group(1).strip() if match else default


def prepare_markdown(source: str) -> str:
    # Authoring templates are useful in Markdown but should not leak into reports.
    source = re.sub(r"<!--.*?-->", "", source, flags=re.DOTALL)
    # Python-Markdown requires four-space nesting, while many Markdown renderers
    # accept two. Normalize list indentation so stage review bullets stay nested.
    source = re.sub(
        r"^( +)([-*+] |\d+\. )",
        lambda match: " " * (len(match.group(1)) * 2) + match.group(2),
        source,
        flags=re.MULTILINE,
    )
    # Ask Python-Markdown to process Markdown inside collapsible HTML sections.
    source = source.replace("<details>", '<details markdown="1">')
    # Render task markers as accessible, stylable status pills.
    source = re.sub(
        r"^- \[x\] ",
        '- <span class="task-state task-done" aria-label="Complete">✓</span> ',
        source,
        flags=re.MULTILINE | re.IGNORECASE,
    )
    source = re.sub(
        r"^- \[ \] ",
        '- <span class="task-state task-pending" aria-label="Pending">○</span> ',
        source,
        flags=re.MULTILINE,
    )
    return source


def render_mermaid_blocks(body: str) -> str:
    pattern = re.compile(r'<pre><code class="language-mermaid">(.*?)</code></pre>', re.DOTALL)
    return pattern.sub(lambda match: f'<div class="mermaid">{html.unescape(match.group(1))}</div>', body)


def validate_report(report: str, source: str) -> None:
    """Fail generation when common formatting regressions are detected."""
    source_without_comments = re.sub(r"<!--.*?-->", "", source, flags=re.DOTALL)
    has_solved_design = bool(re.search(r"^## SD-\d{2} — ", source_without_comments, re.MULTILINE))
    checks = {
        "doctype": report.lstrip().lower().startswith("<!doctype html>"),
        "balanced details": report.count("<details") == report.count("</details>"),
        "balanced layout divs": report.count("<div") == report.count("</div>"),
        "no escaped layout tags": "&lt;details" not in report and "&lt;div class=\"mermaid\"" not in report,
        "converted Mermaid blocks": 'class="language-mermaid"' not in report,
        "all curriculum issues": all(f"SD-{number:02d}" in report for number in range(1, 41)),
        "source represented": "System Design Practice Tracker" in report,
    }
    if has_solved_design:
        checks.update({
            "rendered collapsed Markdown": not re.search(r"\n\s*- \*\*[^\n]+:\*\*", report),
            "collapsed content is HTML": bool(re.search(r"<details[^>]*>.*?<ul>.*?</details>", report, re.DOTALL)),
            "nested review bullets": bool(re.search(r"<li><strong>Your draft:</strong>\s*<ul>", report)),
            "architecture diagram": 'class="mermaid"' in report,
            "draft review": "Draft-to-final review" in report,
        })
    failures = [name for name, passed in checks.items() if not passed]
    if failures:
        raise ValueError("HTML report validation failed: " + ", ".join(failures))


def build_report(source: str) -> str:
    completed_text = extract(r"^- \*\*Completed:\*\*\s*(.+)$", source, "0 / 0")
    completed_match = re.search(r"(\d+)\s*/\s*(\d+)", completed_text)
    completed, total = completed_match.groups() if completed_match else ("0", "0")
    percent = round((int(completed) / int(total)) * 100) if int(total) else 0
    current = extract(r"^- \*\*Current issue:\*\*\s*(.+)$", source, "Not started")
    mode = extract(r"^- \*\*Mode:\*\*\s*(.+)$", source, "—")
    updated = extract(r"^- \*\*Last updated:\*\*\s*(.+)$", source, "—")

    prepared = prepare_markdown(source)
    body = markdown.markdown(
        prepared,
        extensions=["extra", "sane_lists", "toc"],
        extension_configs={"toc": {"permalink": False}},
        output_format="html5",
    )
    body = render_mermaid_blocks(body)

    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Interactive system-design curriculum progress and solved-design report">
  <title>System Design · Practice Report</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f4f6fb; --surface: rgba(255,255,255,.88); --surface-solid: #fff;
      --text: #172033; --muted: #667085; --line: #e3e8f2;
      --brand: #6558e8; --brand-2: #19a78e; --warning: #f59e0b; --danger: #dc4c64;
      --shadow: 0 16px 50px rgba(31,42,68,.09); --radius: 18px;
    }}
    html[data-theme="dark"] {{
      color-scheme: dark; --bg: #0d1220; --surface: rgba(22,29,47,.88); --surface-solid: #161d2f;
      --text: #edf1fa; --muted: #a8b0c2; --line: #2c3650; --brand: #948bff; --brand-2: #42d3b6;
      --shadow: 0 18px 55px rgba(0,0,0,.28);
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{ margin: 0; background: var(--bg); color: var(--text); font: 15.5px/1.68 Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    body::before {{ content:""; position:fixed; inset:0 0 auto; height:420px; pointer-events:none; background:radial-gradient(circle at 16% 8%, rgba(101,88,232,.16), transparent 34%), radial-gradient(circle at 84% 5%, rgba(25,167,142,.12), transparent 28%); }}
    a {{ color: var(--brand); text-decoration-thickness: 1px; text-underline-offset: 3px; }}
    a:hover {{ color: var(--brand-2); }}
    .app {{ position: relative; display:grid; grid-template-columns: 280px minmax(0,1fr); min-height:100vh; }}
    aside {{ position:sticky; top:0; height:100vh; padding:26px 20px; border-right:1px solid var(--line); background:color-mix(in srgb, var(--surface-solid) 82%, transparent); backdrop-filter:blur(18px); overflow:auto; }}
    .brand {{ display:flex; align-items:center; gap:11px; margin:0 8px 25px; font-weight:800; letter-spacing:-.02em; }}
    .brand-mark {{ width:38px; height:38px; display:grid; place-items:center; border-radius:12px; color:#fff; background:linear-gradient(135deg,var(--brand),var(--brand-2)); box-shadow:0 10px 25px rgba(101,88,232,.28); }}
    .eyebrow {{ color:var(--brand); font-size:11px; font-weight:800; letter-spacing:.13em; text-transform:uppercase; }}
    .toc-title {{ margin:22px 9px 8px; color:var(--muted); font-size:11px; font-weight:800; letter-spacing:.1em; text-transform:uppercase; }}
    #toc a {{ display:block; margin:2px 0; padding:7px 10px; border-radius:9px; color:var(--muted); text-decoration:none; font-size:13px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
    #toc a.sub {{ padding-left:22px; font-size:12px; }}
    #toc a:hover, #toc a.active {{ color:var(--brand); background:rgba(101,88,232,.09); }}
    .side-actions {{ display:flex; gap:8px; margin:20px 7px; }}
    button {{ cursor:pointer; border:1px solid var(--line); color:var(--text); background:var(--surface); border-radius:10px; padding:8px 10px; font:inherit; }}
    button:hover {{ border-color:var(--brand); }}
    main {{ min-width:0; padding:42px clamp(22px,5vw,72px) 90px; }}
    .hero {{ max-width:1180px; margin:0 auto 28px; padding:clamp(25px,4vw,48px); border:1px solid rgba(255,255,255,.22); border-radius:26px; color:#fff; background:linear-gradient(128deg,#4037a9 0%,#6558e8 48%,#138d82 115%); box-shadow:0 24px 70px rgba(65,55,169,.25); overflow:hidden; position:relative; }}
    .hero::after {{ content:""; position:absolute; width:300px; height:300px; border:55px solid rgba(255,255,255,.08); border-radius:50%; right:-105px; top:-140px; }}
    .hero h1 {{ margin:7px 0 8px; font-size:clamp(30px,5vw,52px); line-height:1.08; letter-spacing:-.045em; }}
    .hero p {{ margin:0; max-width:700px; color:rgba(255,255,255,.78); }}
    .stats {{ position:relative; z-index:1; display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-top:30px; }}
    .stat {{ padding:16px; border:1px solid rgba(255,255,255,.18); border-radius:14px; background:rgba(255,255,255,.1); backdrop-filter:blur(10px); }}
    .stat b {{ display:block; margin-top:3px; font-size:19px; }}
    .stat small {{ color:rgba(255,255,255,.7); }}
    .progress {{ height:7px; margin-top:9px; border-radius:10px; background:rgba(255,255,255,.2); overflow:hidden; }}
    .progress i {{ display:block; width:{percent}%; height:100%; background:#fff; border-radius:inherit; }}
    article {{ max-width:1180px; margin:auto; padding:clamp(24px,4vw,48px); background:var(--surface); border:1px solid var(--line); border-radius:var(--radius); box-shadow:var(--shadow); backdrop-filter:blur(15px); }}
    article > h1:first-child {{ display:none; }}
    h1,h2,h3,h4 {{ color:var(--text); line-height:1.25; letter-spacing:-.025em; scroll-margin-top:22px; }}
    h2 {{ margin:58px 0 20px; padding-bottom:12px; border-bottom:1px solid var(--line); font-size:27px; }}
    h2:first-of-type {{ margin-top:0; }}
    h3 {{ margin:36px 0 14px; color:var(--brand); font-size:21px; }}
    h4 {{ margin:27px 0 10px; font-size:17px; }}
    p {{ margin:10px 0; }}
    ul,ol {{ padding-left:24px; }}
    li {{ margin:6px 0; }}
    article > ul {{ padding:0; list-style:none; }}
    article > ul > li {{ padding:10px 13px; border-radius:10px; }}
    article > ul > li:has(.task-state) {{ display:flex; align-items:flex-start; gap:10px; margin:7px 0; border:1px solid var(--line); background:var(--surface-solid); }}
    .task-state {{ flex:0 0 24px; width:24px; height:24px; display:inline-grid; place-items:center; border-radius:50%; font-weight:800; line-height:1; }}
    .task-done {{ color:#087e69; background:rgba(25,167,142,.14); }}
    .task-pending {{ color:var(--muted); background:rgba(102,112,133,.10); }}
    code {{ padding:.15em .4em; border:1px solid var(--line); border-radius:6px; background:rgba(101,88,232,.07); font: .9em ui-monospace,SFMono-Regular,Consolas,monospace; }}
    pre {{ overflow:auto; padding:18px; border-radius:13px; color:#dce5ff; background:#121829; }}
    pre code {{ padding:0; border:0; color:inherit; background:none; }}
    blockquote {{ margin:20px 0; padding:10px 18px; border-left:4px solid var(--brand); color:var(--muted); background:rgba(101,88,232,.06); }}
    details {{ margin:22px 0; border:1px solid var(--line); border-radius:14px; background:var(--surface-solid); overflow:hidden; }}
    summary {{ cursor:pointer; padding:17px 20px; color:var(--brand); font-weight:750; }}
    details > :not(summary) {{ margin-left:20px; margin-right:20px; }}
    details > :last-child {{ margin-bottom:20px; }}
    .mermaid {{ margin:24px 0; padding:22px; overflow:auto; text-align:center; border:1px solid var(--line); border-radius:15px; background:#fff; }}
    .report-footer {{ max-width:1180px; margin:22px auto 0; color:var(--muted); text-align:center; font-size:12px; }}
    @media (max-width: 900px) {{ .app {{ display:block; }} aside {{ position:relative; width:auto; height:auto; border-right:0; border-bottom:1px solid var(--line); }} #toc,.toc-title {{ display:none; }} .side-actions {{ position:absolute; right:15px; top:8px; }} main {{ padding:24px 14px 60px; }} .stats {{ grid-template-columns:1fr 1fr; }} article {{ padding:22px 18px; }} }}
    @media (max-width: 520px) {{ .stats {{ grid-template-columns:1fr; }} .stat:nth-child(3),.stat:nth-child(4) {{ display:none; }} }}
    @media print {{ aside,.side-actions {{ display:none!important; }} .app {{ display:block; }} main {{ padding:0; }} .hero {{ color:#111; background:#fff; box-shadow:none; border:1px solid #bbb; }} .hero p,.stat small {{ color:#444; }} article {{ box-shadow:none; border:0; }} details {{ break-inside:avoid; }} details > * {{ display:block!important; }} a {{ color:#111; }} }}
  </style>
</head>
<body>
<div class="app">
  <aside>
    <div class="brand"><span class="brand-mark">SD</span><span>Design Practice</span></div>
    <div class="eyebrow">Progress report</div>
    <div class="toc-title">On this page</div>
    <nav id="toc" aria-label="Report sections"></nav>
    <div class="side-actions">
      <button id="theme" type="button" aria-label="Toggle theme">◐ Theme</button>
      <button type="button" onclick="window.print()" aria-label="Print report">↗ Print</button>
    </div>
  </aside>
  <main>
    <header class="hero">
      <div class="eyebrow" style="color:#bff8eb">System design curriculum</div>
      <h1>Architecture practice,<br>made measurable.</h1>
      <p>A living report of design challenges, decision quality, tradeoffs, and the path from first draft to production-ready reasoning.</p>
      <div class="stats">
        <div class="stat"><small>Completed</small><b>{completed} of {total}</b><div class="progress"><i></i></div></div>
        <div class="stat"><small>Current challenge</small><b>{html.escape(current)}</b></div>
        <div class="stat"><small>Curriculum mode</small><b>{html.escape(mode)}</b></div>
        <div class="stat"><small>Last updated</small><b>{html.escape(updated)}</b></div>
      </div>
    </header>
    <article id="report">{body}</article>
    <footer class="report-footer">Generated from <code>SYSTEM_DESIGG.md</code> on {datetime.now().strftime('%Y-%m-%d %H:%M')} · The Markdown tracker remains the source of truth.</footer>
  </main>
</div>
<script>
  const root = document.documentElement;
  const savedTheme = localStorage.getItem('sd-theme');
  if (savedTheme) root.dataset.theme = savedTheme;
  document.getElementById('theme').addEventListener('click', () => {{
    root.dataset.theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
    localStorage.setItem('sd-theme', root.dataset.theme);
  }});
  document.querySelectorAll('article a').forEach(a => {{ a.target = '_blank'; a.rel = 'noopener noreferrer'; }});
  const toc = document.getElementById('toc');
  const headings = [...document.querySelectorAll('article h2, article h3')];
  headings.forEach(h => {{
    const a = document.createElement('a'); a.href = '#' + h.id; a.textContent = h.textContent;
    if (h.tagName === 'H3') a.className = 'sub'; toc.appendChild(a);
  }});
  const observer = new IntersectionObserver(entries => entries.forEach(e => {{
    if (e.isIntersecting) {{ document.querySelectorAll('#toc a').forEach(a => a.classList.remove('active')); const a = toc.querySelector(`a[href="#${{e.target.id}}"]`); if (a) a.classList.add('active'); }}
  }}), {{ rootMargin: '-15% 0px -75% 0px' }});
  headings.forEach(h => observer.observe(h));
</script>
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
  mermaid.initialize({{ startOnLoad: true, theme: 'neutral', securityLevel: 'strict', flowchart: {{ curve: 'basis', htmlLabels: true }} }});
</script>
</body>
</html>'''


def initialize_tracker(source_path: Path) -> None:
    if source_path.exists():
        raise SystemExit(f"Refusing to overwrite existing tracker: {source_path}")
    template_path = Path(__file__).resolve().parent.parent / "assets" / "SYSTEM_DESIGG.md"
    if not template_path.is_file():
        raise SystemExit(f"Bundled tracker template is missing: {template_path}")
    source = template_path.read_text(encoding="utf-8")
    source = source.replace("YYYY-MM-DD", date.today().isoformat(), 1)
    source_path.parent.mkdir(parents=True, exist_ok=True)
    source_path.write_text(source, encoding="utf-8")
    print(f"Initialized {source_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, help="Repository root containing SYSTEM_DESIGG.md")
    parser.add_argument("--init", action="store_true", help="Create the bundled tracker when it is missing")
    args = parser.parse_args()
    if args.root:
        root = args.root.resolve()
    elif args.init:
        root = Path.cwd().resolve()
    else:
        root = find_root(Path.cwd().resolve())
    source_path = root / "SYSTEM_DESIGG.md"
    output_path = root / "SYSTEM_DESIGG.html"
    if args.init:
        initialize_tracker(source_path)
    elif not source_path.is_file():
        raise SystemExit(f"Could not find tracker: {source_path}")
    source = source_path.read_text(encoding="utf-8")
    report = build_report(source)
    validate_report(report, source)
    output_path.write_text(report, encoding="utf-8")
    # Read the persisted artifact back; validation must cover what users open.
    persisted = output_path.read_text(encoding="utf-8")
    validate_report(persisted, source)
    print(f"Generated and verified {output_path} ({len(persisted):,} bytes)")


if __name__ == "__main__":
    main()
