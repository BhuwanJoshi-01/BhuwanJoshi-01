"""Shared animated pieces: the live-wallpaper banner, snowfall, the 3D signer."""
import math
import random

from svgkit import C, FLAGS, fmt, range_points, ridge_path, snow_path


def banner(s, W, H, cycle=34, seed=7):
    """Himalayan live wallpaper: night to alpenglow and back, with parallax ridges."""
    p = s.uid("b")
    s.style(
        "@keyframes dawn{0%,14%{opacity:0}36%,62%{opacity:1}84%,100%{opacity:0}}"
        "@keyframes night{0%,14%{opacity:1}36%,62%{opacity:0}84%,100%{opacity:1}}"
        "@keyframes drift{to{transform:translateX(var(--w))}}"
        "@keyframes tw{0%,100%{opacity:.25}50%{opacity:1}}"
        "@keyframes sun{0%,14%{transform:translateY(46px);opacity:0}40%,58%{transform:translateY(0);opacity:1}84%,100%{transform:translateY(46px);opacity:0}}"
        "@keyframes shoot{0%,88%{opacity:0;transform:translate(0,0)}89%{opacity:1}94%,100%{opacity:0;transform:translate(170px,62px)}}"
        "@keyframes sway{from{transform:rotate(-7deg) skewX(-4deg)}to{transform:rotate(7deg) skewX(5deg)}}"
        "@keyframes mist{from{transform:translateX(-90px)}to{transform:translateX(90px)}}"
    )
    s.style(f".dn{{opacity:0;animation:dawn {cycle}s ease-in-out infinite}}"
            f".nt{{animation:night {cycle}s ease-in-out infinite}}"
            ".dr{animation:drift linear infinite}"
            ".tw{animation:tw 3.2s ease-in-out infinite}"
            f".sn{{opacity:0;animation:sun {cycle}s ease-in-out infinite}}"
            ".fl{transform-box:fill-box;transform-origin:50% 0;animation:sway 2.6s ease-in-out infinite alternate}"
            ".ms{animation:mist 26s ease-in-out infinite alternate}")

    def grad(i, stops, y2=1):
        st = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
        s.defs.append(f'<linearGradient id="{i}" x1="0" y1="0" x2="0" y2="{y2}">{st}</linearGradient>')

    grad(p + "sky", [(0, "#050912"), (0.55, "#0c1a33"), (1, "#23406a")])
    grad(p + "skyd", [(0, "#1a2150"), (0.45, "#6a4f86"), (0.8, "#f08f78"), (1, "#ffc796")])
    grad(p + "far", [(0, "#4a6c96"), (1, "#14233b")])
    grad(p + "fard", [(0, "#ff9f82"), (0.5, "#8d5f8c"), (1, "#3b2f5f")])
    grad(p + "snw", [(0, "#eaf2fb"), (1, "#a9c1da")])
    grad(p + "snwd", [(0, "#fff0e0"), (1, "#ffb79a")])
    grad(p + "mid", [(0, "#1a2e4a"), (1, "#0c1626")])
    grad(p + "midd", [(0, "#4a3a68"), (1, "#20193a")])
    grad(p + "nea", [(0, "#0b1320"), (1, "#060a12")])
    grad(p + "nead", [(0, "#1c1633"), (1, "#0d0a1c")])
    s.defs.append(f'<radialGradient id="{p}sg"><stop offset="0" stop-color="#ffe2b8" stop-opacity=".95"/>'
                  f'<stop offset=".35" stop-color="#ffb58a" stop-opacity=".45"/><stop offset="1" stop-color="#ffb58a" stop-opacity="0"/></radialGradient>')
    s.defs.append(f'<radialGradient id="{p}mg"><stop offset="0" stop-color="#cfe0f2" stop-opacity=".3"/>'
                  '<stop offset="1" stop-color="#cfe0f2" stop-opacity="0"/></radialGradient>')

    # sky
    s.rect(0, 0, W, H, fill=f"url(#{p}sky)")
    s.rect(0, 0, W, H, fill=f"url(#{p}skyd)", extra='class="dn"')

    # stars and moon
    rng = random.Random(seed)
    stars = ['<g class="nt">']
    for i in range(int(W / 11)):
        x, y, r = rng.uniform(0, W), rng.uniform(4, H * 0.62), rng.choice([.6, .7, .8, 1, 1.3])
        cls = ' class="tw" style="animation-delay:-%.1fs"' % rng.uniform(0, 3.2) if i % 3 == 0 else ""
        stars.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="#fff"{cls}/>')
    mx, my = W * 0.79, H * 0.2
    stars.append(f'<circle cx="{mx:.0f}" cy="{my:.0f}" r="42" fill="url(#{p}mg)"/>')
    stars.append(f'<path d="M{mx + 7:.0f} {my - 12:.0f}a13 13 0 1 0 0 24a10.500 10.500 0 0 1 0-24z" fill="#dce8f5"/>')
    stars.append("</g>")
    s.add("".join(stars))

    # shooting star
    s.add(f'<g style="animation:shoot 17s linear infinite;opacity:0"><path d="M{W * .14:.0f} {H * .1:.0f}l52 19" stroke="#fff" stroke-width="1.6" stroke-linecap="round"/></g>')

    # sun behind the range at dawn
    s.add(f'<circle class="sn" cx="{W * .36:.0f}" cy="{H * .62:.0f}" r="{H * .62:.0f}" fill="url(#{p}sg)"/>')

    # far range with snow
    tile = 1500
    pts = range_points(seed + 1, tile, 4, H * 0.86, H * 0.74, peaks=8, jag=.13, sharp=1.1)
    far = ridge_path(pts, H)
    line = H * 0.42
    snow = snow_path(seed + 2, pts, line)
    idf = p + "F"
    s.defs.append(f'<g id="{idf}"><path d="{far}" fill="url(#{p}far)" stroke="url(#{p}far)"/><path d="{snow}" fill="url(#{p}snw)"/></g>')
    s.defs.append(f'<g id="{idf}d"><path d="{far}" fill="url(#{p}fard)" stroke="url(#{p}fard)"/><path d="{snow}" fill="url(#{p}snwd)"/></g>')
    s.add(f'<g class="dr" style="--w:-{tile}px;animation-duration:260s"><use href="#{idf}"/><use href="#{idf}" x="{tile}"/>'
          f'<g class="dn"><use href="#{idf}d"/><use href="#{idf}d" x="{tile}"/></g></g>')

    # mist band
    s.defs.append(f'<radialGradient id="{p}ms"><stop offset="0" stop-color="#d7e4f2" stop-opacity=".32"/><stop offset="1" stop-color="#d7e4f2" stop-opacity="0"/></radialGradient>')
    s.add(f'<g class="ms"><ellipse cx="{W * .3:.0f}" cy="{H * .73:.0f}" rx="{W * .34:.0f}" ry="{H * .1:.0f}" fill="url(#{p}ms)"/>'
          f'<ellipse cx="{W * .78:.0f}" cy="{H * .68:.0f}" rx="{W * .28:.0f}" ry="{H * .08:.0f}" fill="url(#{p}ms)"/></g>')

    # middle and near ranges
    for name, sd, base, amp, dur, pk in (("mid", 11, .98, .42, 170, 13), ("nea", 23, 1.03, .25, 105, 19)):
        ppts = range_points(seed + sd, tile, 5, H * base, H * amp, peaks=pk, jag=.12, sharp=1.0)
        d = ridge_path(ppts, H)
        i = p + name
        s.defs.append(f'<path id="{i}p" d="{d}"/>')
        s.add(f'<g class="dr" style="--w:-{tile}px;animation-duration:{dur}s">'
              f'<use href="#{i}p" fill="url(#{i})" stroke="url(#{i})"/><use href="#{i}p" x="{tile}" fill="url(#{i})" stroke="url(#{i})"/>'
              f'<g class="dn"><use href="#{i}p" fill="url(#{i}d)" stroke="url(#{i}d)"/><use href="#{i}p" x="{tile}" fill="url(#{i}d)" stroke="url(#{i}d)"/></g></g>')

    # prayer flags on a sagging line
    flags = []
    for ax, ay, bx, by, sag, n, off in (
        (-14, H * .03, W * .34, H * .42, H * .1, max(int(W / 62), 6), 0),
        (W * .67, H * .46, W + 14, H * .02, H * .1, max(int(W / 62), 6), 2),
    ):
        path_pts = []
        for i in range(n + 1):
            t = i / n
            path_pts.append((ax + (bx - ax) * t, ay + (by - ay) * t + sag * 4 * t * (1 - t)))
        flags.append('<path d="M' + "L".join(f"{x:.0f} {y:.0f}" for x, y in path_pts) + '" fill="none" stroke="#fff" stroke-opacity=".3"/>')
        for i, (x, y) in enumerate(path_pts[:-1]):
            c = FLAGS[(i + off) % 5]
            nx, ny = path_pts[i + 1]
            mx_, my_ = (x + nx) / 2, (y + ny) / 2
            flags.append(f'<rect class="fl" x="{mx_ - 5.500:.1f}" y="{my_:.1f}" width="11" height="14" rx="1" fill="{c}" fill-opacity=".9" '
                         f'style="animation-delay:-{(i * .37) % 2.6:.2f}s"/>')
    for px, py in ((W * .34, H * .42), (W * .67, H * .46)):
        flags.append(f'<path d="M{px:.0f} {py - 4:.0f}V{H}" stroke="#05080f" stroke-width="2"/>')
    s.add("<g>" + "".join(flags) + "</g>")


def snowfall(s, W, H, n=38, seed=3, opacity=.8):
    """The profile effect: slow snow drifting over the whole card."""
    s.style(f"@keyframes fa{{from{{transform:translate(0,-14px)}}50%{{transform:translate(22px,{H / 2:.0f}px)}}to{{transform:translate(-8px,{H + 14}px)}}}}"
            f"@keyframes fb{{from{{transform:translate(0,-14px)}}50%{{transform:translate(-26px,{H / 2:.0f}px)}}to{{transform:translate(12px,{H + 14}px)}}}}")
    rng = random.Random(seed)
    parts = []
    for i in range(n):
        x = rng.uniform(0, W)
        r = rng.choice([.9, 1.1, 1.4, 1.8, 2.2])
        dur = rng.uniform(13, 26) * (2.2 / r) ** .35
        parts.append(f'<circle cx="{x:.0f}" r="{r}" fill="#fff" fill-opacity="{rng.uniform(.3, opacity):.2f}" '
                     f'style="animation:{"fa" if i % 2 else "fb"} {dur:.1f}s linear -{rng.uniform(0, dur):.1f}s infinite"/>')
    s.add('<g class="snowfx">' + "".join(parts) + "</g>")
    s.style("@media (prefers-reduced-motion:reduce){.snowfx{display:none}}")


# ---------- a little 3D signer, projected to 2D frames ----------------------

def _rot_y(p, a):
    x, y, z = p
    return (x * math.cos(a) + z * math.sin(a), y, -x * math.sin(a) + z * math.cos(a))


def _arm(shoulder, a1, a2, a3, side, t):
    """Forward kinematics for one arm. Angles in radians."""
    sx, sy, sz = shoulder
    ua, fa = 0.62, 0.56
    elbow = (sx + side * ua * math.sin(a1), sy - ua * math.cos(a1) * math.cos(a2), sz + ua * math.cos(a1) * math.sin(a2))
    hand_dir = (side * math.sin(a3), math.cos(a3), .55)
    n = math.sqrt(sum(v * v for v in hand_dir))
    hand_dir = tuple(v / n for v in hand_dir)
    wrist = tuple(e + fa * h for e, h in zip(elbow, hand_dir))
    fingers = []
    for k, spread in enumerate((-.55, -.18, .18, .55)):
        wiggle = .16 * math.sin(t * 2 * math.pi * 2 + k)
        ang = a3 + spread + wiggle
        d = (side * math.sin(ang), math.cos(ang), .35)
        ln = .24 if k in (1, 2) else .2
        fingers.append(tuple(w + ln * v for w, v in zip(wrist, d)))
    return elbow, wrist, fingers


def signer_frames(size=72, frames=30):
    """Returns (bones_d values, joints_d values) for SMIL path animation."""
    bones, joints = [], []
    k = size / 3.1
    cx, cy = size / 2, size * .54

    def proj(p, a):
        x, y, z = _rot_y(p, a)
        persp = 1 / (1 - z * .12)
        return (round(cx + x * k * persp, 1), round(cy - y * k * persp, 1))

    for f in range(frames + 1):
        t = (f % frames) / frames
        turn = .55 * math.sin(2 * math.pi * t)
        neck = (0, .72, 0)
        head = (0, 1.08, 0)
        hip = (0, -.72, 0)
        ls, rs = (-.42, .62, 0), (.42, .62, 0)
        wave = 2 * math.pi * t
        lel, lwr, lf = _arm(ls, .55 + .25 * math.sin(wave), 1.05 + .3 * math.sin(wave * 2), .55 + .45 * math.sin(wave + 1), -1, t)
        rel, rwr, rf = _arm(rs, .55 + .25 * math.cos(wave), 1.05 + .3 * math.cos(wave * 2), .55 + .45 * math.cos(wave), 1, t)
        segs = [(neck, hip), (ls, rs), (ls, lel), (lel, lwr), (rs, rel), (rel, rwr)]
        segs += [(lwr, q) for q in lf] + [(rwr, q) for q in rf]
        d = "".join("M{} {}L{} {}".format(*proj(a, turn), *proj(b, turn)) for a, b in segs)
        bones.append(d)
        pts = [ls, rs, lel, rel, lwr, rwr, neck, hip]
        jd = "".join("M{} {}l0 0".format(*proj(q, turn)) for q in pts)
        joints.append(jd)
        hx, hy = proj(head, turn)
        joints[-1] += ""
        bones[-1] = (bones[-1], (hx, hy))
    return bones, joints


def signer(s, x, y, size=72, dur=9, color=None, frames=26):
    """Draws the signer at x,y. Animated through SMIL path morphing."""
    bones, joints = signer_frames(size, frames)
    color = color or C["ice"]
    b_vals = ";".join(b[0] for b in bones)
    j_vals = ";".join(joints)
    cx_vals = ";".join(str(b[1][0]) for b in bones)
    cy_vals = ";".join(str(b[1][1]) for b in bones)
    r = size * .1
    s.add(f'<g transform="translate({fmt(x, y)})">'
          f'<path d="{bones[0][0]}" fill="none" stroke="{color}" stroke-width="{fmt(round(size * .022, 2))}" stroke-linecap="round">'
          f'<animate attributeName="d" values="{b_vals}" dur="{dur}s" repeatCount="indefinite"/></path>'
          f'<path d="{joints[0]}" fill="none" stroke="{C["glow"]}" stroke-width="{fmt(round(size * .05, 2))}" stroke-linecap="round">'
          f'<animate attributeName="d" values="{j_vals}" dur="{dur}s" repeatCount="indefinite"/></path>'
          f'<circle cx="{bones[0][1][0]}" cy="{bones[0][1][1]}" r="{fmt(round(r, 2))}" fill="none" stroke="{color}" stroke-width="{fmt(round(size * .024, 2))}">'
          f'<animate attributeName="cx" values="{cx_vals}" dur="{dur}s" repeatCount="indefinite"/>'
          f'<animate attributeName="cy" values="{cy_vals}" dur="{dur}s" repeatCount="indefinite"/></circle></g>')


def card_shell(s, W, H, r=18, comet=True, stroke=None):
    """Card surface, clip and a light that runs around the border."""
    clip = s.uid("c")
    s.defs.append(f'<clipPath id="{clip}"><rect width="{W}" height="{H}" rx="{r}"/></clipPath>')
    s.add(f'<g clip-path="url(#{clip})">')
    s.rect(0, 0, W, H, fill=C["card"])
    return clip


def card_close(s, W, H, r=18, comet=True, dur=11):
    s.add("</g>")
    s.rect(.5, .5, W - 1, H - 1, r - .5, stroke=C["stroke"])
    if comet:
        g = s.uid("g")
        s.defs.append(f'<linearGradient id="{g}" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{W}" y2="{H}">'
                      f'<stop offset="0" stop-color="{C["ice"]}"/><stop offset=".55" stop-color="{C["glow"]}"/><stop offset="1" stop-color="{C["rose"]}"/></linearGradient>')
        s.style("@keyframes run{to{stroke-dashoffset:-100}}")
        s.add(f'<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="{r - .75}" fill="none" stroke="url(#{g})" stroke-width="1.5" '
              f'pathLength="100" stroke-dasharray="16 84" stroke-linecap="round" style="animation:run {dur}s linear infinite"/>')
