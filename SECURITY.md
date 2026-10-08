# Sicherheit

Dieses Repository enthält Dokumentation, Vorlagen und Beispieldateien – keinen ausführbaren Code. Die Installationsanleitungen verweisen auf Software Dritter (Blender, Inkscape, Blockbench, KI-Modelle); für deren Sicherheit gelten die jeweiligen Projekte.

## Was gemeldet werden sollte

- Links auf Seiten, die Schadsoftware verbreiten oder sich als offizielle Downloadquelle ausgeben
- Installationsbefehle, die Sicherheitsmechanismen umgehen (z. B. deaktivierte Zertifikatsprüfung)
- Vorlagen oder Beispieldateien (`.svg`, `.obj`, `.json`) mit eingebetteten Skripten oder externen Referenzen
- Inhalte, die für Kinder ungeeignet sind

## Wie melden

Bitte **nicht** als öffentliches Issue, sondern über die private Schwachstellenmeldung von GitHub:
**Security → Report a vulnerability** auf der Repository-Seite.

Rückmeldung innerhalb von 14 Tagen. Nach Behebung wird die Meldung im [CHANGELOG](CHANGELOG.md) erwähnt, auf Wunsch anonym.

## Hinweis zu KI-Modellen

Die beschriebenen KI-Modelle laufen lokal; es werden keine Bilder oder Daten an Dritte übertragen. Modellgewichte werden beim ersten Start von Hugging Face geladen – die Quelle ist in der jeweiligen Anleitung genannt. Prüfe vor dem Download, dass das Repository dem offiziellen Herausgeber gehört.
