"""Ersetzt die kleinen Paper-Model-Laschen durch kindgerechte Trapezlaschen und stylt die Linien.

Ersatz für die Inkscape-Erweiterung Tabgen, wenn diese nicht headless läuft oder nicht
installiert ist. Tabgen setzt Laschen an *alle* Aussenkanten eines Pfads; dieses Skript
setzt sie nur an die Kanten, die Paper Model als Laschenkante gewählt hat (eine Kante pro
Klebepaar, beim Würfel 7 statt 14).

Eingabe: SVG aus dem Blender-Add-on «Export Paper Model» (``scripts/unfold_obj.py``) mit
``class='outer'`` (Umriss), ``class='convex'`` (Bergfalten), ``class='concave'``
(Talfalten) und ``class='sticker'`` (Laschen).

Ausgabe: SVG mit Inkscape-Ebenen und der Linienkodierung aus README «Schritt 4»:
Schnittlinien schwarz durchgezogen, Bergfalten rot gestrichelt, Talfalten blau gestrichelt,
Laschen grau mit Klebetropfen-Symbol.

Das Skript bricht mit Exit-Code 2 ab, wenn sich vergrösserte Laschen überlappen oder in
das Netz ragen (``--allow-overlap`` schaltet das ab).

Aufruf (PowerShell, eine Zeile):

    python scripts/add_tabs.py examples/01-wuerfel-einstieg/wuerfel-unfolded.svg wuerfel-tabs.svg --height 15 --angle 45

Nur Python-Standardbibliothek, Python 3.10+.
"""

from __future__ import annotations

import argparse
import math
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

Point = tuple[float, float]
Segment = tuple[Point, Point]

EPS = 1e-3  # mm

# Linienkodierung nach README «Schritt 4» und docs/WORKFLOW.md
STYLE = {
    "cut": "#000000",
    "mountain": "#E74C3C",
    "valley": "#2E86C1",
    "tab_fill": "#D5D8DC",
    "tab_stroke": "#BDC3C7",
    "drop_fill": "#FFFFFF",
    "drop_stroke": "#566573",
}

# Klebetropfen, Spitze oben, zentriert auf (0, 0), Höhe 1
DROP_PATH = ("M 0,-0.5 C 0.17,-0.25 0.32,-0.07 0.32,0.13 "
             "A 0.32,0.32 0 0 1 -0.32,0.13 C -0.32,-0.07 -0.17,-0.25 0,-0.5 Z")


# ---------------------------------------------------------------------------
# Geometrie
# ---------------------------------------------------------------------------

def close(p: Point, q: Point, eps: float = EPS) -> bool:
    return abs(p[0] - q[0]) < eps and abs(p[1] - q[1]) < eps


def same_segment(s: Segment, t: Segment) -> bool:
    return (close(s[0], t[0]) and close(s[1], t[1])) or (close(s[0], t[1]) and close(s[1], t[0]))


def point_in_polygon(p: Point, poly: list[Point]) -> bool:
    x, y = p
    inside = False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            inside = not inside
    return inside


def segments_cross(a: Segment, b: Segment) -> bool:
    """Echte Kreuzung im Inneren beider Strecken (Berühren an Endpunkten zählt nicht)."""
    def orient(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    d1, d2 = orient(*b, a[0]), orient(*b, a[1])
    d3, d4 = orient(*a, b[0]), orient(*a, b[1])
    return d1 * d2 < -EPS and d3 * d4 < -EPS


def convex_overlap(p: list[Point], q: list[Point]) -> bool:
    """Separating Axis Test für zwei konvexe Polygone; Berühren gilt nicht als Überlappung."""
    for poly in (p, q):
        for a, b in zip(poly, poly[1:] + poly[:1]):
            nx, ny = b[1] - a[1], a[0] - b[0]
            pa = [nx * x + ny * y for x, y in p]
            qa = [nx * x + ny * y for x, y in q]
            if min(pa) >= max(qa) - EPS or min(qa) >= max(pa) - EPS:
                return False
    return True


def shrink(poly: list[Point], amount: float = 0.05) -> list[Point]:
    cx = sum(x for x, _ in poly) / len(poly)
    cy = sum(y for _, y in poly) / len(poly)
    out = []
    for x, y in poly:
        d = math.hypot(x - cx, y - cy)
        f = (d - amount) / d if d > amount else 0.0
        out.append((cx + (x - cx) * f, cy + (y - cy) * f))
    return out


def polygon_centroid(poly: list[Point]) -> Point:
    a = cx = cy = 0.0
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        c = x1 * y2 - x2 * y1
        a += c
        cx += (x1 + x2) * c
        cy += (y1 + y2) * c
    a *= 0.5
    return cx / (6 * a), cy / (6 * a)


# ---------------------------------------------------------------------------
# Einlesen
# ---------------------------------------------------------------------------

def parse_polylines(d: str) -> list[list[Point]]:
    """Liest absolute M/L/Z-Pfade, wie Paper Model sie schreibt."""
    tokens = re.findall(r"[MLZmlz]|-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?", d)
    lines: list[list[Point]] = []
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t == "M":
            lines.append([(float(tokens[i + 1]), float(tokens[i + 2]))])
            i += 3
        elif t == "L":
            lines[-1].append((float(tokens[i + 1]), float(tokens[i + 2])))
            i += 3
        elif t in "Zz":
            i += 1
        else:
            raise ValueError(f"Nicht unterstützter Pfadbefehl «{t}» – Pfade zuerst linearisieren")
    return lines


@dataclass
class PaperModelNet:
    outline: list[Point]                 # Umriss inkl. Paper-Model-Laschen
    stickers: list[list[Point]]          # je 4 Punkte: Basis-Anfang, oben, oben, Basis-Ende
    mountain: list[Segment]
    valley: list[Segment]


def load_paper_model_svg(path: str) -> PaperModelNet:
    root = ET.parse(path).getroot()
    by_class: dict[str, list[list[Point]]] = {}
    for el in root.iter():
        if el.tag.endswith("path") and el.get("class") in {"outer", "convex", "concave", "sticker"}:
            by_class.setdefault(el.get("class"), []).extend(parse_polylines(el.get("d", "")))
    outers = by_class.get("outer", [])
    if len(outers) != 1:
        sys.exit(f"Erwartet genau eine Insel (class='outer'), gefunden: {len(outers)}")

    def segments(polys):
        segs: list[Segment] = []
        for pl in polys:
            for s in zip(pl, pl[1:]):
                if not any(same_segment(s, t) for t in segs):
                    segs.append(s)
        return segs

    return PaperModelNet(
        outline=outers[0],
        stickers=by_class.get("sticker", []),
        mountain=segments(by_class.get("convex", [])),
        valley=segments(by_class.get("concave", [])),
    )


# ---------------------------------------------------------------------------
# Laschen bauen
# ---------------------------------------------------------------------------

@dataclass
class TabbedNet:
    net: list[Point]                     # Netz ohne Laschen
    outline: list[Point]                 # Schnittlinie inkl. neuer Laschen
    tabs: list[list[Point]]              # Trapeze: Basis-Anfang, oben, oben, Basis-Ende
    mountain: list[Segment]
    valley: list[Segment]
    warnings: list[str] = field(default_factory=list)   # z. B. verkleinerte Laschen
    overlaps: list[str] = field(default_factory=list)   # Fehler: Laschen überlappen

    def transform(self, fn) -> "TabbedNet":
        seg = lambda s: (fn(s[0]), fn(s[1]))  # noqa: E731
        return TabbedNet(
            net=[fn(p) for p in self.net],
            outline=[fn(p) for p in self.outline],
            tabs=[[fn(p) for p in t] for t in self.tabs],
            mountain=[seg(s) for s in self.mountain],
            valley=[seg(s) for s in self.valley],
            warnings=self.warnings,
            overlaps=self.overlaps,
        )

    def bbox(self) -> tuple[float, float, float, float]:
        xs = [x for x, _ in self.outline]
        ys = [y for _, y in self.outline]
        return min(xs), min(ys), max(xs), max(ys)


def build_tabs(pm: PaperModelNet, height: float = 15.0, angle: float = 45.0,
               min_top: float = 5.0) -> TabbedNet:
    tops = [p for s in pm.stickers for p in s[1:3]]
    net = [p for p in pm.outline if not any(close(p, t) for t in tops)]
    bases = [(s[0], s[-1]) for s in pm.stickers]
    warnings: list[str] = []

    outline: list[Point] = []
    tabs: list[list[Point]] = []
    for a, b in zip(net, net[1:] + net[:1]):
        outline.append(a)
        if not any(same_segment((a, b), base) for base in bases):
            continue
        length = math.dist(a, b)
        tx, ty = (b[0] - a[0]) / length, (b[1] - a[1]) / length
        nx, ny = ty, -tx
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        if point_in_polygon((mid[0] + nx * 0.1, mid[1] + ny * 0.1), net):
            nx, ny = -nx, -ny
        h = height
        inset = h / math.tan(math.radians(angle))
        if length - 2 * inset < min_top:
            inset = (length - min_top) / 2
            h = min(h, inset * math.tan(math.radians(angle)))
            warnings.append(f"Kante {length:.1f} mm zu kurz: Lasche auf {h:.1f} mm verkleinert")
        a2 = (a[0] + nx * h + tx * inset, a[1] + ny * h + ty * inset)
        b2 = (b[0] + nx * h - tx * inset, b[1] + ny * h - ty * inset)
        outline += [a2, b2]
        tabs.append([a, a2, b2, b])

    result = TabbedNet(net, outline, tabs, pm.mountain, pm.valley, warnings)
    result.overlaps = find_overlaps(result)
    return result


def find_overlaps(tn: TabbedNet) -> list[str]:
    problems = []
    net_edges = list(zip(tn.net, tn.net[1:] + tn.net[:1]))
    for i, tab in enumerate(tn.tabs):
        small = shrink(tab)
        if any(point_in_polygon(p, tn.net) for p in small) or any(
                segments_cross(e, n) for e in zip(small, small[1:] + small[:1]) for n in net_edges):
            problems.append(f"Lasche {i + 1} ragt ins Netz")
        for j in range(i + 1, len(tn.tabs)):
            if convex_overlap(tab, tn.tabs[j]):
                problems.append(f"Lasche {i + 1} überlappt Lasche {j + 1}")
    return problems


def canonical(tn: TabbedNet) -> TabbedNet:
    """Feste Reihenfolge aller Elemente, damit gleiche Geometrie gleiches SVG ergibt.

    Paper Model beginnt den Umriss bei jedem Lauf an einem anderen Punkt."""
    def from_min(poly):
        i = min(range(len(poly)), key=lambda k: (poly[k][1], poly[k][0]))
        return poly[i:] + poly[:i]

    def norm(seg):
        return tuple(sorted(seg, key=lambda p: (p[1], p[0])))

    key = lambda p: (round(p[1], 2), round(p[0], 2))  # noqa: E731
    return TabbedNet(
        net=from_min(tn.net),
        outline=from_min(tn.outline),
        tabs=sorted(tn.tabs, key=lambda t: sorted(map(key, t))),
        mountain=sorted(map(norm, tn.mountain), key=lambda s: [key(p) for p in s]),
        valley=sorted(map(norm, tn.valley), key=lambda s: [key(p) for p in s]),
        warnings=tn.warnings,
        overlaps=tn.overlaps,
    )


def align_to_axes(tn: TabbedNet) -> TabbedNet:
    """Dreht das Netz so, dass die längste Netzkante achsparallel liegt, und legt es auf (0, 0)."""
    edges = list(zip(tn.net, tn.net[1:] + tn.net[:1]))
    (x1, y1), (x2, y2) = max(edges, key=lambda e: (round(math.dist(*e), 2), -e[0][1], -e[0][0]))
    theta = math.atan2(y2 - y1, x2 - x1)
    theta -= round(theta / (math.pi / 2)) * (math.pi / 2)
    c, s = math.cos(-theta), math.sin(-theta)
    rotated = tn.transform(lambda p: (c * p[0] - s * p[1], s * p[0] + c * p[1]))
    x0, y0, _, _ = rotated.bbox()
    return canonical(rotated.transform(lambda p: (round(p[0] - x0, 4), round(p[1] - y0, 4))))


# ---------------------------------------------------------------------------
# SVG schreiben
# ---------------------------------------------------------------------------

def fmt(v: float) -> str:
    return f"{v:.3f}".rstrip("0").rstrip(".")


def poly_d(poly: list[Point]) -> str:
    return "M " + " L ".join(f"{fmt(x)},{fmt(y)}" for x, y in poly) + " Z"


def fitted_dash(length: float, dash: float, gap: float) -> str:
    """Strichmuster so strecken, dass die Linie an beiden Enden mit einem Strich endet."""
    k = max(1, round((length + gap) / (dash + gap)))
    f = (length + gap) / (k * (dash + gap))
    return f"{fmt(dash * f)},{fmt(gap * f)}"


def drop_icon(cx: float, cy: float, size: float) -> str:
    return (f'<path d="{DROP_PATH}" transform="translate({fmt(cx)},{fmt(cy)}) scale({fmt(size)})" '
            f'fill="{STYLE["drop_fill"]}" stroke="{STYLE["drop_stroke"]}" '
            f'stroke-width="{fmt(0.4 / size)}" stroke-linejoin="round"/>')


def layer(label: str, ident: str, body: list[str]) -> str:
    return (f'<g inkscape:groupmode="layer" inkscape:label="{label}" id="{ident}">\n  '
            + "\n  ".join(body) + "\n</g>")


def render_layers(tn: TabbedNet, cut_width: float = 0.8, fold_width: float = 0.5,
                  face_fills: list[tuple[list[Point], str]] | None = None) -> list[str]:
    """Liefert die Inkscape-Ebenen (unten nach oben) als SVG-Fragmente."""
    out = []
    out.append(layer("Laschen", "laschen", [
        f'<path d="{poly_d(t)}" fill="{STYLE["tab_fill"]}" stroke="{STYLE["tab_stroke"]}" '
        f'stroke-width="0.2"/>' for t in tn.tabs]))
    if face_fills:
        out.append(layer("Flaechen", "flaechen", [
            f'<path d="{poly_d(p)}" fill="{c}" stroke="none"/>' for p, c in face_fills]))
    folds = []
    for segs, color, dash, gap, ident in ((tn.mountain, STYLE["mountain"], 5, 3, "berg"),
                                          (tn.valley, STYLE["valley"], 3, 3, "tal")):
        for (a, b) in segs:
            folds.append(
                f'<path class="{ident}falte" d="M {fmt(a[0])},{fmt(a[1])} L {fmt(b[0])},{fmt(b[1])}" '
                f'fill="none" stroke="{color}" stroke-width="{fmt(fold_width)}" '
                f'stroke-dasharray="{fitted_dash(math.dist(a, b), dash, gap)}" stroke-linecap="butt"/>')
    out.append(layer("Faltlinien", "faltlinien", folds))
    drops = []
    for t in tn.tabs:
        cx, cy = polygon_centroid(t)
        top = math.dist(t[1], t[2])
        h = math.dist(((t[0][0] + t[3][0]) / 2, (t[0][1] + t[3][1]) / 2),
                      ((t[1][0] + t[2][0]) / 2, (t[1][1] + t[2][1]) / 2))
        drops.append(drop_icon(cx, cy, min(0.62 * h, 0.9 * top)))
    out.append(layer("Klebetropfen", "klebetropfen", drops))
    out.append(layer("Schnittlinien", "schnittlinien", [
        f'<path d="{poly_d(tn.outline)}" fill="none" stroke="{STYLE["cut"]}" '
        f'stroke-width="{fmt(cut_width)}" stroke-linejoin="miter" stroke-miterlimit="10"/>']))
    return out


SVG_HEAD = ('<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
            '<svg xmlns="http://www.w3.org/2000/svg" '
            'xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" '
            'xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd" '
            'width="{w}mm" height="{h}mm" viewBox="0 0 {w} {h}">\n'
            '<sodipodi:namedview inkscape:document-units="mm"/>\n')


def write_svg(path: str, tn: TabbedNet, page: tuple[float, float], margin: float,
              cut_width: float, fold_width: float) -> None:
    x0, y0, x1, y1 = tn.bbox()
    w, h = page
    dx = margin + (w - 2 * margin - (x1 - x0)) / 2 - x0
    dy = margin + (h - 2 * margin - (y1 - y0)) / 2 - y0
    body = render_layers(tn.transform(lambda p: (p[0] + dx, p[1] + dy)), cut_width, fold_width)
    with open(path, "w", encoding="utf-8") as f:
        f.write(SVG_HEAD.format(w=fmt(w), h=fmt(h)))
        f.write("\n".join(body))
        f.write("\n</svg>\n")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("input", help="SVG aus Paper Model")
    p.add_argument("output", help="Ausgabe-SVG")
    p.add_argument("--height", type=float, default=15.0, help="Laschenhöhe in mm (Standard 15)")
    p.add_argument("--angle", type=float, default=45.0, help="Flankenwinkel in Grad (Standard 45)")
    p.add_argument("--cut-width", type=float, default=0.8, help="Schnittlinie in mm (Standard 0,8)")
    p.add_argument("--fold-width", type=float, default=0.5, help="Faltlinie in mm (Standard 0,5)")
    p.add_argument("--page", default="210x297", help="Seitengrösse BxH in mm (Standard A4 hochkant)")
    p.add_argument("--margin", type=float, default=10.0, help="Rand in mm (Standard 10)")
    p.add_argument("--no-align", action="store_true", help="Netz nicht achsparallel drehen")
    p.add_argument("--allow-overlap", action="store_true", help="Überlappende Laschen nur melden")
    args = p.parse_args(argv)

    tn = build_tabs(load_paper_model_svg(args.input), args.height, args.angle)
    if not args.no_align:
        tn = align_to_axes(tn)
    for w in tn.warnings + tn.overlaps:
        print("WARNUNG:", w, file=sys.stderr)
    if tn.overlaps and not args.allow_overlap:
        return 2
    page = tuple(float(v) for v in args.page.lower().split("x"))
    write_svg(args.output, tn, page, args.margin, args.cut_width, args.fold_width)
    x0, y0, x1, y1 = tn.bbox()
    note = " (teils verkleinert, siehe Warnungen)" if tn.warnings else ""
    print(f"{len(tn.tabs)} Laschen à {fmt(args.height)} mm{note}, Netz {fmt(x1 - x0)} x {fmt(y1 - y0)} mm -> {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
