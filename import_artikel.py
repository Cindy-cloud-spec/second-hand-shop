#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kleiderschrank Studio — Artikel-Import-Skript
==============================================
Neue Artikel aus dem Verkäufe-Ordner automatisch zur Website hinzufügen.

SO FUNKTIONIERT ES:
───────────────────
1. Neuen Unterordner in ~/Documents/Verkäufe/ anlegen
   (z.B. "Rotes_Sommerkleid")

2. Fotos in den Ordner kopieren
   Benennung bestimmt die Reihenfolge auf der Website:
     01_vorne.jpg
     02_seite.jpg
     03_detail.jpg
     04_maengel.jpg   ← Mängelfotos ans Ende!

3. Vorlage "produkt.json" aus Verkäufe/VORLAGE/ kopieren
   und alle Felder ausfüllen

4. Dieses Skript ausführen:
   → Doppelklick auf "neu_importieren.command" (im Website-Ordner)
   → oder Terminal: python3 import_artikel.py

Um einen Artikel als VERKAUFT zu markieren:
   data/products.json öffnen, "verfügbarkeit": "verkauft" setzen,
   dann import_artikel.py erneut ausführen (aktualisiert products.js).
"""

import json
import os
import re
import shutil
import sys
from datetime import date
from pathlib import Path

# ============================================================
# KONFIGURATION — hier anpassen falls nötig
# ============================================================
VERKÄUFE_ORDNER = Path.home() / "Documents" / "Verkäufe"
WEBSITE_ORDNER  = Path(__file__).parent.resolve()
IMAGES_ORDNER   = WEBSITE_ORDNER / "images"
DATA_ORDNER     = WEBSITE_ORDNER / "data"
PRODUCTS_JSON   = DATA_ORDNER / "products.json"
IMPORTIERT_JSON = DATA_ORDNER / "importiert.json"
PRODUCTS_JS     = WEBSITE_ORDNER / "js" / "products.js"

# ============================================================
# PRODUKTE LADEN / SPEICHERN
# ============================================================
def lade_produkte():
    if PRODUCTS_JSON.exists():
        with open(PRODUCTS_JSON, encoding="utf-8") as f:
            return json.load(f)
    return []

def lade_importiert():
    if IMPORTIERT_JSON.exists():
        with open(IMPORTIERT_JSON, encoding="utf-8") as f:
            return set(json.load(f))
    return set()

def speichere_alles(produkte, importiert):
    DATA_ORDNER.mkdir(exist_ok=True)

    # products.json aktualisieren
    with open(PRODUCTS_JSON, "w", encoding="utf-8") as f:
        json.dump(produkte, f, ensure_ascii=False, indent=2)

    # importiert.json aktualisieren
    with open(IMPORTIERT_JSON, "w", encoding="utf-8") as f:
        json.dump(sorted(importiert), f, ensure_ascii=False, indent=2)

    # products.js regenerieren (wird von der Website geladen)
    regeneriere_products_js(produkte)

def regeneriere_products_js(produkte):
    """Generiert js/products.js vollständig aus data/products.json."""
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

# ============================================================
# HILFSFUNKTIONEN
# ============================================================
def nächste_id(produkte):
    if not produkte:
        return 101
    return max(int(p["id"]) for p in produkte) + 1

def fotos_sortiert(ordner):
    """Alle JPEGs eines Ordners alphabetisch sortiert."""
    fotos = []
    for ext in ["*.jpg", "*.jpeg", "*.JPG", "*.JPEG", "*.png", "*.PNG"]:
        fotos.extend(ordner.glob(ext))
    return sorted(set(fotos), key=lambda f: f.name.lower())

def validiere_meta(meta, ordner_name):
    """Prüft Pflichtfelder und gibt Fehlerliste zurück."""
    pflicht = {
        "titel":     "Name des Artikels (z.B. 'Sommerkleid, blau')",
        "preis":     "Verkaufspreis als Zahl (z.B. 15)",
        "kategorie": "z.B. 'Kleidung', 'Schuhe' oder 'Accessoires'",
        "größe":     "z.B. '128', 'M', '38'",
        "zustand":   "z.B. 'Sehr guter Zustand', 'Guter Zustand'",
    }
    fehler = []
    for feld, hinweis in pflicht.items():
        val = meta.get(feld)
        if not val and val != 0:
            fehler.append(f"    Fehlendes Pflichtfeld '{feld}': {hinweis}")
    return fehler

def importiere_artikel(ordner, neue_id):
    """Importiert einen Artikel-Ordner. Gibt Produktdict oder None zurück."""
    produkt_json_pfad = ordner / "produkt.json"

    # produkt.json prüfen
    if not produkt_json_pfad.exists():
        print(f"  ⚠ Kein 'produkt.json' gefunden → übersprungen")
        print(f"    Vorlage kopieren aus: Verkäufe/VORLAGE/produkt.json")
        return None

    # JSON lesen
    try:
        with open(produkt_json_pfad, encoding="utf-8") as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        print(f"  ✗ Fehler in produkt.json (ungültiges JSON): {e}")
        print(f"    Tipp: Keine einfachen Anführungszeichen verwenden, nur doppelte!")
        return None

    # Anleitung-Feld entfernen (falls Vorlage direkt kopiert)
    meta.pop("_anleitung", None)

    # Pflichtfelder prüfen
    fehler = validiere_meta(meta, ordner.name)
    if fehler:
        print(f"  ✗ Pflichtfelder fehlen:")
        for f in fehler:
            print(f)
        return None

    # Fotos kopieren
    fotos = fotos_sortiert(ordner)
    if not fotos:
        print(f"  ⚠ Keine Fotos gefunden — Artikel wird ohne Bilder importiert")

    bild_pfade = []
    for i, foto in enumerate(fotos, 1):
        endung = foto.suffix.lower().replace(".jpeg", ".jpg")
        ziel_name = f"{neue_id}-{i}{endung}"
        ziel = IMAGES_ORDNER / ziel_name
        shutil.copy2(foto, ziel)
        bild_pfade.append(f"images/{ziel_name}")

    # Produkt zusammensetzen
    heute = date.today().isoformat()
    produkt = {
        "id":                  str(neue_id),
        "titel":               str(meta.get("titel", "")).strip(),
        "kategorie":           str(meta.get("kategorie", "Kleidung")).strip(),
        "unterkategorie":      str(meta.get("unterkategorie", "")).strip(),
        "marke":               str(meta.get("marke", "Unbekannt")).strip(),
        "größe":               str(meta.get("größe", "")).strip(),
        "farbe":               str(meta.get("farbe", "")).strip(),
        "material":            str(meta.get("material", "")).strip(),
        "zustand":             str(meta.get("zustand", "")).strip(),
        "preis":               float(meta.get("preis", 0)),
        "ursprünglicher_preis": meta.get("ursprünglicher_preis", None),
        "beschreibung":        str(meta.get("beschreibung", "")).strip(),
        "maße":                str(meta.get("maße", "")).strip(),
        "saison":              str(meta.get("saison", "")).strip(),
        "stil":                str(meta.get("stil", "")).strip(),
        "verfügbarkeit":       str(meta.get("verfügbarkeit", "verfügbar")).strip(),
        "bilder":              bild_pfade,
        "besonderheiten":      str(meta.get("besonderheiten", "")).strip(),
        "mängel":              str(meta.get("mängel", "Keine")).strip(),
        "erstellt_am":         meta.get("erstellt_am", heute),
    }

    return produkt

# ============================================================
# STATUS AKTUALISIEREN (verfügbar ↔ reserviert ↔ verkauft)
# ============================================================
def aktualisiere_status(produkte):
    """Liest Statusänderungen aus produkt.json-Dateien und überträgt sie."""
    geändert = 0
    for ordner in VERKÄUFE_ORDNER.iterdir():
        if not ordner.is_dir() or ordner.name.startswith(".") or ordner.name == "VORLAGE":
            continue
        status_datei = ordner / "produkt.json"
        if not status_datei.exists():
            continue
        try:
            with open(status_datei, encoding="utf-8") as f:
                meta = json.load(f)
        except Exception:
            continue
        neuer_status = meta.get("verfügbarkeit", "").strip()
        if not neuer_status:
            continue
        for p in produkte:
            if p.get("titel", "").strip() == meta.get("titel", "").strip():
                if p["verfügbarkeit"] != neuer_status:
                    alt = p["verfügbarkeit"]
                    p["verfügbarkeit"] = neuer_status
                    print(f"  ↺ Status geändert: '{p['titel']}': {alt} → {neuer_status}")
                    geändert += 1
    return geändert

# ============================================================
# HAUPTPROGRAMM
# ============================================================
def main():
    trennlinie = "─" * 55

    print()
    print("=" * 55)
    print("  Kleiderschrank Studio — Artikel-Import")
    print("=" * 55)

    # Verzeichnisse prüfen
    if not VERKÄUFE_ORDNER.exists():
        print(f"\n✗ Ordner nicht gefunden:")
        print(f"  {VERKÄUFE_ORDNER}")
        print(f"\nBitte Pfad in import_artikel.py anpassen (KONFIGURATION).")
        input("\nEnter drücken zum Beenden...")
        sys.exit(1)

    IMAGES_ORDNER.mkdir(exist_ok=True)

    # Daten laden
    produkte   = lade_produkte()
    importiert = lade_importiert()

    print(f"\n📦 {len(produkte)} bestehende Artikel")
    print(f"📁 Suche in: {VERKÄUFE_ORDNER}")

    # Status-Updates aus vorhandenen produkt.json-Dateien übernehmen
    print(f"\n{trennlinie}")
    print("  Status-Aktualisierungen prüfen …")
    status_updates = aktualisiere_status(produkte)
    if status_updates == 0:
        print("  Keine Änderungen")

    # Neue Ordner scannen
    print(f"\n{trennlinie}")
    print("  Neue Artikel suchen …")

    unterordner = sorted([
        d for d in VERKÄUFE_ORDNER.iterdir()
        if d.is_dir()
        and not d.name.startswith(".")
        and d.name != "VORLAGE"
    ])

    neu_importiert = 0
    übersprungen   = 0

    for ordner in unterordner:
        if ordner.name in importiert:
            übersprungen += 1
            continue

        print(f"\n→ Neuer Ordner: {ordner.name}")
        neue_id = nächste_id(produkte)
        produkt  = importiere_artikel(ordner, neue_id)

        if produkt:
            produkte.append(produkt)
            importiert.add(ordner.name)
            fotos_anzahl = len(produkt["bilder"])
            print(f"  ✓ Artikel #{neue_id} importiert: {produkt['titel']}")
            print(f"    {fotos_anzahl} Foto(s) · {produkt['preis']} € · Gr. {produkt['größe']}")
            neu_importiert += 1

    # Zusammenfassung
    print(f"\n{trennlinie}")
    print(f"  Neu importiert : {neu_importiert}")
    print(f"  Bereits bekannt: {übersprungen}")
    print(f"  Status-Updates : {status_updates}")

    if neu_importiert > 0 or status_updates > 0:
        speichere_alles(produkte, importiert)
        print(f"\n✅ Website aktualisiert!")
        print(f"   Seite im Browser neu laden: http://localhost:3456")
    else:
        if neu_importiert == 0 and not unterordner:
            print(f"\n  Noch keine Artikel-Ordner in:")
            print(f"  {VERKÄUFE_ORDNER}")
            print(f"\n  So geht's:")
            print(f"  1. Unterordner anlegen (z.B. 'Mein_Kleid')")
            print(f"  2. Fotos + produkt.json einfügen")
            print(f"  3. Dieses Skript erneut ausführen")
        else:
            print(f"\n  Keine Änderungen — Website ist aktuell.")

    print("=" * 55)
    print()

    # Auf Mac: Fenster offen halten wenn per Doppelklick (.command) gestartet
    try:
        if not sys.stdin.isatty():
            pass  # Skript wurde gepiped – kein input() nötig
        else:
            input("Enter drücken zum Schließen...")
    except (EOFError, KeyboardInterrupt):
        pass

if __name__ == "__main__":
    main()
