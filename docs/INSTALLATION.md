# Installation: Alle Tools einrichten

> Schritt-für-Schritt-Anleitung zur Installation des gesamten Software-Stacks.

---

## Übersicht

| Tool | Installationsaufwand | Benötigt GPU? |
|---|---|---|
| Blender | ⭐ Einfach (Download) | Nein |
| Inkscape | ⭐ Einfach (Download) | Nein |
| Blockbench | ⭐ Einfach (Download) | Nein |
| Tabgen (Inkscape) | ⭐ Einfach (Erweiterung) | Nein |
| TripoSR | ⭐⭐⭐ Fortgeschritten (Conda + Git) | Ja (NVIDIA, ab 6 GB) – CPU-Fallback möglich |
| TRELLIS.2 | ⭐⭐⭐⭐ Anspruchsvoll (Conda + Git + CUDA-Kernel) | Ja (NVIDIA, ab 12–16 GB) |
| ComfyUI | ⭐⭐⭐ Fortgeschritten (Conda + Git) | Ja (NVIDIA) |

> **Minimaler Start:** Für Projekt A (Würfel) reichen Blockbench + Blender + Inkscape. KI-Modelle erst installieren, wenn der KI-Workflow benötigt wird – und dann mit TripoSR beginnen.

---

## 1. Blender 4.x

### Download und Installation

1. [blender.org/download](https://www.blender.org/download/) → Aktuelle Version (4.x) herunterladen
2. Installer ausführen (Windows) oder entpacken (Linux/macOS)

### Paper Model Add-on aktivieren

1. **Edit → Preferences → Add-ons**
2. Suche nach «Paper Model» oder «Export Paper Model»
3. Häkchen setzen bei **«Export Paper Model»**
4. Falls nicht vorinstalliert: [extensions.blender.org/add-ons/export-paper-model](https://extensions.blender.org/add-ons/export-paper-model/) herunterladen und über «Install from Disk» hinzufügen

### 3D Print Toolbox aktivieren

1. **Edit → Preferences → Add-ons**
2. Suche nach «3D Print»
3. Häkchen setzen bei **«Mesh: 3D-Print Toolbox»**

---

## 2. Inkscape 1.x

### Download und Installation

1. [inkscape.org/release](https://inkscape.org/release/) → Aktuelle Version herunterladen
2. Installer ausführen

### Tabgen-Erweiterung installieren

Tabgen ist Teil der Erweiterungssammlung **MightyScape** (FabLab Chemnitz), die auch Paperfold enthält. Es gibt zwei Wege:

**Weg A – über den Inkscape-Erweiterungsmanager (empfohlen):**

1. **Erweiterungen → Erweiterungen verwalten…**
2. Nach «Tabgen» oder «MightyScape» suchen und installieren
3. Inkscape neu starten

**Weg B – manuell:**

1. MightyScape von GitHub laden: [github.com/eridur-de/mightyscape-1.X](https://github.com/eridur-de/mightyscape-1.X)
2. Den Ordner `tabgen` nach `~/.config/inkscape/extensions/` (Linux/macOS) oder `%APPDATA%\inkscape\extensions\` (Windows) kopieren
3. Inkscape neu starten

Prüfen: **Erweiterungen → Papercraft → Tabgen** (oder unter **Erweiterungen → FabLab Chemnitz → Papercraft**) sollte erscheinen. Der genaue Menüpfad hängt von der Version der Sammlung ab.

### Paperfold-Erweiterung (optional)

Die Paperfold-Erweiterung (FabLab Chemnitz) kann `.obj`-Dateien direkt in Inkscape entfalten – nützlich für sehr einfache Formen, die Blender nicht benötigen.

1. **Erweiterungen → Erweiterungen verwalten → Paperfold** suchen und installieren
2. Oder: aus derselben MightyScape-Sammlung wie Tabgen (siehe oben)

---

## 3. Blockbench

### Download und Installation

1. [blockbench.net](https://www.blockbench.net/) → Download
2. Verfügbar als Desktop-App (Windows, macOS, Linux) oder Web-Version
3. Keine GPU erforderlich

### Blender-Export-Plugin

Blockbench exportiert nativ als `.obj`, was Blender direkt importieren kann. Kein zusätzliches Plugin nötig.

---

## 4. TripoSR (KI: Bild → 3D)

### Voraussetzungen

- NVIDIA GPU mit mindestens 6 GB VRAM (empfohlen)
- CUDA 11.8+ installiert (NVIDIA-Treiber)
- [Miniconda](https://docs.conda.io/en/latest/miniconda.html) oder Anaconda

Ohne NVIDIA-GPU läuft TripoSR mit `--device cpu` (langsam, 1–5 Minuten pro Modell) und experimentell auf Apple Silicon mit `--device mps`. Für einzelne Bastelbögen ist das durchaus praktikabel.

### Installation

```bash
# 1. Conda-Umgebung erstellen
conda create -n triposr python=3.10
conda activate triposr

# 2. PyTorch mit CUDA-Unterstützung installieren
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# 3. TripoSR klonen und Abhängigkeiten installieren
git clone https://github.com/VAST-AI-Research/TripoSR.git
cd TripoSR
pip install -r requirements.txt
```

### Test

```bash
# Testbild generieren (z. B. ein einfaches Objekt fotografieren)
python run.py test_image.png --output-dir output/ --model-save-format obj
```

> Beim ersten Start wird das Modell heruntergeladen (~1.5 GB). Danach dauert die Generierung unter 2 Sekunden.

### Fehlerbehebung

| Problem | Lösung |
|---|---|
| `CUDA out of memory` | Kleinere Auflösung oder GPU mit mehr VRAM verwenden |
| `ModuleNotFoundError` | `conda activate triposr` vergessen? |
| Modell-Download schlägt fehl | Proxy-Einstellungen prüfen oder Modell manuell von HuggingFace laden |

---

## 5. TRELLIS.2 (KI: Bild → 3D, Qualitätsstufe)

### Voraussetzungen

- NVIDIA GPU mit mindestens 12–16 GB VRAM (je nach Modellvariante)
- CUDA 12.x und passende Toolchain zum Kompilieren von CUDA-Kerneln (nvcc, gcc)
- Linux empfohlen; unter Windows ist WSL2 der zuverlässigste Weg
- [Miniconda](https://docs.conda.io/en/latest/miniconda.html)

### Installation

Das Repository von TRELLIS enthält ein Setup-Skript, das die Abhängigkeiten in einer Conda-Umgebung installiert. Die genauen Schritte ändern sich mit den Releases – die README des Repositories ist massgebend:

```bash
git clone --recurse-submodules https://github.com/microsoft/TRELLIS.git
cd TRELLIS
# Setup-Skript gemäss README ausführen, z. B.:
# . ./setup.sh --new-env --basic --xformers --flash-attn --diffoctreerast --spconv --mipgaussian --kaolin --nvdiffrast
```

Beim ersten Lauf werden die Modellgewichte (mehrere GB) von Hugging Face geladen.

### Test

```bash
conda activate trellis
python example.py   # erzeugt aus einem Beispielbild ein .glb
```

Das `.glb` lässt sich direkt in Blender importieren (**File → Import → glTF 2.0**).

### Wann TripoSR, wann TRELLIS.2?

| Situation | Empfehlung |
|---|---|
| Erster Versuch, schwache GPU, Zeitdruck | TripoSR |
| Einfache Objekte (Fahrzeuge, Gebäude aus Quadern) | TripoSR |
| Organische Objekte (Tiere, Figuren) | TRELLIS.2 |
| Modell hat nach TripoSR viele lose Fragmente (Floaters) | TRELLIS.2 |
| Mehrere Varianten eines Motivs schnell vergleichen | TripoSR |

---

## 6. ComfyUI (optional, für den automatisierten Workflow)

### Installation

```bash
# 1. In die TripoSR-Umgebung oder eine neue
conda activate triposr  # oder: conda create -n comfyui python=3.10

# 2. ComfyUI klonen
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
pip install -r requirements.txt

# 3. Starten
python main.py
```

ComfyUI öffnet sich im Browser unter `http://127.0.0.1:8188`.

### TripoSR-Node installieren

1. Navigiere zu `ComfyUI/custom_nodes/`
2. Klone den TripoSR-Custom-Node (Link im [TripoSR ComfyUI Guide](https://www.triposrai.com/posts/triposr-comfyui-node-guide/))
3. ComfyUI neu starten

### Workflow laden

Beispiel-Workflows befinden sich in [`templates/comfyui/`](../templates/comfyui/). Per Drag & Drop in die ComfyUI-Oberfläche ziehen.

---

## 7. Schneideplotter (optional)

### Inkcut (Open-Source-Plotter-Treiber)

```bash
pip install inkcut
```

Unterstützt Silhouette, Cricut (mit Einschränkungen) und andere Plotter. Export aus Inkscape als `.hpgl` oder `.dxf`.

---

## Schnelltest: Ist alles installiert?

```
✅ Blender: File → Export → Paper Model (.svg) erscheint
✅ Inkscape: Erweiterungen → Papercraft → Tabgen erscheint
✅ Blockbench: "Generic Model" lässt sich erstellen und als .obj exportieren
✅ TripoSR: python run.py test.png erzeugt eine .obj-Datei
✅ TRELLIS.2 (optional): example.py erzeugt ein .glb
✅ ComfyUI: Browser zeigt die Node-Oberfläche
```
