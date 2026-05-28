#!/usr/bin/env python3
"""
🧬 Soul Archive — Path Resolver

Single source of truth for where Soul Archive data lives.

Resolution order (highest to lowest priority):
  1. Explicit --soul-dir / SOUL_DIR env override (caller's choice)
  2. NEW: ~/.agent-commons/skills_data/soul-archive/  (if ~/.agent-commons/ exists)
  3. LEGACY: ~/.skills_data/soul-archive/             (back-compat for existing users)
  4. NEW (default for fresh installs without agent-commons): ~/.skills_data/soul-archive/

Why two locations?
  - If the user has joined the Agent Commons protocol (https://github.com/dqsjqian/agent-commons),
    co-locating Soul Archive data under ~/.agent-commons/skills_data/ gives them a single
    backup root, uniform multi-device sync semantics, and discoverability for other agents.
  - If the user has NOT joined Agent Commons, falling back to ~/.skills_data/ keeps Soul Archive
    100% standalone — no implicit dependency on a project the user may not want to use.

Migration:
  Run `python -m soul migrate` (or `python soul_migrate.py`) to move existing data from the
  legacy location to the new one. The migration is opt-in and reversible.

This module has zero dependencies beyond stdlib.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional


# Public path constants ----------------------------------------------------

AGENT_COMMONS_ROOT = Path.home() / ".agent-commons"
NEW_SOUL_ROOT = AGENT_COMMONS_ROOT / "skills_data" / "soul-archive"
LEGACY_SOUL_ROOT = Path.home() / ".skills_data" / "soul-archive"


def resolve_soul_dir(override: Optional[Path] = None) -> Path:
    """
    Resolve the active Soul Archive data directory.

    Order:
      1. `override` argument (e.g. from --soul-dir CLI flag)
      2. SOUL_DIR environment variable
      3. New default ~/.agent-commons/skills_data/soul-archive/  (if ~/.agent-commons/ exists)
      4. Legacy ~/.skills_data/soul-archive/                     (back-compat)

    Note: this returns the resolved path WHETHER OR NOT it exists. Callers that need the
    directory present should mkdir it themselves (most scripts already do).
    """
    if override is not None:
        return Path(override).expanduser()

    env = os.environ.get("SOUL_DIR")
    if env:
        return Path(env).expanduser()

    # If user joined Agent Commons, prefer co-located data
    if AGENT_COMMONS_ROOT.is_dir():
        # If the new location has data, definitely use it
        if NEW_SOUL_ROOT.exists():
            return NEW_SOUL_ROOT
        # If legacy has data and new doesn't, stay on legacy until user migrates
        if LEGACY_SOUL_ROOT.exists():
            return LEGACY_SOUL_ROOT
        # Fresh install on a machine that already has agent-commons → use new
        return NEW_SOUL_ROOT

    # No agent-commons — use legacy path (the historical default)
    return LEGACY_SOUL_ROOT


def get_default_soul_dir() -> Path:
    """Convenience wrapper for the most common case (no override)."""
    return resolve_soul_dir()


def is_co_located_with_agent_commons(soul_dir: Path) -> bool:
    """Check whether the given soul_dir lives under ~/.agent-commons/."""
    try:
        soul_dir.resolve().relative_to(AGENT_COMMONS_ROOT.resolve())
        return True
    except (ValueError, OSError):
        return False


def detect_legacy_data_to_migrate() -> Optional[Path]:
    """
    Return the legacy path if it contains real data AND the new path doesn't yet exist,
    indicating the user has data they could migrate. Otherwise None.
    """
    if not LEGACY_SOUL_ROOT.exists():
        return None
    # Check the legacy dir actually has profile.json (not just an empty dir)
    if not (LEGACY_SOUL_ROOT / "profile.json").exists():
        return None
    # If new location is already populated, nothing to do
    if (NEW_SOUL_ROOT / "profile.json").exists():
        return None
    # If user hasn't joined agent-commons yet, don't push migration on them
    if not AGENT_COMMONS_ROOT.is_dir():
        return None
    return LEGACY_SOUL_ROOT


__all__ = [
    "AGENT_COMMONS_ROOT",
    "NEW_SOUL_ROOT",
    "LEGACY_SOUL_ROOT",
    "resolve_soul_dir",
    "get_default_soul_dir",
    "is_co_located_with_agent_commons",
    "detect_legacy_data_to_migrate",
]


if __name__ == "__main__":
    # Diagnostic mode — print where data WOULD live right now
    print("🧬 Soul Archive — path resolver diagnostic")
    print(f"  $HOME                            = {Path.home()}")
    print(f"  ~/.agent-commons/                exists = {AGENT_COMMONS_ROOT.is_dir()}")
    print(f"  ~/.skills_data/soul-archive/     exists = {LEGACY_SOUL_ROOT.exists()}")
    print(f"  ~/.agent-commons/skills_data/... exists = {NEW_SOUL_ROOT.exists()}")
    print()
    print(f"  resolved soul_dir = {resolve_soul_dir()}")
    legacy = detect_legacy_data_to_migrate()
    if legacy:
        print(f"  ⚠️  legacy data ready to migrate from: {legacy}")
        print(f"     → run: python -m scripts.soul_migrate")
