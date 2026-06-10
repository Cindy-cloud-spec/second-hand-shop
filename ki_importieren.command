#!/bin/bash
# Doppelklick im Finder → KI analysiert neue Artikel automatisch
cd "$(dirname "$0")"
python3 ki_import.py
