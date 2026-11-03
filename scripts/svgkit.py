"""Tiny SVG toolkit for GitHub READMEs.

GitHub shows repo SVGs through <img>, so nothing inside them can load external
files or run scripts. Text is therefore shaped with HarfBuzz and written as
glyph outlines: it looks identical everywhere and needs no web fonts.
"""
import base64
import io
import random
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.basePen import BasePen
from fontTools.ttLib import TTFont

HERE = Path(__file__).parent
FONT_FILES = {
    "serif": "instrument-serif-latin-400-normal.woff2",
    "serif-i": "instrument-serif-latin-400-italic.woff2",
    "ui": "inter-latin-400-normal.woff2",
    "ui5": "inter-latin-500-normal.woff2",
    "ui6": "inter-latin-600-normal.woff2",
    "ui7": "inter-latin-700-normal.woff2",
    "mono": "jetbrains-mono-latin-400-normal.woff2",
    "mono5": "jetbrains-mono-latin-500-normal.woff2",
    "mono7": "jetbrains-mono-latin-700-normal.woff2",
    "deva": "noto-sans-devanagari-devanagari-500-normal.woff2",
}

# Palette. Surfaces and ice blue follow the portfolio; the rest is prayer flags.
C = dict(
    card="#0e1116", panel="#161b22", panel2="#1c222b", stroke="#262d38",
    text="#f2f4f7", body="#c3cbd6", muted="#8b95a5", dim="#5f6977",
    ice="#89aacc", deep="#4e85bf", glow="#f4a97f", rose="#e8728a",
    online="#23a55a",
    blue="#5b9bd5", white="#e8edf3", red="#e5534b", green="#3fb950", yellow="#e3b341",
)
FLAGS = [C["blue"], C["white"], C["red"], C["green"], C["yellow"]]


def fmt(*nums):
    out = ""
    for n in nums:
        s = f"{n:.2f}".rstrip("0").rstrip(".") if isinstance(n, float) else str(n)
        if s == "-0":
            s = "0"
        out += s if (not out or s.startswith("-")) else " " + s
    return out


class _RelPen(BasePen):
    """Writes glyph outlines as compact, integer, relative path data."""

    def __init__(self, glyph_set):
        super().__init__(glyph_set)
        self.d = []
        self.x = self.y = 0
        self.sx = self.sy = 0

    def _moveTo(self, p):
        self.x, self.y = round(p[0]), round(p[1])
        self.sx, self.sy = self.x, self.y
        self.d.append(f"M{self.x} {self.y}")

    def _lineTo(self, p):
        x, y = round(p[0]), round(p[1])
        self.d.append("l" + fmt(x - self.x, y - self.y))
        self.x, self.y = x, y

    def _qCurveToOne(self, p1, p2):
        x1, y1, x, y = round(p1[0]), round(p1[1]), round(p2[0]), round(p2[1])
        self.d.append("q" + fmt(x1 - self.x, y1 - self.y, x - self.x, y - self.y))
        self.x, self.y = x, y

    def _curveToOne(self, p1, p2, p3):
        vals = [round(v) for p in (p1, p2, p3) for v in p]
        self.d.append("c" + fmt(vals[0] - self.x, vals[1] - self.y, vals[2] - self.x,
                                vals[3] - self.y, vals[4] - self.x, vals[5] - self.y))
        self.x, self.y = vals[4], vals[5]

    def _closePath(self):
        self.d.append("z")
        self.x, self.y = self.sx, self.sy


class _Font:
    def __init__(self, key):
        tt = TTFont(HERE / "fonts" / FONT_FILES[key])
        tt.flavor = None
        buf = io.BytesIO()
        tt.save(buf)
        self.tt = TTFont(io.BytesIO(buf.getvalue()))
        self.glyphs = self.tt.getGlyphSet()
        self.upm = self.tt["head"].unitsPerEm
        self.hb = hb.Font(hb.Face(buf.getvalue()))
        self.mono = key.startswith("mono")
        self.key = key
        self.paths = {}

    def shape(self, text):
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        feats = {"calt": False, "liga": False} if self.mono else {}
        hb.shape(self.hb, buf, feats)
        return [(i.codepoint, p.x_advance, p.x_offset, p.y_offset)
                for i, p in zip(buf.glyph_infos, buf.glyph_positions)]

    def outline(self, gid):
        if gid not in self.paths:
            pen = _RelPen(self.glyphs)
            self.glyphs[self.tt.getGlyphName(gid)].draw(pen)
            self.paths[gid] = "".join(pen.d)
        return self.paths[gid]


_fonts = {}


def font(key):
    if key not in _fonts:
        _fonts[key] = _Font(key)
    return _fonts[key]


def _runs(text, key):
    """Devanagari font only holds Devanagari, so Latin punctuation falls to Inter."""
    if key != "deva":
        return [(text, key)]
    runs = []
    for ch in text:
        k = "deva" if 0x0900 <= ord(ch) <= 0x097F or ch in "‌‍" else "ui5"
        if runs and runs[-1][1] == k:
            runs[-1][0] += ch
        else:
            runs.append([ch, k])
    return [tuple(r) for r in runs]


def text_width(text, key="ui", size=14, ls=0):
    total = 0.0
    for run, k in _runs(text, key):
        f = font(k)
        shaped = f.shape(run)
        for g in shaped:
            if g[0] == 0:
                raise ValueError(f"glyph missing in {k}: {run!r}")
        total += sum(g[1] for g in shaped) * size / f.upm + ls * len(shaped)
    return total


def wrap(text, key, size, width):
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if text_width(trial, key, size) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


class Svg:
    def __init__(self, w, h, label):
        self.w, self.h, self.label = w, h, label
        self.css, self.defs, self.body = [], [], []
        self.glyph_ids = {}
        self._uid = 0

    def uid(self, prefix="u"):
        self._uid += 1
        return f"{prefix}{self._uid}"

    def add(self, s):
        self.body.append(s)
        return self

    def style(self, s):
        if s not in self.css:
            self.css.append(s)

    def _glyph(self, key, gid):
        k = (key, gid)
        if k not in self.glyph_ids:
            gid_name = f"g{len(self.glyph_ids):x}"
            self.glyph_ids[k] = gid_name
            self.defs.append(f'<path id="{gid_name}" d="{font(key).outline(gid)}"/>')
        return self.glyph_ids[k]

    def text(self, x, y, s, key="ui", size=14, fill=None, anchor="start", ls=0, cls=None, opacity=None):
        """Draws text as outlines and returns its width."""
        fill = fill or C["text"]
        w = text_width(s, key, size, ls)
        if anchor == "end":
            x -= w
        elif anchor == "middle":
            x -= w / 2
        attrs = f' fill="{fill}"'
        if cls:
            attrs += f' class="{cls}"'
        if opacity is not None:
            attrs += f' opacity="{opacity}"'
        cursor = x
        parts = []
        for run, k in _runs(s, key):
            f = font(k)
            scale = size / f.upm
            pen = 0
            uses = []
            for gid, adv, ox, oy in f.shape(run):
                if f.outline(gid):
                    gx = pen + ox
                    y_attr = f' y="{oy}"' if oy else ""
                    uses.append(f'<use href="#{self._glyph(k, gid)}" x="{gx}"{y_attr}/>')
                pen += adv + (ls / scale)
            pen = round(pen)
            parts.append(f'<g transform="translate({fmt(round(cursor, 2), round(y, 2))}) '
                         f'scale({scale:.5f} {-scale:.5f})">{"".join(uses)}</g>')
            cursor += pen * scale
        self.add(f'<g{attrs}>{"".join(parts)}</g>')
        return w

    def para(self, x, y, s, width, key="ui", size=14, fill=None, lh=1.5, cls=None, max_lines=None):
        """Word-wrapped paragraph. Returns the y of the next line."""
        lines = wrap(s, key, size, width)
        if max_lines and len(lines) > max_lines:
            raise ValueError(f"text needs {len(lines)} lines, limit {max_lines}: {s}")
        for line in lines:
            self.text(x, y, line, key, size, fill or C["body"], cls=cls)
            y += size * lh
        return y

    def spans(self, x, y, parts, width, size=14, lh=1.5):
        """Mixed-style text with word wrap. parts = [(text, font, color), ...]. Returns next y."""
        cx = x
        space = {}
        for chunk, key, color in parts:
            words = chunk.split(" ")
            for i, word in enumerate(words):
                if word == "":
                    continue
                w = text_width(word, key, size)
                sp = space.setdefault(key, text_width("a a", key, size) - text_width("aa", key, size))
                if cx + w > x + width and cx > x:
                    cx = x
                    y += size * lh
                self.text(cx, y, word, key, size, color)
                cx += w + sp
        return y + size * lh

    def rect(self, x, y, w, h, r=0, fill="none", stroke=None, sw=1, extra=""):
        s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        rr = f' rx="{r}"' if r else ""
        self.add(f'<rect x="{fmt(x)}" y="{fmt(y)}" width="{fmt(w)}" height="{fmt(h)}"{rr} fill="{fill}"{s} {extra}/>')

    def pill(self, x, y, label, key="ui5", size=12.5, fg=None, bg=None, stroke=None, h=26, pad=11, dot=None, cls=None, hollow=False):
        """A role-style pill. Returns its width."""
        tw = text_width(label, key, size)
        dotw = 14 if dot else 0
        w = tw + pad * 2 + dotw
        g = f'<g class="{cls}">' if cls else "<g>"
        self.add(g)
        self.rect(x, y, w, h, h / 2, fill=bg or C["panel2"], stroke=stroke or C["stroke"])
        if dot:
            if hollow:
                self.add(f'<circle cx="{fmt(x + pad + 4)}" cy="{fmt(y + h / 2)}" r="3.5" fill="none" stroke="{dot}" stroke-width="1.5"/>')
            else:
                self.add(f'<circle cx="{fmt(x + pad + 4)}" cy="{fmt(y + h / 2)}" r="4.5" fill="{dot}"/>')
        self.text(x + pad + dotw, y + h / 2 + size * 0.36, label, key, size, fg or C["text"])
        self.add("</g>")
        return w

    def icon(self, name, x, y, size=16, color=None, sw=1.8):
        d = ICONS[name]
        k = size / 24
        self.add(f'<path transform="translate({fmt(x, y)}) scale({k:.4f})" d="{d}" fill="none" '
                 f'stroke="{color or C["muted"]}" stroke-width="{fmt(round(sw / k, 2))}" stroke-linecap="round" stroke-linejoin="round"/>')

    def render(self):
        css = "".join(self.css)
        css += "@media (prefers-reduced-motion:reduce){*{animation:none!important}.smil{display:none}.still{display:inline!important}}"
        defs = "".join(self.defs)
        label = self.label.replace("&", "&amp;").replace("<", "&lt;").replace('"', "&quot;")
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
                f'viewBox="0 0 {self.w} {self.h}" role="img" aria-label="{label}">'
                f"<title>{label}</title><style>{css}</style><defs>{defs}</defs>{''.join(self.body)}</svg>")

    def save(self, path):
        data = self.render()
        Path(path).write_text(data, encoding="utf-8")
        return len(data)


ICONS = {
    "hash": "M4 9h16M4 15h16M10 3 8 21M16 3l-2 18",
    "branch": "M6 3v12M18 9a3 3 0 1 0 0-6 3 3 0 0 0 0 6ZM6 21a3 3 0 1 0 0-6 3 3 0 0 0 0 6ZM18 9a9 9 0 0 1-9 9",
    "star": "m12 3 2.8 5.7 6.2.9-4.5 4.4 1.1 6.2L12 17.3 6.4 20.2l1.1-6.2L3 9.6l6.2-.9Z",
    "fin": "M3 18c5 0 7-3 8-7 1-3 3-6 8-7-1 4-1 9 2 14H3Z",
    "bolt": "M13 2 4 14h7l-1 8 9-12h-7l1-8Z",
    "die": "M5 3h14a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2ZM8 8h.01M16 8h.01M12 12h.01M8 16h.01M16 16h.01",
    "arrow": "M4 12h16M14 6l6 6-6 6",
    "up": "M12 20V5M6 11l6-6 6 6",
    "shield": "M12 3 5 6v6c0 4.5 3 7.5 7 9 4-1.5 7-4.5 7-9V6l-7-3Z",
    "cap": "M2 9l10-5 10 5-10 5L2 9ZM6 11.5V16c3 2.500 9 2.500 12 0v-4.500",
    "lock": "M6 11h12a1 1 0 0 1 1 1v8a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1v-8a1 1 0 0 1 1-1ZM8 11V7a4 4 0 0 1 8 0v4",
    "unlock": "M6 11h12a1 1 0 0 1 1 1v8a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1v-8a1 1 0 0 1 1-1ZM8 11V7a4 4 0 0 1 7.500-2",
    "globe": "M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18ZM3 12h18M12 3c3 3 3.500 15 0 18M12 3c-3 3-3.500 15 0 18",
    "mail": "M3 6h18v12H3V6Zm0 0 9 7 9-7",
    "link": "M9 15l6-6M10 6l1.500-1.500a4.500 4.500 0 0 1 6.500 6.500L16 13M14 18l-1.500 1.500A4.500 4.500 0 0 1 6 13l2-2",
    "plus": "M12 5v14M5 12h14",
    "pin": "M12 21s7-6.500 7-12a7 7 0 1 0-14 0c0 5.500 7 12 7 12ZM12 11.500a2.500 2.500 0 1 0 0-5 2.500 2.500 0 0 0 0 5Z",
    "flag": "M5 21V4M5 4c4-2 7 2 13 0v9c-6 2-9-2-13 0",
    "send": "M4 12 21 4l-5 17-4-7-8-2ZM12 14l9-10",
}


# ---------- scenery ---------------------------------------------------------

def ridge_points(seed, width, step, base, amp, rough=0.56, f0=3, octaves=6, power=1.5):
    """Periodic ridge heights, so a layer can scroll forever without a seam."""
    rng = random.Random(seed)
    tables = [(f0 * 2 ** i, [rng.random() for _ in range(f0 * 2 ** i)], rough ** i) for i in range(octaves)]
    norm = sum(t[2] for t in tables)
    pts = []
    for x in range(0, width + step, step):
        t = (x % width) / width
        h = 0.0
        for f, tab, a in tables:
            u = t * f
            i = int(u)
            fr = u - i
            h += a * (tab[i % f] * (1 - fr) + tab[(i + 1) % f] * fr)
        h = (h / norm)
        pts.append((x, base - amp * (max(h - 0.18, 0) * 1.45) ** power))
    return pts


def range_points(seed, width, step, base, amp, peaks=9, jag=0.1, sharp=1.25):
    """A deliberate range of separate summits, periodic over the tile width."""
    rng = random.Random(seed)
    summits = []
    for i in range(peaks):
        x = (i + rng.uniform(-.28, .28)) / peaks
        summits.append((x, rng.uniform(.5, 1.0), rng.uniform(.75, 1.25) / peaks * 1.55))
    tables = [(f, [rng.random() - .5 for _ in range(f)], a) for f, a in
              ((peaks * 3, 1.0), (peaks * 7, .55), (peaks * 17, .3), (peaks * 41, .16))]
    pts = []
    for px in range(0, width + step, step):
        t = (px % width) / width
        h = 0.0
        for x, peak, w in summits:
            d = min(abs(t - x), 1 - abs(t - x)) / w
            if d < 1:
                h = max(h, peak * (1 - d) ** sharp)
        n = 0.0
        for f, tab, a in tables:
            u = t * f
            i = int(u)
            fr = u - i
            n += a * (tab[i % f] * (1 - fr) + tab[(i + 1) % f] * fr)
        h = max(h + n * jag * (.35 + h), 0)
        pts.append((px, base - amp * h))
    return pts


def ridge_path(pts, bottom):
    x0, y0 = pts[0]
    d = [f"M{x0} {bottom}L{x0} {round(y0, 1)}"]
    px, py = x0, round(y0)
    for x, y in pts[1:]:
        y = round(y)
        d.append("l" + fmt(x - px, y - py))
        px, py = x, y
    d.append(f"L{px} {bottom}z")
    return "".join(d)


def snow_path(seed, pts, line, jag=9):
    """Snow cap: everything above the snow line, with a torn lower edge."""
    rng = random.Random(seed)
    lower = []
    for x, y in pts:
        edge = line + rng.uniform(-jag, jag)
        lower.append((x, max(y, edge)))
    top = "".join(f"L{x} {round(y)}" for x, y in pts)
    bottom = "".join(f"L{x} {round(y)}" for x, y in reversed(lower))
    return "M" + top[1:] + bottom + "z"


def data_uri(path, mime):
    return f"data:{mime};base64," + base64.b64encode(Path(path).read_bytes()).decode()
