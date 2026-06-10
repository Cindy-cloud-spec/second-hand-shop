#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Neuen Artikel anlegen — interaktiver Assistent
Doppelklick auf neuer_artikel.command zum Starten.
"""

import json
import subprocess
import sys
from pathlib import Path

VERKÄUFE_ORDNER = Path.home() / "Documents" / "Verkäufe"

def frage(text, pflicht=True, standard=None):
    """Stellt eine Frage und gibt die Antwort zurück."""
    hinweis = ""
    if standard:
        hinweis = f" [{standard}]"
    if not pflicht:
        hinweis += " (optional, Enter zum Überspringen)"

    while True:
        print(f"\n  {text}{hinweis}")
        print("  → ", end="", flush=True)
        try:
            antwort = input().strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nAbgebrochen.")
            sys.exit(0)

        if antwort == "" and standard:
            return standard
        if antwort == "" and not pflicht:
            return ""
        if antwort == "" and pflicht:
            print("  ⚠ Pflichtfeld — bitte ausfüllen.")
            continue
        return antwort


def frage_zahl(text, standard=None):
    """Fragt nach einer Zahl (Preis)."""
    while True:
        antwort = frage(text, pflicht=True, standard=str(standard) if standard else None)
        try:
            return float(antwort.replace(",", ".").replace("€", "").strip())
        except ValueError:
            print("  ⚠ Bitte eine Zahl eingeben, z.B. 15 oder 12.50")


def frage_auswahl(text, optionen, standard=None):
    """Zeigt Auswahloptionen und gibt die gewählte zurück."""
    print(f"\n  {text}")
    for i, opt in enumerate(optionen, 1):
        marker = " ←" if opt == standard else ""
        print(f"    {i}) {opt}{marker}")
    print("  → ", end="", flush=True)
    try:
        antwort = input().strip()
    except (EOFError, KeyboardInterrupt):
        print("\n\nAbgebrochen.")
        sys.exit(0)

    if antwort == "" and standard:
        return standard
    try:
        idx = int(antwort) - 1
        if 0 <= idx < len(optionen):
            return optionen[idx]
    except ValueError:
        # Freitext akzeptieren
        if antwort:
            return antwort
    if standard:
        return standard
    return optionen[0]


def main():
    print()
    print("=" * 55)
    print("  Kleiderschrank Studio — Neuer Artikel")
    print("=" * 55)
    print()
    print("  Ich stelle dir ein paar Fragen zum Artikel.")
    print("  Am Ende wird die produkt.json automatisch gespeichert.")
    print()

    # ── Ordnername ──────────────────────────────────────────
    print("─" * 55)
    print("  SCHRITT 1: Ordner auswählen")
    print("─" * 55)

    # Ordner ohne produkt.json anzeigen
    if not VERKÄUFE_ORDNER.exists():
        print(f"\n✗ Ordner nicht gefunden: {VERKÄUFE_ORDNER}")
        input("\nEnter drücken zum Beenden...")
        sys.exit(1)

    offene_ordner = []
    for d in sorted(VERKÄUFE_ORDNER.iterdir()):
        if d.is_dir() and not d.name.startswith(".") and d.name != "VORLAGE":
            if not (d / "produkt.json").exists():
                offene_ordner.append(d)

    if not offene_ordner:
        print("\n  Alle Ordner haben bereits eine produkt.json.")
        print("  Lege zuerst einen neuen Unterordner in")
        print(f"  {VERKÄUFE_ORDNER}")
        print("  an und kopiere die Fotos hinein.")
        input("\nEnter drücken zum Beenden...")
        sys.exit(0)

    print("\n  Für welchen Ordner soll die produkt.json erstellt werden?")
    for i, d in enumerate(offene_ordner, 1):
        # Fotos zählen
        fotos = list(d.glob("*.jpg")) + list(d.glob("*.jpeg")) + \
                list(d.glob("*.JPG")) + list(d.glob("*.JPEG")) + \
                list(d.glob("*.png")) + list(d.glob("*.PNG"))
        foto_info = f"  ({len(fotos)} Foto{'s' if len(fotos) != 1 else ''})" if fotos else "  ⚠ noch keine Fotos!"
        print(f"    {i}) {d.name}{foto_info}")

    print("  → ", end="", flush=True)
    try:
        wahl = input().strip()
    except (EOFError, KeyboardInterrupt):
        print("\n\nAbgebrochen.")
        sys.exit(0)

    try:
        idx = int(wahl) - 1
        if 0 <= idx < len(offene_ordner):
            ziel_ordner = offene_ordner[idx]
        else:
            raise ValueError
    except ValueError:
        print(f"\n✗ Ungültige Auswahl.")
        input("\nEnter drücken zum Beenden...")
        sys.exit(1)

    print(f"\n  ✓ Ordner: {ziel_ordner.name}")

    # ── Artikeldaten ────────────────────────────────────────
    print()
    print("─" * 55)
    print("  SCHRITT 2: Artikeldaten eingeben")
    print("─" * 55)

    titel = frage("Wie heißt der Artikel? (z.B. 'Strickjacke, bordeaux')")

    preis = frage_zahl("Für wie viel € möchtest du ihn verkaufen?")

    kategorie = frage_auswahl(
        "Welche Kategorie?",
        ["Kleidung", "Schuhe", "Accessoires", "Taschen"],
        standard="Kleidung"
    )

    unterkategorie_optionen = {
        "Kleidung": ["Kleider", "Röcke", "Hosen", "Tops & Shirts", "Pullover & Strick",
                     "Jacken & Mäntel", "Sportbekleidung", "Sonstiges"],
        "Schuhe":   ["Sneaker", "Stiefel", "Sandalen", "Halbschuhe", "Sonstiges"],
        "Accessoires": ["Schmuck", "Gürtel", "Schals & Tücher", "Mützen", "Sonstiges"],
        "Taschen": ["Handtaschen", "Rucksäcke", "Clutches", "Sonstiges"],
    }
    optionen = unterkategorie_optionen.get(kategorie, ["Sonstiges"])
    unterkategorie = frage_auswahl("Welche Unterkategorie?", optionen)

    marke = frage("Welche Marke?  (z.B. Zara, H&M, unbekannt)", pflicht=False, standard="Unbekannt")

    größe = frage("Welche Größe?  (z.B. M, 38, 128/134, 42)")

    farbe = frage("Welche Farbe?  (z.B. Bordeaux, Dunkelblau, gemustert)", pflicht=False)

    material = frage("Material?  (z.B. 100 % Baumwolle)", pflicht=False)

    zustand = frage_auswahl(
        "Zustand?",
        ["Neuwertig (kaum getragen)", "Sehr guter Zustand", "Guter Zustand",
         "Getragen, mit kleinen Gebrauchsspuren"],
        standard="Sehr guter Zustand"
    )

    mängel = frage(
        "Gibt es Mängel? (z.B. 'Kleiner Fleck am Ärmel') — oder Enter für 'Keine'",
        pflicht=False,
        standard="Keine"
    )

    beschreibung = frage(
        "Kurze Beschreibung für die Website?",
        pflicht=False
    )

    saison = frage_auswahl(
        "Saison?",
        ["Frühling/Sommer", "Herbst/Winter", "Ganzjährig"],
        standard="Ganzjährig"
    )

    # ── Zusammenfassung ─────────────────────────────────────
    print()
    print("─" * 55)
    print("  ZUSAMMENFASSUNG")
    print("─" * 55)
    print(f"  Titel:       {titel}")
    print(f"  Preis:       {preis:.2f} €")
    print(f"  Kategorie:   {kategorie} › {unterkategorie}")
    print(f"  Marke:       {marke}")
    print(f"  Größe:       {größe}")
    if farbe:
        print(f"  Farbe:       {farbe}")
    print(f"  Zustand:     {zustand}")
    print(f"  Mängel:      {mängel}")
    print(f"  Saison:      {saison}")

    print()
    print("  Soll die produkt.json so gespeichert werden?")
    print("  → Ja (Enter) / Nein (n): ", end="", flush=True)
    try:
        bestätigung = input().strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\n\nAbgebrochen.")
        sys.exit(0)

    if bestätigung in ("n", "nein", "no"):
        print("\n  Abgebrochen — nichts gespeichert.")
        input("\nEnter drücken zum Beenden...")
        sys.exit(0)

    # ── Speichern ────────────────────────────────────────────
    produkt = {
        "titel":               titel,
        "preis":               preis,
        "ursprünglicher_preis": None,
        "kategorie":           kategorie,
        "unterkategorie":      unterkategorie,
        "marke":               marke,
        "größe":               größe,
        "farbe":               farbe,
        "material":            material,
        "zustand":             zustand,
        "mängel":              mängel,
        "beschreibung":        beschreibung,
        "besonderheiten":      "",
        "maße":                "",
        "saison":              saison,
        "stil":                "",
        "verfügbarkeit":       "verfügbar"
    }

    ziel_datei = ziel_ordner / "produkt.json"
    with open(ziel_datei, "w", encoding="utf-8") as f:
        json.dump(produkt, f, ensure_ascii=False, indent=2)

    print()
    print("─" * 55)
    print("  SCHRITT 3: Artikel wird zur Website hinzugefügt …")
    print("─" * 55)

    import_skript = Path(__file__).parent / "import_artikel.py"
    result = subprocess.run(
        [sys.executable, str(import_skript)],
        capture_output=True, text=True
    )
    # Relevante Zeilen aus dem Import-Output anzeigen
    for line in result.stdout.splitlines():
        if any(x in line for x in ["✓ Artikel", "✅", "✗", "Neu importiert", "Website aktualisiert"]):
            print(f"  {line.strip()}")

    print()
    print("=" * 55)
    print(f"  ✅ Fertig! Artikel ist jetzt online.")
    print(f"  → Browser neu laden: http://localhost:3456")
    print("=" * 55)
    print()

    try:
        if sys.stdin.isatty():
            input("Enter drücken zum Schließen...")
    except (EOFError, KeyboardInterrupt):
        pass


if __name__ == "__main__":
    main()
