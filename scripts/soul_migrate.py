#!/usr/bin/env python3
"""
🧬 Soul Archive — Migrate from legacy ~/.skills_data/ to ~/.agent-commons/skills_data/

This is opt-in: it only runs when explicitly invoked.

What it does:
  1. Detect data at ~/.skills_data/soul-archive/
  2. Confirm with user (unless --yes)
  3. Move (rename) the directory to ~/.agent-commons/skills_data/soul-archive/
  4. Leave a small README at the legacy location explaining the move
  5. Report what changed

What it does NOT do:
  - Touch any agent-commons protocol files (identity/, rules/, handoff/, log/, registry.json)
  - Read or modify the contents of your soul-archive data
  - Sync, transform, or upload anything anywhere

Usage:
  python soul_migrate.py             # interactive
  python soul_migrate.py --yes       # non-interactive
  python soul_migrate.py --dry-run   # show what would happen
  python soul_migrate.py --rollback  # move data back from new to legacy
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

try:
    from soul_paths import (
        AGENT_COMMONS_ROOT,
        LEGACY_SOUL_ROOT,
        NEW_SOUL_ROOT,
    )
except ImportError:
    # Allow running standalone without package context
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from soul_paths import (  # noqa: E402
        AGENT_COMMONS_ROOT,
        LEGACY_SOUL_ROOT,
        NEW_SOUL_ROOT,
    )


LEGACY_README = """\
# Soul Archive — moved

Your Soul Archive data has been migrated to:

    ~/.agent-commons/skills_data/soul-archive/

This new location lives under the Agent Commons directory
(https://github.com/dqsjqian/agent-commons) so that all your AI-agent-related
data shares a single backup root.

If you want to roll back, run:

    python soul_migrate.py --rollback

If you no longer use Soul Archive, this directory can be safely deleted.
"""


def show_status():
    print("🧬 Soul Archive migration status")
    print(f"  agent-commons root:  {AGENT_COMMONS_ROOT}  (exists: {AGENT_COMMONS_ROOT.is_dir()})")
    print(f"  legacy soul-archive: {LEGACY_SOUL_ROOT}  (exists: {LEGACY_SOUL_ROOT.exists()})")
    print(f"  new soul-archive:    {NEW_SOUL_ROOT}  (exists: {NEW_SOUL_ROOT.exists()})")


def confirm(prompt: str, assume_yes: bool) -> bool:
    if assume_yes:
        return True
    try:
        ans = input(f"{prompt} [y/N]: ").strip().lower()
    except EOFError:
        return False
    return ans in ("y", "yes")


def migrate(dry_run: bool, assume_yes: bool) -> int:
    show_status()
    print()

    # Pre-flight checks
    if not LEGACY_SOUL_ROOT.exists():
        print("✅ Nothing to migrate — legacy directory does not exist.")
        return 0

    if not (LEGACY_SOUL_ROOT / "profile.json").exists():
        # Just a stale empty dir, not real data — still warn but don't block
        print("⚠️  Legacy directory exists but has no profile.json (looks empty).")
        if not confirm("Continue anyway?", assume_yes):
            return 1

    if not AGENT_COMMONS_ROOT.is_dir():
        print("❌ ~/.agent-commons/ does not exist.")
        print("   Install Agent Commons first:")
        print("     curl -fsSL https://raw.githubusercontent.com/dqsjqian/agent-commons/main/install.sh | bash")
        return 2

    if NEW_SOUL_ROOT.exists():
        print(f"❌ Target already exists: {NEW_SOUL_ROOT}")
        print("   Migration aborted to avoid overwriting. Inspect both directories,")
        print("   then either remove the target manually or use --rollback first.")
        return 3

    # Show plan
    print("Migration plan:")
    print(f"  MOVE  {LEGACY_SOUL_ROOT}")
    print(f"  →     {NEW_SOUL_ROOT}")
    print(f"  WRITE {LEGACY_SOUL_ROOT}/README.md  (forwarding pointer)")
    print()

    if dry_run:
        print("🔍 Dry run — no changes made.")
        return 0

    if not confirm("Proceed with migration?", assume_yes):
        print("Aborted.")
        return 1

    # Ensure parent directory exists for the new location
    NEW_SOUL_ROOT.parent.mkdir(parents=True, exist_ok=True)

    # Atomic-ish move (same FS = atomic; cross-FS = copy+delete via shutil.move)
    print(f"  → moving {LEGACY_SOUL_ROOT} ...")
    shutil.move(str(LEGACY_SOUL_ROOT), str(NEW_SOUL_ROOT))

    # Recreate the legacy dir with just a README pointer (so users who go look there see why it's empty)
    LEGACY_SOUL_ROOT.mkdir(parents=True, exist_ok=True)
    (LEGACY_SOUL_ROOT / "README.md").write_text(LEGACY_README, encoding="utf-8")

    print()
    print("✅ Migration complete.")
    print(f"   Data is now at: {NEW_SOUL_ROOT}")
    print(f"   Forwarding note left at: {LEGACY_SOUL_ROOT}/README.md")
    return 0


def rollback(dry_run: bool, assume_yes: bool) -> int:
    show_status()
    print()

    if not NEW_SOUL_ROOT.exists():
        print("✅ Nothing to roll back — new location does not exist.")
        return 0

    if LEGACY_SOUL_ROOT.exists() and (LEGACY_SOUL_ROOT / "profile.json").exists():
        print(f"❌ Legacy location already has data: {LEGACY_SOUL_ROOT}")
        print("   Rollback would overwrite it. Inspect both, then act manually.")
        return 3

    print("Rollback plan:")
    print(f"  MOVE  {NEW_SOUL_ROOT}")
    print(f"  →     {LEGACY_SOUL_ROOT}")
    print()

    if dry_run:
        print("🔍 Dry run — no changes made.")
        return 0

    if not confirm("Proceed with rollback?", assume_yes):
        print("Aborted.")
        return 1

    # Remove the placeholder README dir if it exists
    if LEGACY_SOUL_ROOT.exists():
        # Only remove if it's just our forwarding placeholder
        contents = list(LEGACY_SOUL_ROOT.iterdir())
        if len(contents) == 1 and contents[0].name == "README.md":
            (LEGACY_SOUL_ROOT / "README.md").unlink()
            LEGACY_SOUL_ROOT.rmdir()
        else:
            print(f"❌ Legacy directory has unexpected contents: {[p.name for p in contents]}")
            print("   Refusing to clobber. Manually clean it up first.")
            return 4

    LEGACY_SOUL_ROOT.parent.mkdir(parents=True, exist_ok=True)
    print(f"  → moving {NEW_SOUL_ROOT} ...")
    shutil.move(str(NEW_SOUL_ROOT), str(LEGACY_SOUL_ROOT))

    print()
    print("✅ Rollback complete.")
    print(f"   Data is back at: {LEGACY_SOUL_ROOT}")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Migrate Soul Archive data between legacy and Agent Commons locations.",
    )
    parser.add_argument("--yes", "-y", action="store_true",
                        help="non-interactive: assume yes to all prompts")
    parser.add_argument("--dry-run", "-n", action="store_true",
                        help="show what would happen without making changes")
    parser.add_argument("--rollback", action="store_true",
                        help="move data back from new location to legacy")
    parser.add_argument("--status", action="store_true",
                        help="just show current status, don't migrate")
    args = parser.parse_args()

    if args.status:
        show_status()
        return 0

    if args.rollback:
        return rollback(dry_run=args.dry_run, assume_yes=args.yes)
    return migrate(dry_run=args.dry_run, assume_yes=args.yes)


if __name__ == "__main__":
    sys.exit(main())
