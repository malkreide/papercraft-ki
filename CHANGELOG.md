# Changelog

Alle wesentlichen Änderungen an diesem Projekt werden in dieser Datei festgehalten.

Das Format folgt [Keep a Changelog](https://keepachangelog.com/de/1.0.0/),
die Versionierung [Semantic Versioning](https://semver.org/lang/de/).

## [Unreleased]

### Added
- `examples/01-wuerfel-einstieg/`: Würfel-Bastelbogen für 5–6-Jährige (`wuerfel.obj`, `wuerfel-unfolded.svg`, `wuerfel-final.svg`, `wuerfel-final.pdf`, Vorschau-PNG), headless erzeugt, noch nicht gebaut
- `scripts/unfold_obj.py`: OBJ headless mit Blender und Paper Model entfalten
- `scripts/add_tabs.py`: Trapezlaschen (Standard 15 mm, 45°) und Linienkodierung nach README «Schritt 4», Ersatz für Tabgen mit Überlappungsprüfung
- `scripts/make_wuerfel_final.py`: Zahlen 1–6 (Gegenseiten ergeben 7), Legende und A4-Layout für den Würfel
- `templates/inkscape/legende-zyklus1.svg`: Legende mit Icons für Zyklus 1
- Würfel-Variante mit Würfelaugen statt Ziffern (`wuerfel-augen-final.*`, `scripts/make_wuerfel_final.py --motiv augen`)

### Changed
- Würfel-Beispiel auf 55 mm Kantenlänge vergrössert (vorher 50 mm); Mindestabstand Netz–Legende in `scripts/make_wuerfel_final.py` von 5 auf 4 mm, damit beides auf A4 passt
- `docs/PAEDAGOGIK.md`: Linienstil der Faltlinien an README und WORKFLOW angeglichen (Bergfalte gestrichelt 5/3 statt Strich-Punkt, Talfalte gestrichelt 3/3)

### Geplant
- Projekt A (Würfel) real bauen: Zeitaufwand und Foto in `examples/01-wuerfel-einstieg/README.md`
- Weitere Inkscape-Vorlagen (Legende Zyklus 2, Symbole) in `templates/inkscape/`
- Beurteilungsraster für Lehrpersonen (Zyklus 1 und 2)
- MI-Kompetenzstufen gegen das offizielle Poster prüfen

## [0.1.0] - 2026-10-08

### Added
- Dokumentation des fünfstufigen Workflows: Generieren → Vereinfachen → Entfalten → Gestalten → Bauen
- `docs/LEHRPLAN21.md`: Kompetenzmatrix TTG, Mathematik und MI, gegen die Kompetenz-Poster des Lehrplan 21 (Zyklus 1 und 2) abgeglichen
- `docs/PAEDAGOGIK.md`: Feinmotorik, räumliches Vorstellungsvermögen, Zone der nächsten Entwicklung, Differenzierung
- `docs/WORKFLOW.md`: technischer Deep-Dive inkl. Vergleich der offenen 3D-Modelle (Stand Oktober 2026)
- `docs/INSTALLATION.md`: Blender, Inkscape (Tabgen via MightyScape), Blockbench, TripoSR, TRELLIS.2, ComfyUI
- Zwei Einstiegsprojekte (Würfel ab 5 Jahren, LKW ab 7 Jahren) als Beschreibung
- Workshop-Format (90 Min.) und Differenzierungshinweise für Lehrpersonen
