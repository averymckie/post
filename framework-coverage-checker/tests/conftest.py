import sys
from pathlib import Path
from hypothesis import settings

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
settings.register_profile("checker", max_examples=100, deadline=None, derandomize=True, database=None)
settings.load_profile("checker")
