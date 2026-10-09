# Vorlagen (Templates)

Dieses Verzeichnis enthält wiederverwendbare Vorlagen für den Workflow.

## Verzeichnisstruktur

```
templates/
├── comfyui/          # ComfyUI-Workflow-Dateien (.json)
│   ├── text-to-3d-basic.json            (Roadmap)
│   └── image-to-3d-triposr.json         (Roadmap)
├── inkscape/         # Inkscape-Vorlagen (.svg)
│   ├── legende-zyklus1.svg      # Legende mit Icons für 5–7-Jährige
│   ├── legende-zyklus2.svg      # Legende mit Text für 8–12-Jährige (Roadmap)
│   ├── farbschema-standard.svg  # Standard-Farbkodierung (Roadmap)
│   └── symbole-matching.svg     # Symbol-Paare für Laschen-Zuordnung (Roadmap)
└── blender/          # Blender-Presets
    ├── decimate-kinderfreundlich.py  # Preset: Planar, Angle 15° (Roadmap)
    └── seams-fahrzeug.py             # Beispiel-Seams für Fahrzeugtypen (Roadmap)
```

## Nutzung

### ComfyUI-Workflows

Die `.json`-Dateien per Drag & Drop in die ComfyUI-Oberfläche ziehen. Checkpoints und Custom Nodes müssen separat installiert sein (siehe [docs/INSTALLATION.md](../docs/INSTALLATION.md)).

### Inkscape-Vorlagen

Die SVG-Vorlagen in Inkscape öffnen und Elemente per Copy-Paste in den eigenen Bastelbogen übernehmen.

`legende-zyklus1.svg` enthält vier Zeilen (Schneiden, Bergfalte, Talfalte, Kleben) als Icons; die grauen Wörter sind für die begleitende erwachsene Person. Zeilen, die auf dem Bogen nicht vorkommen, löschen. `scripts/make_wuerfel_final.py` liest die Vorlage direkt und lässt nicht benötigte Zeilen automatisch weg.

### Blender-Presets

Die Python-Skripte in Blenders Scripting-Tab laden und ausführen, oder als Add-on installieren.
