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

Ermittelt auf dem Windows-Entwicklungsrechner am 9. Oktober 2026 mit `Get-Command` und einer Suche in `C:\Program Files`.

| Programm | Windows (9. Oktober 2026) | Linux (Testlauf 9. Oktober 2026) |
|---|---|---|
| Blender | `C:\Program Files\Blender Foundation\Blender 5.2\blender.exe` (5.2, **nicht im `PATH`**) | `/usr/bin/blender` (4.0.2, Ubuntu-Paket, Paper Model 1.2 enthalten) |
| Inkscape | nicht gefunden – weder im `PATH` noch unter `C:\Program Files\Inkscape\bin` | `/usr/bin/inkscape` (1.2.2, Ubuntu-Paket) |
| Python | `C:\Python313\python.exe` (3.13.8, im `PATH`) | `/usr/bin/python3` (3.13) |

Weil Blender nicht im `PATH` liegt, in PowerShell mit vollem Pfad und Aufrufoperator `&` starten:

```powershell
& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --background --python scripts/unfold_obj.py -- examples/01-wuerfel-einstieg/wuerfel.obj examples/01-wuerfel-einstieg/wuerfel-unfolded.svg --scale 18.181818
```

Für Inkscape unter Windows `inkscape.com` statt `inkscape.exe` verwenden: Nur dann erscheinen Meldungen und Fehler in der Konsole. Pfad nach der Installation hier nachtragen.

Offen auf Windows (nicht getestet):

- **Inkscape** installieren oder den Installationsort ermitteln (z. B. Microsoft Store, Winget, eigener Ordner).
- **Paper Model unter Blender 5.2:** Seit Blender 4.2 ist Paper Model kein mitgeliefertes Add-on mehr, sondern eine Extension, die separat installiert werden muss. Den Modulnamen für `--addon` nach der Installation so ermitteln:

  ```powershell
  & "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --background --python-expr "import addon_utils; print([m.__name__ for m in addon_utils.modules() if 'paper' in m.__name__.lower()])"
  ```

- **`unfold_obj.py` unter Blender 5.2:** Nur mit Blender 4.0.2 getestet. Ob `wm.obj_import` und der Paper-Model-Operator in 5.2 gleich heissen, ist ungeprüft.

Hinweise aus dem Testlauf:

- Paper Model braucht headless `scene.paper_model.use_auto_scale = False`, sonst bricht der Export mit «An island is too big» ab (das Skript setzt das).
- Die Ziffern nutzen die Schrift Andika (SIL, OFL). Fürs PDF `--export-text-to-path` verwenden, dann ist die Schrift beim Drucken nicht nötig.
