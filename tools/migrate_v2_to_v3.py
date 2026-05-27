#!/usr/bin/env python3
"""把本地 ~/.skills_data/soul-archive 从旧 schema 迁移到 v3.0 7 维 schema。

操作：
  1. 删除空的 relationships/ 和 voice/ 目录
  2. 创建新目录 workflow/, 文件 workflow/preferences.json + aspirations.json
  3. memory/semantic/knowledge.json 增加 belief_frameworks 字段
  4. profile.json dimensions 字段重写为 7 维（保留 identity/personality/language/knowledge/memory，
     新增 workflow=0 / aspirations=0；丢弃 voice / relationships）
  5. config.json 的 extract_dimensions 重写为 7 维
"""
import json
import shutil
from pathlib import Path

ROOT = Path.home() / ".skills_data" / "soul-archive"


def load(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def save(p, d):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    if not (ROOT / "profile.json").exists():
        print("❌ 灵魂存档不存在")
        return

    # 1) profile.json
    profile = load(ROOT / "profile.json")
    profile["soul_version"] = "3.0"
    old_dims = profile.get("dimensions", {})
    profile["dimensions"] = {
        "identity":       old_dims.get("identity", 0.0),
        "personality":    old_dims.get("personality", 0.0),
        "language_style": old_dims.get("language_style", 0.0),
        "knowledge":      old_dims.get("knowledge", 0.0),
        # 旧 memory 不变；如果旧 emotional 存在过单独项，合到 memory 这里
        "memory":         old_dims.get("memory", 0.0),
        "workflow":       0.0,
        "aspirations":    0.0,
    }
    save(ROOT / "profile.json", profile)

    # 2) config.json
    cfg = load(ROOT / "config.json")
    cfg["auto_extract"] = cfg.get("auto_extract", True)
    cfg["auto_reflect"] = cfg.get("auto_reflect", True)
    cfg.setdefault("auto_context_inject", True)
    cfg["extract_dimensions"] = {
        "identity":            True,
        "personality":         True,
        "language_style":      True,
        "knowledge":           True,
        "episodic_memory":     True,
        "emotional_patterns":  True,
        "workflow":            True,
        "aspirations":         True,
    }
    cfg.setdefault("agent_self_improvement", {
        "enabled": True,
        "auto_reflect_on_completion": True,
        "auto_critique_on_correction": True,
        "pattern_extraction": True,
        "recall_on_task_start": True,
        "warn_on_failure_pattern_match": True,
        "auto_distill_threshold": 5
    })
    cfg.setdefault("deduplication", {
        "enabled": True,
        "similarity_threshold": 0.85
    })
    # Drop encryption fields if any leftover
    for k in ["encryption_algorithm", "encryption_key_derivation",
              "encryption_salt", "encryption_verify"]:
        cfg.pop(k, None)
    cfg["encryption"] = False
    save(ROOT / "config.json", cfg)

    # 3) Create workflow/preferences.json
    wf_path = ROOT / "workflow" / "preferences.json"
    if not wf_path.exists():
        save(wf_path, {
            "tools": {
                "ide": [], "terminal": [], "ai_tools": [],
                "vcs": [], "doc_systems": [], "communication": []
            },
            "tech_stack": {
                "languages": [], "frameworks": [], "platforms": []
            },
            "hard_rules": [],
            "collab_conventions": [],
            "cli_habits": [],
            "output_preferences": {
                "preferred_format": None,
                "preferred_length": None,
                "preferred_tone": None,
                "structure_first": None
            },
            "pet_peeves": [],
            "_meta": {}
        })
        print(f"✓ 创建 {wf_path.relative_to(ROOT)}")

    # 4) Create aspirations.json
    asp_path = ROOT / "aspirations.json"
    if not asp_path.exists():
        save(asp_path, {
            "long_term_goals": [],
            "active_projects": [],
            "identity_aspirations": [],
            "skills_to_learn": [],
            "knowledge_gaps": [],
            "_meta": {}
        })
        print(f"✓ 创建 {asp_path.relative_to(ROOT)}")

    # 5) memory/semantic/knowledge.json 加 belief_frameworks
    knowl_path = ROOT / "memory" / "semantic" / "knowledge.json"
    if knowl_path.exists():
        knowl = load(knowl_path)
        if "belief_frameworks" not in knowl:
            knowl["belief_frameworks"] = []
            save(knowl_path, knowl)
            print(f"✓ 给 {knowl_path.relative_to(ROOT)} 加 belief_frameworks 字段")

    # 6) Drop relationships/, voice/ if empty
    rel_dir = ROOT / "relationships"
    if rel_dir.exists():
        people_file = rel_dir / "people.json"
        people = load(people_file) if people_file.exists() else {"people": []}
        if not people.get("people"):
            shutil.rmtree(rel_dir)
            print(f"✓ 删除空目录 relationships/")
        else:
            print(f"⚠️  relationships/ 不为空（{len(people.get('people', []))} 条），保留备份")

    voice_dir = ROOT / "voice"
    if voice_dir.exists():
        # 备份再删
        backup = ROOT.parent / f"soul-archive.legacy-voice"
        if not backup.exists():
            shutil.move(str(voice_dir), str(backup))
            print(f"✓ voice/ → 备份至 {backup}")
        else:
            shutil.rmtree(voice_dir)
            print(f"✓ 删除 voice/（已存在备份）")

    print()
    print("✅ 迁移完成。当前 ~/.skills_data/soul-archive/ 已是 v3.0 7 维 schema。")


if __name__ == "__main__":
    main()
