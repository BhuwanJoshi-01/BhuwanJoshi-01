"""All the cards below the hero. Copy lives here: edit a string, run build.py."""
import json
import math
import random
from datetime import date, timedelta
from pathlib import Path

from scene import card_close, card_shell, signer
from svgkit import C, FLAGS, Svg, fmt, range_points, ridge_path, snow_path, text_width, wrap

ROOT = Path(__file__).resolve().parent.parent

RISE = ("@keyframes rise{0%{opacity:0;transform:translateY(9px)}3%{opacity:1;transform:translateY(0)}"
        "95%{opacity:1;transform:translateY(0)}99%,100%{opacity:0;transform:translateY(0)}}")


def two_pass(W, label, draw):
    """Runs a layout once to learn its height, then again for real."""
    H = draw(Svg(W, 2000, label), 2000)
    s = Svg(W, round(H), label)
    draw(s, round(H))
    return s


# ---------- experience: the server log ---------------------------------------

EXPERIENCE = [
    ("September 2024", "cap", C["ice"], [("Bhuwan ", "ui6", C["text"]), ("enrolled at ", "ui", C["body"]), ("Sunway College Kathmandu", "ui6", C["text"])],
     "BSc (Hons) Computer Science with Artificial Intelligence. Expected May 2028.", None),
    ("January 2026", "arrow", C["online"], [("Bhuwan ", "ui6", C["text"]), ("joined ", "ui", C["body"]), ("RAIN, Sunway College Kathmandu ", "ui6", C["text"]), ("as Development Intern", "ui", C["body"])],
     "Building MySunway: real-time floor and seat booking in React Native, TypeScript, Node.js and Firebase.", "NOW"),
    ("February 2026", "arrow", C["online"], [("Bhuwan ", "ui6", C["text"]), ("joined ", "ui", C["body"]), ("Prateek Innovations ", "ui6", C["text"]), ("as Software Development Intern", "ui", C["body"])],
     "Shipped user-facing web features, backend integrations and API work.", "v1.0"),
    ("July 2026", "up", C["glow"], [("Bhuwan ", "ui6", C["text"]), ("leveled up to ", "ui", C["body"]), ("Junior AI Developer", "ui6", C["glow"])],
     "Promoted after five months. Now on inclusive AI products, 3D systems and interactive 3D for the web.", "v2.0"),
    ("Also in 2026", "shield", C["ice"], [("Bhuwan ", "ui6", C["text"]), ("served as ", "ui", C["body"]), ("IT Head at AIDA", "ui6", C["text"])],
     "Worked on the whole AIDA website and its custom CMS, with an application portal and a WCAG 2.2 AA target.", None),
]


def experience(W):
    label = ("Career log: enrolled at Sunway College in September 2024. Joined RAIN as Development Intern in January 2026. "
             "Joined Prateek Innovations as Software Development Intern in February 2026, promoted to Junior AI Developer in July 2026. Also served as IT Head at AIDA.")

    def draw(s, H):
        s.style(RISE + ".m{animation:rise 28s ease-out infinite both}"
                "@keyframes dots{0%,60%,100%{transform:translateY(0);opacity:.4}30%{transform:translateY(-4px);opacity:1}}")
        card_shell(s, W, H, comet=False)
        m = 22 if W > 500 else 16
        tx = m + 36
        y = 12
        for i, (when, icon, color, head, body, tag) in enumerate(EXPERIENCE):
            s.add(f'<g class="m" style="animation-delay:{.25 + i * .55:.2f}s">')
            y += 24
            tw = text_width(when, "mono5", 11)
            s.rect(m, y - 4, (W - 2 * m - tw - 24) / 2, 1, fill=C["stroke"])
            s.rect(W - m - (W - 2 * m - tw - 24) / 2, y - 4, (W - 2 * m - tw - 24) / 2, 1, fill=C["stroke"])
            s.text(W / 2, y, when, "mono5", 11, C["muted"], anchor="middle")
            y += 28
            # the icon sits in a soft tile, the way system messages do
            s.add(f'<rect x="{m}" y="{y - 15}" width="26" height="26" rx="8" fill="{color}" fill-opacity=".13"/>')
            s.icon(icon, m + 5, y - 10, 16, color, sw=2)
            wide = W - tx - m - (58 if tag else 0)
            ny = s.spans(tx, y, head, wide, size=14.5, lh=1.42)
            if tag:
                now = tag == "NOW"
                s.pill(W - m - text_width(tag, "mono7", 10.5) - 18, y - 15, tag, "mono7", 10.5,
                       fg=C["online"] if now else C["glow"], bg=C["panel"], h=22, pad=9)
            y = s.para(tx, ny, body, W - tx - m, "ui", 13.5, C["muted"], lh=1.45) - 8
            s.add("</g>")
        # typing indicator
        y += 30
        s.add(f'<g class="m" style="animation-delay:{.25 + len(EXPERIENCE) * .55:.2f}s">')
        for i in range(3):
            cx = m + 8 + i * 9
            s.add(f'<circle cx="{cx}" cy="{y - 4}" r="3" fill="{C["body"]}" style="animation:dots 1.2s ease-in-out {i * .16:.2f}s infinite"/>')
        s.spans(m + 42, y, [("Bhuwan ", "ui6", C["body"]), ("is typing the next one", "ui", C["muted"])], W, size=12.5)
        s.add("</g>")
        y += 18
        card_close(s, W, H, dur=16)
        return y

    return two_pass(W, label, draw)


# ---------- stack: roles ------------------------------------------------------

STACK = [
    ("FRONTEND + MOBILE", C["blue"], ["React", "React Native", "TypeScript", "Expo", "Tailwind CSS", "Framer Motion", "Three.js", "~Next.js"]),
    ("BACKEND", C["green"], ["Node.js", "Express", "Fastify", "Django", "FastAPI", "REST", "Socket.IO", "WebRTC", "~GraphQL"]),
    ("DATA", C["yellow"], ["PostgreSQL", "Firebase", "Redis", "SQLite", "Prisma", "pgvector", "~MongoDB"]),
    ("AI + 3D", C["red"], ["Python", "Blender", "PyTorch", "RAG", "Ollama", "~TensorFlow"]),
    ("SYSTEMS", C["white"], ["Linux", "systemd", "MQTT", "ESP32", "Git", "Playwright", "Vitest", "~Docker", "~GitHub Actions"]),
]


def stack(W):
    label = "Tech stack as roles. " + " ".join(f"{g}: " + ", ".join(i.lstrip("~") for i in items) + "." for g, _, items in STACK)

    def draw(s, H):
        s.style(RISE + ".m{animation:rise 30s ease-out infinite both}"
                "@keyframes wave{0%,100%{transform:skewY(0)}50%{transform:skewY(-9deg)}}"
                "@keyframes sweep{0%,55%{transform:translateX(-200px) skewX(-20deg)}100%{transform:translateX(1200px) skewX(-20deg)}}")
        card_shell(s, W, H, comet=False)
        m = 22 if W > 500 else 16
        col = 170 if W > 500 else 0
        y = 20
        n = 0
        for label_, color, items in STACK:
            # a small prayer flag marks each group
            ly = y + 3
            s.add(f'<rect x="{m}" y="{ly}" width="15" height="19" rx="2" fill="{color}" style="transform-origin:{m}px {ly}px;animation:wave 2.8s ease-in-out infinite"/>')
            s.text(m + 24, y + 17, label_, "mono5", 11, C["body"], ls=.8)
            if col:
                px, py = m + col, y
            else:
                px, py = m, y + 30
            start = px
            for item in items:
                learning = item.startswith("~")
                name = item.lstrip("~")
                w = text_width(name, "ui5", 12.5) + 36
                if px + w > W - m:
                    px = start
                    py += 33
                s.add(f'<g class="m" style="animation-delay:{.1 + n * .035:.2f}s">')
                px += s.pill(px, py, name, dot=color, hollow=learning, fg=C["muted"] if learning else C["text"]) + 7
                s.add("</g>")
                n += 1
            y = py + 42
        # key for hollow dots
        y += 2
        s.add(f'<circle cx="{m + 5}" cy="{y}" r="4.5" fill="{C["muted"]}"/>')
        s.text(m + 16, y + 4, "daily and comfortable", "ui", 11.5, C["muted"])
        kx = m + 16 + text_width("daily and comfortable", "ui", 11.5) + 22
        s.add(f'<circle cx="{kx}" cy="{y}" r="3.500" fill="none" stroke="{C["muted"]}" stroke-width="1.5"/>')
        s.text(kx + 11, y + 4, "still learning", "ui", 11.5, C["muted"])
        y += 20
        # one light sweep across the whole card
        g = s.uid("sw")
        s.defs.append(f'<linearGradient id="{g}"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".07"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>')
        s.add(f'<rect x="0" y="-40" width="170" height="{H + 80}" fill="url(#{g})" style="transform:translateX(-200px);animation:sweep 9s ease-in-out infinite"/>')
        card_close(s, W, H, dur=18)
        return y

    return two_pass(W, label, draw)


# ---------- wayland-wallpaperengine: the featured embed -----------------------

def desktop_demo(s, x, y, w, h):
    """Plays the project's main trick: focus an app, the wallpaper freezes, the load drops."""
    cyc = 13
    s.style(f"@keyframes wp{{0%{{transform:translateX(0)}}44%{{transform:translateX(-{.8302 * 300:.1f}px)}}"
            f"92%{{transform:translateX(-{.8302 * 300:.1f}px)}}100%{{transform:translateX(-300px)}}}}"
            f"@keyframes wp2{{0%{{transform:translateX(0)}}44%{{transform:translateX(-{.8302 * 180:.1f}px)}}"
            f"92%{{transform:translateX(-{.8302 * 180:.1f}px)}}100%{{transform:translateX(-180px)}}}}"
            f"@keyframes wp3{{0%{{transform:translateY(0)}}44%{{transform:translateY({.8302 * 50:.1f}px)}}"
            f"92%{{transform:translateY({.8302 * 50:.1f}px)}}100%{{transform:translateY(50px)}}}}"
            f"@keyframes win{{0%,42%{{transform:translateY({h}px)}}49%,91%{{transform:translateY(0)}}98%,100%{{transform:translateY({h}px)}}}}"
            f"@keyframes pl{{0%,44%{{opacity:1}}47%,92%{{opacity:0}}95%,100%{{opacity:1}}}}"
            f"@keyframes fz{{0%,44%{{opacity:0}}47%,92%{{opacity:1}}95%,100%{{opacity:0}}}}"
            f".pl{{animation:pl {cyc}s ease infinite}}.fz{{opacity:0;animation:fz {cyc}s ease infinite}}")
    clip = s.uid("dk")
    s.defs.append(f'<clipPath id="{clip}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10"/></clipPath>')
    g = s.uid("ds")
    s.defs.append(f'<linearGradient id="{g}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#141c44"/><stop offset=".55" stop-color="#6a4f86"/><stop offset=".85" stop-color="#f08f78"/><stop offset="1" stop-color="#ffc796"/></linearGradient>')
    s.add(f'<g clip-path="url(#{clip})">')
    s.rect(x, y, w, h, fill=f"url(#{g})")
    # falling snow, frozen with everything else
    rng = random.Random(9)
    dots = "".join(f'<circle cx="{x + rng.uniform(0, w):.0f}" cy="{y + rng.uniform(-50, h):.0f}" r="{rng.choice((.9, 1.3, 1.7))}" fill="#fff" fill-opacity=".8"/>' for _ in range(34))
    s.add(f'<g style="animation:wp3 {cyc}s linear infinite">{dots}<g transform="translate(0 -50)">{dots}</g></g>')
    # two ridge layers moving
    pts = range_points(51, 300, 3, y + h * .88, h * .62, peaks=4, jag=.1)
    d = ridge_path(pts, y + h)
    pts2 = range_points(52, 180, 3, y + h * 1.01, h * .34, peaks=4, jag=.1)
    d2 = ridge_path(pts2, y + h)
    copies = max(2, int(w / 300) + 2)
    far = "".join(f'<path d="{d}" transform="translate({i * 300} 0)" fill="#4a3a68" stroke="#4a3a68"/>' for i in range(copies))
    copies = max(3, int(w / 180) + 2)
    near = "".join(f'<path d="{d2}" transform="translate({i * 180} 0)" fill="#17132b" stroke="#17132b"/>' for i in range(copies))
    s.add(f'<g transform="translate({x} 0)"><g style="animation:wp {cyc}s linear infinite">{far}</g></g>')
    s.add(f'<g transform="translate({x} 0)"><g style="animation:wp2 {cyc}s linear infinite">{near}</g></g>')
    # GNOME-ish top bar
    s.rect(x, y, w, 20, fill="#000", extra='fill-opacity=".62"')
    s.text(x + 10, y + 14, "Activities", "ui5", 9.5, "#dfe5ee")
    s.text(x + w / 2, y + 14, "Tue 8:03 PM", "ui5", 9.5, "#dfe5ee", anchor="middle")
    s.add(f'<circle cx="{x + w - 14}" cy="{y + 10}" r="3.500" fill="#dfe5ee"/>')
    # the app window slides up and takes focus
    wx, wy, ww, wh = x + w * .14, y + 34, w * .72, h - 46
    s.add(f'<g style="transform:translateY({h}px);animation:win {cyc}s cubic-bezier(.2,.8,.2,1) infinite">')
    s.rect(wx, wy, ww, wh, 8, fill="#14181f", stroke="#39424f")
    s.rect(wx, wy, ww, 20, 8, fill="#1f252e")
    for i, c in enumerate(("#e5534b", "#e3b341", "#3fb950")):
        s.add(f'<circle cx="{wx + 13 + i * 12:.1f}" cy="{wy + 10}" r="3.200" fill="{c}"/>')
    code_rng = random.Random(4)
    for i in range(int((wh - 34) / 13)):
        lx = wx + 14 + (code_rng.choice((0, 0, 12, 24)))
        lw = code_rng.uniform(.25, .68) * ww
        s.rect(lx, wy + 30 + i * 13, lw, 5, 2.5, fill=code_rng.choice((C["ice"], C["dim"], C["glow"], C["dim"])), extra='fill-opacity=".75"')
    s.add("</g></g>")
    s.rect(x, y, w, h, 10, stroke=C["stroke"])


def meters(s, x, y, w):
    """CPU and GPU load. Numbers are the project's own measurements on an Intel iGPU."""
    cyc = 13
    rows = (("Renderer CPU", 13, 0), ("GNOME Shell CPU", 22, 3), ("GPU", 71, 7))
    labw = 118
    bw = w - labw - 44
    for i, (name, a, b) in enumerate(rows):
        yy = y + i * 24
        s.text(x, yy + 10, name, "ui", 12, C["muted"])
        bx = x + labw
        s.rect(bx, yy + 2, bw, 8, 4, fill=C["panel2"])
        s.style(f"@keyframes me{i}{{0%,42%{{transform:scaleX({a / 100})}}49%,91%{{transform:scaleX({b / 100})}}98%,100%{{transform:scaleX({a / 100})}}}}")
        s.rect(bx, yy + 2, bw, 8, 4, fill=C["glow"] if i == 2 else C["ice"],
               extra=f'style="transform-origin:{bx}px {yy + 6}px;transform:scaleX({a / 100});animation:me{i} {cyc}s cubic-bezier(.2,.8,.2,1) infinite"')
        s.text(x + w, yy + 10, f"{a} %", "mono5", 11.5, C["text"], anchor="end", cls="pl")
        s.text(x + w, yy + 10, f"{b} %", "mono5", 11.5, C["online"], anchor="end", cls="fz")
    return y + len(rows) * 24


def state_chip(s, x, y):
    s.pill(x, y, "on the desktop: playing", "mono5", 11, fg=C["ice"], bg=C["panel"], h=24, pad=10, dot=C["online"], cls="pl")
    s.pill(x, y, "app focused: frozen", "mono5", 11, fg=C["glow"], bg=C["panel"], h=24, pad=10, dot=C["glow"], cls="fz")


def oss_wwe(W):
    label = ("wayland-wallpaperengine. Your Steam Wallpaper Engine wallpapers as a live desktop background on Linux Wayland, including GNOME. "
             "An animation shows the wallpaper freezing when an app takes focus: renderer CPU drops from 13 to 0 percent, GNOME Shell CPU from 22 to 3 percent, GPU from 71 to 7 percent, measured on an Intel iGPU.")
    wide = W > 500

    def draw(s, H):
        card_shell(s, W, H, comet=False)
        s.rect(0, 0, 5, H, fill=C["ice"])
        m = 26 if wide else 18
        tw = 408 if wide else W - m - 16
        y = 32
        s.icon("branch", m, y - 12, 14, C["muted"])
        s.text(m + 20, y, "open source", "mono5", 11.5, C["muted"])
        lic = text_width("open source", "mono5", 11.5)
        s.text(m + 34 + lic, y, "GPL-3.0", "mono5", 11.5, C["ice"])
        y += 36
        s.text(m, y, "wayland-wallpaperengine", "ui7", 25 if wide else 22, C["text"])
        y += 28
        y = s.para(m, y, "Your Steam Wallpaper Engine wallpapers as a live desktop background on Linux Wayland, including GNOME.", tw, "ui5", 15, C["text"], lh=1.42)
        y += 4
        y = s.para(m, y, "No tool could put these on the GNOME desktop, since GNOME has no wlr-layer-shell. A small Shell extension does it here. Mouse interaction, sound on the desktop only, and it stops completely while you work or game.", tw, "ui", 13.5, C["body"], lh=1.5)
        y += 6
        if wide:
            fy = y
            s.text(m, fy + 8, "RUNS ON", "mono5", 10, C["muted"], ls=1)
            s.text(m, fy + 27, "GNOME 46-50, KDE Plasma 6, Hyprland, Sway, niri", "ui5", 13, C["text"])
            y = fy + 46
            s.text(m, y + 8, "CONTROL", "mono5", 10, C["muted"], ls=1)
            s.text(m, y + 27, "wwe", "mono7", 13, C["glow"])
            s.text(m + 34, y + 27, "CLI and a top-bar picker", "ui", 13, C["body"])
            left_end = y + 48
            # right column: live demo and meters
            dx = 456
            dw = W - dx - 22
            desktop_demo(s, dx, 22, dw, 212)
            state_chip(s, dx + 10, 196)
            my = meters(s, dx, 250, dw)
            end = max(left_end, my + 8)
        else:
            s.text(m, y + 8, "RUNS ON", "mono5", 10, C["muted"], ls=1)
            y = s.para(m, y + 27, "GNOME 46-50, KDE Plasma 6, Hyprland, Sway, niri", tw, "ui5", 13, C["text"]) + 2
            dw = W - m - 16
            desktop_demo(s, m, y, dw, 190)
            state_chip(s, m + 10, y + 158)
            y = meters(s, m, y + 204, dw)
            end = y + 6
        card_close(s, W, H, dur=13)
        return end

    return two_pass(W, label, draw)


# ---------- thumbnails --------------------------------------------------------

def tile(s, x, y, t=86):
    s.rect(x, y, t, t, 12, fill="#0a0d12", stroke=C["stroke"])
    clip = s.uid("t")
    s.defs.append(f'<clipPath id="{clip}"><rect x="{x}" y="{y}" width="{t}" height="{t}" rx="12"/></clipPath>')
    s.add(f'<g clip-path="url(#{clip})">')


def th_friday(s, x, y, t):
    tile(s, x, y, t)
    s.style("@keyframes pop{0%{opacity:0;transform:scale(.7)}6%,84%{opacity:1;transform:scale(1)}92%,100%{opacity:0;transform:scale(1)}}"
            "@keyframes dots{0%,60%,100%{transform:translateY(0);opacity:.4}30%{transform:translateY(-3px);opacity:1}}")
    bubbles = ((x + 9, y + 11, 44, 16, "#2a313c", 0), (x + 33, y + 33, 44, 16, C["green"], 1.1))
    for bx, by, bw, bh, c, d in bubbles:
        s.add(f'<g style="transform-origin:{bx + bw / 2}px {by + bh / 2}px;animation:pop 8s ease-out {d}s infinite both">')
        s.rect(bx, by, bw, bh, 7, fill=c)
        s.rect(bx + 7, by + 6, bw - 18, 4, 2, fill="#fff", extra='fill-opacity=".75"')
        s.add("</g>")
    bx, by = x + 9, y + 56
    s.add(f'<g style="transform-origin:{bx + 16}px {by + 8}px;animation:pop 8s ease-out 2.2s infinite both">')
    s.rect(bx, by, 34, 18, 8, fill="#2a313c")
    for i in range(3):
        s.add(f'<circle cx="{bx + 9 + i * 8}" cy="{by + 9}" r="2.4" fill="#fff" style="animation:dots 1.1s ease-in-out {i * .15:.2f}s infinite"/>')
    s.add("</g></g>")


def th_mala(s, x, y, t):
    tile(s, x, y, t)
    s.style("@keyframes bead{0%{fill:#3a4452}.5%{fill:#f4a97f}55%{fill:#f4a97f}95%{fill:#3a4452}100%{fill:#3a4452}}")
    cx, cy, r = x + t / 2, y + t / 2, t * .38
    cyc = 21.6
    beads = []
    for i in range(108):
        a = -math.pi / 2 + i / 108 * 2 * math.pi
        beads.append(f'<circle cx="{cx + r * math.cos(a):.1f}" cy="{cy + r * math.sin(a):.1f}" r="1.25" fill="#3a4452" style="animation:bead {cyc}s linear {i * .2:.1f}s infinite"/>')
    s.add("".join(beads))
    s.text(cx, cy + 6, "108", "ui7", 17, C["text"], anchor="middle")
    s.add("</g>")


def th_layers(s, x, y, t):
    tile(s, x, y, t)
    s.style("@keyframes px{0%,100%{transform:translate(0,0)}50%{transform:translate(var(--dx),var(--dy))}}")
    for i, (o, dx, dy, c) in enumerate(((.45, -6, 4, C["dim"]), (.75, 3, -3, C["deep"]), (1, 8, -7, C["ice"]))):
        ox = x + 14 + i * 9
        oy = y + 18 + i * 10
        s.add(f'<g style="--dx:{dx}px;--dy:{dy}px;animation:px 7s ease-in-out infinite">')
        s.rect(ox, oy, 42, 30, 5, fill=c, extra=f'fill-opacity="{o}"')
        s.add("</g>")
    s.add("</g>")


def th_signer(s, x, y, t):
    tile(s, x, y, t)
    signer(s, x + 2, y + 2, t - 4, dur=9, frames=22)
    s.add("</g>")


def th_aa(s, x, y, t):
    tile(s, x, y, t)
    cx, cy, r = x + t / 2, y + t / 2, t * .38
    s.style("@keyframes ringa{0%{stroke-dashoffset:100}40%,88%{stroke-dashoffset:0}100%{stroke-dashoffset:-100}}")
    s.add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{C["panel2"]}" stroke-width="4"/>')
    s.add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{C["green"]}" stroke-width="4" stroke-linecap="round" pathLength="100" stroke-dasharray="100 100" transform="rotate(-90 {cx} {cy})" style="animation:ringa 7s ease-in-out infinite"/>')
    s.text(cx, cy + 8, "AA", "ui7", 23, C["text"], anchor="middle")
    s.add("</g>")


def th_seats(s, x, y, t):
    tile(s, x, y, t)
    s.style("@keyframes seat{0%,8%{fill:#2a313c}14%,78%{fill:var(--on)}86%,100%{fill:#2a313c}}")
    rng = random.Random(5)
    cols, rows = 6, 6
    gap = 11.5
    ox, oy = x + (t - (cols - 1) * gap - 8) / 2, y + (t - (rows - 1) * gap - 8) / 2
    for r_ in range(rows):
        for c_ in range(cols):
            on = rng.choice((C["ice"], C["ice"], C["glow"]))
            if rng.random() > .72:
                s.rect(ox + c_ * gap, oy + r_ * gap, 8, 8, 2, fill="#2a313c")
            else:
                s.rect(ox + c_ * gap, oy + r_ * gap, 8, 8, 2, fill="#2a313c",
                       extra=f'style="--on:{on};animation:seat 11s ease-in-out -{rng.uniform(0, 11):.1f}s infinite"')
    s.add("</g>")


def th_mesh(s, x, y, t):
    tile(s, x, y, t)
    cx, cy = x + t / 2, y + t / 2
    s.style("@keyframes ping{0%{transform:scale(.25);opacity:.9}100%{transform:scale(1);opacity:0}}")
    for i in range(3):
        s.add(f'<circle cx="{cx}" cy="{cy}" r="{t * .44}" fill="none" stroke="{C["green"]}" stroke-width="1.6" style="transform-origin:{cx}px {cy}px;animation:ping 4.5s ease-out {i * 1.5}s infinite both"/>')
    for dx, dy in ((-27, -24), (27, -24), (-29, 22), (29, 22), (0, 32)):
        s.add(f'<path d="M{cx} {cy}L{cx + dx} {cy + dy}" stroke="{C["dim"]}"/><circle cx="{cx + dx}" cy="{cy + dy}" r="3.500" fill="{C["green"]}"/>')
    s.rect(cx - 12, cy - 12, 24, 24, 4, fill=C["panel2"], stroke=C["green"])
    s.add(f'<rect x="{cx - 5}" y="{cy - 5}" width="10" height="10" rx="1.500" fill="{C["green"]}"/>')
    s.add("</g>")


def th_radar(s, x, y, t):
    tile(s, x, y, t)
    cx, cy, r = x + t / 2, y + t / 2, t * .42
    s.style("@keyframes spin{to{transform:rotate(360deg)}}@keyframes blip{0%,100%{opacity:.2}50%{opacity:1}}")
    for k in (1, .66, .33):
        s.add(f'<circle cx="{cx}" cy="{cy}" r="{r * k:.1f}" fill="none" stroke="{C["panel2"]}"/>')
    g = s.uid("rd")
    s.defs.append(f'<linearGradient id="{g}" gradientUnits="userSpaceOnUse" x1="{cx}" y1="{cy}" x2="{cx + r}" y2="{cy - r * .6}"><stop offset="0" stop-color="{C["ice"]}" stop-opacity=".7"/><stop offset="1" stop-color="{C["ice"]}" stop-opacity="0"/></linearGradient>')
    a1, a2 = -.75, 0
    s.add(f'<g style="transform-origin:{cx}px {cy}px;animation:spin 3.6s linear infinite"><path d="M{cx} {cy}L{cx + r * math.cos(a1):.1f} {cy + r * math.sin(a1):.1f}A{r} {r} 0 0 1 {cx + r:.1f} {cy:.1f}z" fill="url(#{g})"/></g>')
    rng = random.Random(8)
    for i in range(9):
        a, d = rng.uniform(0, 6.28), rng.uniform(.25, .92)
        s.add(f'<circle cx="{cx + r * d * math.cos(a):.1f}" cy="{cy + r * d * math.sin(a):.1f}" r="1.800" fill="{C["glow"]}" style="animation:blip 3.6s ease-in-out -{rng.uniform(0, 3.6):.1f}s infinite"/>')
    s.add("</g>")


def th_scales(s, x, y, t):
    tile(s, x, y, t)
    cx = x + t / 2
    top = y + 20
    s.style("@keyframes tilt{0%,100%{transform:rotate(-7deg)}50%{transform:rotate(7deg)}}"
            "@keyframes untilt{0%,100%{transform:rotate(7deg)}50%{transform:rotate(-7deg)}}")
    s.add(f'<path d="M{cx} {top - 6}V{y + t - 16}M{cx - 15} {y + t - 15}H{cx + 15}" stroke="{C["ice"]}" stroke-width="2.600" stroke-linecap="round" fill="none"/>')
    s.add(f'<g style="transform-origin:{cx}px {top}px;animation:tilt 6s ease-in-out infinite">')
    s.add(f'<path d="M{cx - 27} {top}H{cx + 27}" stroke="{C["ice"]}" stroke-width="2.600" stroke-linecap="round"/>')
    for side, c in ((-27, C["glow"]), (27, C["ice"])):
        px = cx + side
        s.add(f'<g style="transform-origin:{px}px {top}px;animation:untilt 6s ease-in-out infinite">'
              f'<path d="M{px} {top}L{px - 10} {top + 22}M{px} {top}L{px + 10} {top + 22}" stroke="{C["dim"]}"/>'
              f'<path d="M{px - 12} {top + 22}H{px + 12}a12 9 0 0 1-24 0z" fill="{c}"/></g>')
    s.add("</g></g>")


THUMBS = dict(friday=th_friday, mala=th_mala, layers=th_layers, signer=th_signer, aa=th_aa, seats=th_seats, mesh=th_mesh, radar=th_radar, scales=th_scales)


def typed_address(s, x, y, w):
    """A small form field that accepts an address most websites reject."""
    addr = "राम@नेपाल.नेपाल"
    s.rect(x, y, w, 32, 8, fill=C["panel"], stroke=C["stroke"])
    clip = s.uid("ad")
    s.defs.append(f'<clipPath id="{clip}"><rect x="{x}" y="{y}" width="{w}" height="32" rx="8"/></clipPath>')
    tw = text_width(addr, "deva", 14)
    s.style(f"@keyframes adr{{0%{{transform:translateX(0)}}30%,92%{{transform:translateX({tw + 4:.0f}px)}}100%{{transform:translateX({tw + 4:.0f}px)}}}}"
            "@keyframes ok{0%,30%{opacity:0;transform:scale(.6)}36%,92%{opacity:1;transform:scale(1)}100%{opacity:0}}")
    s.add(f'<g clip-path="url(#{clip})">')
    s.text(x + 12, y + 21, addr, "deva", 14, C["text"])
    s.rect(x + 10, y + 2, tw + 4, 28, fill=C["panel"], extra=f'style="transform:translateX({tw + 4:.0f}px);animation:adr 9s steps(14) infinite"')
    s.add("</g>")
    ox = x + w - 66
    s.add(f'<g style="transform-origin:{ox + 30}px {y + 17}px;animation:ok 9s ease infinite">')
    s.pill(ox, y + 5, "valid", "mono7", 10.5, fg=C["green"], bg=C["card"], stroke=C["green"], h=22, pad=9)
    s.add("</g>")


def embed(name, title, desc, color, thumb, foot, kicker, link_icon="branch", strip=None):
    """A chat-app style rich embed, 420 wide so two sit side by side."""
    W, H = 420, 204
    s = Svg(W, H, f"{title}. {desc} {' / '.join(foot)}.")
    card_shell(s, W, H, r=14, comet=False)
    s.rect(0, 0, 4, H, fill=color)
    m, t = 20, 86
    tx = W - t - 16
    has_thumb = thumb is not None
    width = (tx - m - 14) if has_thumb else (W - m - 20)
    s.icon(link_icon, m, 15, 13, C["muted"])
    s.text(m + 18, 26, kicker, "mono5", 11, C["muted"])
    y = 54
    tsize = 18
    if text_width(title, "ui7", tsize) > width:
        tsize = 16.5
    s.text(m, y, title, "ui7", tsize, C["text"])
    y += 24
    s.para(m, y, desc, width, "ui", 13, C["body"], lh=1.46, max_lines=(2 if strip else 5))
    if has_thumb:
        THUMBS[thumb](s, tx, 16, t)
    if strip:
        strip(s, m, 119, W - m - 18)
    # footer fields
    fx = m
    fy = H - 24
    s.rect(m, fy - 21, W - m - 16, 1, fill=C["stroke"])
    for i, f in enumerate(foot):
        if i == 0:
            s.add(f'<circle cx="{fx + 4}" cy="{fy - 4}" r="4" fill="{color}"/>')
            fx += 13
        fx += s.text(fx, fy, f, "ui5" if i == 0 else "ui", 12, C["body"] if i == 0 else C["muted"]) + 14
    card_close(s, W, H, r=14, comet=False)
    return s


OSS_CARDS = {
    "oss-friday": dict(title="friday-whatsapp-ai-bot", kicker="open source  MIT", color=C["green"], thumb="friday",
                       desc="A personal operator for WhatsApp, on Groq AI. It tracks follow-ups, schedules reminders and learns your reply style.",
                       foot=["JavaScript", "Baileys", "SQLite"]),
    "oss-ua": dict(title="UA-Hackathon-2026", kicker="national hackathon", color=C["blue"], thumb=None, strip=typed_address,
                   desc="A contact form that accepts internationalised email across Devanagari, Arabic, Han and Latin scripts.",
                   foot=["TypeScript", "React", "Fastify", "Vitest"]),
    "oss-mantra": dict(title="MantraTracker", kicker="open source  MIT", color=C["glow"], thumb="mala",
                       desc="Naam Jap Counter: an offline, ad-free mantra counter with a 108-bead mala and session tracking.",
                       foot=["TypeScript", "React Native", "Expo"]),
    "oss-portfolio": dict(title="Portfolio", kicker="public repo", color=C["ice"], thumb="layers",
                          desc="The site behind joshibhuwan.com.np: a dark, cinematic scroll story with parallax and motion.",
                          foot=["JavaScript", "React", "Framer Motion"]),
}

WORK_CARDS = {
    "work-setu": dict(title="SETU", kicker="live  Prateek Innovations", color=C["red"], thumb="signer", link_icon="globe",
                      desc="Turns speech and text into Nepali Sign Language on a 3D signer. I work on the avatars and the 3D web.",
                      foot=["Three.js", "Blender", "Python"]),
    "work-aida": dict(title="AIDA 2026", kicker="live  site and CMS", color=C["green"], thumb="aa", link_icon="globe",
                      desc="Website, application portal and custom CMS for an AI hackathon for people with disabilities.",
                      foot=["React", "Express", "Prisma"]),
    "work-mysunway": dict(title="MySunway", kicker="RAIN  Sunway College", color=C["blue"], thumb="seats", link_icon="flag",
                          desc="Real-time campus floor and seat booking: a React Native app, web console and push notifications.",
                          foot=["React Native", "Expo", "Firebase"]),
    "work-terranode": dict(title="TerraNode", kicker="research  smart irrigation", color=C["green"], thumb="mesh", link_icon="flag",
                           desc="Per-crop irrigation: ESP32 firmware runs valves offline, with web and mobile control and a digital twin.",
                           foot=["ESP32", "MQTT", "React Native"]),
    "work-eai": dict(title="EAI Readiness Audit", kicker="from a winning hackathon entry", color=C["ice"], thumb="radar", link_icon="flag",
                     desc="Probes .np mail servers for internationalised email. A June 2026 pilot audited 394 domains.",
                     foot=["Python", "Fastify", "Docker"]),
    "work-nyaya": dict(title="Nyaya Sathi", kicker="local-first AI", color=C["yellow"], thumb="scales", link_icon="flag",
                       desc="A private legal assistant for Nepal, in English and Nepali, citing law with hybrid search and no cloud calls.",
                       foot=["TypeScript", "pgvector", "Ollama"]),
}


# ---------- next up: repos on their way to public -----------------------------

GOING_PUBLIC = {
    "next-screenshare": dict(repo="screenshare-doctor", color=C["blue"], status="in development", cmd="screenshare-doctor doctor",
                             desc="Find out why screen sharing fails on your Linux Wayland desktop."),
    "next-gpu": dict(repo="gpu-stack-inspector", color=C["red"], status="0.1.0 in testing", cmd="gpu-stack-inspector rules list",
                     desc="Explain why your AI code uses the GPU in one Python environment but not another."),
    "next-worktree": dict(repo="worktree-shield", color=C["yellow"], status="in development", cmd="worktree-shield scan --strict",
                          desc="Audit parallel Git worktrees for shared ports, databases and Docker resources before your agents collide."),
}


def next_card(repo, desc, color, status, cmd):
    """A private repo on its way out. Swap the lock for a link once it is public."""
    W, H = 280, 202
    s = Svg(W, H, f"{repo}, going open source soon, {status}. {desc} Python, MIT.")
    s.style("@keyframes lk{0%,45%{opacity:1}55%,92%{opacity:0}100%{opacity:1}}"
            "@keyframes ul{0%,45%{opacity:0}55%,92%{opacity:1}100%{opacity:0}}")
    card_shell(s, W, H, r=14, comet=False)
    s.rect(0, 0, W, 3, fill=color)
    m = 16
    s.add('<g style="animation:lk 7s ease infinite both">')
    s.icon("lock", m, 18, 17, C["muted"])
    s.add('</g><g style="opacity:0;animation:ul 7s ease infinite both">')
    s.icon("unlock", m, 18, 17, C["green"])
    s.add("</g>")
    s.text(m + 25, 32, repo, "mono7", 13.5, C["text"])
    s.para(m, 58, desc, W - 2 * m, "ui", 12.5, C["body"], lh=1.45, max_lines=4)
    # the command types itself
    by = 124
    s.rect(m, by, W - 2 * m, 28, 7, fill="#0a0d12", stroke=C["stroke"])
    line = "$ " + cmd
    cw = text_width("m", "mono", 11)
    full = len(line) * cw + 2
    clip = s.uid("nc")
    s.defs.append(f'<clipPath id="{clip}"><rect x="{m}" y="{by}" width="{W - 2 * m}" height="28" rx="7"/></clipPath>')
    s.style(f"@keyframes ty{{0%{{transform:translateX(0)}}36%,92%{{transform:translateX({full:.1f}px)}}100%{{transform:translateX({full:.1f}px)}}}}"
            "@keyframes bl{50%{opacity:0}}")
    s.add(f'<g clip-path="url(#{clip})">')
    s.text(m + 10, by + 18, line, "mono", 11, C["ice"])
    s.rect(m + 8, by + 2, full + 4, 24, fill="#0a0d12", extra=f'style="transform:translateX({full:.1f}px);animation:ty 9s steps({len(line)}) infinite"')
    s.add(f'<g style="transform:translateX({full:.1f}px);animation:ty 9s steps({len(line)}) infinite"><rect x="{m + 10}" y="{by + 7}" width="6" height="14" fill="{C["ice"]}" style="animation:bl 1s steps(1) infinite"/></g>')
    s.add("</g>")
    # footer
    fy = H - 20
    s.add(f'<circle cx="{m + 4}" cy="{fy - 4}" r="4" fill="{color}"/>')
    x = m + 13
    x += s.text(x, fy, "Python", "ui5", 12, C["body"]) + 10
    s.text(x, fy, "MIT", "ui", 12, C["muted"])
    s.text(W - m, fy, status, "mono5", 10.5, C["glow"], anchor="end")
    card_close(s, W, H, r=14, comet=False)
    return s


# ---------- activity: a year of commits as a mountain range --------------------

def activity(W):
    data = json.loads((ROOT / "data" / "github.json").read_text())
    weeks = data["weeks"]
    totals = [w["total"] for w in weeks]
    peak_i = max(range(len(totals)), key=lambda i: (totals[i], i))
    peak_date = date.fromisoformat(weeks[peak_i]["start"])
    active = data.get("active_days") or 0
    contrib = data.get("total_contributions")
    label = (f"The last 12 months of GitHub activity drawn as a mountain range, one point per week: {active} active days. "
             f"The busiest week started {peak_date:%B} {peak_date.day}, {peak_date.year}.")

    wide = W > 500
    H = 318 if wide else 360
    s = Svg(W, H, label)
    card_shell(s, W, H, comet=False)
    m = 22 if wide else 16
    s.style("@keyframes draw{0%{stroke-dashoffset:1}18%,92%{stroke-dashoffset:0}100%{stroke-dashoffset:0}}"
            "@keyframes rise2{0%,6%{opacity:0}22%,100%{opacity:1}}"
            "@keyframes wave{0%,100%{transform:skewY(0)}50%{transform:skewY(-9deg)}}")
    # headline stats
    y = 40
    stats = [(f"{active}", "active days")]
    if contrib:
        stats.insert(0, (f"{contrib:,}", "contributions"))
    stats.append((f"{peak_date:%b} {peak_date.day}", "busiest week"))
    x = m
    for value, name in stats:
        vw = s.text(x, y, value, "serif", 34, C["text"])
        s.text(x, y + 19, name, "mono5", 10.5, C["muted"], ls=.6)
        x += max(vw, text_width(name, "mono5", 10.5, .6)) + (36 if wide else 26)
    if wide:
        rx = W - m
        for name in ("YOLO", "Quickdraw", "Pull Shark x2", "Starstruck"):
            w = text_width(name, "ui5", 12) + 22
            rx -= w
            s.pill(rx, 22, name, "ui5", 12, fg=C["body"], bg=C["panel"], h=26)
            rx -= 6
    # the range
    top = 92 if wide else 84
    base = H - 44 if wide else H - 92
    cw = W - 2 * m
    n = len(totals)
    mx = max(totals) or 1

    def yv(v, k=1.0):
        return base - (base - top - 8) * k * (v / mx) ** .72

    pts = [(m + cw * i / (n - 1), yv(v)) for i, v in enumerate(totals)]
    back = []
    for i in range(n):
        a, b, c = totals[max(i - 2, 0)], totals[i], totals[min(i + 2, n - 1)]
        back.append((m + cw * i / (n - 1), yv((a + b + c) / 3, .86)))
    g1, g2 = s.uid("ag"), s.uid("ah")
    s.defs.append(f'<linearGradient id="{g1}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{C["glow"]}" stop-opacity=".95"/><stop offset=".55" stop-color="#7a5a8f" stop-opacity=".75"/><stop offset="1" stop-color="#17132b" stop-opacity=".9"/></linearGradient>')
    s.defs.append(f'<linearGradient id="{g2}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{C["ice"]}" stop-opacity=".55"/><stop offset="1" stop-color="{C["deep"]}" stop-opacity=".06"/></linearGradient>')

    def poly(p):
        return "M" + "L".join(f"{a:.1f} {b:.1f}" for a, b in p)

    area_back = poly(back) + f"L{back[-1][0]:.1f} {base}L{back[0][0]:.1f} {base}z"
    area = poly(pts) + f"L{pts[-1][0]:.1f} {base}L{pts[0][0]:.1f} {base}z"
    s.add(f'<path d="{area_back}" fill="url(#{g2})" style="animation:rise2 24s ease infinite both"/>')
    s.add(f'<path d="{area}" fill="url(#{g1})" style="animation:rise2 24s ease .3s infinite both"/>')
    s.add(f'<path d="{poly(pts)}" fill="none" stroke="#ffe2c7" stroke-width="1.6" stroke-linejoin="round" pathLength="1" stroke-dasharray="1 1" style="animation:draw 24s ease-out infinite both"/>')
    # snow on the high weeks
    cap_line = yv(mx * .5)
    sp = [(round(a, 1), b) for a, b in pts]
    s.add(f'<path d="{snow_path(13, sp, cap_line, jag=4)}" fill="#fff4ea" fill-opacity=".92" style="animation:rise2 24s ease .6s infinite both"/>')
    # a climber walks the ridge
    s.add(f'<circle r="4" fill="#fff"><animateMotion path="{poly(pts)}" dur="24s" repeatCount="indefinite" calcMode="linear"/></circle>')
    # flag on the highest summit
    px, py = pts[peak_i]
    s.add(f'<path d="M{px:.1f} {py:.1f}v-22" stroke="{C["text"]}" stroke-width="1.4"/>')
    for i, c in enumerate(FLAGS[:3]):
        fx = px + i * 9
        s.add(f'<rect x="{fx:.1f}" y="{py - 22:.1f}" width="8" height="10" rx="1" fill="{c}" style="transform-origin:{fx:.1f}px {py - 22:.1f}px;animation:wave 2.4s ease-in-out -{i * .3}s infinite"/>')
    # axis
    s.rect(m, base, cw, 1, fill=C["stroke"])
    last_m = None
    every = 2 if wide else 3
    shown = 0
    for i, w in enumerate(weeks):
        d = date.fromisoformat(w["start"])
        if d.month != last_m and d.day <= 7:
            last_m = d.month
            if shown % every == 0 and i < n - 2:
                s.text(m + cw * i / (n - 1), base + 18, f"{d:%b}", "mono", 10.5, C["dim"])
            shown += 1
    if not wide:
        rx = m
        ry = H - 58
        for name in ("Starstruck", "Pull Shark x2", "Quickdraw", "YOLO"):
            w = text_width(name, "ui5", 12) + 22
            if rx + w > W - m:
                rx = m
                ry += 30
            s.pill(rx, ry, name, "ui5", 12, fg=C["body"], bg=C["panel"], h=26)
            rx += w + 6
    card_close(s, W, H, dur=20)
    return s


# ---------- contact -----------------------------------------------------------

def message_bar(W):
    lines = "Message @bhuwan"
    H = 58
    s = Svg(W, H, "A chat box. Click to email Bhuwan.")
    s.rect(.5, .5, W - 1, H - 1, 12, fill=C["panel"], stroke=C["stroke"])
    s.add(f'<circle cx="31" cy="29" r="13" fill="{C["panel2"]}"/>')
    s.icon("plus", 23, 21, 16, C["body"], sw=2.2)
    text = "Message @bhuwan: full-time and internship roles welcome"
    if text_width(text, "ui", 14) > W - 120:
        text = "Message @bhuwan"
    s.text(56, 34, text, "ui", 14, C["muted"])
    tw = text_width(text, "ui", 14)
    s.style("@keyframes bl{50%{opacity:0}}@keyframes nudge{0%,80%,100%{transform:translateX(0)}88%{transform:translateX(5px)}}")
    s.add(f'<rect x="{58 + tw:.1f}" y="19" width="2" height="20" fill="{C["ice"]}" style="animation:bl 1.05s steps(1) infinite"/>')
    s.add('<g style="animation:nudge 5s ease-in-out infinite">')
    s.icon("send", W - 40, 18, 21, C["ice"], sw=1.9)
    s.add("</g>")
    return s


def button(label, icon, primary=False):
    H = 42
    tw = text_width(label, "ui6", 13.5)
    W = round(tw + 58)
    s = Svg(W, H, label)
    clip = s.uid("bt")
    s.defs.append(f'<clipPath id="{clip}"><rect width="{W}" height="{H}" rx="10"/></clipPath>')
    fill = C["deep"] if primary else C["panel"]
    s.rect(.5, .5, W - 1, H - 1, 10, fill=fill, stroke=C["deep"] if primary else C["stroke"])
    fg = "#ffffff" if primary else C["text"]
    s.icon(icon, 16, 13, 16, fg, sw=2)
    s.text(40, 26, label, "ui6", 13.5, fg)
    s.style(f"@keyframes sh{{0%,70%{{transform:translateX(-60px) skewX(-20deg)}}100%{{transform:translateX({W + 60}px) skewX(-20deg)}}}}")
    s.add(f'<g clip-path="url(#{clip})"><rect width="30" height="{H}" fill="#fff" fill-opacity=".15" style="transform:translateX(-60px);animation:sh 6s ease-in-out infinite"/></g>')
    return s
