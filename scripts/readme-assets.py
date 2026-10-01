#!/usr/bin/env python3
"""Generate the README images in docs/assets/ (banner, pipeline, checkpoints).

Colors follow the Nocturne design system the original pipeline diagram used.
Edit the data below and run:  python3 scripts/readme-assets.py
"""
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "docs" / "assets"

C = {
    "bg": "#161826", "surface": "#232532", "text": "#e9e9ed",
    "muted": "#9397ab", "faint": "#75798c", "rail": "#3f424d",
    "accent": "#9184d9", "a300": "#d2cefd", "a400": "#b5abfc",
    "a600": "#796cbf", "a700": "#5d5294", "a800": "#423a6a", "a900": "#2b2741",
    "n900": "#292b31",
}
SANS = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"


def t(x, y, s, size=13, fill=C["text"], weight=400, family=SANS, anchor="start", extra=""):
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" {extra}>{escape(s)}</text>')


def wrap(s, chars):
    words, lines, cur = s.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > chars and cur:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    return lines + [cur] if cur else lines


def pill(x, y, label, fill, color, family=SANS, size=11, pad=8, h=20):
    w = int(len(label) * size * (0.62 if family == MONO else 0.58)) + pad * 2
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="{fill}"/>'
            + t(x + w / 2, y + h / 2 + size * 0.36, label, size, color, 600, family, "middle")), w


def svg(w, h, body, defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img">{f"<defs>{defs}</defs>" if defs else ""}{body}</svg>\n')


FADE_DEFS = f"""
<linearGradient id="railfade" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{C['rail']}" stop-opacity="0"/>
  <stop offset="0.04" stop-color="{C['rail']}"/>
  <stop offset="0.96" stop-color="{C['rail']}"/>
  <stop offset="1" stop-color="{C['rail']}" stop-opacity="0"/>
</linearGradient>
<radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">
  <stop offset="0" stop-color="{C['accent']}" stop-opacity="0.35"/>
  <stop offset="1" stop-color="{C['accent']}" stop-opacity="0"/>
</radialGradient>"""

FLAG = "M-5,7 L-5,-7 M-5,-7 C-1,-9 1,-5 5,-6 L5,1 C1,2 -1,-2 -5,0"


# --------------------------------------------------------------------------- banner
def banner():
    W, H = 1200, 300
    b = [f'<rect width="{W}" height="{H}" rx="16" fill="{C["bg"]}"/>',
         f'<ellipse cx="930" cy="150" rx="330" ry="210" fill="url(#glow)"/>']
    tag, tw = pill(64, 62, "CLAUDE CODE PLUGIN · SDD → TDD", "none", C["a300"], size=12, pad=12, h=26)
    b.append(f'<rect x="64" y="62" width="{tw}" height="26" rx="6" fill="none" stroke="{C["a700"]}"/>')
    b.append(tag)
    b.append(t(62, 160, "claude-", 64, C["text"], 650, extra='letter-spacing="-1.5"')
             .replace("</text>", f'<tspan fill="{C["accent"]}">sdd</tspan></text>'))
    b.append(t(64, 206, "One command, ten specialized agents, three checkpoints.", 20, C["muted"]))
    b.append(t(64, 236, "From a ticket to tested, reviewed pull requests.", 20, C["muted"]))
    # mini rail on the right
    x0, y0 = 760, 70
    stages = ["explore", "spec", "plan", "design", "test", "build", "review", "verify"]
    b.append(f'<line x1="{x0 + 20}" y1="{y0 + 80}" x2="{x0 + 20 + 52 * (len(stages) - 1)}" '
             f'y2="{y0 + 80}" stroke="{C["rail"]}" stroke-width="2"/>')
    for i, s in enumerate(stages):
        cx = x0 + 20 + 52 * i
        cp = s in ("spec", "design", "verify")
        b.append(f'<circle cx="{cx}" cy="{y0 + 80}" r="{11 if cp else 8}" '
                 f'fill="{C["a800"] if cp else C["surface"]}" stroke="{C["a600"] if cp else C["rail"]}" '
                 f'stroke-width="{1.5 if cp else 1}"/>')
        b.append(t(cx, y0 + 112 + (16 if i % 2 else 0), s, 11, C["a300"] if cp else C["faint"], 500,
                   anchor="middle"))
    b.append(t(x0 + 20, y0 + 190, "● checkpoint: waits for your approval", 11, C["a400"], 500))
    return svg(W, H, "".join(b), FADE_DEFS)


# --------------------------------------------------------------------------- pipeline
ROWS = [
    ("step", "intake", None, "A request, a ticket link or a key. Fetches the ticket and reads the project's ## SDD config.", "→ request.md, config.md"),
    ("step", "memory recall", "optional", "Prior decisions and gotchas from Engram, when it's connected. Skipped otherwise.", "→ memory.md"),
    ("agent", "explorer", "haiku", "Read-only codebase recon: files, patterns, integration points.", "→ exploration.md"),
    ("agent", "spec-writer", "opus", "Testable spec: what and why, not how.", "→ spec.md"),
    ("cp", "CHECKPOINT 1", None, "Spec summary and blocking questions. Nothing continues without your approval.", None),
    ("agent", "task-planner", "sonnet", "Ordered, dependency-aware tasks. Estimates size and proposes slices for stacked PRs.", "→ tasks.md"),
    ("agent", "architect", "opus", "Where it lives, data flow, trade-offs. Checks every slice boundary.", "→ architecture.md"),
    ("agent", "designer", "opus", "Exact interfaces, schemas and errors.", "→ design.md"),
    ("cp", "CHECKPOINT 2", None, "Architecture and interfaces, plus single PR or stack of N. No code before this.", None),
    ("agent", "test-author", "sonnet", "TDD red: failing tests first. Skipped with --no-tests.", "→ tests + tests.md"),
    ("agent", "implementer", "sonnet", "TDD green: the minimum code to pass the tests. No scope creep.", "→ code + implementation.md"),
    ("step", "review", "tiered", "none · light · standard · deep, plus /security-review for sensitive areas.", "→ review.md"),
    ("agent", "verifier", "sonnet", "Independent PASS/FAIL with evidence. On FAIL, back to the implementer (up to 3 cycles).", "→ verification.md"),
    ("note", None, None, "Stacked mode: test → implement → review → verify → local commit, once per slice, each on its own branch.", None),
    ("cp", "CHECKPOINT 3", None, "Offers to launch the app and watch the feature work, not just pass tests. Optional.", None),
    ("agent", "archivist", "haiku", "Durable closeout record. Cleans up the scratch files.", "→ archive/<slug>.md"),
    ("step", "/sdd:publish-stack", "stacked only", "Pushes the slices and opens the PRs bottom-up, each based on the previous slice.", "→ N linked PRs"),
]
MODEL_FILL = {"opus": C["a800"], "sonnet": C["n900"], "haiku": C["n900"]}


def pipeline():
    W, X_RAIL, X_CARD, X_DESC, X_OUT = 960, 44, 84, 262, 930
    b, y = [], 28
    heights = {"agent": 64, "step": 64, "cp": 46, "note": 38}
    gaps = 12
    total = 28 + sum(heights[r[0]] + gaps for r in ROWS) + 16
    b.append(f'<rect width="{W}" height="{total}" rx="16" fill="{C["bg"]}"/>')
    b.append(f'<rect x="{X_RAIL - 1}" y="12" width="2" height="{total - 24}" fill="url(#railfade)"/>')
    n = 0
    for kind, name, model, desc, out in ROWS:
        h = heights[kind]
        cy = y + h / 2
        if kind == "note":
            b.append(f'<path d="M{X_RAIL - 6},{cy - 5} a6,6 0 1,0 6,-6" fill="none" stroke="{C["faint"]}" '
                     f'stroke-width="1.5" transform="translate(0,4)"/>')
            b.append(t(X_CARD, cy + 4, desc, 12.5, C["muted"], 400, extra='font-style="italic"'))
        elif kind == "cp":
            b.append(f'<circle cx="{X_RAIL}" cy="{cy}" r="19" fill="{C["a800"]}" stroke="{C["a600"]}"/>')
            b.append(f'<path d="{FLAG}" transform="translate({X_RAIL},{cy})" fill="none" '
                     f'stroke="{C["a300"]}" stroke-width="1.6" stroke-linejoin="round"/>')
            b.append(f'<rect x="{X_CARD}" y="{y}" width="{W - X_CARD - 16}" height="{h}" rx="8" '
                     f'fill="{C["a900"]}" stroke="{C["a700"]}"/>')
            p, pw = pill(X_CARD + 12, cy - 10, name, C["a800"], C["a300"], size=10.5)
            b.append(p)
            b.append(t(X_CARD + 24 + pw, cy + 4.5, desc, 13, C["text"], 500))
        else:
            n += 1 if kind == "agent" else 0
            ring = C["rail"]
            b.append(f'<circle cx="{X_RAIL}" cy="{cy}" r="18" fill="{C["surface"]}" stroke="{ring}"/>')
            label = str(n) if kind == "agent" else "·"
            b.append(t(X_RAIL, cy + 5, label, 13 if kind == "agent" else 22, C["a400"], 600, anchor="middle"))
            b.append(f'<rect x="{X_CARD}" y="{y}" width="{W - X_CARD - 16}" height="{h}" rx="8" fill="{C["surface"]}"/>')
            b.append(t(X_CARD + 14, y + 26, name, 15 if kind == "agent" else 13.5,
                       C["text"], 600, MONO))
            if model:
                fill = MODEL_FILL.get(model, "none")
                p, pw = pill(X_CARD + 14, y + 36, model, fill, C["a300"] if model == "opus" else C["muted"], size=10.5, h=18)
                if fill == "none":
                    b.append(f'<rect x="{X_CARD + 14}" y="{y + 36}" width="{pw}" height="18" rx="5" fill="none" stroke="{C["rail"]}"/>')
                b.append(p)
            lines = wrap(desc, 62)
            base = cy + 5 - (len(lines) - 1) * 9
            for i, line in enumerate(lines):
                b.append(t(X_DESC, base + i * 18, line, 13, C["text"] if i == 0 or True else C["muted"]))
            if out:
                b.append(t(X_OUT, cy + 4, out, 11.5, C["faint"], 500, MONO, "end"))
        y += h + gaps
    return svg(W, total, "".join(b), FADE_DEFS)


# --------------------------------------------------------------------------- checkpoints
CPS = [
    ("CHECKPOINT 1", "After spec-writer", "The spec summary and any blocking questions.", "Approve, or answer the questions. The spec-writer loops if revisions are needed."),
    ("CHECKPOINT 2", "After designer", "Architecture approach, exact interfaces, and single PR or stack of N.", "No code is written before this. Approving a stack creates local branches only."),
    ("CHECKPOINT 3", "After verifier passes", "An offer to launch the app and watch the feature work.", "Optional. Confirms it works live, not just in tests."),
]


def checkpoints():
    W, H, gap, pad = 960, 210, 16, 16
    cw = (W - pad * 2 - gap * 2) / 3
    b = [f'<rect width="{W}" height="{H}" rx="16" fill="{C["bg"]}"/>']
    for i, (tag, title, body, foot) in enumerate(CPS):
        x = pad + i * (cw + gap)
        b.append(f'<rect x="{x}" y="{pad}" width="{cw}" height="{H - pad * 2}" rx="10" fill="{C["surface"]}" stroke="{C["a700"]}"/>')
        p, _ = pill(x + 14, pad + 14, tag, C["a800"], C["a300"], size=10.5)
        b.append(p)
        b.append(t(x + 14, pad + 66, title, 17, C["text"], 600))
        for j, line in enumerate(wrap(body, 40)):
            b.append(t(x + 14, pad + 92 + j * 19, line, 13, C["text"]))
        b.append(f'<line x1="{x + 14}" y1="{H - pad - 52}" x2="{x + cw - 14}" y2="{H - pad - 52}" stroke="{C["rail"]}"/>')
        for j, line in enumerate(wrap(foot, 46)):
            b.append(t(x + 14, H - pad - 32 + j * 16, line, 11.5, C["muted"]))
    return svg(W, H, "".join(b))


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in (("banner", banner), ("pipeline", pipeline), ("checkpoints", checkpoints)):
        (OUT / f"{name}.svg").write_text(fn())
        print(f"wrote docs/assets/{name}.svg")
