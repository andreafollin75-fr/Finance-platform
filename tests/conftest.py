import sys
from pathlib import Path

# Make "pipeline" importable when running plain `pytest` from the repository root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
