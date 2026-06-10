#!/bin/bash
# Doppelklick → ZIP für Netlify-Upload erstellen
cd "$(dirname "$0")/.."

echo ""
echo "======================================================="
echo "  Kleiderschrank Studio — ZIP für Netlify erstellen"
echo "======================================================="
echo ""
echo "  Bilder werden optimiert …"

# Bilder auf Webgröße komprimieren
for f in second-hand-shop/images/*.jpg; do
  sips -Z 900 --setProperty formatOptions 70 "$f" --out "$f" -s format jpeg > /dev/null 2>&1
done

echo "  ZIP wird erstellt …"
rm -f second-hand-shop.zip
zip -r second-hand-shop.zip second-hand-shop \
  --exclude "second-hand-shop/.env" \
  --exclude "second-hand-shop/*.py" \
  --exclude "second-hand-shop/*.command" \
  --exclude "second-hand-shop/__pycache__/*" \
  --exclude "second-hand-shop/.DS_Store" \
  --exclude "second-hand-shop/.claude/*" \
  -q

GROESSE=$(du -sh second-hand-shop.zip | cut -f1)

echo ""
echo "======================================================="
echo "  ✅ Fertig! ZIP-Datei: second-hand-shop.zip ($GROESSE)"
echo ""
echo "  Nächster Schritt:"
echo "  → cindy-secondhand.netlify.app aufrufen"
echo "  → Deploys → ZIP-Datei reinziehen"
echo "======================================================="
echo ""

# Finder öffnen und ZIP-Datei markieren
open -R second-hand-shop.zip

read -p "Enter drücken zum Schließen..."
