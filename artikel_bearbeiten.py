#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Artikel bearbeiten — interaktiver Assistent
Doppelklick auf artikel_bearbeiten.command zum Starten.
"""

import json
import sys
from pathlib import Path

WEBSITE_ORDNER = Path(__file__).parent.resolve()
DATA_ORDNER    = WEBSITE_ORDNER / "data"
PRODUCTS_JSON  = DATA_ORDNER / "products.json"
PRODUCTS_JS    = WEBSITE_ORDNER / "js" / "products.js"


def lade_produkte():
    with open(PRODUCTS_JSON, encoding="utf-8") as f:
        return json.load(f)


def speichere_produkte(produkte):
    with open(PRODUCTS_JSON, "w", encoding="utf-8") as f:
        json.dump(produkte, f, ensure_ascii=False, indent=2)
    regeneriere_products_js(produkte)


def regeneriere_products_js(produkte):
    products_json_str = json.dumps(produkte, ensure_ascii=False, indent=2)
    inhalt = f"""// ============================================================
// PRODUCTS.JS
// Automatisch generiert von import_artikel.py
// ⚠ NICHT manuell bearbeiten — wird beim nächsten Import überschrieben!
// Artikel pflegen über: data/products.json + import_artikel.py
// ============================================================

const products = {products_json_str};

// Hilfsfunktionen
function getUniqueValues(field) {{
  const values = products
    .map(p => p[field])
    .filter(v => v && v !== "Unbekannt" && v !== null);
  return [...new Set(values)].sort();
}}

function getProductById(id) {{
  return products.find(p => p.id === id) || null;
}}

function getPriceRange() {{
  const prices = products.map(p => p.preis);
  return {{ min: Math.min(...prices), max: Math.max(...prices) }};
}}
"""
    with open(PRODUCTS_JS, "w", encoding="utf-8") as f:
        f.write(inhalt)


def eingabe(text, standard=None):
    hinweis = f" [{standard}]" if standard is not None else ""
    print(f"  {text}{hinweis}")
    print("  → ", end="", flush=True)
    try:
        antwort = input().strip()
    except (EOFError, KeyboardInterrupt):
        print("\n\nAbgebrochen.")
        sys.exit(0)
    if antwort == "" and standard is not None:
        return standard
    return antwort


# Felder die bearbeitet werden können, mit lesbaren Bezeichnungen
FELDER = [
    ("titel",          "Titel"),
    ("preis",          "Preis (€)"),
    ("marke",          "Marke"),
    ("größe",          "Größe"),
    ("farbe",          "Farbe"),
    ("material",       "Material"),
    ("zustand",        "Zustand"),
    ("mängel",         "Mängel"),
    ("beschreibung",   "Beschreibung"),
    ("besonderheiten", "Besonderheiten"),
    ("maße",           "Maße"),
    ("kategorie",      "Kategorie"),
    ("unterkategorie", "Unterkategorie"),
    ("saison",         "Saison"),
    ("verfügbarkeit",  "Verfügbarkeit (verfügbar / reserviert / verkauft)"),
]


def main():
    print()
    print("=" * 55)
    print("  Kleiderschrank Studio — Artikel bearbeiten")
    print("=" * 55)

    produkte = lade_produkte()

    # ── Artikel auswählen ────────────────────────────────────
    print("\n  Welchen Artikel möchtest du bearbeiten?\n")
    for i, p in enumerate(produkte, 1):
        status = ""
        if p.get("verfügbarkeit") == "verkauft":
            status = "  [VERKAUFT]"
        elif p.get("verfügbarkeit") == "reserviert":
            status = "  [RESERVIERT]"
        print(f"    {i:>2})  #{p['id']}  {p['titel']}  –  {p['preis']:.0f} €  Gr. {p['größe']}{status}")

    print()
    wahl = eingabe("Nummer eingeben (oder Enter zum Abbrechen)")

    if wahl == "":
        print("\n  Abgebrochen.")
        sys.exit(0)

    try:
        idx = int(wahl) - 1
        if not (0 <= idx < len(produkte)):
            raise ValueError
    except ValueError:
        print(f"\n  ✗ Ungültige Auswahl.")
        sys.exit(1)

    artikel = produkte[idx]

    # ── Endlosschleife: Felder bearbeiten ────────────────────
    while True:
        print()
        print("─" * 55)
        print(f"  Artikel #{artikel['id']}: {artikel['titel']}")
        print("─" * 55)
        print("\n  Welches Feld möchtest du ändern?\n")

        for i, (key, label) in enumerate(FELDER, 1):
            wert = artikel.get(key, "")
            # Lange Texte kürzen für die Anzeige
            anzeige = str(wert) if wert else "—"
            if len(anzeige) > 50:
                anzeige = anzeige[:47] + "…"
            print(f"    {i:>2})  {label:<30} {anzeige}")

        print()
        print(f"    0)  Fertig — Änderungen speichern")
        print()
        wahl = eingabe("Nummer eingeben")

        if wahl == "0" or wahl == "":
            break

        try:
            feld_idx = int(wahl) - 1
            if not (0 <= feld_idx < len(FELDER)):
                raise ValueError
        except ValueError:
            print("  ✗ Ungültige Auswahl.")
            continue

        key, label = FELDER[feld_idx]
        alter_wert = artikel.get(key, "")

        print()
        print(f"  Aktuell: {alter_wert if alter_wert else '—'}")
        neuer_wert = eingabe(f"Neuer Wert für '{label}' (Enter = unverändert lassen)", standard=str(alter_wert))

        if neuer_wert == str(alter_wert):
            print("  Keine Änderung.")
            continue

        # Preis als Zahl speichern
        if key == "preis":
            try:
                neuer_wert = float(neuer_wert.replace(",", ".").replace("€", "").strip())
            except ValueError:
                print("  ✗ Bitte eine Zahl eingeben (z.B. 15 oder 12.50)")
                continue

        artikel[key] = neuer_wert
        print(f"  ✓ '{label}' geändert.")

    # ── Speichern ────────────────────────────────────────────
    print()
    print("─" * 55)
    print("  ZUSAMMENFASSUNG DER ÄNDERUNGEN")
    print("─" * 55)
    print(f"  Titel:        {artikel['titel']}")
    print(f"  Preis:        {artikel['preis']} €")
    print(f"  Zustand:      {artikel['zustand']}")
    print(f"  Verfügbar:    {artikel['verfügbarkeit']}")
    print()

    bestätigung = eingabe("Änderungen speichern? → Ja (Enter) / Nein (n)")
    if bestätigung.lower() in ("n", "nein", "no"):
        print("\n  Abgebrochen — nichts gespeichert.")
        try:
            if sys.stdin.isatty():
                input("\nEnter drücken zum Schließen...")
        except (EOFError, KeyboardInterrupt):
            pass
        sys.exit(0)

    speichere_produkte(produkte)

    print()
    print("=" * 55)
    print("  ✅ Änderungen gespeichert!")
    print("  → Browser neu laden: http://localhost:3456")
    print("=" * 55)
    print()

    try:
        if sys.stdin.isatty():
            input("Enter drücken zum Schließen...")
    except (EOFError, KeyboardInterrupt):
        pass


if __name__ == "__main__":
    main()
