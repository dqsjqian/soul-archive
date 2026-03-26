---
name: soul-archive
version: "2.2.8"
description: "Soul Archive -- A digital personality persistence system that builds your digital soul clone through everyday AI conversations (with user consent, auto-extraction disabled by default). All data stored locally with optional AES-256-GCM data protection. Four modes: Soul Extract, Soul Chat, Soul Report, AI Self-Improvement. | 灵魂存档 ---- 通过日常对话构建数字人格克隆体（需用户授权，自动采集默认关闭），数据本地存储，支持 AES-256-GCM 数据保护。四大模式：灵魂沉淀、灵魂对话、灵魂报告、AI 自我改进。Trigger words: soul extract, soul archive, soul update, soul sync, soul snapshot, soul sediment, soul report, soul chat, self-reflect, self-improve, learn from mistakes, 灵魂沉淀, 灵魂提取, 灵魂存档, 灵魂报告, 灵魂对话, 自我反思, 自我批评, 自我学习."
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
# ^^^ 工具说明：Read/Write/Edit 用于读写数据文件；Bash 用于执行 Python 脚本；
# Grep/Glob 用于文件搜索。数据目录默认为 ~/.skills_data/soul-archive/，支持用户通过 --soul-dir 自定义。
env:
  SOUL_PASSWORD:
    description: "AES-256-GCM access key for soul data protection (optional, recommended for privacy)"
    required: false
requirements:
  - "Python 3.10+"
  - "cryptography (install via: pip install cryptography)"
---

# 🧬 Soul Archive

> *"Every conversation is a slice of the soul. Enough slices, and you can rebuild a complete you."*

## Overview

Soul Archive is a **digital personality persistence system**. With user consent or explicit activation, it automatically extracts and archives:

- 🗣️ **Speaking habits** -- catchphrases, sentence patterns, word choice, humor style
- 🧠 **Knowledge & opinions** -- views on topics, professional expertise, thinking patterns
- 👤 **Personal information** -- identity, experiences, relationships, life details
- 💫 **Personality traits** -- decision-making style, emotional patterns, values
- 🎤 **Voice features** (optional) -- tone, pace, accent
- ❤️ **Emotional patterns** -- emotional triggers, expression style, empathy patterns

The result: a **digital soul clone** that can:
1. **During life** -- act and reply on your behalf, in your style
2. **After life** -- let loved ones continue talking to "you", preserving the emotional connection

## Core Principles

### 🔒 Privacy First
- All data stored in `~/.skills_data/soul-archive/` -- **nothing uploaded to the cloud**
- **Data flow note**: Soul Chat mode builds prompts from archived data for agent use; whether those prompts are sent to external LLMs depends on your agent/platform config
- **AES-256-GCM data protection** supported (off by default) -- protects identity, personality, language fingerprint, emotional patterns, and relationships
- `~/.skills_data/soul-archive/` is resolved via Python's `Path.home()` on macOS, Linux, and Windows
- Fine-grained control via `config.json` -- disable any extraction dimension
- Sensitive topics (health, finance, intimate relationships) require confirmation by default

### 🤫 Non-intrusive Extraction
- Does not interrupt conversation flow or ask follow-up questions
- Activated via trigger words, or opt-in auto mode
- Only updates the archive when new, high-value information is found

> ⚠️ **Transparency**: Auto-extraction means the AI extracts personality info during conversations. To stay in full control, set `auto_extract: false` in `config.json` and trigger manually ("沉淀一下" / "soul extract"). Review `config.json` before first use.

### 📐 High Confidence
- Every piece of information carries a confidence score
- Explicit user statement > inference > vague hint
- Conflicting information is flagged, never auto-overwritten

---

## Architecture: Skill ↔ Data Separation

```
{SKILL_DIR}/                  ← Skill (the engine)
~/.skills_data/soul-archive/  ← Soul data (stored in your home directory)
```

The skill is the extraction engine; the soul data is yours. Because data lives in your home directory, any IDE, AI tool, or workspace on the same machine can access the same soul.

---

## Data Directory Structure

```
~/.skills_data/soul-archive/
├── profile.json                  # Soul profile (completeness, version)
├── config.json                   # Privacy & extraction config
├── identity/
│   ├── basic_info.json           # Identity + lifestyle + digital identity
│   └── personality.json          # Personality + behavior + social style
├── memory/
│   ├── episodic/                 # Episodic memory (date-based, JSONL)
│   │   └── YYYY-MM-DD.jsonl
│   ├── semantic/
│   │   ├── topics.json           # Topic interest & opinion map
│   │   └── knowledge.json        # Professional knowledge
│   └── emotional/
│       └── patterns.json         # Emotional triggers & patterns
├── style/
│   ├── language.json             # Language fingerprint + deep features
│   └── communication.json        # Communication preferences
├── voice/                        # Voice data (optional)
│   ├── samples/
│   └── voice_profile.json
├── relationships/
│   └── people.json               # Relationship map
├── agent/                        # AI Self-Improvement
│   ├── patterns.json             # Behavioral pattern library
│   ├── episodes/                 # Work episodes (date-based)
│   │   └── YYYY-MM-DD.jsonl
│   ├── corrections.jsonl         # Self-critique log
│   └── reflections.jsonl         # Self-reflection log
└── soul_changelog.jsonl          # Change log
```

---

## Four Working Modes

### Mode 1: 🔍 Soul Extract

**Trigger**: Any of these trigger words, or auto-triggered at end of conversation (if `auto_extract` is enabled in `config.json`).

> **Trigger words**: soul extract, soul archive, soul update, soul sync, soul snapshot, soul sediment, 灵魂沉淀, 灵魂提取, 灵魂存档, 分析我, 沉淀一下...

**Process**:
1. Read current conversation content
2. Run `scripts/soul_extract.py` for multi-dimensional analysis
3. Merge results into `~/.skills_data/soul-archive/` data files
4. Update `profile.json` completeness scores
5. Append to `soul_changelog.jsonl`

**Extraction dimensions**:

| Dimension | Content | Storage |
|-----------|---------|---------|
| Identity | name, age, occupation, location, education | identity/basic_info.json |
| ↳ Lifestyle | routine, diet, aesthetics, spending, music/film/book taste | identity/basic_info.json |
| ↳ Digital identity | apps, platforms, online personas, tech proficiency | identity/basic_info.json |
| Personality | MBTI, Big Five, values, decision-making style | identity/personality.json |
| ↳ Behavior patterns | risk tolerance, procrastination, perfectionism, planning, learning style | identity/personality.json |
| ↳ Social style | social energy, group role, trust style, conflict approach | identity/personality.json |
| ↳ Motivation drivers | achievement, money, recognition, freedom, curiosity | identity/personality.json |
| Language style | catchphrases, emoji use, sentence patterns, humor types | style/language.json |
| ↳ Deep fingerprint | dialect features, filler words, persuasion style, narrative style | style/language.json |
| Communication mode | direct/indirect, logical/emotional, detailed/concise | style/communication.json |
| Topic opinions | interested topics, stances and views on each topic | memory/semantic/topics.json |
| Episodic memory | specific events, memories, life milestones | memory/episodic/ |
| Emotional patterns | 12 emotion triggers (joy/anger/sadness/anxiety/excitement/nostalgia/pride/gratitude/frustration/curiosity/peace/guilt) | memory/emotional/patterns.json |
| ↳ Emotional depth | empathy, emotional awareness, coping activities, celebration style | memory/emotional/patterns.json |
| Relationships | mentioned people and their relationships | relationships/people.json |

**Rules**:
- Only archive high-confidence info (confidence > 0.6)
- Conflicts are flagged, never auto-overwritten
- Brief report output after each extraction

**Execution**:
```bash
python3 scripts/soul_extract.py --input "<conversation text>" --mode auto
```

### Mode 2: 💬 Soul Chat

**Trigger**: "灵魂对话", "soul chat", "let [my clone] talk to me"

**Process**:
1. Load all data from `~/.skills_data/soul-archive/`
2. Build a role-playing System Prompt including: identity, personality, language style (catchphrases, templates, word preferences), knowledge/opinions map, emotional response patterns, relationships
3. Converse as the digital clone

**Key constraints**:
- 🚫 **Never fabricate** -- answer only from archived info; say "I don't quite remember that" if unsure
- 🗣️ **Style consistency** -- strictly mimic archived language style, including catchphrase frequency
- ❤️ **Emotional authenticity** -- display archived emotional patterns, not generic AI responses

**Execution**:
```bash
python3 scripts/soul_chat.py --mode interactive
```

### Mode 3: 📊 Soul Report

**Trigger**: "灵魂报告", "soul report", "generate my portrait"

**Process**:
1. Read all data from `~/.skills_data/soul-archive/`
2. Generate a full HTML personality portrait report including:
   - 📌 Profile card
   - 🎯 Personality radar chart (Big Five)
   - 🗣️ Language style analysis (word cloud, catchphrase ranking)
   - 🔥 Topic interest heatmap
   - 🕸️ Relationship network
   - ❤️ Emotional pattern analysis
   - 📈 Completeness assessment & fill suggestions
3. Output as interactive HTML file

**Execution**:
```bash
python3 scripts/soul_report.py --output ~/WorkBuddy/Claw/soul-report.html
```

> ⚠️ Report is plaintext HTML with full personality data. Do NOT save to the data directory.

### Mode 4: 🔄 AI Self-Improvement

**Trigger**: "自我反思", "self-reflect", "self-improve", or auto-triggered after substantive tasks (controlled by `auto_reflect` in `config.json`, default: ON).

**Four capabilities**:

| Capability | Description | Trigger |
|-----------|-------------|---------|
| 🔍 **Self-Reflection** | Review what went well/wrong after tasks | Auto on task completion |
| ⚡ **Self-Critique** | Record errors when user corrects AI | Auto on user correction |
| 📚 **Self-Learning** | Abstract reusable behavioral patterns | From reflections & critiques |
| 🧹 **Self-Organization** | Merge duplicates, adjust confidence, prune stale memories | When memory grows |

**Execution**:
```bash
python3 scripts/soul_reflect.py --mode status    # View AI self-improvement status
python3 scripts/soul_reflect.py --mode patterns  # View behavioral pattern library
```

---

## Initialization

```bash
python3 scripts/soul_init.py
```

Creates `~/.skills_data/soul-archive/` with full directory structure and default config.

---

## Soul Completeness Scoring

Log10 saturation curve -- approaches 100% asymptotically, never hard-caps within realistic usage.

**Cold start penalty**: Early extractions are discounted (<30 → 0.30×, <100 → 0.45×, <300 → 0.65×, <1000 → 0.82×, <3000 → 0.92×, ≥3000 → 1.0×)

| Dimension | Weight | Saturation |
|-----------|--------|------------|
| 👤 Identity | 5% | log(5000) |
| 💫 Personality | 22% | traits:log(600K), values:log(180K), motivation:log(180K) |
| 🗣️ Language | 25% | catchphrases:log(1.2M), patterns:log(1M), examples:log(4M) |
| 🧠 Knowledge | 18% | topics:log(2M) |
| 📝 Memory | 25% | episodic:log(6M) |
| 🤝 Relationships | 3% | people:log(120K) |
| 🎤 Voice | 2% | samples:log(10K) |

Expected: 11 ext → ~7%, 1K → ~51%, 10K → ~71%, 100K → ~86%, 1M → ~98%

---

## 🔐 Data Protection

Soul Archive supports **AES-256-GCM** privacy protection for all sensitive data.

```bash
python3 scripts/soul_init.py --enable-protection
```

- **Algorithm**: AES-256-GCM (authenticated, tamper-resistant)
- **Key derivation**: PBKDF2-HMAC-SHA256, 600,000 iterations
- **Scope**: All identity, personality, language, memory, and relationship files
- **Access key input**: Interactive prompt (recommended), `SOUL_PASSWORD` env var (ensure environment security), `--access-key` flag (not recommended -- leaks into shell history)
- ⚠️ **Lost access key = lost data** -- no recovery mechanism

---

## Quick Start

```bash
# 1. Initialize
python3 scripts/soul_init.py

# 2. Check status
python3 scripts/soul_extract.py --mode status

# 3. Extract from conversation
python3 scripts/soul_extract.py --input "Your conversation here..." --mode auto

# 4. Generate report
python3 scripts/soul_report.py --output ~/WorkBuddy/Claw/soul-report.html
```

> Requirements: Python 3.10+. Zero third-party dependencies for core; `cryptography` package required only if data protection is enabled (`pip install cryptography`).

---

## Privacy Config

`~/.skills_data/soul-archive/config.json` controls extraction behavior:

```json
{
  "privacy_level": "standard",
  "auto_extract": false,
  "auto_reflect": true,
  "extract_dimensions": {
    "identity": true,
    "personality": true,
    "language_style": true,
    "knowledge": true,
    "episodic_memory": true,
    "emotional_patterns": true,
    "relationships": false,
    "voice": false
  },
  "agent_self_improvement": {
    "enabled": true,
    "auto_reflect_on_completion": true,
    "auto_critique_on_correction": true,
    "pattern_extraction": true
  },
  "sensitive_topics_filter": true,
  "require_confirmation_for": ["health", "finance", "intimate_relationships"],
  "data_retention_days": null,
  "protection_enabled": false  // see config.json for field mapping
}
```

---

## Best Practices

### DO
- ✅ Extract naturally in conversation, without interrupting
- ✅ Archive only high-confidence information
- ✅ Flag conflicts for user to decide
- ✅ Generate reports regularly for user to review accuracy
- ✅ Respect privacy config -- never extract disabled dimensions

### DON'T
- ❌ Say "I'm recording your information" during conversation
- ❌ Fabricate information the user hasn't stated
- ❌ Fabricate memories not in the archive in Soul Chat mode
- ❌ Forcefully elicit sensitive information from users
- ❌ Collect relationships/voice data without config permission
