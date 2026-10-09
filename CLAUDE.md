# CLAUDE.md – Arbeitsregeln für dieses Repository

Dieses Repo dokumentiert einen FOSS-Workflow für pädagogische Papercraft-Bastelbögen (Blockbench/KI → Blender → Paper Model → Inkscape → Bauen) mit Bezug zum Schweizer Lehrplan 21. Zielgruppe: Eltern und Lehrpersonen, Kinder 5–12 Jahre. Privates Projekt von Hayal Özkan (`malkreide`), MIT-Lizenz.

## Zuerst lesen

1. `.github/repo-meta.yml` – einzige Quelle für Name, Description, Topics, Version, Autor. Werte dort ändern, nicht in einzelnen Dateien raten.
2. `README.md` – Abschnitt «Status» oben sagt, was getestet ist und was nicht.
3. `CHANGELOG.md` – `[Unreleased]` → «Geplant» ist die Roadmap.

## Sprache und Stil

- Deutsch mit **schweizerischer Rechtschreibung**: `ss` statt `ß`, immer. Guillemets «…» als Anführungszeichen.
- `README.md` ist bewusst die deutsche Hauptdatei, `README.en.md` die englische Kurzfassung. Nicht umdrehen.
- Keine Emoji in Überschriften. Im Fliesstext sparsam.
- Technische Begriffe, Befehle, Menüpfade und Code bleiben englisch (Edit Mode, Decimate Modifier, `--background`).
- Schluss-Sektionen der READMEs in dieser Reihenfolge: Danksagung → Changelog → Mitmachen → Sicherheit → Lizenz → Autor.

## Qualitätsregeln für Inhalte

- **Lehrplan 21:** Jeder Kompetenzcode wird gegen die offiziellen Kompetenz-Poster auf `v-ef.lehrplan.ch/container/STAMM_DE_Poster_*.pdf` geprüft, bevor er in `docs/LEHRPLAN21.md` landet. Wortlaut zitieren (gekürzt mit «…»), Stufenkennung mitführen (`TTG.2.D.1.2a`). Was nicht geprüft werden konnte, steht als solches im Verifizierungsblock am Dateianfang – nie stillschweigend aufnehmen.
- **KI-Modelle:** Angaben zu Modellen, VRAM und Lizenzen tragen ein Datum («Stand Oktober 2026»). Vor dem Ändern das jeweilige GitHub-Repository prüfen, nicht aus dem Gedächtnis schreiben.
- **Zahlen:** Zeitangaben, Polygonzahlen, Laschengrössen, Altersgrenzen sind Heuristiken, bis sie durch einen realen Durchlauf belegt sind. Belegte Werte in `examples/*/README.md` dokumentieren und dann in die Hauptdokumentation übernehmen – nicht umgekehrt.
- **Nichts versprechen, was nicht da ist:** Ordner und Dateien, die noch nicht existieren, werden als «(Roadmap)» gekennzeichnet. Keine toten Links.

## Technische Arbeit

- Entwicklungsrechner ist **Windows mit PowerShell**: Befehle einzeln je Zeile, kein `&&`. Blender und Inkscape laufen headless (`blender --background --python …`, `inkscape --actions=…`); Pfade zu den `.exe` beim ersten Mal ermitteln und in `scripts/README.md` festhalten.
- Skripte nach `scripts/`, mit Docstring und Aufrufbeispiel. Python 3.10+, nur Standardbibliothek plus `bpy` (in Blender) – keine zusätzlichen Abhängigkeiten ohne Grund.
- Beispielprojekte nach `examples/NN-name/` mit `README.md` (Zielgruppe, Einstellungen, Zeitaufwand real, Foto), `.obj`, `.svg`, `.pdf`. Grosse Binärdateien (Modellgewichte, Renderings über 2 MB) gehören nicht ins Repo.
- Vorlagen nach `templates/inkscape/`, `templates/blender/`, `templates/comfyui/`.

## Git

- Direkt auf `main` committen ist in Ordnung (Solo-Repo); kleine, thematische Commits.
- Conventional Commits: `feat`, `fix`, `docs`, `chore`, `test`.
- Autor-E-Mail: `8864492+malkreide@users.noreply.github.com` (GitHub blockt die private Adresse).
- Vor jedem Push: keine Secrets, keine Personendaten, keine Fotos mit erkennbaren Gesichtern ohne Einverständnis.
- `CHANGELOG.md` bei jedem inhaltlichen Commit unter `[Unreleased]` ergänzen.
- Release-Tag erst, wenn mindestens ein Beispielprojekt real durchlaufen und dokumentiert ist.

## Was dieses Repo nicht ist

Keine offizielle Publikation einer Behörde oder Schule. Keine Aussagen über Lehrpläne anderer Kantone oder Länder ohne Quelle. Kein Marketing für kommerzielle KI-Dienste.
