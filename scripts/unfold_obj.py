"""Entfaltet ein OBJ-Modell headless mit dem Blender-Add-on «Export Paper Model» zu einem SVG.

Läuft innerhalb von Blender (``bpy``), nicht mit einem normalen Python-Interpreter.
Getestet mit Blender 4.0.2 und dem mitgelieferten Add-on ``io_export_paper_model`` 1.2.
Ab Blender 4.2 ist Paper Model eine Extension; der Modulname kann dort abweichen
(Option ``--addon``).

Paper Model erzeugt kleine Klebelaschen (``class='sticker'``). Sie markieren, welche
Kante eines Kantenpaares die Lasche bekommt – diese Information braucht
``scripts/add_tabs.py``, um daraus kindgerechte 15-mm-Trapezlaschen zu machen.

Aufruf (PowerShell, eine Zeile):

    blender --background --python scripts/unfold_obj.py -- examples/01-wuerfel-einstieg/wuerfel.obj examples/01-wuerfel-einstieg/wuerfel-unfolded.svg --scale 18.181818

``--scale`` ist der Divisor wie im Add-on: 1 Blender-Einheit (1 m) / 20 = 50 mm auf Papier,
1 m / 18.181818 = 55 mm (Würfel-Beispiel).
"""

import argparse
import sys

import bpy


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("obj", help="Eingabe-OBJ")
    parser.add_argument("svg", help="Ausgabe-SVG")
    parser.add_argument("--scale", type=float, default=20.0,
                        help="Divisor: Blender-Einheiten (m) / scale = Papiermass (Standard 20)")
    parser.add_argument("--addon", default="io_export_paper_model",
                        help="Modulname des Paper-Model-Add-ons")
    return parser.parse_args(argv)


def main():
    args = parse_args()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.preferences.addon_enable(module=args.addon)
    bpy.ops.wm.obj_import(filepath=args.obj)

    obj = bpy.context.selected_objects[0]
    bpy.context.view_layer.objects.active = obj

    # Ohne GUI läuft invoke() nicht; die automatische Skalierung muss deshalb
    # in den Szenen-Einstellungen abgeschaltet und der Massstab dort gesetzt werden.
    settings = bpy.context.scene.paper_model
    settings.use_auto_scale = False
    settings.scale = args.scale

    result = bpy.ops.export_mesh.paper_model(
        filepath=args.svg,
        file_format="SVG",
        scale=args.scale,
        page_size_preset="A4",
        output_type="NONE",
        do_create_stickers=True,
        do_create_numbers=True,
    )
    if result != {"FINISHED"}:
        sys.exit(f"Paper Model Export fehlgeschlagen: {result}")
    print(f"Entfaltet: {args.obj} -> {args.svg} ({len(obj.data.polygons)} Flächen)")


if __name__ == "__main__":
    main()
