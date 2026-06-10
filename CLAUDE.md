# Second-Hand-Shop – Projektnotizen für Claude

## Hosting

Das Projekt wird über **GitHub Pages** gehostet (vorher: Netlify).

- GitHub-Repository: https://github.com/Cindy-cloud-spec/second-hand-shop
- Das Repository ist **öffentlich** (public)

## Sicherheitsregeln – IMMER beachten

Da das Repository öffentlich ist, darf niemals Sensibles hochgeladen werden:

- **`.env`** und alle Dateien mit API-Keys oder Secrets → immer in `.gitignore` ausschließen
- Der Anthropic API-Key (`ANTHROPIC_API_KEY`) liegt ausschließlich lokal in `.env` – nie committen
- Vor jedem `git push` prüfen, ob keine Secrets in den geänderten Dateien enthalten sind
- Keine Kundendaten oder persönlichen Informationen ins Repository

## Projektstruktur

- Statische Website (HTML, CSS, JS)
- Produktdaten in `data/products.json`
- KI-gestützter Artikel-Import via `ki_import.py` (nutzt Anthropic API, Key nur lokal)
- Verwaltungsskripte als `.py` und `.command` Dateien (werden nicht über GitHub Pages ausgeliefert)
