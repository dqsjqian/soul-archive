# Multi-device sync & backup

This document covers how to safely back up, sync, or migrate Soul Archive data — especially when you're on multiple machines.

## Where your data lives

The path is resolved at runtime by [`scripts/soul_paths.py`](../scripts/soul_paths.py):

| Condition | Resolved location |
|---|---|
| `~/.agent-commons/` exists (you've joined Agent Commons) | `~/.agent-commons/skills_data/soul-archive/` |
| Otherwise (standalone use) | `~/.skills_data/soul-archive/` |
| `--soul-dir` CLI flag or `SOUL_DIR` env var | overrides everything |

To check the actual path on your machine:

```bash
python scripts/soul_paths.py
```

## Recommended sync strategies

### Option A — co-located with Agent Commons (recommended if you use both)

If you have joined the [Agent Commons](https://github.com/dqsjqian/agent-commons) protocol, your soul data lives under `~/.agent-commons/`. You can back up everything as a unit:

```bash
# Private git on your own server
cd ~/.agent-commons && git init && git add . && git commit -m "snapshot"

# rsync to a NAS / external drive / another machine
rsync -avz --delete ~/.agent-commons/ user@host:~/.agent-commons/
```

This is the simplest story: **one directory, all your AI agent state**.

### Option B — soul-archive only

If you don't use Agent Commons, sync `~/.skills_data/soul-archive/` directly:

```bash
rsync -avz --delete ~/.skills_data/soul-archive/ user@host:~/.skills_data/soul-archive/
```

## Privacy layering (important)

Soul Archive data has **two sensitivity levels**:

| Sensitivity | Files | Should sync? |
|---|---|---|
| **Public-ish** | `profile.json`, `config.json`, `identity/`, `style/`, `workflow/`, `aspirations.json` | ✅ usually safe — your basic profile and preferences |
| **Highly sensitive** | `memory/episodic/`, `memory/emotional/`, `agent/corrections.jsonl`, `agent/reflections.jsonl` | ⚠️ contains specific events, emotional patterns, AI self-critique logs |

**Recommended `.gitignore` if you version-control your soul data**:

```gitignore
# Highly sensitive — keep out of any git history
memory/episodic/
memory/emotional/
agent/corrections.jsonl
agent/reflections.jsonl
agent/episodes/

# Encrypted backups (auto-generated)
*.enc-bak

# OS clutter
.DS_Store
```

For Agent Commons users, add the equivalent to your `~/.agent-commons/.gitignore` (or the `.gitignore` of whatever wraps it):

```gitignore
skills_data/soul-archive/memory/episodic/
skills_data/soul-archive/memory/emotional/
skills_data/soul-archive/agent/corrections.jsonl
skills_data/soul-archive/agent/reflections.jsonl
skills_data/soul-archive/agent/episodes/
skills_data/soul-archive/*.enc-bak
```

## Migrating between locations

If you started with the legacy path `~/.skills_data/soul-archive/` and have since installed Agent Commons, you can move your data:

```bash
# See what would happen
python scripts/soul_migrate.py --dry-run

# Actually migrate (interactive prompt)
python scripts/soul_migrate.py

# Or non-interactive
python scripts/soul_migrate.py --yes
```

The migration:
- Moves the entire directory (preserves everything: timestamps, encrypted backups, jsonl logs)
- Leaves a forwarding `README.md` at the legacy location
- Is reversible via `--rollback`

## Migrating to a new machine

```bash
# On the old machine: pack it up
cd "$(dirname "$(python scripts/soul_paths.py | grep 'resolved' | awk '{print $NF}')")"
tar czf soul-backup.tgz "$(python scripts/soul_paths.py | grep 'resolved' | awk '{print $NF}' | xargs basename)"

# Transfer soul-backup.tgz to the new machine.

# On the new machine:
mkdir -p ~/.agent-commons/skills_data/    # or ~/.skills_data/  if standalone
tar xzf soul-backup.tgz -C ~/.agent-commons/skills_data/    # adjust target dir to taste
```

Or simpler with rsync:

```bash
rsync -avz $(python scripts/soul_paths.py | grep resolved | awk '{print $NF}')/ \
  newhost:~/.agent-commons/skills_data/soul-archive/
```

## Multi-device gotchas

- **Don't sync `*.enc-bak` if you're regenerating encryption keys per machine** — the backups won't be readable.
- **Don't run two machines extracting at the same time without sync** — you'll get conflicting writes to JSON files (last write wins).
- **`config.json` is per-user, not per-machine** — sync it freely.
- **`registry.json` (Agent Commons protocol layer) is also per-user** — agents on different machines will all show up in it; that's fine.

## What NOT to do

- ❌ Don't push your soul data to a **public** git repository, even with `memory/` excluded — `identity/basic_info.json` and `aspirations.json` still contain personal info.
- ❌ Don't sync via cloud providers that read your file contents (e.g. third-party "AI-enhanced" backup services).
- ❌ Don't symlink across two physical machines via NFS / SMB and expect concurrent writes to be safe — Soul Archive's JSON files are not designed for multi-writer concurrency.
