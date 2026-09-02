"""Test configuration: deterministic by default.

Hypothesis runs under its built-in `ci` profile (derandomize=True,
database=None, print_blob=True) unless HYPOTHESIS_PROFILE says otherwise, so
every run generates the same cases until the library, Python, or a test
changes. No test opens a network connection.
"""

from __future__ import annotations

import os

from hypothesis import settings

settings.load_profile(os.getenv("HYPOTHESIS_PROFILE", "ci"))
