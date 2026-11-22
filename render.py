#!/usr/bin/env python3
"""Draw the news-image-20261121 r2 front page (Saturday 21 November 2026).

Renders one 1024x1024 cream newspaper page with PIL and writes entry.png
next to this file. Every story, number and date on the page was verified
against fresh reporting on 21-22 November 2026 (see NOTES.md); the layout
follows the 9-component cream-newspaper template that won the 20 November
board, with the story set the 21 November leaderboard converged on:
COP31 overtime, three missiles downed over Riyadh, and the Peru M6.7 quake
as the three leads, 35 stories across 7 regions, a per-card verification
status, and a DATE CHECK box.

Text is measured before it is drawn: any block that would overflow its
box raises instead of shipping clipped text.
"""

import hashlib
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")
OUT = os.path.join(HERE, "entry.png")

PAGE = 1024
MARGIN = 14
CONTENT = PAGE - 2 * MARGIN  # 996

CREAM = (246, 241, 227)
PAPER = (253, 250, 241)
INK = (26, 26, 26)
MUTED = (90, 84, 70)
RED = (163, 22, 33)
DARKRED = (140, 20, 28)
NAVY = (16, 35, 63)
SLATE = (71, 85, 105)
GOLD = (180, 83, 9)
TEAL = (14, 116, 144)
GREEN = (21, 128, 61)
PURPLE = (109, 40, 217)
BLUE = (29, 78, 216)
RULE = (26, 26, 26)
CARD_LINE = (201, 188, 158)
MAP_SEA = (220, 235, 240)
MAP_LAND = (232, 220, 192)
MAP_EDGE = (185, 167, 126)


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


SERIF = "DejaVuSerif.ttf"
SERIF_B = "DejaVuSerif-Bold.ttf"
SERIF_I = "DejaVuSerif-Italic.ttf"
SANS = "DejaVuSans.ttf"
SANS_B = "DejaVuSans-Bold.ttf"


def text_w(draw, xy, s, f, fill=INK):
    draw.text(xy, s, font=f, fill=fill)


def width_of(draw, s, f):
    return draw.textlength(s, font=f)


def wrap(draw, s, f, max_w):
    """Greedy word wrap; returns lines that each fit max_w."""
    words = s.split(" ")
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=f) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def block(draw, x, y, w, lines, f, leading, fill=INK, max_lines=None):
    """Draw lines of text; raise if they do not fit max_lines."""
    if max_lines is not None and len(lines) > max_lines:
        raise ValueError("overflow: %d lines > %d for %r"
                         % (len(lines), max_lines, lines[0][:40]))
    for i, line in enumerate(lines):
        draw.text((x, y + i * leading), line, font=f, fill=fill)
    return y + len(lines) * leading


def one_line(draw, s, f, max_w):
    if draw.textlength(s, font=f) > max_w:
        raise ValueError("line too wide (%d > %d): %r"
                         % (draw.textlength(s, font=f), max_w, s))


def pill(draw, x, y, s, f, bg, fg=(255, 255, 255), pad_x=6, pad_y=2):
    w = draw.textlength(s, font=f) + 2 * pad_x
    h = f.size + 2 * pad_y + 2
    draw.rounded_rectangle([x, y, x + w, y + h], radius=3, fill=bg)
    draw.text((x + pad_x, y + pad_y), s, font=f, fill=fg)
    return w, h


def chip(draw, x, y, label, count, bg):
    s = "%s %d" % (label, count)
    f = font(SANS_B, 11)
    w = draw.textlength(s, font=f) + 16
    h = 20
    draw.rounded_rectangle([x, y, x + w, y + h], radius=3, fill=bg)
    draw.text((x + 8, y + 4), s, font=f, fill=(255, 255, 255))
    return w


STATUS_FILL = {
    "CONFIRMED": (21, 128, 61),
    "OFFICIAL": (29, 78, 216),
    "REPORTED": (180, 83, 9),
    "CLAIM": (185, 28, 28),
}


def status_tag(draw, x_right, y, status):
    f = font(SANS_B, 9)
    w = draw.textlength(status, font=f) + 12
    h = 15
    x = x_right - w
    draw.rounded_rectangle([x, y, x + w, y + h], radius=3,
                           fill=STATUS_FILL[status])
    draw.text((x + 6, y + 3), status, font=f, fill=(255, 255, 255))
    return w


# ---------------------------------------------------------------- art scenes
# Each scene draws into the box (x, y, w, h) and fills it completely with
# big simple shapes -- no thin line icons, no wide empty sky or sea.

def scene_cop31(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(220, 234, 217))
    cx, cy, r = x + 62, y + h // 2 + 4, 52
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(47, 127, 168))
    d.ellipse([cx - 34, cy - 26, cx + 6, cy + 2], fill=(74, 160, 90))
    d.ellipse([cx + 2, cy + 8, cx + 34, cy + 38], fill=(74, 160, 90))
    d.ellipse([cx - 12, cy - r, cx + 22, cy - r + 22], fill=(74, 160, 90))
    # thermometer
    tx = x + 150
    d.rounded_rectangle([tx, y + 18, tx + 16, y + h - 26], radius=8,
                        fill=(255, 255, 255), outline=(163, 22, 33), width=2)
    d.rectangle([tx + 4, y + 42, tx + 12, y + h - 30], fill=(185, 28, 28))
    d.ellipse([tx - 6, y + h - 40, tx + 22, y + h - 12], fill=(185, 28, 28))
    d.text((tx + 24, y + 16), "+1.5°C", font=font(SANS_B, 13), fill=RED)
    d.text((tx + 24, y + 34), "LIMIT", font=font(SANS_B, 10), fill=INK)
    d.text((tx + 24, y + 48), "AT RISK", font=font(SANS_B, 10), fill=INK)
    # clock
    kx, ky, kr = x + w - 48, y + 52, 28
    d.ellipse([kx - kr, ky - kr, kx + kr, ky + kr], fill=(255, 255, 255),
              outline=INK, width=2)
    for ang, ln in ((90, 18), (10, 22)):
        a = math.radians(ang)
        d.line([kx, ky, kx + ln * math.cos(a), ky - ln * math.sin(a)],
               fill=INK, width=3)


def scene_riyadh(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    for sx, sy in ((x + 40, y + 22), (x + 120, y + 14), (x + 210, y + 26),
                   (x + 280, y + 16), (x + 170, y + 34)):
        d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(250, 204, 21))
    d.ellipse([x + w - 124, y + 8, x + w - 96, y + 36], fill=(253, 244, 200))
    d.ellipse([x + w - 118, y + 4, x + w - 96, y + 32], fill=NAVY)
    # skyline with lit windows
    base = y + h
    for bx, bw, bh in ((0, 52, 58), (58, 40, 84), (104, 62, 66),
                       (172, 44, 92), (222, 56, 60), (284, 42, 78)):
        d.rectangle([x + bx, base - bh, x + bx + bw, base], fill=(10, 18, 34))
        for wy in range(base - bh + 10, base - 8, 16):
            for wx in range(x + bx + 8, x + bx + bw - 8, 14):
                if (wx + wy) % 3 == 0:
                    d.rectangle([wx, wy, wx + 5, wy + 7], fill=(250, 204, 21))
    # three missile arcs ending in bursts
    for ax, apex in ((x + 60, y + 34), (x + 160, y + 22), (x + 250, y + 30)):
        pts = []
        for t in range(0, 21):
            tt = t / 20.0
            px = ax + tt * 46
            py = (y + h - 58) - (y + h - 58 - apex) * math.sin(tt * math.pi / 2)
            pts.append((px, py))
        d.line(pts, fill=(250, 204, 21), width=2)
        bx, by = pts[-1]
        for dx, dy in ((0, -9), (7, -6), (9, 0), (7, 6), (0, 9),
                       (-7, 6), (-9, 0), (-7, -6)):
            d.line([bx, by, bx + dx, by + dy], fill=(250, 204, 21), width=2)


def scene_peru(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(239, 227, 200))
    base = y + h
    for mx, mw, mh, col in ((0, 150, 60, (146, 110, 72)),
                            (110, 170, 78, (120, 88, 56)),
                            (230, 120, 50, (146, 110, 72))):
        d.polygon([(x + mx, base), (x + mx + mw // 2, base - mh),
                   (x + mx + mw, base)], fill=col)
        d.polygon([(x + mx + mw // 2 - 12, base - mh),
                   (x + mx + mw // 2, base - mh + 14),
                   (x + mx + mw // 2 + 12, base - mh)], fill=(250, 250, 250))
    # houses
    for hx, hw in ((x + 36, 44), (x + 96, 38), (x + 236, 46)):
        d.rectangle([hx, base - 34, hx + hw, base - 12], fill=(253, 250, 241))
        d.polygon([(hx - 4, base - 34), (hx + hw // 2, base - 48),
                   (hx + hw + 4, base - 34)], fill=(185, 28, 28))
        d.rectangle([hx + hw // 2 - 4, base - 24, hx + hw // 2 + 4, base - 12],
                    fill=(90, 60, 30))
    # seismograph trace
    pts = []
    for i in range(0, 33):
        px = x + 8 + i * (w - 16) / 32.0
        amp = (16 if i % 8 == 3 else 9 if i % 4 == 1 else 4)
        py = y + 28 + (amp if i % 2 else -amp)
        pts.append((px, py))
    d.line(pts, fill=(185, 28, 28), width=3)


def scene_bridge(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(219, 234, 254))
    d.rectangle([x, y + h - 16, x + w, y + h], fill=(120, 113, 108))
    for tx in (x + 46, x + w - 52):
        d.rectangle([tx, y + 12, tx + 6, y + h - 16], fill=(120, 113, 108))
        d.rectangle([tx - 4, y + 6, tx + 10, y + 14], fill=(185, 28, 28))
    for i in range(6):
        d.line([x + 50 + i * 20, y + 12, x + 70 + i * 20, y + h - 16],
               fill=(90, 84, 70), width=1)
    d.polygon([(x + 10, y + 6), (x + 28, y + 6), (x + 19, y + 26)],
              fill=(250, 204, 21), outline=INK)
    d.text((x + 16, y + 10), "!", font=font(SANS_B, 12), fill=INK)


def scene_drone(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(186, 220, 232))
    for cx, cy, r in ((x + w - 30, y + 16, 18), (x + w - 30, y + 16, 12)):
        d.arc([cx - r, cy - r, cx + r, cy + r], 200, 340, fill=(90, 84, 70),
              width=2)
    cx, cy = x + w // 2, y + h // 2
    d.ellipse([cx - 26, cy - 7, cx + 26, cy + 7], fill=(60, 60, 66))
    d.polygon([(cx + 20, cy - 4), (cx + 52, cy - 9), (cx + 52, cy + 1),
               (cx + 20, cy + 4)], fill=(60, 60, 66))
    d.polygon([(cx - 20, cy - 4), (cx - 52, cy - 9), (cx - 52, cy + 1),
               (cx - 20, cy + 4)], fill=(60, 60, 66))
    d.polygon([(cx - 6, cy + 4), (cx - 14, cy + 18), (cx + 2, cy + 18),
               (cx + 6, cy + 4)], fill=(60, 60, 66))
    for ex in (cx - 46, cx + 46, cx - 8, cx + 8):
        d.ellipse([ex - 7, cy - 16, ex + 7, cy - 6], fill=(40, 40, 44))
    d.rectangle([x, y + h - 12, x + w, y + h], fill=(47, 127, 168))


def scene_atom(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(254, 243, 199))
    cx, cy = x + w // 2 - 14, y + h // 2
    for ang in (0, 60, 120):
        a = math.radians(ang)
        rx, ry = 34, 13
        pts = []
        for t in range(0, 49):
            th = 2 * math.pi * t / 48.0
            px = cx + rx * math.cos(th) * math.cos(a) - ry * math.sin(th) * math.sin(a)
            py = cy + rx * math.cos(th) * math.sin(a) + ry * math.sin(th) * math.cos(a)
            pts.append((px, py))
        d.line(pts, fill=(26, 26, 26), width=2)
    d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=RED)
    d.rounded_rectangle([x + 8, y + h - 24, x + 56, y + h - 4], radius=3,
                        fill=RED)
    d.text((x + 14, y + h - 21), "60%", font=font(SANS_B, 11),
           fill=(255, 255, 255))


def scene_tax(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    for rx in (x + 48, x + 86, x + 124):
        d.rectangle([rx, y + 10, rx + 30, y + h - 10], fill=(30, 58, 95))
        for ly in range(y + 16, y + h - 12, 10):
            d.rectangle([rx + 5, ly, rx + 11, ly + 4], fill=(74, 222, 128))
            d.rectangle([rx + 16, ly, rx + 25, ly + 4], fill=(250, 204, 21))
    d.text((x + 8, y + 10), "%", font=font(SERIF_B, 30), fill=(250, 204, 21))


def scene_flags(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(253, 250, 241))
    d.rectangle([x + 10, y + 10, x + 80, y + h - 10], fill=(222, 41, 16))
    for sx, sy in ((x + 20, y + 16), (x + 34, y + 20), (x + 34, y + 30),
                   (x + 42, y + 18), (x + 42, y + 32)):
        d.ellipse([sx, sy, sx + 5, sy + 5], fill=(255, 222, 0))
    d.rectangle([x + 88, y + 10, x + 158, y + h - 10], fill=(255, 255, 255),
                outline=(180, 180, 180))
    d.ellipse([x + 108, y + 14, x + 138, y + h - 14], fill=(188, 0, 45))


def scene_plane(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(186, 220, 240))
    for cx, cy in ((x + 26, y + 12), (x + 150, y + 10), (x + 90, y + 30)):
        d.ellipse([cx - 14, cy - 6, cx + 14, cy + 6], fill=(255, 255, 255))
    cx, cy = x + w // 2, y + h // 2 + 2
    d.ellipse([cx - 52, cy - 9, cx + 52, cy + 9], fill=(255, 255, 255))
    d.polygon([(cx + 40, cy - 6), (cx + 72, cy - 16), (cx + 72, cy - 2),
               (cx + 40, cy + 2)], fill=(255, 255, 255))
    d.polygon([(cx - 10, cy + 6), (cx - 30, cy + 18), (cx - 18, cy + 18),
               (cx + 2, cy + 6)], fill=(220, 230, 235))
    d.polygon([(cx - 52, cy - 4), (cx - 68, cy - 12), (cx - 68, cy - 2),
               (cx - 52, cy + 2)], fill=(220, 230, 235))
    for wx in range(x + 8, x + w - 8, 16):
        d.rectangle([wx, y + h - 8, wx + 8, y + h - 5], fill=(255, 255, 255))
    d.rectangle([x, y + h - 4, x + w, y + h], fill=(120, 113, 108))


def scene_mercury(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    for sx, sy in ((x + 16, y + 10), (x + 60, y + 8), (x + 150, y + 12),
                   (x + 186, y + 22), (x + 30, y + 38)):
        d.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=(255, 255, 255))
    cx, cy, r = x + 62, y + h // 2, 24
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(203, 191, 168))
    for kx, ky, kr in ((cx - 10, cy - 8, 5), (cx + 8, cy + 2, 4),
                       (cx - 2, cy + 12, 3), (cx + 12, cy - 12, 3)):
        d.ellipse([kx - kr, ky - kr, kx + kr, ky + kr], fill=(170, 156, 130))
    bx, by = x + 138, y + 20
    d.rectangle([bx, by, bx + 22, by + 12], fill=(200, 200, 205))
    d.rectangle([bx - 16, by + 2, bx, by + 10], fill=(47, 127, 168))
    d.rectangle([bx + 22, by + 2, bx + 38, by + 10], fill=(47, 127, 168))
    d.line([bx + 11, by, bx + 11, by - 10], fill=(255, 255, 255), width=2)
    d.ellipse([bx + 8, by - 14, bx + 14, by - 8], fill=(250, 204, 21))


def scene_bitcoin(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(88, 28, 28))
    base = y + h - 10
    bars = [(14, 18, True), (34, 26, True), (54, 12, False), (74, 30, True),
            (94, 20, False), (114, 34, True), (134, 16, False)]
    for bx, bh, up in bars:
        col = (34, 197, 94) if up else (239, 68, 68)
        d.rectangle([x + bx, base - bh, x + bx + 12, base], fill=col)
        d.line([x + bx + 6, base - bh - 6, x + bx + 6, base + 2], fill=col,
               width=2)


def scene_racecar(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(38, 38, 44))
    for i in range(8):
        cx = x + i * 24
        d.rectangle([cx, y + 4, cx + 12, y + 12],
                    fill=(255, 255, 255) if i % 2 == 0 else (20, 20, 20))
        d.rectangle([cx, y + 12, cx + 12, y + 20],
                    fill=(20, 20, 20) if i % 2 == 0 else (255, 255, 255))
    cx, cy = x + w // 2, y + h // 2 + 6
    d.polygon([(cx - 62, cy + 8), (cx - 62, cy - 2), (cx - 30, cy - 6),
               (cx + 10, cy - 8), (cx + 44, cy - 6), (cx + 62, cy + 2),
               (cx + 62, cy + 8)], fill=(220, 38, 38))
    d.polygon([(cx - 6, cy - 8), (cx + 6, cy - 20), (cx + 26, cy - 20),
               (cx + 22, cy - 8)], fill=(220, 38, 38))
    d.rectangle([cx + 48, cy - 22, cx + 62, cy - 8], fill=(20, 20, 20))
    for wx in (cx - 40, cx + 34):
        d.ellipse([wx - 12, cy - 2, wx + 12, cy + 16], fill=(15, 15, 15),
                  outline=(200, 200, 200))
        d.ellipse([wx - 5, cy + 3, wx + 5, cy + 11], fill=(120, 120, 120))


def scene_cricket(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(34, 139, 34))
    d.rectangle([x, y + h - 14, x + w, y + h], fill=(139, 110, 58))
    cx, cy = x + w // 2, y + h // 2
    d.polygon([(cx - 34, cy - 26), (cx - 22, cy - 28), (cx + 6, cy + 16),
               (cx - 6, cy + 22)], fill=(222, 184, 135),
              outline=(120, 90, 40))
    d.rectangle([cx - 38, cy - 34, cx - 24, cy - 24], fill=(120, 90, 40))
    for sx in (cx + 22, cx + 30, cx + 38):
        d.rectangle([sx, cy - 6, sx + 4, cy + 18], fill=(250, 204, 21))
        d.rectangle([sx, cy - 10, sx + 4, cy - 6], fill=(250, 204, 21))
    d.ellipse([x + 14, y + 6, x + 30, y + 22], fill=(185, 28, 28),
              outline=(255, 255, 255))


# ------------------------------------------------------------------- content

TICKER = [
    ("13", "day of COP31, meant to close on day 12"),
    ("3", "missiles shot down over Riyadh"),
    ("6.7", "magnitude of the Peru quake"),
    ("146", "people safe after the Davao landing"),
    ("$58,983", "bitcoin early Saturday, down 3.9% in a day"),
    ("124*", "K L Rahul's score at tea in Wellington"),
]

CHIPS = [
    ("EUROPE", 4, BLUE), ("ASIA", 10, GOLD), ("MIDDLE EAST", 5, RED),
    ("AFRICA", 1, GREEN), ("AMERICAS", 11, PURPLE), ("OCEANIA", 2, TEAL),
    ("GLOBAL", 2, SLATE),
]

LEADS = [
    dict(scene=scene_cop31, banner="COP31: OVERTIME", banner_bg=RED,
         pill="No deal · day 13",
         kicker="1 · ANTALYA, TÜRKIYE · CLIMATE",
         headline="Climate talks run into Saturday with no deal",
         body=("No deal by Friday's deadline. A draft stripped of fossil "
               "fuels and a $120bn adaptation fund split nearly 200 "
               "countries; a third text was due Saturday. (Reuters, AP)"),
         status="CONFIRMED"),
    dict(scene=scene_riyadh, banner="SAUDI: MISSILES DOWNED", banner_bg=NAVY,
         pill="3 shot down",
         kicker="2 · RIYADH · WAR",
         headline="Three Houthi missiles shot down over Riyadh",
         body=("The coalition destroyed three ballistic missiles fired at "
               "the capital before dawn, two days after a strike damaged "
               "the PIF tower. A drone headed south was downed too. "
               "(Reuters, AFP)"),
         status="OFFICIAL"),
    dict(scene=scene_peru, banner="PERU: QUAKE 6.7", banner_bg=RED,
         pill="00:09 UTC · 108 km deep",
         kicker="3 · JUNÍN, PERU · EARTHQUAKE",
         headline="Magnitude 6.7 earthquake shakes central Peru",
         body=("The deep quake near Carhuamayo was felt in Lima and along "
               "the coast. Peru's institute reported no deaths, damage or "
               "tsunami risk. (USGS, IGP)"),
         status="OFFICIAL"),
]

PANELS = [
    dict(scene=scene_bridge, banner="KYIV: WARNING", banner_bg=RED,
         headline="Zelensky: Crimea bridge 'will not stay'",
         body=("He warns of double-tap strikes ahead as Russia hits "
               "Kyiv's bridges. (NBC)"),
         status="REPORTED"),
    dict(scene=scene_drone, banner="HORMUZ: DRONE", banner_bg=NAVY,
         headline="Iran says it shot down a US drone",
         body=("Tehran calls it the 58th MQ-9 downed. No US confirmation. "
               "(IRIB)"),
         status="CLAIM"),
    dict(scene=scene_atom, banner="IRAN: URANIUM", banner_bg=GOLD,
         headline="Iran: uranium stock stays at home",
         body=("Rules out sending its 60% uranium abroad; still seeks a "
               "'fair solution'. (ToI)"),
         status="REPORTED"),
    dict(scene=scene_tax, banner="TRUMP: AI TAX", banner_bg=NAVY,
         headline="Trump vows tax on data centres abroad",
         body=("\u2018Tremendous\u2019 penalty, no rate or details; he had "
               "not told his staff. (Reuters)"),
         status="REPORTED"),
    dict(scene=scene_flags, banner="CHINA–JAPAN", banner_bg=RED,
         headline="China tells Japan to \u2018correct\u2019 Taiwan words",
         body=("Beijing repeats the demand; Tokyo says its stance is "
               "unchanged. (AFP)"),
         status="OFFICIAL"),
    dict(scene=scene_plane, banner="DAVAO: 146 SAFE", banner_bg=TEAL,
         headline="Jet lands safely after engine fire alert",
         body=("Air Niugini 767 diverts after midnight; all 146 leave by "
               "the slides. (CAAP, AP)"),
         status="OFFICIAL"),
    dict(scene=scene_mercury, banner="MERCURY: ORBIT", banner_bg=NAVY,
         headline="BepiColombo reaches Mercury after eight years",
         body=("Enters orbit at 18:24 UTC; its two orbiters part in "
               "December. (ESA, Nature)"),
         status="CONFIRMED"),
    dict(scene=scene_bitcoin, banner="BITCOIN: $58,983", banner_bg=DARKRED,
         headline="Bitcoin slips below $59,000",
         body=("Down 3.9% in 24 hours to $58,983; later low $55,130. "
               "(CoinGecko)"),
         status="CONFIRMED"),
    dict(scene=scene_racecar, banner="RUSSELL: P1", banner_bg=(20, 20, 20),
         headline="Russell fastest in final Las Vegas practice",
         body=("1:34.041 in the only dry session; Antonelli second, 0.911 "
               "back. (Formula 1)"),
         status="OFFICIAL"),
    dict(scene=scene_cricket, banner="RAHUL: 124*", banner_bg=GREEN,
         headline="Rahul century puts India on top",
         body=("India 344 for 2 at tea, replying to 368; his 13th hundred, "
               "off 207 balls. (AFP)"),
         status="CONFIRMED"),
]

BRIEFS = [
    (14, "Kryvyi Rih", "Double strike kills 2, injures 60", "AP"),
    (15, "Copenhagen", "Russian attaché expelled over plot", "Al Jazeera"),
    (16, "Antalya", "EU warns COP31 risks a \u2018fossil summit\u2019", "AFP"),
    (17, "Antalya", "Panama threatens to block climate text", "AFP"),
    (18, "Antalya", "Indonesia\u2019s PLN signs 6 clean-power deals", "Antara"),
    (19, "Yemen", "Houthis threaten Jeddah and Red Sea ports", "AJ"),
    (20, "Washington", "Vance: Iran strikes were Trump\u2019s call", "Reuters"),
    (21, "Washington", "Lawmaker threatens SpaceX\u2019s funding", "CNN"),
    (22, "Texas", "Execution of a man of 70 takes 63 minutes", "ABC"),
    (23, "Los Angeles", "Jury convicts Palisades fire starter", "ABC"),
    (24, "Missouri", "Judge approves $7.25bn Roundup settlement", "AFP"),
    (25, "Vancouver", "Canada rests defence in youth climate trial", "AFP"),
    (26, "Pyongyang", "Kim tours factories after no Trump meeting", "AFP"),
    (27, "Sejong", "Freight train derails; no one hurt", "Korea Herald"),
    (28, "Taipei", "Budget and cash payout are passed", "Taipei Times"),
    (29, "Bangkok", "Six-point plan on arsenic in two rivers", "The Nation"),
    (30, "New Delhi", "Pakistani minister joins SCO forum in India", "Dawn"),
    (31, "E. India", "Rain alerts as Akvan\u2019s remnants move inland", "ETV"),
    (32, "Myanmar", "Rights groups urge sanctions after court ruling", "AP"),
    (33, "Port Louis", "African rating agency talks to 15 states", "AJ"),
    (34, "Melbourne", "Cummins keeps the Australian captaincy", "ABC"),
    (35, "Las Vegas", "Verstappen to stewards after contact", "Autosport"),
]

DATE_CHECK = (
    "DATE CHECK \u2014 Left out as Friday 20 November\u2019s news: Wall "
    "Street\u2019s fall into a correction, the Russian barrage that hit "
    "Kyiv\u2019s bridges, the missile that landed in Poland, the UK\u2013EU "
    "deal and Cyclone Akvan\u2019s landfall. Older still: Voyager 1\u2019s "
    "light-day (18 Nov). Not confirmed when drawn, so not shown: a final "
    "COP31 text.")

# Continents as coarse lon/lat outlines (general geography, equirectangular).
CONTINENTS = [
    [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-75, 73), (-60, 60),
     (-55, 47), (-70, 42), (-75, 35), (-80, 26), (-90, 21), (-97, 16),
     (-105, 20), (-110, 24), (-117, 33), (-125, 40), (-125, 49),
     (-135, 58), (-155, 58), (-168, 66)],
    [(-80, 9), (-62, 10), (-52, 5), (-40, -5), (-35, -9), (-40, -20),
     (-48, -28), (-58, -35), (-65, -41), (-70, -52), (-73, -44),
     (-73, -30), (-77, -18), (-80, -4), (-80, 9)],
    [(-6, 35), (10, 37), (20, 32), (33, 31), (35, 28), (43, 12), (51, 11),
     (48, -1), (40, -10), (36, -18), (32, -29), (26, -34), (18, -35),
     (15, -27), (12, -18), (9, -1), (8, 4), (-8, 5), (-17, 15), (-17, 21),
     (-10, 31), (-6, 35)],
    [(27, 71), (40, 68), (55, 68), (70, 72), (100, 77), (130, 72),
     (160, 70), (178, 66), (162, 60), (140, 40), (127, 40), (120, 30),
     (110, 20), (105, 9), (100, 8), (92, 16), (88, 22), (80, 13), (77, 8),
     (73, 20), (66, 25), (57, 26), (50, 29), (44, 29), (35, 36), (27, 40),
     (23, 40), (19, 45), (12, 44), (3, 43), (-2, 37), (-9, 37), (-9, 43),
     (0, 48), (5, 55), (10, 57), (18, 56), (21, 60), (27, 71)],
    [(114, -22), (124, -14), (132, -12), (142, -11), (150, -22),
     (153, -27), (150, -37), (140, -38), (135, -35), (129, -32),
     (122, -34), (115, -32), (114, -22)],
]

# (lon, lat) of the numbered pins; 10 is Mercury (space), 11 is markets.
PINS = {
    1: (30.7, 36.9), 2: (46.7, 24.7), 3: (-76.0, -11.0), 4: (30.5, 50.4),
    5: (56.5, 26.5), 6: (51.4, 35.7), 7: (-77.0, 38.9), 8: (116.4, 39.9),
    9: (125.6, 7.1), 12: (-115.1, 36.2), 13: (174.8, -41.3),
}
PIN_NUDGE = {2: (-6, 4), 5: (7, -3), 6: (0, -7), 1: (-4, -6), 4: (5, 2)}


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=MAP_SEA,
                outline=CARD_LINE)
    lon0, lon1, lat0, lat1 = -180.0, 190.0, 84.0, -58.0

    def proj(lon, lat):
        px = x + (lon - lon0) / (lon1 - lon0) * w
        py = y + (lat0 - lat) / (lat0 - lat1) * h
        return (px, py)

    for poly in CONTINENTS:
        d.polygon([proj(lon, lat) for lon, lat in poly], fill=MAP_LAND,
                  outline=MAP_EDGE)
    for num, (lon, lat) in PINS.items():
        dx, dy = PIN_NUDGE.get(num, (0, 0))
        px, py = proj(lon, lat)
        px += dx
        py += dy
        r = 8
        d.polygon([(px, py - r), (px + r, py), (px, py + r), (px - r, py)],
                  fill=RED, outline=(255, 255, 255))
        tf = font(SANS_B, 8)
        tw = d.textlength(str(num), font=tf)
        d.text((px - tw / 2, py - 5), str(num), font=tf,
               fill=(255, 255, 255))


def draw_lead(d, x, y, w, lead):
    art_h = 138
    lead["scene"](d, x, y, w, art_h)
    d.rectangle([x, y, x + w, y + art_h], outline=CARD_LINE)
    pill(d, x + 8, y + art_h - 26, lead["pill"], font(SANS_B, 10),
         (255, 255, 255), fg=INK)
    status_tag(d, x + w - 6, y + 6, lead["status"])
    by = y + art_h
    d.rectangle([x, by, x + w, by + 22], fill=lead["banner_bg"])
    d.text((x + 8, by + 5), lead["banner"], font=font(SANS_B, 12),
           fill=(255, 255, 255))
    ky = by + 26
    d.text((x, ky), lead["kicker"], font=font(SANS_B, 10), fill=RED)
    hy = ky + 15
    lines = wrap(d, lead["headline"], font(SERIF_B, 19), w)
    block(d, x, hy, w, lines, font(SERIF_B, 19), 23, max_lines=2)
    byy = hy + 2 * 23 + 3
    blines = wrap(d, lead["body"], font(SANS, 10), w)
    block(d, x, byy, w, blines, font(SANS, 10), 13, max_lines=3)


def draw_panel(d, x, y, w, panel, num):
    art_h = 46
    panel["scene"](d, x, y, w, art_h)
    d.rectangle([x, y, x + w, y + art_h], outline=CARD_LINE)
    status_tag(d, x + w - 4, y + 4, panel["status"])
    by = y + art_h
    d.rectangle([x, by, x + w, by + 15], fill=panel["banner_bg"])
    d.text((x + 6, by + 3), panel["banner"], font=font(SANS_B, 9),
           fill=(255, 255, 255))
    ky = by + 18
    d.text((x, ky), "%d · %s" % (num, panel["banner"].split(":")[0]),
           font=font(SANS_B, 9), fill=RED)
    hy = ky + 11
    lines = wrap(d, panel["headline"], font(SERIF_B, 12), w)
    block(d, x, hy, w, lines, font(SERIF_B, 12), 14, max_lines=2)
    byy = hy + 2 * 14 + 2
    blines = wrap(d, panel["body"], font(SANS, 9), w)
    block(d, x, byy, w, blines, font(SANS, 9), 11, max_lines=2)


def draw_brief(d, x, y, w, num, place, text, src):
    f_num = font(SANS_B, 9)
    f_b = font(SANS_B, 9)
    f_t = font(SANS, 9)
    lead = "%d %s \u2014 %s (%s)" % (num, place, text, src)
    one_line(d, lead, f_t, w)  # raises if it does not fit
    d.text((x, y), str(num), font=f_num, fill=RED)
    nx = x + d.textlength(str(num) + " ", font=f_num)
    d.text((nx, y), place, font=f_b, fill=INK)
    px = nx + d.textlength(place + " ", font=f_b)
    d.text((px, y), "\u2014 %s (%s)" % (text, src), font=f_t, fill=INK)


def main():
    img = Image.new("RGB", (PAGE, PAGE), CREAM)
    d = ImageDraw.Draw(img)

    # Masthead.
    d.text((MARGIN, 10), "THE WORLD IN ONE DAY", font=font(SANS_B, 13),
           fill=RED)
    right = "35 STORIES \u00b7 7 REGIONS \u00b7 EVERY ONE DATED SATURDAY 21 NOVEMBER 2026"
    rf = font(SANS_B, 10)
    d.text((PAGE - MARGIN - d.textlength(right, font=rf), 12), right,
           font=rf, fill=INK)
    d.line([MARGIN, 32, PAGE - MARGIN, 32], fill=RULE, width=2)

    # Date + sub-dek.
    date = "Saturday 21 November 2026"
    df = font(SERIF_B, 56)
    d.text(((PAGE - d.textlength(date, font=df)) / 2, 36), date, font=df,
           fill=INK)
    sub = ("COP31 talks run into overtime \u00b7 missiles over Riyadh "
           "\u00b7 a quake shakes Peru")
    sf = font(SERIF_I, 15)
    d.text(((PAGE - d.textlength(sub, font=sf)) / 2, 96), sub, font=sf,
           fill=RED)
    d.line([MARGIN, 116, PAGE - MARGIN, 116], fill=RULE, width=1)

    # Ticker: six big numbers.
    cell_w = CONTENT // 6
    for i, (num, cap) in enumerate(TICKER):
        cx = MARGIN + i * cell_w
        if i:
            d.line([cx - 4, 122, cx - 4, 162], fill=CARD_LINE, width=1)
        nf = font(SERIF_B, 26)
        d.text((cx + 4, 120), num, font=nf, fill=RED)
        clines = wrap(d, cap, font(SANS, 9), cell_w - 12)
        block(d, cx + 4, 148, cell_w - 12, clines, font(SANS, 9), 10,
              max_lines=2)
    d.line([MARGIN, 172, PAGE - MARGIN, 172], fill=RULE, width=1)

    # Region chips.
    cx = MARGIN
    for label, count, bg in CHIPS:
        cx += chip(d, cx, 178, label, count, bg) + 6
    total = "35 STORIES"
    tf = font(SANS_B, 11)
    d.text((PAGE - MARGIN - d.textlength(total, font=tf), 182), total,
           font=tf, fill=INK)

    # Three leads.
    lead_w, lead_gap = 326, 9
    for i, lead in enumerate(LEADS):
        draw_lead(d, MARGIN + i * (lead_w + lead_gap), 204, lead_w, lead)

    # Ten panels, two rows of five.
    panel_w, panel_gap = 195, 5
    row_y = [486, 618]
    for i, panel in enumerate(PANELS):
        row, col = divmod(i, 5)
        draw_panel(d, MARGIN + col * (panel_w + panel_gap), row_y[row],
                   panel_w, panel, 4 + i)

    # Map + briefs.
    map_x, map_w = MARGIN, 322
    d.text((map_x, 754), "WHERE IT HAPPENED", font=font(SANS_B, 11), fill=INK)
    draw_map(d, map_x, 770, map_w, 136)
    d.text((map_x, 910),
           "Red numbers mark stories 1\u201313. No. 10 is in space: Mercury.",
           font=font(SANS, 8), fill=MUTED)
    d.text((map_x, 921),
           "No. 11 is everywhere: markets. Positions are approximate.",
           font=font(SANS, 8), fill=MUTED)
    bx = map_x + map_w + 8
    bw = PAGE - MARGIN - bx
    d.text((bx, 754), "ALSO ON SATURDAY 21 NOVEMBER \u2014 22 MORE STORIES",
           font=font(SANS_B, 11), fill=INK)
    col_w = (bw - 10) // 2
    for j, (num, place, text, src) in enumerate(BRIEFS):
        col, row = divmod(j, 11)
        draw_brief(d, bx + col * (col_w + 10), 770 + row * 15, col_w,
                   num, place, text, src)

    # DATE CHECK.
    d.rectangle([MARGIN, 936, PAGE - MARGIN, 972], outline=RED, width=2)
    dlines = wrap(d, DATE_CHECK, font(SANS, 9), CONTENT - 20)
    block(d, MARGIN + 10, 941, CONTENT - 20, dlines, font(SANS, 9), 11,
          max_lines=3)

    # Footer.
    foot1 = ("Every story here happened, or was first reported, on Saturday "
             "21 November 2026. Sources named beside each story \u00b7 "
             "Original drawings.")
    ff = font(SANS, 9)
    d.text(((PAGE - d.textlength(foot1, font=ff)) / 2, 978), foot1, font=ff,
           fill=INK)
    foot2 = ("HOW WE CHECKED: CONFIRMED = 2+ outlets \u00b7 OFFICIAL = on "
             "the record \u00b7 REPORTED = one outlet \u00b7 CLAIM = one "
             "side\u2019s account")
    d.text(((PAGE - d.textlength(foot2, font=ff)) / 2, 991), foot2, font=ff,
           fill=MUTED)

    img.save(OUT, "PNG", optimize=True)
    size = os.path.getsize(OUT)
    with open(OUT, "rb") as f:
        digest = hashlib.sha256(f.read()).hexdigest()
    print("wrote %s (%d bytes, sha256 %s)" % (OUT, size, digest))
    if size > 1048576:
        print("entry.png exceeds 1 MiB", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
