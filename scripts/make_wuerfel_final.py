"""Baut aus dem entfalteten Würfel den fertigen Bastelbogen für Zyklus 1 (5–6 Jahre).

Schritte:
1. Laschen und Linienkodierung über ``scripts/add_tabs.py`` (15 mm, Trapez 45°).
2. Netz achsparallel drehen und die sechs Würfelflächen im Raster erkennen.
3. Zahlen 1–6 so verteilen, dass gegenüberliegende Seiten zusammen 7 ergeben wie bei
   einem echten Spielwürfel (das Netz wird dazu virtuell «abgerollt»). Die 6 wird
   unterstrichen, damit sie gedreht nicht als 9 gelesen wird. Mit ``--motiv augen``
   stehen statt Ziffern Würfelaugen (Mengenbild) auf den Flächen.
4. Legende aus ``templates/inkscape/legende-zyklus1.svg`` unten rechts einsetzen;
   Zeilen ohne Entsprechung auf dem Bogen (z. B. Talfalte) werden weggelassen.
5. Alles auf A4 hochkant mit 10 mm Rand platzieren, ohne dass Netz und Legende sich berühren.

Das Ergebnis ist ein editierbares Inkscape-SVG mit Ebenen. PDF und PNG danach mit Inkscape:

    inkscape examples/01-wuerfel-einstieg/wuerfel-final.svg --export-type=pdf --export-text-to-path --export-filename=examples/01-wuerfel-einstieg/wuerfel-final.pdf

Aufruf (PowerShell, eine Zeile):

    python scripts/make_wuerfel_final.py examples/01-wuerfel-einstieg/wuerfel-unfolded.svg examples/01-wuerfel-einstieg/wuerfel-final.svg
    python scripts/make_wuerfel_final.py examples/01-wuerfel-einstieg/wuerfel-unfolded.svg examples/01-wuerfel-einstieg/wuerfel-augen-final.svg --motiv augen

Nur Python-Standardbibliothek, Python 3.10+.
"""

from __future__ import annotations

import argparse
import copy
import math
import re
import sys
import xml.etree.ElementTree as ET
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import add_tabs  # noqa: E402
from add_tabs import Point, fmt  # noqa: E402

SVG_NS = "http://www.w3.org/2000/svg"
INKSCAPE_NS = "http://www.inkscape.org/namespaces/inkscape"
SODIPODI_NS = "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
ET.register_namespace("", SVG_NS)
ET.register_namespace("inkscape", INKSCAPE_NS)
ET.register_namespace("sodipodi", SODIPODI_NS)

REPO = Path(__file__).resolve().parent.parent
DEFAULT_LEGEND = REPO / "templates" / "inkscape" / "legende-zyklus1.svg"

# Helle, kontrastreiche Flächenfarben; Zahlen dunkel darauf
FACE_COLORS = {1: "#FFF3B0", 2: "#CDEFD8", 3: "#FFD8C2", 4: "#D6EAF8", 5: "#E8DAF5", 6: "#FAD4E4"}
NUMBER_COLOR = "#1B2631"
NUMBER_FONT = "Andika, 'Comic Neue', 'DejaVu Sans', sans-serif"
FOOTER_COLOR = "#808B96"


# ---------------------------------------------------------------------------
# Würfelflächen und Zahlen
# ---------------------------------------------------------------------------

def find_faces(tn: add_tabs.TabbedNet) -> tuple[float, dict[tuple[int, int], list[Point]]]:
    """Findet die quadratischen Flächen eines achsparallelen Würfelnetzes."""
    edges = [math.dist(a, b) for a, b in zip(tn.net, tn.net[1:] + tn.net[:1])]
    size = sorted(edges)[len(edges) // 2]
    x0 = min(x for x, _ in tn.net)
    y0 = min(y for _, y in tn.net)
    cols = round((max(x for x, _ in tn.net) - x0) / size)
    rows = round((max(y for _, y in tn.net) - y0) / size)
    faces = {}
    for r in range(rows):
        for c in range(cols):
            center = (x0 + (c + 0.5) * size, y0 + (r + 0.5) * size)
            if add_tabs.point_in_polygon(center, tn.net):
                xa, ya = x0 + c * size, y0 + r * size
                faces[(c, r)] = [(xa, ya), (xa + size, ya), (xa + size, ya + size), (xa, ya + size)]
    if len(faces) != 6:
        sys.exit(f"Kein Würfelnetz: {len(faces)} Flächen gefunden")
    return size, faces


def die_numbers(tn: add_tabs.TabbedNet, faces: dict) -> dict[tuple[int, int], int]:
    """Rollt einen Spielwürfel über das Netz: gegenüberliegende Seiten ergeben 7."""
    folds = tn.mountain + tn.valley

    def connected(f, g):
        shared = [p for p in faces[f] if any(add_tabs.close(p, q, 0.05) for q in faces[g])]
        return len(shared) == 2 and any(add_tabs.same_segment(tuple(shared), s) for s in folds)

    # Würfelstellung: welche Zahl liegt unten, oben, in welcher Himmelsrichtung
    start = max(faces, key=lambda f: sum(connected(f, g) for g in faces if g != f))
    state = {start: {"unten": 1, "oben": 6, "n": 2, "s": 5, "o": 3, "w": 4}}
    rolls = {(1, 0): ("o", "w"), (-1, 0): ("w", "o"), (0, -1): ("n", "s"), (0, 1): ("s", "n")}
    queue = deque([start])
    while queue:
        f = queue.popleft()
        for (dc, dr), (fwd, back) in rolls.items():
            g = (f[0] + dc, f[1] + dr)
            if g in faces and g not in state and connected(f, g):
                d = state[f]
                state[g] = {**d, "unten": d[fwd], fwd: d["oben"], "oben": d[back], back: d["unten"]}
                queue.append(g)
    if len(state) != 6:
        sys.exit("Netz nicht zusammenhängend über Faltlinien")
    numbers = {f: s["unten"] for f, s in state.items()}
    assert sorted(numbers.values()) == [1, 2, 3, 4, 5, 6]
    return numbers


def number_svg(face: list[Point], n: int, size: float) -> str:
    cx = sum(x for x, _ in face) / 4
    cy = sum(y for _, y in face) / 4
    fs = 0.72 * size
    baseline = cy + 0.35 * fs  # Ziffernhöhe Andika ≈ 0,7 em, optisch zentriert
    out = (f'<text x="{fmt(cx)}" y="{fmt(baseline)}" text-anchor="middle" '
           f'style="font-family:{NUMBER_FONT};font-weight:bold;font-size:{fmt(fs)}px;'
           f'fill:{NUMBER_COLOR}">{n}</text>')
    if n == 6:
        w, h = 0.36 * fs, 0.055 * fs
        out += (f'\n  <rect x="{fmt(cx - w / 2)}" y="{fmt(baseline + 0.07 * fs)}" width="{fmt(w)}" '
                f'height="{fmt(h)}" rx="{fmt(h / 2)}" fill="{NUMBER_COLOR}"/>')
    return out


# Augenpositionen im 3x3-Raster (-1, 0, 1), wie auf einem Spielwürfel
PIPS = {
    1: [(0, 0)],
    2: [(-1, -1), (1, 1)],
    3: [(-1, -1), (0, 0), (1, 1)],
    4: [(-1, -1), (1, -1), (-1, 1), (1, 1)],
    5: [(-1, -1), (1, -1), (0, 0), (-1, 1), (1, 1)],
    6: [(-1, -1), (-1, 0), (-1, 1), (1, -1), (1, 0), (1, 1)],
}


def pips_svg(face: list[Point], n: int, size: float) -> str:
    """Würfelaugen: Durchmesser 18 % der Kante (bei 55 mm ≈ 10 mm), Raster 27 % der Kante."""
    cx = sum(x for x, _ in face) / 4
    cy = sum(y for _, y in face) / 4
    step, r = 0.27 * size, 0.09 * size
    return "\n  ".join(f'<circle cx="{fmt(cx + i * step)}" cy="{fmt(cy + j * step)}" r="{fmt(r)}" '
                       f'fill="{NUMBER_COLOR}"/>' for i, j in PIPS[n])


# ---------------------------------------------------------------------------
# Legende
# ---------------------------------------------------------------------------

def load_legend(path: Path, has_valley: bool) -> tuple[ET.Element, float, float]:
    root = ET.parse(path).getroot()
    group = next(g for g in root.iter(f"{{{SVG_NS}}}g") if g.get("id") == "legende-zyklus1")
    group = copy.deepcopy(group)
    row_h = float(group.get("data-row-height"))
    top = float(group.get("data-padding-top"))
    bottom = float(group.get("data-padding-bottom"))
    width = float(group.get("data-width"))
    rows = [g for g in group if g.tag == f"{{{SVG_NS}}}g" and g.get("id", "").startswith("legende-")]
    if not has_valley:
        for g in rows:
            if g.get("id") == "legende-talfalte":
                group.remove(g)
        rows = [g for g in rows if g.get("id") != "legende-talfalte"]
    for i, g in enumerate(rows):
        g.set("transform", f"translate(0,{fmt(top + i * row_h)})")
    height = top + len(rows) * row_h + bottom
    frame = next(e for e in group if e.get("id") == "legende-rahmen")
    frame.set("height", fmt(height))
    return group, width, height


def element_svg(el: ET.Element) -> str:
    s = ET.tostring(el, encoding="unicode")
    return re.sub(r'\s+xmlns(:\w+)?="[^"]+"', "", s)


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

def rect_hits_shape(rect: tuple[float, float, float, float], tn: add_tabs.TabbedNet, gap: float) -> bool:
    x0, y0, x1, y1 = rect[0] - gap, rect[1] - gap, rect[2] + gap, rect[3] + gap
    corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    shape = tn.outline
    if any(x0 <= x <= x1 and y0 <= y <= y1 for x, y in shape):
        return True
    if any(add_tabs.point_in_polygon(c, shape) for c in corners):
        return True
    rect_edges = list(zip(corners, corners[1:] + corners[:1]))
    return any(add_tabs.segments_cross(e, s) for e in rect_edges for s in zip(shape, shape[1:] + shape[:1]))


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("input", help="SVG aus Paper Model (wuerfel-unfolded.svg)")
    p.add_argument("output", help="Ausgabe-SVG (wuerfel-final.svg)")
    p.add_argument("--legend", type=Path, default=DEFAULT_LEGEND, help="Legenden-Vorlage")
    p.add_argument("--tab-height", type=float, default=15.0, help="Laschenhöhe in mm (Standard 15)")
    p.add_argument("--cut-width", type=float, default=0.8, help="Schnittlinie in mm (Standard 0,8)")
    p.add_argument("--margin", type=float, default=10.0, help="Seitenrand in mm (Standard 10)")
    p.add_argument("--motiv", choices=("ziffern", "augen"), default="ziffern",
                   help="Ziffern 1–6 (Standard) oder Würfelaugen")
    args = p.parse_args(argv)

    page_w, page_h, m = 210.0, 297.0, args.margin
    tn = add_tabs.build_tabs(add_tabs.load_paper_model_svg(args.input), args.tab_height, 45.0)
    if tn.warnings or tn.overlaps:
        sys.exit("Laschen-Problem: " + "; ".join(tn.warnings + tn.overlaps))
    tn = add_tabs.align_to_axes(tn)

    legend, lw, lh = load_legend(args.legend, has_valley=bool(tn.valley))
    stroke = 0.2  # halbe Rahmenstrichbreite, damit der Rand exakt frei bleibt
    lx, ly = page_w - m - lw - stroke, page_h - m - lh - stroke
    legend_rect = (lx, ly, lx + lw, ly + lh)

    # Netz horizontal zentrieren, vertikal möglichst mittig, mit mindestens 4 mm Abstand zur Legende
    # (beim 55-mm-Würfel bleiben unter dem Netz nur 4,7 mm bis zur Legende)
    x0, y0, x1, y1 = tn.bbox()
    if x1 - x0 > page_w - 2 * m or y1 - y0 > page_h - 2 * m:
        sys.exit(f"Netz {fmt(x1 - x0)} x {fmt(y1 - y0)} mm passt nicht auf A4 mit {fmt(m)} mm Rand")
    dx = m + (page_w - 2 * m - (x1 - x0)) / 2 - x0
    dy = m + (page_h - 2 * m - (y1 - y0)) / 2 - y0
    while rect_hits_shape(legend_rect, tn.transform(lambda q: (q[0] + dx, q[1] + dy)), gap=4.0):
        dy -= 0.5
        if y0 + dy < m:
            sys.exit("Netz und Legende passen nicht gemeinsam auf die Seite")
    tn = tn.transform(lambda q: (round(q[0] + dx, 3), round(q[1] + dy, 3)))

    size, faces = find_faces(tn)
    numbers = die_numbers(tn, faces)
    fills = [(faces[f], FACE_COLORS[numbers[f]]) for f in sorted(faces)]

    layers = add_tabs.render_layers(tn, cut_width=args.cut_width, face_fills=fills)
    if args.motiv == "augen":
        layers.append(add_tabs.layer("Augen", "augen",
                                     [pips_svg(faces[f], numbers[f], size) for f in sorted(faces)]))
    else:
        layers.append(add_tabs.layer("Zahlen", "zahlen",
                                     [number_svg(faces[f], numbers[f], size) for f in sorted(faces)]))
    legend.set("transform", f"translate({fmt(lx)},{fmt(ly)})")
    layers.append(add_tabs.layer("Legende", "legende", [element_svg(legend)]))
    # Fusszeile für Erwachsene, links neben der Legende (max. Breite lx - m - 5 mm)
    footer = (f'<text x="{fmt(m)}" y="{fmt(page_h - m - 1)}" style="font-family:{NUMBER_FONT};'
              f'font-size:3px;fill:{FOOTER_COLOR}">Papercraft-KI · Würfel {fmt(size)} mm · '
              f'160–200 g/m² · in Originalgrösse (100 %) drucken</text>')
    layers.append(add_tabs.layer("Fusszeile", "fusszeile", [footer]))

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(add_tabs.SVG_HEAD.format(w=fmt(page_w), h=fmt(page_h)))
        f.write("\n".join(layers))
        f.write("\n</svg>\n")

    pairs = sorted((numbers[f], f) for f in faces)
    print(f"Würfel {fmt(size)} mm, {len(tn.tabs)} Laschen, Flächen: "
          + ", ".join(f"{n}@{c}" for n, c in pairs) + f" -> {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
