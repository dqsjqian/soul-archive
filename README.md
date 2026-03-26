<div align="center">

# 🧬 Soul Archive

### A Digital Personality Persistence System

> *"Every conversation is a slice of the soul. Enough slices, and you can rebuild a complete you."*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![Core: Zero Deps](https://img.shields.io/badge/Core-Zero%20Deps-green.svg)](#tech-stack)
[![Data Protection: Optional](https://img.shields.io/badge/Data%20Protection-AES--256--GCM-orange.svg)](#data-protection)
[![Privacy First](https://img.shields.io/badge/Privacy-Local%20Only-purple.svg)](#privacy-by-design)

[中文](./README_CN.md) · [Quick Start](#quick-start) · [Architecture](#architecture) · [Four Modes](#four-modes) · [Privacy](#privacy-by-design)

---

**Soul Archive** automatically extracts your speaking habits, personality traits, knowledge, opinions, and emotional patterns through everyday AI conversations -- building a **digital soul clone** that is uniquely, authentically *you*.

🗣️ It knows how you talk &nbsp;·&nbsp; 🧠 It understands how you think &nbsp;·&nbsp; ❤️ It feels what moves you &nbsp;·&nbsp; 👤 It *is* the digital you

</div>

---

## ✨ Why Soul Archive?

We exchange hundreds of messages with AI every day. But when the conversation ends, **everything vanishes** -- the AI doesn't remember who you are, how you speak, or what you care about.

Soul Archive changes that. It works alongside your normal AI conversations -- **no interruptions, no interrogations** -- gradually building a multi-dimensional digital portrait of your personality.

### What Can Your "Digital Soul" Do?

| Scenario | Description |
|----------|-------------|
| 🤖 **Act on Your Behalf** | Reply to messages, write content in *your* style -- not "AI-flavored", but genuinely *you* |
| 🪞 **Self-Discovery** | Generate a personality portrait report, revealing language habits and thinking patterns you never noticed |
| 💬 **Soul Conversation** | Let your clone talk to others -- using your catchphrases, your tone, your values |
| 🌅 **Digital Legacy** | One day, your loved ones can continue talking to "you", preserving the emotional connection |

---

## 📐 Architecture

Soul Archive uses a **separation of engine and data** architecture:

```
┌─────────────────────────────────────────┐
│            Soul Archive Engine           │
│                                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │  Extract  │ │  Report  │ │   Chat   │ │
│  │  Engine   │ │ Generator│ │  Engine  │ │
│  └─────┬────┘ └────┬─────┘ └────┬─────┘ │
└────────┼───────────┼────────────┼────────┘
         │           │            │
         ▼           ▼            ▼
┌─────────────────────────────────────────┐
│           .skills_data/soul-archive/ Soul Data          │
│           (~/.skills_data/soul-archive/)                │
│                                          │
│  identity/     style/      memory/       │
│  ├── basic_info    ├── language   ├── episodic/   │
│  └── personality   └── comm      ├── semantic/    │
│                                  └── emotional/   │
│  relationships/    voice/    reports/     │
└─────────────────────────────────────────┘
```

**Why this design?**
- 🔄 **Upgradeable engine** -- Update extraction algorithms without affecting existing data
- 🏠 **Portable data** -- The `~/.skills_data/soul-archive/` directory *is* the complete soul; copy it to migrate
- 🔒 **Controllable privacy** -- Data stays local in your home directory; you decide what gets collected
- 🌐 **Cross-tool access** -- Data in home directory means any IDE, AI tool, or workspace on the same machine can access the same soul

---

## 🧬 Seven Dimensions, Thirteen Layers Deep

Soul Archive extracts personality data across **7 core dimensions**, each with deep sub-dimensions:

```
🧬 Soul Completeness
│
├── 👤 Identity ····················· Who you are
│   ├── Core Profile: name, age, occupation, education, location
│   ├── 🎯 Lifestyle: routine, diet, aesthetics, spending, travel
│   └── 🌐 Digital Identity: apps, platforms, online personas
│
├── 💫 Personality ·················· How you think
│   ├── Models: MBTI, Big Five, trait tags
│   ├── ⚡ Behavior Patterns: risk tolerance, planning, learning style
│   ├── 🤝 Social Style: social energy, group role, conflict approach
│   └── 🔥 Motivation Drivers: what keeps you going
│
├── 🗣️ Language Style ··············· How you talk
│   ├── Linguistic Fingerprint: catchphrases, sentence patterns, word choice
│   └── 🔬 Deep Fingerprint: dialect, filler words, narrative style, persuasion
│
├── 🧠 Knowledge & Opinions ········ What you know and believe
│   ├── Topic Map: interests, stances, frequency
│   └── Expertise: skills, domains, depth
│
├── 📝 Memories ···················· What you've experienced
│   └── Episodic Memory: events, milestones, emotional markers
│
├── ❤️ Emotional Patterns ·········· What moves you
│   ├── 12 Emotion Triggers: joy / anger / sadness / anxiety / excitement /
│   │   nostalgia / pride / gratitude / frustration / curiosity / peace / guilt
│   └── Emotional Depth: empathy, coping, celebration style
│
└── 🤝 Relationships ··············· Who matters to you
    └── People Map: names, relationships, interaction descriptions
```

---

## 🚀 Quick Start

### Requirements

- Python 3.10+
- Zero third-party dependencies for core functionality
- `cryptography` package required only if you enable data protection (`pip install cryptography`)

### Initialize

```bash
# Initialize soul archive (data stored in ~/.skills_data/soul-archive/ by default)
python3 scripts/soul_init.py


# This creates a ~/.skills_data/soul-archive/ data directory in your home folder
```

> **Windows users**: Use `python` instead of `python3` if `python3` is not recognized.
> **Cross-platform note**: `~/.skills_data/soul-archive/` is resolved via Python's `Path.home()`, which works correctly on macOS, Linux, and Windows.

### Check Status

```bash
python3 scripts/soul_extract.py --mode status
```

Example output:

```
🧬 Soul Archive Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Completeness: 49.8%

Dimension Scores:
  👤 Identity:     [████░░░░░░] 36%
  💫 Personality:  [██████░░░░] 61%
  🗣️ Language:     [████████░░] 81%
  🧠 Knowledge:    [██████░░░░] 60%
  📝 Memory:       [██░░░░░░░░] 20%
  🤝 Relationships:[░░░░░░░░░░]  0%
  🎤 Voice:        [░░░░░░░░░░]  0%
```

---

## 🔍 Four Modes

### Mode 1: Soul Extract

Analyze conversation text and extract personality information across all dimensions.

```bash
# Extract from text
python3 scripts/soul_extract.py \
  --soul-dir ~/.skills_data/soul-archive \
  --input "Your conversation content here..." \
  --mode auto
```

**Extraction Rules:**
- 🎯 Only high-confidence information (confidence > 0.6)
- ⚖️ Conflicting data is flagged, never automatically overwritten
- 📊 Completeness scores updated after every extraction
- 📝 All changes logged to `soul_changelog.jsonl`

### Mode 2: Soul Chat

Load the soul archive and generate a role-playing System Prompt that speaks *as you*.

```bash
# Generate role-playing prompt
python3 scripts/soul_chat.py --soul-dir ~/.skills_data/soul-archive --mode prompt

# Output soul summary
python3 scripts/soul_chat.py --soul-dir ~/.skills_data/soul-archive --mode summary
```

**Key Constraints:**
- 🚫 Never fabricate memories that aren't in the archive
- 🗣️ Strictly mimic language style, including catchphrase frequency
- ❤️ Display authentic emotional response patterns

### Mode 3: Soul Report

Generate an interactive HTML personality portrait report.

```bash
python3 scripts/soul_report.py \
  --soul-dir ~/.skills_data/soul-archive \
  --output ~/WorkBuddy/Claw/soul_report.html
```

> ⚠️ The report is plaintext HTML containing full personality data. Do NOT save it to the data directory. Output to your work directory instead.

The report includes:
- 📌 Profile card with core identity
- 🎯 Personality radar chart (Big Five visualization)
- 🗣️ Language style analysis (catchphrase ranking, word cloud)
- 🔥 Topic interest heatmap
- 🕸️ Relationship network
- ❤️ Emotional pattern analysis
- 📈 Completeness assessment & suggestions

<div align="center">
  <img src="docs/en/screenshot_header.png" alt="Soul Portrait Overview -- Completeness ring & dimension progress bars" width="700" />
  <p><em>▲ Soul Portrait Overview -- Completeness Score & 7-Dimension Progress</em></p>
  <br/>
  <img src="docs/en/screenshot_identity.png" alt="Identity & Personality -- Big Five radar chart" width="700" />
  <p><em>▲ Identity & Personality -- Life Habits, Behavioral Patterns, Big Five Radar Chart</em></p>
  <br/>
  <img src="docs/en/screenshot_language.png" alt="Language Fingerprint -- Catchphrases, patterns, speech samples" width="700" />
  <p><em>▲ Language Fingerprint -- Catchphrases, Sentence Patterns, Speech Samples</em></p>
  <br/>
  <img src="docs/en/screenshot_topics.png" alt="Topics, Emotions, Memories" width="700" />
  <p><em>▲ Topic Interests, Emotional Patterns, Relationships & Memory Fragments</em></p>
</div>

---

### Mode 4: AI Self-Improvement

Continuously improve AI capabilities through self-reflection, self-critique, and pattern learning.

```bash
# View AI improvement status
python3 scripts/soul_reflect.py --mode status

# View behavioral patterns
python3 scripts/soul_reflect.py --mode patterns
```

**Four capabilities:**

| Capability | Description | Trigger |
|-----------|-------------|---------|
| 🔍 **Self-Reflection** | Review what went well/wrong after tasks | Auto on task completion |
| ⚡ **Self-Critique** | Record errors when user corrects AI | Auto on user correction |
| 📚 **Self-Learning** | Abstract reusable behavioral patterns | From reflections & critiques |
| 🧹 **Self-Organization** | Merge, prune, and connect memories | When memory grows large |

**Auto-trigger:** After every substantial interaction, the AI automatically reflects and records lessons learned -- no hooks required. Agents that support hooks (e.g., Claude Code) can also configure automatic triggers.

---

## 📁 Data Directory Structure

```
~/.skills_data/soul-archive/
├── profile.json                  # Soul profile (completeness, version)
├── config.json                   # Privacy & collection config
├── soul_changelog.jsonl          # Change log
│
├── agent/                        # 🆕 AI Self-Improvement
│   ├── patterns.json             # Behavioral pattern library
│   ├── episodes/                 # Work episodes (date-based)
│   │   └── YYYY-MM-DD.jsonl
│   ├── corrections.jsonl         # Self-critique log
│   └── reflections.jsonl         # Self-reflection log
├── .gitignore                    # Blocks all data by default
│
├── identity/
│   ├── basic_info.json           # Identity + lifestyle + digital identity
│   └── personality.json          # Personality + behavior + social style
│
├── style/
│   ├── language.json             # Language fingerprint + deep features
│   └── communication.json        # Communication preferences
│
├── memory/
│   ├── episodic/                 # Episodic memory (date-based, JSONL)
│   │   └── YYYY-MM-DD.jsonl
│   ├── semantic/
│   │   ├── topics.json           # Topic interest & opinion map
│   │   └── knowledge.json        # Professional knowledge
│   └── emotional/
│       └── patterns.json         # Emotional triggers & patterns
│
├── relationships/
│   └── people.json               # Relationship map
│
├── voice/                        # Voice data (optional)
│   ├── samples/
│   └── voice_profile.json
```

> Reports are generated on-demand to your specified output path (not stored in the data directory).

---

## 🔒 Privacy by Design

**Privacy is not a feature. It's a baseline.**

| Decision | Why |
|----------|-----|
| 🏠 **100% Local Storage** | All data lives in `~/.skills_data/soul-archive/` -- nothing leaves your machine |
| 🔧 **Granular Control** | `config.json` lets you disable any dimension |
| 🛡️ **Sensitive Protection** | Health, finance, and intimate topics require explicit confirmation |
| 🚫 **Git Isolation** | Data lives outside any project directory, safe from accidental commits |
| 🤫 **Silent Collection** | Never tells the user "I'm recording you" during conversation |
| ⚙️ **Minimal Defaults** | Relationships and voice dimensions are OFF by default |
| 🔐 **AES-256-GCM Data Protection** | Strongly recommended -- protect all sensitive data files |

### 🔐 Data Protection

Soul Archive supports **AES-256-GCM** data protection for all sensitive data files.

> ⚠️ **Strongly recommended.** Soul Archive stores highly sensitive personal data (identity, personality, language fingerprints, emotional patterns, relationships). If data files are exposed without protection, the consequences are irreversible. With AES-256-GCM data protection enabled, files are unreadable without the access key.

```bash
# Initialize with data protection enabled
python3 scripts/soul_init.py --enable-protection
```

- **Algorithm**: AES-256-GCM (authenticated, tamper-resistant)
- **Key derivation**: PBKDF2-HMAC-SHA256 (600,000 iterations)
- **Scope**: All identity, personality, language, memory, and relationship files
- **No recovery**: Lost access key = lost data
- **Access key input**: Interactive prompt (recommended), `SOUL_PASSWORD` env var (ensure your environment is secure), or `--access-key` flag (not recommended -- leaks into shell history)
- **Dependency**: `pip install cryptography` (optional; install only if you enable data protection)
- **Env var**: `SOUL_PASSWORD` -- only required when data protection is enabled

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Core Language | Python 3 (pure standard library for core; `cryptography` package optional for data protection) |
| Init Script | Python (cross-platform) / Bash (macOS & Linux) |
| Data Format | JSON (structured) / JSONL (time-series logs) |
| Report Output | HTML + Chart.js (interactive visualization) |
| AI Integration | LLM Prompt Engineering |
| Platforms | macOS, Linux, Windows |

---

## 🧭 Completeness Scoring

Each dimension uses a **log10 saturation curve** -- extremely slow, asymptotic growth that never hard-caps at 100% within realistic usage. Thresholds are set very high (100K~6M) to reflect true long-term personality accumulation.

**Cold start penalty**: Early extractions are heavily discounted (<30 ext → 0.30x, <100 → 0.45x, <300 → 0.65x, <1000 → 0.82x, <3000 → 0.92x, ≥3000 → 1.0x).

Total = Σ(dimension score × weight) × cold_start_penalty:

| Dimension | Weight | Saturation Curve |
|-----------|--------|-------------------|
| 👤 Identity | 5% | Field fill rate (30%) + extraction count log(5000) (70%), cap 85% |
| 💫 Personality | 22% | traits log(600K)×0.30 + values log(180K)×0.10 + motivation log(180K)×0.55 + enum×0.04 |
| 🗣️ Language | 25% | catchphrases log(1.2M)×0.30 + patterns log(1M)×0.25 + examples log(4M)×0.43 + deep×0.02 |
| 🧠 Knowledge | 18% | topics log(2M) |
| 📝 Memory | 25% | episodic records log(6M) |
| 🤝 Relationships | 3% | people log(120K) |
| 🎤 Voice | 2% | voice samples log(10K) |

**Typical scores**: 11 extractions → ~7%, 1K → ~51%, 10K → ~71%, 100K → ~86%, 1M → ~98%

---

## 🗺️ Roadmap

- [x] Core extraction engine (7 dimensions + deep sub-dimensions)
- [x] Interactive HTML personality portrait report (dark theme, radar chart, word cloud)
- [x] Soul Chat System Prompt generation
- [x] Confidence scoring & conflict detection
- [x] Change log & completeness scoring
- [ ] LLM-powered automatic conversation analysis
- [ ] Voice feature collection & voice cloning
- [ ] Multi-soul management (separate archives for family/friends)
- [ ] Soul import/export (cross-platform migration)
- [ ] Web UI management dashboard
- [x] Data protection option (AES-256-GCM)
- [x] AI self-improvement engine (self-reflection, self-critique, pattern learning)

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

You are free to use, modify, and distribute this software for any purpose, including commercial use.

---

## 🤝 Acknowledgments

This project was born from a simple thought: **If every conversation were treasured, would anyone ever truly disappear?**

Thank you to everyone willing to let AI remember them. Your trust is the reason Soul Archive exists.

---

<div align="center">

**Soul Archive** · Making conversations immortal, keeping souls alive.

*Built with ❤️ and a belief that every conversation matters.*

</div>
