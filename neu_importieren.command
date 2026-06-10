#!/bin/bash
# Doppelklick im Finder → importiert neue Artikel automatisch
cd "$(dirname "$0")"
python3 import_artikel.py
