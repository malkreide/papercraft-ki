# Hilfsskripte

Headless-Bausteine für die Pipeline. Python 3.10+, nur Standardbibliothek; `unfold_obj.py` läuft in Blender (`bpy`).

| Skript | Zweck | Läuft mit |
|---|---|---|
| `unfold_obj.py` | OBJ → entfaltetes SVG über das Add-on «Export Paper Model» | `blender --background --python` |
| `add_tabs.py` | Paper-Model-Laschen durch 15-mm-Trapezlaschen ersetzen, Linien nach README «Schritt 4» stylen (Ersatz für Tabgen) | `python` |
| `make_wuerfel_final.py` | Würfel-Bogen für Zyklus 1: Zahlen 1–6, Flächenfarben, Legende, A4-Layout | `python` |

Aufrufbeispiele stehen im Docstring jedes Skripts und in [examples/01-wuerfel-einstieg/README.md](../examples/01-wuerfel-einstieg/README.md).

## Warum Paper-Model-Laschen statt «No Tabs»?

README und WORKFLOW empfehlen in Paper Model «No Tabs» und Laschen später mit Tabgen. Tabgen setzt aber an *jede* Aussenkante eine Lasche – beim Würfel 14 statt 7, sodass Lasche auf Lasche geklebt würde. Paper Model weiss aus dem 3D-Modell, welche Kanten zusammengehören, und setzt pro Paar genau eine Lasche. `add_tabs.py` übernimmt diese Auswahl und ersetzt nur Form und Grösse.

## Programmpfade

`.exe`-Pfade auf dem Windows-Entwicklungsrechner beim ersten Lauf ermitteln (`Get-Command blender`, `Get-Command inkscape`) und hier eintragen.

| Programm | Windows | Linux (Testlauf 9. Oktober 2026) |
|---|---|---|
| Blender | noch nicht ermittelt | `/usr/bin/blender` (4.0.2, Ubuntu-Paket, Paper Model 1.2 enthalten) |
| Inkscape | noch nicht ermittelt | `/usr/bin/inkscape` (1.2.2, Ubuntu-Paket) |
| Python | noch nicht ermittelt | `/usr/bin/python3` (3.13) |

Hinweise aus dem Testlauf:

- Paper Model braucht headless `scene.paper_model.use_auto_scale = False`, sonst bricht der Export mit «An island is too big» ab (das Skript setzt das).
- Ab Blender 4.2 ist Paper Model eine Extension; Modulname gegebenenfalls mit `--addon` übergeben (nicht getestet).
- Die Ziffern nutzen die Schrift Andika (SIL, OFL). Fürs PDF `--export-text-to-path` verwenden, dann ist die Schrift beim Drucken nicht nötig.
