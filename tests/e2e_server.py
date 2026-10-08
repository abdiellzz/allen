import os
from pathlib import Path

from backend.app import create_app

DB_PATH = Path(os.environ["ALLEN_DB_PATH"])
app = create_app(DB_PATH, require_license=False)
