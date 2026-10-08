# Technischer Workflow: Deep Dive

> Detaillierte technische Dokumentation aller Pipeline-Schritte mit Parametern, Algorithmen und Troubleshooting.

---

## Pipeline-Architektur

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  1. GENERATE │────▶│  2. SIMPLIFY │────▶│  3. UNFOLD   │────▶│  4. LAYOUT   │────▶│  5. BUILD    │
│              │     │              │     │              │     │              │     │              │
│ Blockbench  │     │ Blender      │     │ Blender      │     │ Inkscape     │     │ Drucker      │
│ TripoSR     │     │ MeshLab      │     │ Paper Model  │     │ Tabgen       │     │ Schere       │
│ TRELLIS.2   │     │ Blockbench   │     │ Add-on       │     │              │     │ Klebstoff    │
│              │     │              │     │              │     │              │     │              │
│ .png → .obj │     │ .obj → .obj  │     │ .obj → .svg  │     │ .svg → .svg  │     │ .svg → 🎉   │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

---

## Schritt 1: 3D-Modell generieren

### Modellwahl: Welches KI-Modell für welchen Zweck?

Die Landschaft der offenen 3D-Generierungsmodelle verändert sich innert Monaten. Dieser Abschnitt gibt den Stand vom **Oktober 2026** wieder; vor einer Installation lohnt sich ein Blick auf die jeweiligen Repositories.

| Modell | Hersteller / Datum | Lizenz | Eingabe | VRAM (lokal) | Stärke | Schwäche | Empfehlung |
|---|---|---|---|---|---|---|---|
| **Blockbench** (kein KI) | JannisX11 | GPL-3.0 | Hand | keine GPU | Perfekte Box-Topologie, Kind baut mit | Nur Quader-Formen | **Einstieg und Schule** |
| **TripoSR** | Stability AI + Tripo, März 2024 | MIT | Bild | ab 6 GB | Schnellstes Modell, geringste Hürde, geschlossene Hüllen | Unscharfe Texturen, grobe Details | **KI-Einstieg** |
| **TRELLIS.2** | Microsoft Research, Dez. 2025 | MIT | Bild | ab 12–16 GB | Beste Geometrie unter offenen Modellen, wenig Floaters | Aufwendige Installation, hoher VRAM | **KI-Qualitätsstufe** |
| **Hunyuan3D 2.1** | Tencent, Juni 2025 | Tencent Community | Bild / Text | ab 12 GB | Beste Texturen, Text-Eingabe | Lizenz nicht vollständig offen; neuere 3.x-Versionen nur gehostet | Alternative, wenn Texturen wichtig sind |
| **Stable Fast 3D** | Stability AI | Community | Bild | ab 6 GB | Nachfolger von TripoSR, unter 1 Sekunde | Lizenz prüfen (nicht MIT) | Alternative zu TripoSR |
| Shap-E | OpenAI, 2023 | MIT | Text / Bild | ab 6 GB | Direkte Text-Eingabe, organische Formen | «Blob»-Topologie, niedrige Auflösung, veraltet | Nur noch für Experimente |

**Warum Qualität für Papercraft zweitrangig ist:** Jedes KI-Modell wird in Schritt 2 auf 20–50 Flächen reduziert. Ob das Rohmodell 50'000 oder 500'000 Dreiecke hat, ist nach der Planar Decimation egal. Entscheidend sind zwei Eigenschaften:

1. **Geschlossene Hülle** (manifold) – alle genannten Modelle liefern das meistens, TRELLIS.2 am zuverlässigsten.
2. **Keine «Floaters»** (lose schwebende Fragmente) – hier ist TRELLIS.2 klar besser als TripoSR. Floaters werden beim Entfalten zu unverbundenen Mini-Teilen, die ein Kind nicht zuordnen kann.

Für einfache Objekte (Fahrzeuge, Gebäude) genügt TripoSR. Für organische Objekte (Tiere, Figuren) oder Architektur mit Details lohnt sich TRELLIS.2.

### TripoSR: Architektur und Parameter

TripoSR basiert auf der **LRM-Architektur** (Large Reconstruction Model). Im Gegensatz zu optimierungsbasierten Verfahren (NeRFs) ist es ein Feed-Forward-Modell: Es inferiert die 3D-Struktur in einem einzigen Durchlauf.

**Leistung nach GPU (Richtwerte):**

| GPU | Inference-Zeit | VRAM-Bedarf |
|---|---|---|
| RTX 4090 | < 1 Sek. | ~6–8 GB |
| RTX 3060 (12 GB) | < 2 Sek. | ~6–8 GB |
| RTX 3060 (6 GB) | ~3 Sek. | Grenzwertig, Auflösung reduzieren |
| CPU (ohne GPU) | 1–5 Min. | – |

**Stärken für Papercraft:**

- Generiert geschlossene Hüllen («Manifold»-Geometrie)
- Schnelle Iteration: verschiedene Perspektiven ausprobieren
- Läuft auf Consumer-Hardware und notfalls auf der CPU

**Schwächen:**

- Texturunschärfe (Farben werden oft verwaschen)
- Benötigt ein Eingabebild (nicht direkt aus Text)
- Neigt zu Floaters bei komplexen Silhouetten

### TRELLIS.2: Strukturierte Latents

TRELLIS arbeitet mit «Structured Latents» (SLAT): einer spärlichen 3D-Gitterstruktur, aus der Meshes, Gaussian Splats oder Radiance Fields dekodiert werden können. Die Version 2 (Dezember 2025) ist das aktuell beste frei herunterladbare Modell für Bild-zu-3D.

**Für Papercraft relevant:**

- Deutlich weniger Floaters als TripoSR
- Saubere, geschlossene Meshes mit klaren Kanten – die Planar Decimation funktioniert besser
- Optional PBR-Texturen (für Papercraft nicht nötig)

**Nachteile:**

- Installation umfangreicher (mehrere Abhängigkeiten, CUDA-Kernel-Kompilierung)
- VRAM-Bedarf ab 12–16 GB je nach Variante
- Generierung dauert 15–30 Sekunden statt unter 2

### Eingabebild-Optimierung (für alle Bild-zu-3D-Modelle)

Die Qualität des Eingabebilds bestimmt die Qualität des 3D-Modells:

- **Freigestellt** vor hellem/weissem Hintergrund
- **Einfache, klare Formen** (Low-Poly-Stil ist ideal)
- **Perspektive:** Leichte Dreiviertelansicht zeigt mehr Geometrie als Frontalansicht
- **Auflösung:** 512×512 px genügt für TripoSR; TRELLIS.2 profitiert von 1024×1024 px
- **Prompt für die Bildgenerierung** (Stable Diffusion o. ä.): `low poly toy [Objekt], flat shading, simple shapes, white background, 3/4 view`

### Hinweis zur Modellwahl für Schulen

In Schulen ist lokale KI-Generierung selten realistisch: Keine NVIDIA-GPUs, keine Conda-Installation, oft nur Tablets oder Chromebooks. Der sinnvolle Weg für den Unterricht:

- **Zyklus 1:** Lehrperson bereitet Bastelbögen zu Hause oder im Makerspace vor (Blockbench → Blender → Inkscape).
- **Zyklus 2:** Schülerinnen und Schüler modellieren selbst in Blockbench (läuft im Browser); Entfaltung und Layout übernimmt die Lehrperson oder erfolgt gemeinsam an einem Gerät.
- **KI-Demonstration:** Die Lehrperson zeigt die Generierung einmal vor (vorbereitet oder über einen gehosteten Dienst) und nutzt sie als Gesprächsanlass für MI.2.3 – nicht als Arbeitsmittel für die Klasse.

---

## Schritt 2: Geometrische Vereinfachung

### Manifold-Analyse

Ein Mesh muss «wasserdicht» (manifold) sein, damit es entfaltet werden kann. Jede Kante muss **exakt zwei Flächen** verbinden.

**Prüfung in Blender:**

1. 3D Print Toolbox aktivieren
2. Sidebar → 3D-Print Tab → **«Check All»**
3. Ergebnisse prüfen: Non-Manifold Edges, Bad Contiguous Edges

**Automatische Reparatur:**

- Blender: «Make Manifold» Button (kann Form verzerren)
- MeshLab: Filters → Cleaning and Repairing → Repair Non-Manifold Edges

**Manuelle Reparatur (präziser):**

1. Edit Mode → Select → Non-Manifold (Shift+Ctrl+Alt+F)
2. Innere Flächen löschen (X → Faces)
3. Löcher schliessen: Randkanten selektieren → F (Fill)

### Decimation-Algorithmen

Der **Decimate Modifier** in Blender bietet drei Modi:

#### Collapse (prozentuale Reduktion)

```
Ratio: 0.01–1.0 (1.0 = keine Änderung)
```

- Reduziert Vertices basierend auf Fehlerminimierung
- Gut für organische Formen
- Erzeugt chaotische Dreiecksnetze → schlecht für Papercraft

#### Planar (winkelbasierte Vereinfachung) – **EMPFOHLEN**

```
Angle Limit: 10–20° (für kindgerechte Modelle)
```

- Fasst Flächen zusammen, die im ähnlichen Winkel stehen
- Flache Seiten → ein Polygon, Kanten (90°) bleiben erhalten
- **Erzeugt «Box-Modelling»-Look** → ideal für Papercraft
- Schlüsselparameter: Je kleiner der Angle Limit, desto aggressiver die Vereinfachung

#### Un-Subdivide (Rückgängigmachen von Subdivision)

- Nur nützlich, wenn das Modell durch Subdivision Surface entstanden ist
- Für KI-generierte Modelle selten relevant

### Blockbench-Retopologie (Alternative)

Für maximale Kontrolle: Das KI-Rohmodell nur als Referenz nutzen und in Blockbench komplett aus Quadern nachbauen. Blockbench arbeitet nativ mit Cubes → automatisch perfekte Papercraft-Topologie.

Export: `.obj` → Blender Import für Unfolding.

---

## Schritt 3: Nähte und Entfaltung

### Seam-Strategie

Die Platzierung der Nähte (Seams) bestimmt, wie das Modell aufgeschnitten wird. Ziel: Wenige, grosse zusammenhängende Teile («Inseln»).

**Grundregeln:**

- Nähte an der **Unterseite** oder **Rückseite** des Objekts
- Nähte entlang **natürlicher Kanten** (z. B. wo Kabine auf Ladefläche trifft)
- **«Shell»-Unfolding**: Die Kabine eines LKW sollte ein zusammenhängendes Teil bleiben

**In Blender:**

1. Edit Mode → Edge Select (2)
2. Kanten selektieren
3. **Strg+E → Mark Seam** (erscheint rot)
4. Zum Testen: **U → Unwrap** im UV Editor

### Paper Model Add-on: Konfiguration

| Parameter | Standard | Empfehlung Kinder | Erklärung |
|---|---|---|---|
| Scale | 1.0 | Experimentieren | 1 Blender-Unit = X mm auf Papier |
| Island Margin | 1.0 mm | 2.0 mm | Abstand zwischen Teilen |
| Tab Size | Relativ | «No Tabs» | Laschen lieber extern via Tabgen |
| Texture | None | From Materials | Farben und Muster auf den Bogen |
| Texture Resolution | 100 DPI | 300 DPI | Scharfe Drucke auf A4 |
| Lighting | Default | Shadeless/AO | Mehr Tiefe ohne reale Schatten |

### Ausgabeformat

**Zwingend SVG** – nicht PDF.

PDF ist ein Endformat und verliert die Vektorinformationen. SVG bewahrt:
- Schnittlinien als separate Pfade
- Faltlinien als editierbare Objekte
- Texturen als eingebettete Bilder
- Alle Elemente einzeln bearbeitbar in Inkscape

---

## Schritt 4: Vektor-Layout in Inkscape

### Linienstile konfigurieren

Die SVG aus Blender enthält verschiedene Ebenen/Farben. Anpassung:

| Element | Strichfarbe | Strichstärke | Strichart |
|---|---|---|---|
| Schnittlinien | #000000 (Schwarz) | 0,5–1,0 mm | Durchgezogen |
| Bergfalten | #E74C3C (Rot) | 0,3–0,5 mm | Gestrichelt (5,3) |
| Talfalten | #2E86C1 (Blau) | 0,3–0,5 mm | Gestrichelt (3,3) |
| Klebelaschen | #BDC3C7 (Grau) | 0,2 mm | Durchgezogen |

### Tabgen: Laschen generieren

1. Von Blender generierte Laschen-Pfade löschen
2. Kanten-Pfade selektieren
3. **Erweiterungen → Papercraft → Tabgen**
4. Konfiguration:
   - **Höhe:** 10–15 mm (für 5–7 Jahre), 8–10 mm (für 8–10 Jahre)
   - **Winkel:** 45° (Trapezform – stabilste Form für Papier)
5. Generieren

> **Voraussetzung:** Alle Kurven müssen linearisiert sein (Path → Object to Path / Extensions → Convert to Polyline). Papiermodelle können keine echten Kurven haben.

### Nesting (Layout auf A4)

- Dokumentgrösse: A4 (210 × 297 mm) mit 10 mm Rand
- Teile nicht über Seitengrenzen platzieren
- Zusammengehörige Teile gruppieren
- **Strg+Shift+A**: Ausrichtungs-Werkzeuge für gleichmässige Verteilung

### Plotter-Export (optional)

Für Schneideplotter:
- **File → Save As → DXF** oder **HPGL**
- Nur Schnittlinien-Ebene exportieren (Faltlinien nicht schneiden!)
- Perforations-Modus einstellen: Nicht durchschneiden, nur anritzen

---

## Troubleshooting

| Problem | Ursache | Lösung |
|---|---|---|
| Modell hat Löcher nach Decimation | Manifold-Fehler | 3D Print Toolbox → Check → Manuell reparieren |
| Laschen zu klein im Ausdruck | Scale-Faktor zu niedrig | In Inkscape skalieren oder Tabgen-Höhe anpassen |
| Texturen pixelig | DPI zu niedrig | Export-Auflösung auf 300 DPI setzen |
| Teile passen beim Zusammenbau nicht | Seams falsch gesetzt | Seams prüfen, ev. UV Unwrap im UV Editor kontrollieren |
| SVG zeigt keine Farben | Textur-Baking fehlt | In Blender: «From Materials» beim Export aktivieren |
