# Papercraft-KI: Educational Papercraft with Open-Source AI

![Version](https://img.shields.io/badge/version-0.1.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

> Generate, unfold and build your own 3D paper models – entirely with free software and locally running AI, designed for children aged 5–12 and mapped to the Swiss curriculum (Lehrplan 21).

🇩🇪 [Deutsche Version (vollständig)](README.md)

> **This is a short summary.** The full documentation – pedagogical background, curriculum mapping, installation and workflow details – is in German, because the target audience is German-speaking teachers and parents in Switzerland. Contributions in English are welcome.

## Overview

This repository documents a complete FOSS pipeline for producing papercraft templates (nets of 3D objects) that children cut, fold and glue. The pipeline replaces proprietary tools such as Pepakura Designer with Blender, Inkscape and Blockbench, and optionally uses local image-to-3D models (TripoSR, TRELLIS.2) to turn a child's idea into a 3D object in seconds. No cloud services, no cost.

```
Idea ("a fire truck!")
  → 3D model: hand-built (Blockbench) or AI-generated (TripoSR / TRELLIS.2)
    → Blender reduces it to 20–50 faces
      → Paper Model add-on unfolds it into a net
        → Inkscape adapts lines, tabs and symbols for small hands
          → Print, cut, fold, glue
```

## Why

- **Fine motor skills:** cutting and folding train bimanual coordination; the workflow deliberately produces long, gentle cut lines and 10–15 mm glue tabs.
- **Spatial reasoning:** children experience the net of a solid physically – a concept the Swiss curriculum requires explicitly in Mathematics (MA.2.C.1: draw the net of cubes and cuboids by unrolling; MA.2.B.2: verify nets by folding).
- **AI literacy:** children see that AI is a tool with strengths and weaknesses, and that the reduction, the seams and the layout remain human decisions.
- **Differentiation:** difficulty is tuned through three parameters – polygon count, tab size, and optional pre-perforation with a cutting plotter.

## Curriculum mapping

The project maps each step to competencies of the Swiss [Lehrplan 21](https://v-fe.lehrplan.ch) in three subject areas: Textiles and Technical Design (TTG), Mathematics (Form and Space) and Media and Informatics. Codes and wording were checked against the official competency posters for cycles 1 and 2. Details: [docs/LEHRPLAN21.md](docs/LEHRPLAN21.md) (German).

## Software stack

| Step | Tool | Licence |
|---|---|---|
| Box modelling (no AI) | [Blockbench](https://www.blockbench.net/) | GPL-3.0 |
| Image → 3D, entry level | [TripoSR](https://github.com/VAST-AI-Research/TripoSR) | MIT |
| Image → 3D, quality tier | [TRELLIS.2](https://github.com/microsoft/TRELLIS) | MIT |
| Simplify, unfold | [Blender](https://www.blender.org/) + Export Paper Model add-on | GPL |
| Layout, tabs | [Inkscape](https://inkscape.org/) + Tabgen (MightyScape) | GPL |

The no-AI path (Blockbench → Blender → Inkscape) runs on any laptop and is the recommended starting point, especially for schools.

## Status

**v0.1 – documentation.** The workflow is described but not yet tested end to end; `examples/` and `templates/` are placeholders. First-hand reports and example projects are welcome.

## Project structure

```
papercraft-ki/
├── README.md              ← full documentation (German)
├── README.en.md           ← this summary
├── docs/
│   ├── LEHRPLAN21.md      ← curriculum mapping
│   ├── PAEDAGOGIK.md      ← pedagogical background
│   ├── WORKFLOW.md        ← technical deep dive, model comparison
│   └── INSTALLATION.md    ← tool setup
├── templates/             ← ComfyUI, Inkscape, Blender presets (roadmap)
├── examples/              ← example projects by difficulty (roadmap)
└── assets/                ← pipeline diagram
```

## Changelog

See [CHANGELOG.md](CHANGELOG.md) (German).

## Contributing

Contributions are welcome – see [CONTRIBUTING.md](CONTRIBUTING.md) (German). English contributions are fine; please keep German spelling Swiss (ss, not ß) in German files.

## Security

Documentation only, no executable code. Report problematic links or template files as described in [SECURITY.md](SECURITY.md) (German).

## License

MIT License – see [LICENSE](LICENSE).

## Author

Hayal Özkan · [malkreide](https://github.com/malkreide)

A private project. Not an official publication of any public authority or school.
