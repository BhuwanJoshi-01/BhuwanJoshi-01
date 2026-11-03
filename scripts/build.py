#!/usr/bin/env python3
"""Generates every animated card in assets/. Run: python scripts/build.py"""
import json
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import cards  # noqa: E402
from scene import banner, card_close, card_shell, signer, snowfall  # noqa: E402
from svgkit import C, FLAGS, Svg, data_uri, fmt, range_points, ridge_path, text_width, wrap  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
AVATAR = Path(__file__).parent / "avatar.jpg"

STATUS_LINES = ["building 3D signing avatars", "live wallpapers on Wayland", "open to full-time roles"]


# ---------- hero: the profile card -------------------------------------------

def typed_status(s, x, y, lines, size=13, cycle=18, clip=None, bg=None):
    """Mono-spaced typewriter cycling through status lines."""
    bg = bg or C["card"]
    cw = text_width("m", "mono", size)
    n = len(lines)
    for i, line in enumerate(lines):
        c = len(line)
        a, b = i / n * 100, (i + 1) / n * 100
        tw = (b - a) * .42
        full = c * cw + 2
        vis = (f"@keyframes v{i}{{" + ("0%" if i == 0 else f"0%,{a - .01:.2f}%{{opacity:0}}{a:.2f}%") +
               f",{b - .5:.2f}%{{opacity:1}}{b:.2f}%,100%{{opacity:0}}}}")
        start = "0%" if i == 0 else f"0%,{a:.2f}%"
        cov = (f"@keyframes t{i}{{{start}{{transform:translateX(0);animation-timing-function:steps({c})}}"
               f"{a + tw:.2f}%,100%{{transform:translateX({full:.1f}px)}}}}")
        s.style(vis + cov)
        base = "" if i == 0 else "opacity:0;"
        s.add(f'<g style="{base}animation:v{i} {cycle}s linear infinite">')
        s.text(x, y, line, "mono", size, C["body"])
        s.rect(x - 1, y - size - 2, full + 3, size * 1.6, fill=bg,
               extra=f'style="transform:translateX({full:.1f}px);animation:t{i} {cycle}s infinite"')
        s.add(f'<g style="transform:translateX({full:.1f}px);animation:t{i} {cycle}s infinite">'
              f'<rect class="caret" x="{x:.1f}" y="{y - size + 1:.1f}" width="2" height="{size + 2}" fill="{C["ice"]}"/></g>')
        s.add("</g>")
    s.style("@keyframes bl{50%{opacity:0}}.caret{animation:bl 1s steps(1) infinite}")


def avatar(s, cx, cy, r, ring_bg):
    """Avatar with an animated decoration, the way Discord profiles have them."""
    clip = s.uid("av")
    s.defs.append(f'<clipPath id="{clip}"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath>')
    g = s.uid("rg")
    s.defs.append(f'<linearGradient id="{g}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{C["ice"]}"/>'
                  f'<stop offset=".5" stop-color="{C["glow"]}"/><stop offset="1" stop-color="{C["rose"]}"/></linearGradient>')
    s.style("@keyframes spin{to{transform:rotate(360deg)}}@keyframes spinr{to{transform:rotate(-360deg)}}"
            "@keyframes pulse{0%{opacity:.8;transform:scale(1)}70%,100%{opacity:0;transform:scale(2.3)}}"
            "@keyframes spark{0%,100%{opacity:.25;transform:scale(.6)}50%{opacity:1;transform:scale(1.1)}}"
            f".orb{{transform-origin:{cx}px {cy}px}}")
    s.add(f'<circle cx="{cx}" cy="{cy}" r="{r + 8}" fill="{ring_bg}"/>')
    s.add(f'<image href="{data_uri(AVATAR, "image/jpeg")}" x="{cx - r}" y="{cy - r}" width="{r * 2}" height="{r * 2}" clip-path="url(#{clip})"/>')
    # gradient ring
    s.add(f'<circle class="orb" cx="{cx}" cy="{cy}" r="{r + 4}" fill="none" stroke="url(#{g})" stroke-width="3.2" stroke-linecap="round" '
          f'stroke-dasharray="{(r + 4) * 4.2:.0f} {(r + 4) * 2.08:.0f}" style="animation:spin 7s linear infinite"/>')
    # orbiting prayer-flag beads
    beads = "".join(f'<circle cx="{cx + (r + 13)}" cy="{cy}" r="3" fill="{c}" transform="rotate({i * 72} {cx} {cy})"/>' for i, c in enumerate(FLAGS))
    s.add(f'<g class="orb" style="animation:spinr 18s linear infinite">{beads}</g>')
    s.add(f'<circle class="orb" cx="{cx}" cy="{cy}" r="{r + 13}" fill="none" stroke="#fff" stroke-opacity=".22" stroke-dasharray="1 7" stroke-linecap="round" '
          f'style="animation:spin 40s linear infinite"/>')
    # sparkles
    for i, (dx, dy, k) in enumerate(((-.93, -.74, 1), (1.02, -.66, .75), (-1.14, .32, .6))):
        px, py = cx + dx * r, cy + dy * r
        q = 7 * k
        s.add(f'<path d="M{px:.1f} {py - q:.1f}Q{px:.1f} {py:.1f} {px + q:.1f} {py:.1f}Q{px:.1f} {py:.1f} {px:.1f} {py + q:.1f}Q{px:.1f} {py:.1f} {px - q:.1f} {py:.1f}Q{px:.1f} {py:.1f} {px:.1f} {py - q:.1f}z" '
              f'fill="#fff" style="transform-origin:{px:.1f}px {py:.1f}px;animation:spark {2.4 + i * .7}s ease-in-out -{i * .8}s infinite"/>')
    # online status
    ox, oy = cx + r * .72, cy + r * .72
    s.add(f'<circle cx="{ox:.1f}" cy="{oy:.1f}" r="13" fill="{ring_bg}"/>'
          f'<circle cx="{ox:.1f}" cy="{oy:.1f}" r="8.5" fill="{C["online"]}" style="transform-origin:{ox:.1f}px {oy:.1f}px;animation:pulse 2.4s ease-out infinite"/>'
          f'<circle cx="{ox:.1f}" cy="{oy:.1f}" r="8.5" fill="{C["online"]}"/>')


def badge_tray(s, right, y):
    """Achievement icons, right aligned. Returns its left edge."""
    icons = ["branch", "star", "fin", "bolt", "die"]
    w = 12 + len(icons) * 26
    x = right - w
    clip = s.uid("tr")
    s.defs.append(f'<clipPath id="{clip}"><rect x="{x}" y="{y}" width="{w}" height="34" rx="10"/></clipPath>')
    s.rect(x, y, w, 34, 10, fill=C["panel"], stroke=C["stroke"])
    colors = [C["ice"], C["yellow"], C["blue"], C["glow"], C["rose"]]
    for i, (name, c) in enumerate(zip(icons, colors)):
        s.icon(name, x + 10 + i * 26, y + 8, 18, c)
    s.style("@keyframes shine{0%,72%{transform:translateX(-60px)}100%{transform:translateX(220px)}}")
    s.add(f'<g clip-path="url(#{clip})"><rect x="{x}" y="{y}" width="26" height="34" fill="#fff" fill-opacity=".14" '
          f'style="transform:translateX(-60px) skewX(-18deg);animation:shine 7s ease-in-out infinite"/></g>')
    return x


def presence(s, x, y, w, label, title, sub, meta, kind):
    """A rich-presence panel. Height 104."""
    s.rect(x, y, w, 104, 12, fill=C["panel"], stroke=C["stroke"])
    s.text(x + 14, y + 22, label, "mono5", 10.5, C["ice"], ls=1.1)
    tile = 62
    tx, ty = x + 14, y + 32
    s.rect(tx, ty, tile, tile, 10, fill="#0a0d12", stroke=C["stroke"])
    clip = s.uid("pt")
    s.defs.append(f'<clipPath id="{clip}"><rect x="{tx}" y="{ty}" width="{tile}" height="{tile}" rx="10"/></clipPath>')
    s.add(f'<g clip-path="url(#{clip})">')
    if kind == "signer":
        signer(s, tx + 1, ty + 1, tile - 2, dur=9)
    else:
        mini_wall(s, tx, ty, tile, tile)
    s.add("</g>")
    bx = tx + tile + 12
    s.text(bx, y + 46, title, "ui6", 14.5, C["text"])
    yy = y + 64
    for line in wrap(sub, "ui", 12, w - tile - 40)[:2]:
        s.text(bx, yy, line, "ui", 12, C["body"])
        yy += 16
    if yy < y + 92:
        s.text(bx, yy, meta, "mono", 10.5, C["muted"])


def mini_wall(s, x, y, w, h):
    """A pocket-sized wallpaper, for icons."""
    g = s.uid("mw")
    s.defs.append(f'<linearGradient id="{g}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#16244a"/><stop offset=".65" stop-color="#7a5a8f"/><stop offset="1" stop-color="#f7a585"/></linearGradient>')
    s.rect(x, y, w, h, fill=f"url(#{g})")
    tile = 180
    pts = range_points(41, tile, 3, y + h * .96, h * .66, peaks=4, jag=.1)
    d = ridge_path(pts, y + h)
    pts2 = range_points(42, tile, 3, y + h * 1.02, h * .38, peaks=5, jag=.1)
    d2 = ridge_path(pts2, y + h)
    s.style("@keyframes drift{to{transform:translateX(var(--w))}}")
    s.add(f'<g transform="translate({x} 0)"><g style="--w:-{tile}px;animation:drift 22s linear infinite"><path d="{d}" fill="#3b3a66" stroke="#3b3a66"/><path d="{d}" transform="translate({tile} 0)" fill="#3b3a66" stroke="#3b3a66"/></g></g>')
    s.add(f'<g transform="translate({x} 0)"><g style="--w:-{tile}px;animation:drift 12s linear infinite"><path d="{d2}" fill="#101428" stroke="#101428"/><path d="{d2}" transform="translate({tile} 0)" fill="#101428" stroke="#101428"/></g></g>')


def field(s, x, y, label, value, key="ui5", size=13.5, color=None):
    s.text(x, y, label, "mono5", 10, C["muted"], ls=1)
    s.text(x, y + 19, value, key, size, color or C["text"])


def hero_body(s, W, H, wide):
    BN = 196 if wide else 148
    card_shell(s, W, H)
    banner(s, W, BN)
    r = 70 if wide else 54
    cx, cy = (104 if wide else 82), BN + 2
    s.rect(0, BN, W, H - BN, fill=C["card"])

    # status bubble, floating off the avatar
    size = 13 if wide else 12
    bx, by, bh = (192 if wide else 150), BN - (58 if wide else 56), 38 if wide else 34
    lines = STATUS_LINES
    bw = 34 + text_width("m", "mono", size) * max(len(x) for x in lines)
    s.add(f'<circle cx="{bx - 8}" cy="{by + bh + 2}" r="6" fill="{C["card"]}"/><circle cx="{bx - 19}" cy="{by + bh + 11}" r="3.5" fill="{C["card"]}"/>')
    clip = s.uid("bb")
    s.defs.append(f'<clipPath id="{clip}"><rect x="{bx}" y="{by}" width="{bw:.0f}" height="{bh}" rx="{bh / 2}"/></clipPath>')
    s.rect(bx, by, bw, bh, bh / 2, fill=C["card"], stroke=C["stroke"])
    s.add(f'<g clip-path="url(#{clip})">')
    typed_status(s, bx + 17, by + (24 if wide else 21), lines, size=size)
    s.add("</g>")

    avatar(s, cx, cy, r, C["card"])
    badge_tray(s, W - (28 if wide else 18), BN + (14 if wide else 12))

    # identity
    nx = 34 if wide else 20
    ny = BN + (130 if wide else 106)
    nw = s.text(nx, ny, "Bhuwan Joshi", "serif", 50 if wide else 44, C["text"])
    s.text(nx + nw + 12, ny - 3, "भुवन जोशी", "deva", 19 if wide else 16, C["muted"])
    s.text(nx + 1, ny + 25, "BhuwanJoshi-01", "mono5", 13, C["ice"])
    hw = text_width("BhuwanJoshi-01", "mono5", 13)
    s.add(f'<circle cx="{nx + hw + 12:.0f}" cy="{ny + 21}" r="2" fill="{C["dim"]}"/>')
    s.icon("pin", nx + hw + 20, ny + 13, 14, C["muted"])
    s.text(nx + hw + 38, ny + 25, "Kathmandu, Nepal", "ui", 13, C["muted"])

    # about
    aw = 410 if wide else W - 2 * nx
    s.rect(nx, ny + 44, aw, 1, fill=C["stroke"])
    s.text(nx, ny + 66, "ABOUT ME", "mono5", 10.5, C["muted"], ls=1.1)
    y = s.para(nx, ny + 88, "Junior AI Developer at Prateek Innovations and Development Intern at RAIN. I build "
               "end-to-end products across web, mobile and 3D, from sign-language avatars to the Linux tools I wish already existed.",
               aw, "ui", 14.5 if wide else 14, C["body"], lh=1.45)

    # roles
    px = nx
    y += 0
    for label, c in (("AI + 3D", C["red"]), ("React Native", C["blue"]), ("TypeScript", C["blue"]), ("Python", C["red"])):
        if px + text_width(label, "ui5", 12.5) + 36 > nx + aw:
            break
        px += s.pill(px, y, label, dot=c) + 6
    left_end = y + 44

    # right column on desktop, stacked on mobile
    if wide:
        rx, rw = 484, W - 484 - 28
        py = BN + 62
    else:
        rx, rw = nx, W - 2 * nx
        py = y + 42
    presence(s, rx, py, rw, "BUILDING AT WORK", "SETU", "Speech and text to Nepali Sign Language, performed by a 3D signer.", "", "signer")
    presence(s, rx, py + 114, rw, "LATEST OPEN SOURCE", "wayland-wallpaperengine", "Steam Wallpaper Engine wallpapers as a live desktop on Wayland, GNOME included.", "", "wall")
    fy = py + 114 + 104 + 12
    field(s, rx + 2, fy + 8, "BUILDING SINCE", "2022")
    field(s, rx + 2 + (118 if wide else 110), fy + 8, "LOOKING FOR", "Full-time and internship roles", size=12.5)
    end = max(left_end, fy + 40)

    snowfall(s, W, H, n=30 if wide else 22, opacity=.65)
    card_close(s, W, H)
    return end


def hero():
    label = "Profile card for Bhuwan Joshi: Junior AI Developer at Prateek Innovations and Development Intern at RAIN, in Kathmandu, Nepal. Animated Himalayan banner with prayer flags."
    h = hero_body(Svg(900, 900, label), 900, 900, True)
    s = Svg(900, round(h), label)
    hero_body(s, 900, round(h), True)
    return s


def hero_mobile():
    label = "Profile card for Bhuwan Joshi: Junior AI Developer at Prateek Innovations and Development Intern at RAIN, in Kathmandu, Nepal."
    h = hero_body(Svg(420, 1200, label), 420, 1200, False)
    s = Svg(420, round(h), label)
    hero_body(s, 420, round(h), False)
    return s


BUILDERS = {
    "hero": hero, "hero-mobile": hero_mobile,
    "experience": lambda: cards.experience(900), "experience-mobile": lambda: cards.experience(420),
    "stack": lambda: cards.stack(900), "stack-mobile": lambda: cards.stack(420),
    "oss-wwe": lambda: cards.oss_wwe(900), "oss-wwe-mobile": lambda: cards.oss_wwe(420),
    "activity": lambda: cards.activity(900), "activity-mobile": lambda: cards.activity(420),
    "message": lambda: cards.message_bar(900), "message-mobile": lambda: cards.message_bar(420),
    "btn-portfolio": lambda: cards.button("Portfolio", "globe", primary=True),
    "btn-linkedin": lambda: cards.button("LinkedIn", "link"),
    "btn-email": lambda: cards.button("Email", "mail"),
}
for _name, _cfg in cards.GOING_PUBLIC.items():
    BUILDERS[_name] = (lambda c: lambda: cards.next_card(**c))(_cfg)
for _name, _cfg in {**cards.OSS_CARDS, **cards.WORK_CARDS}.items():
    BUILDERS[_name] = (lambda c: lambda: cards.embed(None, **c))(_cfg)


def main(names):
    OUT.mkdir(exist_ok=True)
    total = 0
    for name, fn in BUILDERS.items():
        if names and name not in names:
            continue
        s = fn()
        size = s.save(OUT / f"{name}.svg")
        total += size
        print(f"{name:<22}{s.w:>4}x{s.h:<5}{size / 1024:8.1f} KB")
    print(f"{'total':<32}{total / 1024:8.1f} KB")


if __name__ == "__main__":
    main(sys.argv[1:])
