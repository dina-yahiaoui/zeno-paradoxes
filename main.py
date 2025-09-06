# main.py
import sys
from pathlib import Path

# Ajouter src/ au PYTHONPATH pour pouvoir faire "from zenon_menu import main"
ROOT = Path(__file__).resolve().parent
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from src.zenon_menu import main as menu_main

if __name__ == "__main__":
    menu_main(SRC_DIR)