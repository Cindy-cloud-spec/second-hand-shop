#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KI-gestützter Artikel-Import
Erkennt neue Ordner in ~/Documents/Verkäufe, analysiert die Fotos mit Claude
und stellt die Artikel automatisch auf die Website.
Doppelklick auf ki_importieren.command zum Starten.
"""

import base64
import json
import os
import shutil
import sys
from datetime import date
from pathlib import Path

# ── Konfiguration ────────────────────────────────────────────
VERKÄUFE_ORDNER = Path.home() / "Documents" / "Verkäufe"
WEBSITE_ORDNER  = Path(__file__).parent.resolve()
IMAGES_ORDNER   = WEBSITE_ORDNER / "images"
DATA_ORDNER     = WEBSITE_ORDNER / "data"
PRODUCTS_JSON   = DATA_ORDNER / "products.json"
IMPORTIERT_JSON = DATA_ORDNER / "importiert.json"
PRODUCTS_JS     = WEBSITE_ORDNER / "js" / "products.js"
ENV_DATEI       = WEBSITE_ORDNER / ".env"

# ── API-Key laden ────────────────────────────────────────────
def lade_api_key():
    # 1. Umgebungsvariable
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if key and not key.startswith("HIER"):
        return key
    # 2. .env-Datei
    if ENV_DATEI.exists():
        for zeile in ENV_DATEI.read_text().splitlines():
            if zeile.startswith("ANTHROPIC_API_KEY="):
                key = zeile.split("=", 1)[1].strip()
                if key and not key.startswith("HIER"):
                    return key
    return None

# ── Daten laden/speichern ────────────────────────────────────
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
    with open(PRODUCTS_JSON, "w", encoding="utf-8") as f:
        json.dump(produkte, f, ensure_ascii=False, indent=2)
    with open(IMPORTIERT_JSON, "w", encoding="utf-8") as f:
        json.dump(sorted(importiert), f, ensure_ascii=False, indent=2)
    regeneriere_products_js(produkte)

def regeneriere_products_js(produkte):
    products_json_str = json.dumps(produkte, ensure_ascii=False, indent=2)
    inhalt = f"""// ============================================================
// PRODUCTS.JS — Automatisch generiert
// ⚠ NICHT manuell bearbeiten!
// ============================================================

const products = {products_json_str};

function getUniqueValues(field) {{
  const values = products.map(p => p[field]).filter(v => v && v !== "Unbekannt" && v !== null);
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

# ── Hilfsfunktionen ──────────────────────────────────────────
def nächste_id(produkte):
    if not produkte:
        return 101
    return max(int(p["id"]) for p in produkte) + 1

def fotos_sortiert(ordner):
    fotos = []
    for ext in ["*.jpg", "*.jpeg", "*.JPG", "*.JPEG", "*.png", "*.PNG"]:
        fotos.extend(ordner.glob(ext))
    return sorted(set(fotos), key=lambda f: f.name.lower())

def foto_als_base64(pfad):
    """Foto laden, bei Bedarf verkleinern (max 1500px, max 4MB), als base64 zurückgeben."""
    import subprocess, tempfile

    # Dateigröße prüfen
    groesse = pfad.stat().st_size
    if groesse > 4_000_000:
        # Mit macOS sips auf max 1500px verkleinern
        tmp = Path(tempfile.mktemp(suffix=".jpg"))
        subprocess.run(
            ["sips", "-Z", "1500", "--setProperty", "formatOptions", "85",
             str(pfad), "--out", str(tmp)],
            capture_output=True
        )
        if tmp.exists():
            with open(tmp, "rb") as f:
                data = f.read()
            tmp.unlink()
            return base64.standard_b64encode(data).decode("utf-8")

    with open(pfad, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")

# ── KI-Analyse ───────────────────────────────────────────────
def analysiere_mit_ki(fotos, ordner_name, client):
    """Schickt bis zu 3 Fotos an Claude und bekommt Produktdaten zurück."""

    # Maximal 3 Fotos senden (Kosten sparen)
    auswahl = fotos[:3]

    bild_inhalte = []
    for foto in auswahl:
        endung = foto.suffix.lower().lstrip(".")
        mime = "image/jpeg" if endung in ("jpg", "jpeg") else "image/png"
        bild_inhalte.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": mime,
                "data": foto_als_base64(foto),
            }
        })

    bild_inhalte.append({
        "type": "text",
        "text": f"""Analysiere diesen Kleidungsartikel für eine Second-Hand-Verkaufswebsite.
Ordnername als Hinweis: "{ordner_name}"

Antworte NUR mit einem JSON-Objekt, ohne Erklärungen davor oder danach.
Schreibe alle Texte auf Deutsch.

Felder:
{{
  "titel": "Kurzer, klarer Produktname (z.B. 'Jeans, blau – Zara, Gr. 38')",
  "kategorie": "Kleidung oder Schuhe oder Accessoires oder Taschen",
  "unterkategorie": "z.B. Hosen, Kleider, Jacken & Mäntel, Pullover & Strick, Tops & Shirts, Schuhe, Sonstiges",
  "marke": "Markenname falls erkennbar, sonst 'Unbekannt'",
  "größe": "Größe falls erkennbar, sonst ''",
  "farbe": "Hauptfarbe(n)",
  "material": "Material falls auf Etikett erkennbar, sonst ''",
  "zustand": "Eines von: Neuwertig, Sehr guter Zustand, Guter Zustand, Getragen",
  "mängel": "Sichtbare Mängel beschreiben, oder 'Keine'",
  "beschreibung": "2-3 Sätze ansprechende Beschreibung für die Website",
  "besonderheiten": "Besondere Details wie Taschen, Schnitt, Muster (kurz)",
  "saison": "Frühling/Sommer oder Herbst/Winter oder Ganzjährig",
  "preis_vorschlag": Zahl zwischen 3 und 40 basierend auf Zustand und Marke
}}"""
    })

    antwort = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        messages=[{"role": "user", "content": bild_inhalte}]
    )

    text = antwort.content[0].text.strip()

    # JSON aus Antwort extrahieren
    if "```" in text:
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    text = text.strip()

    return json.loads(text)


# ── Artikel importieren ──────────────────────────────────────
def importiere_ordner(ordner, neue_id, client):
    fotos = fotos_sortiert(ordner)
    if not fotos:
        print(f"  ⚠ Keine Fotos — übersprungen")
        return None

    print(f"  🔍 KI analysiert {len(fotos)} Foto(s) …")

    try:
        ki_daten = analysiere_mit_ki(fotos, ordner.name, client)
    except Exception as e:
        print(f"  ✗ KI-Fehler: {e}")
        return None

    # Fotos kopieren
    bild_pfade = []
    for i, foto in enumerate(fotos, 1):
        endung = foto.suffix.lower().replace(".jpeg", ".jpg")
        ziel_name = f"{neue_id}-{i}{endung}"
        shutil.copy2(foto, IMAGES_ORDNER / ziel_name)
        bild_pfade.append(f"images/{ziel_name}")

    heute = date.today().isoformat()
    preis = float(ki_daten.get("preis_vorschlag", 10))

    produkt = {
        "id":                  str(neue_id),
        "titel":               ki_daten.get("titel", ordner.name).strip(),
        "kategorie":           ki_daten.get("kategorie", "Kleidung").strip(),
        "unterkategorie":      ki_daten.get("unterkategorie", "").strip(),
        "marke":               ki_daten.get("marke", "Unbekannt").strip(),
        "größe":               ki_daten.get("größe", "").strip(),
        "farbe":               ki_daten.get("farbe", "").strip(),
        "material":            ki_daten.get("material", "").strip(),
        "zustand":             ki_daten.get("zustand", "Guter Zustand").strip(),
        "preis":               preis,
        "ursprünglicher_preis": None,
        "beschreibung":        ki_daten.get("beschreibung", "").strip(),
        "maße":                "",
        "saison":              ki_daten.get("saison", "Ganzjährig").strip(),
        "stil":                "",
        "verfügbarkeit":       "verfügbar",
        "bilder":              bild_pfade,
        "besonderheiten":      ki_daten.get("besonderheiten", "").strip(),
        "mängel":              ki_daten.get("mängel", "Keine").strip(),
        "erstellt_am":         heute,
    }

    return produkt, preis


# ── Hauptprogramm ────────────────────────────────────────────
def main():
    print()
    print("=" * 55)
    print("  Kleiderschrank Studio — KI-Import")
    print("=" * 55)

    # API-Key prüfen
    api_key = lade_api_key()
    if not api_key:
        print("\n✗ Kein API-Key gefunden.")
        print(f"  Bitte in {ENV_DATEI} eintragen:")
        print("  ANTHROPIC_API_KEY=sk-ant-...")
        input("\nEnter drücken zum Beenden...")
        sys.exit(1)

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
    except ImportError:
        print("\n✗ Anthropic-Paket fehlt. Bitte im Terminal ausführen:")
        print("  pip3 install anthropic")
        input("\nEnter drücken zum Beenden...")
        sys.exit(1)

    IMAGES_ORDNER.mkdir(exist_ok=True)

    produkte   = lade_produkte()
    importiert = lade_importiert()

    print(f"\n📦 {len(produkte)} bestehende Artikel")
    print(f"📁 Suche in: {VERKÄUFE_ORDNER}")

    unterordner = sorted([
        d for d in VERKÄUFE_ORDNER.iterdir()
        if d.is_dir() and not d.name.startswith(".") and d.name != "VORLAGE"
    ])

    neue = [d for d in unterordner if d.name not in importiert]

    if not neue:
        print("\n  Keine neuen Ordner gefunden — alles aktuell.")
        print("=" * 55)
        try:
            if sys.stdin.isatty():
                input("\nEnter drücken zum Schließen...")
        except (EOFError, KeyboardInterrupt):
            pass
        return

    print(f"\n  {len(neue)} neuer Ordner gefunden:")
    for d in neue:
        fotos = fotos_sortiert(d)
        hat_json = (d / "produkt.json").exists()
        info = f"{len(fotos)} Fotos" + (" + produkt.json" if hat_json else " → KI analysiert")
        print(f"    • {d.name}  ({info})")

    print()
    print("─" * 55)

    neu_importiert = 0

    for ordner in neue:
        print(f"\n→ {ordner.name}")
        neue_id = nächste_id(produkte)

        # Hat der Ordner bereits eine produkt.json? → Normal importieren
        if (ordner / "produkt.json").exists():
            from import_artikel import importiere_artikel
            produkt = importiere_artikel(ordner, neue_id)
        else:
            # KI-Analyse
            ergebnis = importiere_ordner(ordner, neue_id, client)
            if ergebnis is None:
                continue
            produkt, preis = ergebnis

        if produkt:
            produkte.append(produkt)
            importiert.add(ordner.name)
            print(f"  ✓ Artikel #{neue_id}: {produkt['titel']}")
            print(f"    {len(produkt['bilder'])} Foto(s) · {produkt['preis']} € · Gr. {produkt['größe'] or '?'}")
            neu_importiert += 1

    print()
    print("─" * 55)
    print(f"  Neu importiert: {neu_importiert}")

    if neu_importiert > 0:
        speichere_alles(produkte, importiert)
        print(f"\n✅ Website aktualisiert!")
        print(f"   Tipp: Mit 'artikel_bearbeiten.command' kannst du")
        print(f"   Preis oder Details noch anpassen.")
        print(f"   → Browser neu laden: http://localhost:3456")

    print("=" * 55)
    print()

    try:
        if sys.stdin.isatty():
            input("Enter drücken zum Schließen...")
    except (EOFError, KeyboardInterrupt):
        pass


if __name__ == "__main__":
    main()
