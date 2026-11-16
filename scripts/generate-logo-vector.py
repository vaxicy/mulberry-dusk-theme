#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mulberry Dusk Theme — flat vector logo candidates (SVG, headless Chromium).

Style: **flat** — solid fills only, no gradients, no highlights, no outlines. Two
or three shapes per mark.

Palette is one plum→pink ramp. Because the frame is dark plum and the page is pale
pink, every mark keeps a pale disc or a pale shape next to the plum ones, so the
same icon reads on the toolbar and on the New Tab Page.

Playwright screenshots each SVG cell with omit_background=True (true
transparency); PIL only composes the contact sheets, the inline strip and the
official logo/logo.png exported from SELECTED.

Colours come from manifest.json. Change SELECTED and re-run; never hand-copy PNGs.
"""
import json
import math
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
os.chdir(str(ROOT))                      # relative paths only (non-ASCII path safety)

SIZE = 128
CELL = 512
PREVIEW = 256
SELECTED = "01"
CAND_DIR = Path("logo/candidates")
LOGO_OUT = Path("logo/logo.png")

with open("manifest.json", "r", encoding="utf-8") as f:
    _m = json.load(f)
_C, _P = _m["theme"]["colors"], _m["theme"]["properties"]


def hx(vals):
    return "#%02X%02X%02X" % tuple(vals)


PLUM = hx(_C["frame"])                             # #540863
MAUVE = hx(_C["button_background_secondary"])      # #92487A
ROSE = hx(_C["button_background"])                 # #E49BA6
PALE = hx(_C["ntp_background"])                    # #FFD3D5
LINK = hx(_C["ntp_link"])                          # #7A3268
TOOLBAR = hx(_C["toolbar"])                        # #69216F


def svg_open(body, defs=""):
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
            'viewBox="0 0 256 256">%s<g transform="translate(128 128) scale(0.94) '
            'translate(-128 -128)">%s</g></svg>' % (CELL, CELL, defs, body))


def circle(cx, cy, r, fill):
    return '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>' % (cx, cy, r, fill)


def leaf(cx, cy, length, width, angle, fill):
    half = length * 0.5
    d = ("M0 0 C %.1f %.1f %.1f %.1f 0 %.1f C %.1f %.1f %.1f %.1f 0 0 Z"
         % (width, -half * 0.55, width * 0.86, -half * 1.25, -length,
            -width * 0.86, -half * 1.25, -width, -half * 0.55))
    return ('<g transform="translate(%.1f %.1f) rotate(%.1f)"><path d="%s" fill="%s"/></g>'
            % (cx, cy, angle, d, fill))


# ------------------------------------------------------------------ candidates
SVG_01 = svg_open("""
%s
%s
%s
""" % (circle(102, 104, 48, PLUM),
       circle(160, 132, 36, MAUVE),
       circle(118, 178, 28, ROSE)))

SVG_02 = svg_open("""
%s
%s
%s
""" % (circle(128, 128, 96, PALE),
       leaf(128, 186, 116, 44, 0, PLUM),
       circle(128, 120, 34, ROSE)))

SVG_03 = svg_open("""
%s
%s
%s
""" % (circle(128, 128, 96, PALE),
       '<path d="M32 168 a96 96 0 0 1 192 0 Z" fill="%s"/>' % PLUM,
       circle(128, 96, 26, ROSE)))

SVG_04 = svg_open("""
%s
%s
%s
%s
%s
""" % (circle(128, 128, 96, PALE),
       '<path d="M128 40 V120" stroke="%s" stroke-width="8" stroke-linecap="round" fill="none"/>' % PLUM,
       circle(104, 142, 22, PLUM),
       circle(128, 154, 26, MAUVE),
       circle(152, 142, 22, ROSE)))

SVG_05 = svg_open("""
<defs><clipPath id="c5"><circle cx="128" cy="128" r="96"/></clipPath></defs>
<g clip-path="url(#c5)">
  <rect x="32" y="32" width="192" height="64" fill="%s"/>
  <rect x="32" y="96" width="192" height="60" fill="%s"/>
  <rect x="32" y="156" width="192" height="68" fill="%s"/>
</g>
""" % (PLUM, MAUVE, ROSE))

SVG_06 = svg_open("""
%s
%s
%s
%s
""" % (circle(128, 128, 96, PALE),
       circle(112, 112, 44, PLUM),
       circle(162, 160, 26, ROSE),
       leaf(112, 112, 46, 18, -30, MAUVE)))

CANDIDATES = [
    ("01", "berry-trio", "Three berries on a pale disc — reads as mulberry", SVG_01),
    ("02", "leaf-berry", "One berry sitting on a plum leaf", SVG_02),
    ("03", "dusk-arc", "Plum horizon with a rose sun — most 'dusk'", SVG_03),
    ("04", "berry-hang", "Three berries hanging from a stem", SVG_04),
    ("05", "band-stack", "Three palette bands in a disc — most graphic", SVG_05),
    ("06", "berry-pair", "A plum berry with a rose one tucked beside it", SVG_06),
]


def font(size, bold=False):
    for name in (("segoeuib.ttf", "seguisb.ttf") if bold else ("segoeui.ttf", "segoeuisl.ttf")):
        p = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", name)
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def render_cells():
    cells = "".join('<div id="cell%s" style="width:%dpx;height:%dpx">%s</div>' % (num, CELL, CELL, svg)
                    for num, _n, _d, svg in CANDIDATES)
    html = ('<!doctype html><html><head><meta charset="utf-8"><style>'
            'html,body{margin:0;padding:0;background:transparent}'
            '#grid{display:flex;flex-wrap:wrap;width:%dpx}div[id^=cell]{display:block}'
            '</style></head><body><div id="grid">%s</div></body></html>' % (CELL * 3, cells))
    out = {}
    with sync_playwright() as p:
        try:
            b = p.chromium.launch()
        except Exception:
            # bundled headless shell may be missing after a Playwright update
            b = p.chromium.launch(channel="chrome")
        pg = b.new_page(viewport={"width": CELL * 3, "height": CELL * 2})
        pg.set_content(html)
        for num, name, _d, _svg in CANDIDATES:
            path = CAND_DIR / ("%s-%s.png" % (num, name))
            pg.locator("#cell" + num).screenshot(path=str(path), omit_background=True)
            img = Image.open(path).convert("RGBA").resize((PREVIEW, PREVIEW), Image.LANCZOS)
            img.save(path)
            bbox = img.split()[3].getbbox()
            assert bbox, "candidate %s rendered empty" % name
            assert bbox[0] > 6 and bbox[1] > 6 and bbox[2] < PREVIEW - 6 and bbox[3] < PREVIEW - 6, \
                "candidate %s touches the canvas edge: %s" % (name, bbox)
            out[num] = img
            print("candidate %s %s -> alpha bbox %s" % (num, name, bbox))
        b.close()
    return out


def contact_sheet(rendered, bg, txt, sub, path, title):
    cols, rows = 3, 2
    cw, ch = 384, 374
    gap, margin = 28, 40
    W = margin * 2 + cols * cw + (cols - 1) * gap
    H = margin * 2 + 34 + rows * ch + (rows - 1) * gap
    sheet = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(sheet)
    f_title, f_name, f_desc, f_file = font(24, True), font(21, True), font(15), font(14)
    d.text((margin, margin), title, font=f_title, fill=txt)
    y0 = margin + 34
    for i, (num, name, desc, _svg) in enumerate(CANDIDATES):
        r, c = divmod(i, cols)
        x = margin + c * (cw + gap)
        y = y0 + r * (ch + gap)
        big = rendered[num].resize((220, 220), Image.LANCZOS)
        sheet.paste(big, (x + (cw - 220) // 2, y + 14), big)
        d.text((x + 18, y + 250), "%s · %s" % (num, name), font=f_name, fill=txt)
        d.text((x + 18, y + 280), desc, font=f_desc, fill=sub)
        thumb = rendered[num].resize((32, 32), Image.LANCZOS)
        sheet.paste(thumb, (x + 18, y + 330), thumb)
        d.text((x + 60, y + 339), "%s.png  256x256" % name, font=f_file, fill=sub)
        assert y + 300 <= y + 322, "text block collides with the thumbnail row"
    sheet.save(path)
    print("saved:", path, sheet.size)


def inline_strip(rendered, path):
    n, cell, gap, margin = len(CANDIDATES), 108, 22, 30
    W = margin * 2 + n * cell + (n - 1) * gap
    H = margin * 2 + cell + 30
    strip = Image.new("RGB", (W, H), PALE)
    d = ImageDraw.Draw(strip)
    f = font(15, True)
    for i, (num, _n, _d, _s) in enumerate(CANDIDATES):
        x = margin + i * (cell + gap)
        img = rendered[num].resize((cell, cell), Image.LANCZOS)
        strip.paste(img, (x, margin), img)
        d.text((x + cell // 2 - 8, margin + cell + 8), num, font=f, fill=PLUM)
    strip.save(path)
    print("saved:", path, strip.size)


def main():
    CAND_DIR.mkdir(parents=True, exist_ok=True)
    rendered = render_cells()
    contact_sheet(rendered, (255, 211, 213), (84, 8, 99), (150, 90, 120),
                  CAND_DIR / "contact-light.png", "Mulberry Dusk — flat candidates (light)")
    contact_sheet(rendered, (84, 8, 99), (255, 211, 213), (200, 150, 175),
                  CAND_DIR / "contact-dark.png", "Mulberry Dusk — flat candidates (dark)")
    inline_strip(rendered, CAND_DIR / "inline-strip.png")
    sel = [c for c in CANDIDATES if c[0] == SELECTED][0]
    icon = rendered[sel[0]].resize((SIZE, SIZE), Image.LANCZOS)
    icon.save(LOGO_OUT)
    print("official icon from SELECTED=%s (%s):" % (sel[0], sel[1]), LOGO_OUT, icon.size)


if __name__ == "__main__":
    main()
