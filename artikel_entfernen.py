#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Artikel von der Website entfernen — interaktiver Assistent
Doppelklick auf artikel_entfernen.command zum Starten.
"""

import json
import sys
from pathlib import Path

WEBSITE_ORDNER  = Path(__file__).parent.resolve()
DATA_ORDNER     = WEBSITE_ORDNER / "data"
PRODUCTS_JSON   = DATA_ORDNER / "products.json"
PRODUCTS_JS     = WEBSITE_ORDNER / "js" / "products.js"
IMAGES_ORDNER   = WEBSITE_ORDNER / "images"


def lade_produkte():
    with open(PRODUCTS_JSON, encoding="utf-8") as f:
        return json.load(f)


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


def main():
    print()
    print("=" * 55)
    print("  Kleiderschrank Studio — Artikel entfernen")
    print("=" * 55)

    produkte = lade_produkte()

    if not produkte:
        print("\n  Keine Artikel vorhanden.")
        input("\nEnter drücken zum Beenden...")
        sys.exit(0)

    # Alle Artikel anzeigen
    print("\n  Welcher Artikel soll entfernt werden?\n")
    for i, p in enumerate(produkte, 1):
        status = ""
        if p.get("verfügbarkeit") == "verkauft":
            status = "  [VERKAUFT]"
        elif p.get("verfügbarkeit") == "reserviert":
            status = "  [RESERVIERT]"
        print(f"    {i:>2})  #{p['id']}  {p['titel']}  –  {p['preis']:.0f} €  Gr. {p['größe']}{status}")

    print()
    print("  Nummer eingeben (oder Enter zum Abbrechen):")
    print("  → ", end="", flush=True)

    try:
        wahl = input().strip()
    except (EOFError, KeyboardInterrupt):
        print("\n\nAbgebrochen.")
        sys.exit(0)

    if wahl == "":
        print("\n  Abgebrochen.")
        input("\nEnter drücken zum Beenden...")
        sys.exit(0)

    try:
        idx = int(wahl) - 1
        if not (0 <= idx < len(produkte)):
            raise ValueError
    except ValueError:
        print(f"\n  ✗ Ungültige Auswahl.")
        input("\nEnter drücken zum Beenden...")
        sys.exit(1)

    artikel = produkte[idx]

    # Bestätigung
    print()
    print("─" * 55)
    print(f"  Artikel:  #{artikel['id']} {artikel['titel']}")
    print(f"  Preis:    {artikel['preis']:.0f} €  |  Gr. {artikel['größe']}")
    print(f"  Bilder:   {len(artikel.get('bilder', []))} Foto(s) werden ebenfalls gelöscht")
    print("─" * 55)
    print()
    print("  ⚠ Dieser Vorgang kann nicht rückgängig gemacht werden!")
    print()
    print("  Wirklich löschen? → ja eingeben und Enter:")
    print("  → ", end="", flush=True)

    try:
        bestätigung = input().strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\n\nAbgebrochen.")
        sys.exit(0)

    if bestätigung != "ja":
        print("\n  Abgebrochen — nichts gelöscht.")
        input("\nEnter drücken zum Beenden...")
        sys.exit(0)

    # Bilder löschen
    bilder = artikel.get("bilder", [])
    gelöscht = 0
    for bild_pfad in bilder:
        bild = WEBSITE_ORDNER / bild_pfad
        if bild.exists():
            bild.unlink()
            gelöscht += 1

    # Artikel aus Liste entfernen
    produkte.pop(idx)

    # Speichern
    with open(PRODUCTS_JSON, "w", encoding="utf-8") as f:
        json.dump(produkte, f, ensure_ascii=False, indent=2)

    regeneriere_products_js(produkte)

    # Ergebnis
    print()
    print("=" * 55)
    print(f"  ✅ Artikel #{artikel['id']} wurde entfernt.")
    print(f"     {gelöscht} Foto(s) gelöscht.")
    print(f"     Noch {len(produkte)} Artikel auf der Website.")
    print()
    print("  → Seite im Browser neu laden: http://localhost:3456")
    print("=" * 55)
    print()

    try:
        if sys.stdin.isatty():
            input("Enter drücken zum Schließen...")
    except (EOFError, KeyboardInterrupt):
        pass


if __name__ == "__main__":
    main()
