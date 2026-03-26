#!/usr/bin/env python3
"""
🧬 Soul Report Generator (Multi-language)
Generate an interactive HTML personality portrait report.

Supports automatic language detection:
  - Chinese name → Chinese report
  - Non-Chinese name → English report
  - Manual override via --lang zh/en

Usage:
  python3 soul_report.py [--output /path/to/report.html] [--lang zh|en]
  python3 soul_report.py --soul-dir /custom/path --output report.html

Default data directory: ~/.skills_data/soul-archive/ (resolved via Path.home(), cross-platform)
"""

import json
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from soul_extract import SoulArchive, load_json


# ============================================================
# Multi-language Translation Dictionaries
# ============================================================

I18N = {
    "zh": {
        "html_lang": "zh-CN",
        "title": "{name} 的灵魂画像",
        "subtitle": "基于 {n} 次对话提取 · 最后更新 {date}",
        "soul_completeness": "灵魂完整度",
        "dim_completeness": "各维度完整度",
        "identity": "身份信息",
        "personality": "性格特征",
        "language_fp": "语言指纹",
        "topics": "话题兴趣",
        "emotions": "情感模式",
        "relationships": "人际关系",
        "memories": "记忆片段",
        "footer": "灵魂存档 Soul Archive {version} · 生成于 {time}",
        # Identity fields
        "id_name": "姓名", "id_nickname": "昵称", "id_age": "年龄",
        "id_gender": "性别", "id_location": "所在地", "id_hometown": "老家",
        "id_occupation": "职业", "id_company": "公司", "id_education": "学历",
        "id_hobbies": "爱好", "id_motto": "人生信条",
        # Lifestyle
        "lifestyle": "🎯 生活习惯",
        "ls_routine": "作息", "ls_sleep": "睡眠",
        "ls_food": "饮食偏好", "ls_music": "音乐品味",
        "ls_movie": "电影品味", "ls_book": "阅读偏好",
        "ls_aesthetic": "审美风格", "ls_spending": "消费风格",
        "ls_travel": "旅行偏好", "ls_pet": "宠物",
        # Digital
        "digital": "🌐 数字身份",
        "dg_apps": "常用App", "dg_social": "社交平台",
        "dg_personas": "网名风格", "dg_tech": "技术水平",
        "dg_habits": "上网习惯",
        # Personality
        "ps_decision": "决策",
        "ps_behavior": "⚡ 行为模式",
        "ps_risk": "风险偏好", "ps_procrastination": "拖延程度",
        "ps_perfectionism": "完美主义", "ps_planning": "计划性",
        "ps_learning": "学习方式", "ps_work": "工作风格",
        "ps_social": "🤝 社交风格",
        "ps_energy": "社交能量", "ps_role": "群体角色",
        "ps_conflict": "冲突方式", "ps_trust": "信任方式",
        "ps_drivers": "🔥 核心驱动力",
        "no_data": "暂无数据",
        "no_data_chat": "暂无数据，继续聊天来补充...",
        # Language
        "catchphrases": "💬 口头禅",
        "sentence_patterns": "📐 句式模式",
        "speech_samples": "✍️ 说话示例",
        "formality": "正式度", "verbosity": "话量",
        "humor": "幽默", "thinking": "思考表达",
        "filler_words": "💭 语气词/填充词",
        "dialect": "🏠 方言特征",
        "agree_expr": "👍 同意时的表达",
        "disagree_expr": "👎 不同意时的表达",
        "deep_fp": "🔬 深度指纹",
        "persuasion": "说服方式", "storytelling": "叙事风格",
        "question_style": "提问风格", "greeting": "打招呼",
        "farewell": "告别方式", "typing": "打字习惯",
        "no_lang_data": "暂无语言数据",
        "no_topic_data": "暂无话题数据",
        "no_emotion_data": "暂无情感数据",
        "no_people_data": "暂无人际关系数据（需在 config.json 中启用 relationships 采集）",
        "no_memory_data": "暂无记忆数据，继续对话来积累...",
        # Big Five
        "bf_openness": "开放性", "bf_conscientiousness": "尽责性",
        "bf_extraversion": "外向性", "bf_agreeableness": "宜人性",
        "bf_stability": "情绪稳定",
        # Custom personality dimensions
        "urgency": "🔥 紧迫感", "satisfaction": "😌 满意",
        # MBTI
        "mbti_title": "MBTI 人格类型",
        "mbti_dimension": "维度",
        "mbti_E": "外向 (E)", "mbti_I": "内向 (I)",
        "mbti_S": "感觉 (S)", "mbti_N": "直觉 (N)",
        "mbti_T": "思考 (T)", "mbti_F": "情感 (F)",
        "mbti_J": "判断 (J)", "mbti_P": "知觉 (P)",
        "mbti_confidence": "置信度",
        "mbti_note": "基于对话行为模式推断，仅供参考",
        "mbti_energy": "能量指向", "mbti_info": "信息获取",
        "mbti_decision": "决策方式", "mbti_lifestyle": "生活态度",
        "confidence": "置信度",
        # Emotion labels
        "emo_joy": "😊 开心", "emo_anger": "😤 生气",
        "emo_sadness": "😢 伤感", "emo_anxiety": "😰 焦虑",
        "emo_excitement": "🤩 兴奋", "emo_nostalgia": "🥹 怀旧",
        "emo_pride": "🏆 自豪", "emo_gratitude": "🙏 感恩",
        "emo_frustration": "😤 挫败", "emo_curiosity": "🧐 好奇",
        "emo_peace": "😌 平静", "emo_guilt": "😔 愧疚",
        # Episodic emotion labels
        "calm": "😌 平静", "clarity": "💡 清明", "focused": "🎯 专注",
        "relief": "😮 松了口气", "satisfaction": "😌 满意",
        "shock_then_urgency": "😱 震惊后紧迫", "thoughtful": "🤔 若有所思",
        "excitement": "🤩 兴奋", "curiosity": "🧐 好奇", "peace": "😌 平静",
        "好奇": "🧐 好奇", "平静": "😌 平静", "满意": "😌 满意",
        # Dimension names for progress bars
        "dim_identity": "身份信息", "dim_personality": "性格特征",
        "dim_language": "语言风格", "dim_knowledge": "知识观点",
        "dim_memory": "记忆经历", "dim_relationships": "人际关系",
        "dim_voice": "语音特征",
    },
    "en": {
        "html_lang": "en",
        "title": "Soul Portrait of {name}",
        "subtitle": "Extracted from {n} conversations · Last updated {date}",
        "soul_completeness": "Soul Completeness",
        "dim_completeness": "Dimension Completeness",
        "identity": "Identity",
        "personality": "Personality",
        "language_fp": "Language Fingerprint",
        "topics": "Topic Interests",
        "emotions": "Emotional Patterns",
        "relationships": "Relationships",
        "memories": "Memory Fragments",
        "footer": "Soul Archive {version} · Generated on {time}",
        # Identity fields
        "id_name": "Name", "id_nickname": "Nickname", "id_age": "Age",
        "id_gender": "Gender", "id_location": "Location", "id_hometown": "Hometown",
        "id_occupation": "Occupation", "id_company": "Company", "id_education": "Education",
        "id_hobbies": "Hobbies", "id_motto": "Life Motto",
        # Lifestyle
        "lifestyle": "🎯 Lifestyle",
        "ls_routine": "Routine", "ls_sleep": "Sleep",
        "ls_food": "Food Preferences", "ls_music": "Music Taste",
        "ls_movie": "Movie Taste", "ls_book": "Reading Preferences",
        "ls_aesthetic": "Aesthetic Style", "ls_spending": "Spending Style",
        "ls_travel": "Travel Preferences", "ls_pet": "Pets",
        # Digital
        "digital": "🌐 Digital Identity",
        "dg_apps": "Favorite Apps", "dg_social": "Social Platforms",
        "dg_personas": "Online Personas", "dg_tech": "Tech Proficiency",
        "dg_habits": "Digital Habits",
        # Personality
        "ps_decision": "Decision",
        "ps_behavior": "⚡ Behavioral Patterns",
        "ps_risk": "Risk Tolerance", "ps_procrastination": "Procrastination",
        "ps_perfectionism": "Perfectionism", "ps_planning": "Planning Style",
        "ps_learning": "Learning Style", "ps_work": "Work Style",
        "ps_social": "🤝 Social Style",
        "ps_energy": "Social Energy", "ps_role": "Group Role",
        "ps_conflict": "Conflict Approach", "ps_trust": "Trust Building",
        "ps_drivers": "🔥 Core Drivers",
        "no_data": "No data yet",
        "no_data_chat": "No data yet. Keep chatting to fill in...",
        # Language
        "catchphrases": "💬 Catchphrases",
        "sentence_patterns": "📐 Sentence Patterns",
        "speech_samples": "✍️ Speech Samples",
        "formality": "Formality", "verbosity": "Verbosity",
        "humor": "Humor", "thinking": "Thinking Style",
        "filler_words": "💭 Filler Words",
        "dialect": "🏠 Dialect Features",
        "agree_expr": "👍 Agreement Expressions",
        "disagree_expr": "👎 Disagreement Expressions",
        "deep_fp": "🔬 Deep Fingerprint",
        "persuasion": "Persuasion Style", "storytelling": "Storytelling Style",
        "question_style": "Question Style", "greeting": "Greeting Style",
        "farewell": "Farewell Style", "typing": "Typing Habits",
        "no_lang_data": "No language data yet",
        "no_topic_data": "No topic data yet",
        "no_emotion_data": "No emotional data yet",
        "no_people_data": "No relationship data yet (enable relationships collection in config.json)",
        "no_memory_data": "No memory data yet. Keep chatting to build up...",
        # Big Five
        "bf_openness": "Openness", "bf_conscientiousness": "Conscientiousness",
        "bf_extraversion": "Extraversion", "bf_agreeableness": "Agreeableness",
        "bf_stability": "Emotional Stability",
        # Custom personality dimensions
        "urgency": "Urgency", "satisfaction": "Satisfaction",
        # MBTI
        "mbti_title": "MBTI Personality Type",
        "mbti_dimension": "Dimension",
        "mbti_E": "Extraversion (E)", "mbti_I": "Introversion (I)",
        "mbti_S": "Sensing (S)", "mbti_N": "Intuition (N)",
        "mbti_T": "Thinking (T)", "mbti_F": "Feeling (F)",
        "mbti_J": "Judging (J)", "mbti_P": "Perceiving (P)",
        "mbti_confidence": "Confidence",
        "mbti_note": "Inferred from conversational behavior patterns. For reference only.",
        "mbti_energy": "Energy Orientation", "mbti_info": "Information Gathering",
        "mbti_decision": "Decision Making", "mbti_lifestyle": "Lifestyle",
        "confidence": "Confidence",
        # Emotion labels
        "emo_joy": "😊 Joy", "emo_anger": "😤 Anger",
        "emo_sadness": "😢 Sadness", "emo_anxiety": "😰 Anxiety",
        "emo_excitement": "🤩 Excitement", "emo_nostalgia": "🥹 Nostalgia",
        "emo_pride": "🏆 Pride", "emo_gratitude": "🙏 Gratitude",
        "emo_frustration": "😤 Frustration", "emo_curiosity": "🧐 Curiosity",
        "emo_peace": "😌 Peace", "emo_guilt": "😔 Guilt",
        # Episodic emotion labels
        "calm": "😌 Calm", "clarity": "💡 Clarity", "focused": "🎯 Focused",
        "relief": "😮 Relief", "satisfaction": "😌 Satisfaction",
        "shock_then_urgency": "😱 Shock→Urgency", "thoughtful": "🤔 Thoughtful",
        "excitement": "🤩 Excitement", "curiosity": "🧐 Curiosity",
        "peace": "😌 Peace",
        # Dimension names for progress bars
        "dim_identity": "Identity", "dim_personality": "Personality",
        "dim_language": "Language Style", "dim_knowledge": "Knowledge",
        "dim_memory": "Memory", "dim_relationships": "Relationships",
        "dim_voice": "Voice",
    }
}


def _has_chinese(text: str) -> bool:
    """Check if a string contains Chinese characters."""
    if not text:
        return False
    return bool(re.search(r'[\u4e00-\u9fff\u3400-\u4dbf]', text))


def detect_language(name: str) -> str:
    """
    Auto-detect report language based on user's name.
    Chinese name → 'zh', otherwise → 'en'.
    """
    if _has_chinese(name or ""):
        return "zh"
    return "en"


def generate_html_report(archive: SoulArchive, output_path: str = None, lang: str = None, skill_version: str = "v1.3.0") -> str:
    """Generate an HTML personality portrait report with automatic language detection."""
    data = archive.load_all()
    bi = data["basic_info"]
    ps = data["personality"]
    lang_data = data["language"]
    comm = data["communication"]
    topics_data = data["topics"]
    emotional = data["emotional"]
    people = data["people"]
    profile = data["profile"]

    name = bi.get("name") or bi.get("nickname") or "Unknown Soul"

    # Auto-detect language from name if not specified
    if lang is None:
        lang = detect_language(name)

    t = I18N.get(lang, I18N["en"])  # fallback to English

    scores = profile.get("dimensions", {})
    completeness = profile.get("completeness_score", 0)

    # --- Build data JSON for JS ---
    # Topics
    topics_list = topics_data.get("topics", [])
    topics_json = json.dumps([
        {"name": tp.get("name", ""), "frequency": tp.get("frequency", 1), "sentiment": tp.get("sentiment", "neutral")}
        for tp in sorted(topics_list, key=lambda x: x.get("frequency", 0), reverse=True)[:15]
    ], ensure_ascii=False)

    # Big Five
    bf = ps.get("big_five", {})
    bf_json = json.dumps({
        t["bf_openness"]: (bf.get("openness", 0) or 0) * 100,
        t["bf_conscientiousness"]: (bf.get("conscientiousness", 0) or 0) * 100,
        t["bf_extraversion"]: (bf.get("extraversion", 0) or 0) * 100,
        t["bf_agreeableness"]: (bf.get("agreeableness", 0) or 0) * 100,
        t["bf_stability"]: (1 - (bf.get("neuroticism", 0) or 0)) * 100
    }, ensure_ascii=False)

    # ---- MBTI Inference (multi-signal holistic derivation) ----
    def infer_mbti(ps, emotional_data, topics_data, episodic_data=None):
        """Infer MBTI from the FULL personality profile — not just Big Five.
        Uses decision_style, communication_preference, values, strengths, planning_style,
        group_role, and behavioral patterns as first-class signals.
        Works for both Chinese and English personality data.
        Returns (type_str, dims).
        """
        bf = ps.get("big_five", {})
        extraversion = bf.get("extraversion", 0.5) or 0.5
        openness = bf.get("openness", 0.5) or 0.5
        agreeableness = bf.get("agreeableness", 0.5) or 0.5
        conscientiousness = bf.get("conscientiousness", 0.5) or 0.5

        # Helper: check if ANY keyword appears in a text (substring match, not equality)
        def _any_kw_in(text, keywords):
            if not text:
                return False
            text_lower = str(text).lower()
            return any(kw.lower() in text_lower for kw in keywords)

        # --- E / I: social energy direction ---
        e_score = extraversion
        social_energy = str(ps.get("social_energy", "")).lower()
        if _any_kw_in(social_energy, ["外倾", "高", "强", "extrovert", "outgoing"]):
            e_score = min(e_score + 0.15, 1.0)
        elif _any_kw_in(social_energy, ["内倾", "低", "弱", "introvert", "reserved"]):
            e_score = max(e_score - 0.15, 0.0)
        letter_e = "E" if e_score >= 0.5 else "I"
        conf_e = round(min(abs(e_score - 0.5) * 2.5, 1.0), 2)

        # --- S / N: information gathering preference ---
        topics = topics_data.get("topics", [])
        topic_count = len(topics)
        abstract_keywords = [
            "哲学", "未来", "意义", "宇宙", "AI", "理论", "概念", "抽象",
            "pattern", "principle", "system", "framework", "philosophy",
            "future", "meaning", "universe", "concept", "abstract", "theory"
        ]
        abstract_count = sum(
            1 for tp in topics
            if _any_kw_in(tp.get("name", ""), abstract_keywords)
        )
        abstract_ratio = abstract_count / max(topic_count, 1)
        n_score = openness * 0.7 + min(abstract_ratio * 2, 1.0) * 0.3
        letter_n = "N" if n_score >= 0.5 else "S"
        conf_n = round(min(abs(n_score - 0.5) * 2.5, 1.0), 2)

        # --- T / F: decision-making style ---
        # T = rational/analytical/direct/systematic decision making
        # F = empathetic/harmony-oriented/people-centered decision making
        t_signals = []
        f_signals = []

        decision_style = str(ps.get("decision_style", "") or "")
        decision_making = str(ps.get("decision_making", "") or "")
        comm_pref = str(ps.get("communication_preference", "") or "")
        comm_style = ps.get("communication_style", {}) or {}
        if isinstance(comm_style, str):
            # comm_style might be a description string — treat as text for keyword matching
            comm_style_text = comm_style
            comm_style = {}
        else:
            comm_style_text = comm_style.get("tone", "")
        values = ps.get("values", []) or []
        strengths = ps.get("strengths", []) or []
        conflict_approach = str(ps.get("conflict_approach", "") or "")
        group_role = str(ps.get("group_role", "") or "")
        work_style = str(ps.get("work_style", "") or "")

        # T signal: rational/analytical keywords in decision style (SUBSTRING match)
        t_decision_kw = ["分析", "理性", "逻辑", "优缺点", "评估", "判断", "客观",
                          "reason", "logical", "rational", "analyze", "evaluate",
                          "objective", "systematic", "evidence", "data-driven"]
        for kw in t_decision_kw:
            if kw.lower() in decision_style.lower() or kw.lower() in decision_making.lower():
                t_signals.append(1.0)

        # T signal: direct/efficient communication style (SUBSTRING match)
        t_comm_kw = ["直接", "高效", "简洁", "惜字如金", "不废话",
                      "direct", "efficient", "concise", "factual", "blunt", "no-nonsense"]
        if _any_kw_in(comm_pref, t_comm_kw) or _any_kw_in(comm_style_text, t_comm_kw):
            t_signals.append(0.8)

        # T signal: analytical/strategic strengths (SUBSTRING match)
        t_strength_kw = ["分析", "理性", "逻辑", "战略", "系统", "技术", "思维",
                          "reason", "logical", "strategic", "systematic", "analytical",
                          "technical", "thinking", "problem-solving"]
        for s in strengths:
            if _any_kw_in(s, t_strength_kw):
                t_signals.append(0.6)

        # T signal: leadership/ownership role (SUBSTRING match)
        t_role_kw = ["owner", "architect", "决策者", "leader", "发起者", "initiator",
                      "strategist", "主导", "负责人"]
        if _any_kw_in(group_role, t_role_kw):
            t_signals.append(0.5)

        # T signal: independent/systematic work style
        t_work_kw = ["独立", "系统", "independent", "systematic", "structured"]
        if _any_kw_in(work_style, t_work_kw):
            t_signals.append(0.3)

        # T signal: direct/confrontational conflict approach
        t_conflict_kw = ["直面", "对抗", "解决问题", "confront", "direct", "problem-solving"]
        if _any_kw_in(conflict_approach, t_conflict_kw):
            t_signals.append(0.5)

        # F signal: empathetic/relationship values (precise keywords to avoid false positives)
        f_value_kw = ["情感连接", "共情", "人情味", "人际", "关怀", "温暖",
                       "emotional connection", "empathy", "warmth", "caring",
                       "relationship", "feeling", "compassion"]
        for v in values:
            if _any_kw_in(v, f_value_kw):
                f_signals.append(0.8)

        # F signal: empathetic/warm communication style
        f_comm_kw = ["共鸣", "共情", "温暖", "关怀", "耐心",
                      "empathetic", "warm", "caring", "patient", "supportive"]
        if _any_kw_in(comm_pref, f_comm_kw) or _any_kw_in(comm_style_text, f_comm_kw):
            f_signals.append(0.8)

        # F signal: harmony-oriented conflict approach
        f_conflict_kw = ["和解", "协调", "包容", "妥协",
                          "harmony", "accommodate", "compromise", "mediate"]
        if _any_kw_in(conflict_approach, f_conflict_kw):
            f_signals.append(0.6)

        # F signal: emotional richness (many triggers = emotionally attuned)
        emo_triggers = emotional_data.get("triggers", {})
        emotional_count = sum(len(v) for v in emo_triggers.values())
        if emotional_count >= 15:
            f_signals.append(min(emotional_count / 30, 1.0) * 0.4)

        # Combine T/F signals
        t_total = sum(t_signals)
        f_total = sum(f_signals)
        total = t_total + f_total

        if total == 0:
            # No signals: use agreeableness as weak proxy (high agreeableness → slight F lean)
            t_ratio = 0.5 - (agreeableness - 0.5) * 0.2
        else:
            # t_ratio = how much T dominates (0..1, >0.5 = T dominant)
            t_ratio = t_total / total

        # f_score: 0 = pure T, 1 = pure F, 0.5 = balanced
        # t_ratio > 0.5 → T dominant → f_score < 0.5
        f_score = 1.0 - t_ratio
        f_score = max(0.05, min(0.95, f_score))
        letter_t = "F" if f_score >= 0.5 else "T"
        conf_t = round(min(abs(f_score - 0.5) * 2.5, 1.0), 2)

        # --- J / P: lifestyle / structure orientation ---
        j_signals = []
        p_signals = []

        planning_style = str(ps.get("planning_style", "") or "")
        risk_tolerance = str(ps.get("risk_tolerance", "") or "")

        # J signal: conscientiousness as anchor
        j_signals.append(conscientiousness)

        # J signal: decisive/action-oriented style
        j_decision_kw = ["快速决断", "立即行动", "果断", "高效", "快速",
                          "decisive", "action", "quick", "efficient", "determined"]
        if _any_kw_in(decision_style, j_decision_kw) or _any_kw_in(decision_making, j_decision_kw):
            j_signals.append(0.9)

        # J signal: execution/control strengths
        j_strength_kw = ["决断", "执行", "控制", "组织", "统筹", "落地",
                          "decisive", "execute", "control", "organize", "lead", "deliver"]
        for s in strengths:
            if _any_kw_in(s, j_strength_kw):
                j_signals.append(0.6)

        # J signal: leadership/ownership role
        j_role_kw = ["owner", "architect", "决策者", "leader", "发起者", "initiator", "主导"]
        if _any_kw_in(group_role, j_role_kw):
            j_signals.append(0.7)

        # J signal: structured planning → J; flexible/iterative → P
        j_plan_kw = ["计划", "结构", "安排", "固定", "plan", "struct", "schedule", "organized"]
        p_plan_kw = ["弹性", "灵活", "迭代", "适应", "flexible", "adaptive", "iterative", "agile"]
        if _any_kw_in(planning_style, j_plan_kw):
            j_signals.append(0.6)
        if _any_kw_in(planning_style, p_plan_kw):
            p_signals.append(0.5)

        # P signal: high risk tolerance + exploration
        p_risk_kw = ["高", "冒险", "探索", "high", "adventurous", "exploratory"]
        if _any_kw_in(risk_tolerance, p_risk_kw):
            p_signals.append(0.4)

        # Episodic: planned vs spontaneous events (weak supporting signal)
        episodes = episodic_data or []
        planned_kw = ["计划", "安排", "预约", "决定", "目标",
                       "plan", "schedule", "decided", "goal"]
        spontaneous_kw = ["突然", "临时", "意外", "spontaneous", "sudden", "impromptu"]
        if episodes:
            planned_count = sum(1 for ep in episodes if _any_kw_in(ep.get("event", ""), planned_kw))
            spontaneous_count = sum(1 for ep in episodes if _any_kw_in(ep.get("event", ""), spontaneous_kw))
            plan_ratio = planned_count / max(len(episodes), 1)
            if plan_ratio > 0.5:
                j_signals.append(plan_ratio * 0.3)
            elif spontaneous_count > planned_count:
                p_signals.append(spontaneous_count / max(len(episodes), 1) * 0.2)

        j_total = sum(j_signals)
        p_total = sum(p_signals)
        jp_total = j_total + p_total
        j_score = j_total / max(jp_total, 1) if jp_total > 0 else 0.5
        j_score = max(0.05, min(0.95, j_score))
        letter_j = "J" if j_score >= 0.5 else "P"
        conf_j = round(min(abs(j_score - 0.5) * 2.5, 1.0), 2)

        mbti_type = letter_e + letter_n + letter_t + letter_j

        # Gauge bar scores:
        # Each score represents how far toward the LEFT label (first letter listed).
        # E/I: score = e_score (high = E, left)
        # N/S: score = n_score (high = N, left)
        # T/F: score = (1 - f_score) = t_score (high = T, left)
        # J/P: score = j_score (high = J, left)
        t_display_score = round((1 - f_score) * 100)
        dims = [
            {"letter": letter_e, "other": "I", "label": t.get("mbti_E", "E"), "other_label": t.get("mbti_I", "I"),
             "score": round(e_score * 100), "conf": conf_e, "dim": t.get("mbti_energy", "Energy")},
            {"letter": letter_n, "other": "S", "label": t.get("mbti_N", "N"), "other_label": t.get("mbti_S", "S"),
             "score": round(n_score * 100), "conf": conf_n, "dim": t.get("mbti_info", "Info")},
            {"letter": letter_t, "other": "F", "label": t.get("mbti_T", "T"), "other_label": t.get("mbti_F", "F"),
             "score": t_display_score, "conf": conf_t, "dim": t.get("mbti_decision", "Decision")},
            {"letter": letter_j, "other": "P", "label": t.get("mbti_J", "J"), "other_label": t.get("mbti_P", "P"),
             "score": round(j_score * 100), "conf": conf_j, "dim": t.get("mbti_lifestyle", "Lifestyle")},
        ]
        return mbti_type, dims

    # Dimension scores
    dim_json = json.dumps({
        t["dim_identity"]: scores.get("identity", 0) * 100,
        t["dim_personality"]: scores.get("personality", 0) * 100,
        t["dim_language"]: scores.get("language_style", 0) * 100,
        t["dim_knowledge"]: scores.get("knowledge", 0) * 100,
        t["dim_memory"]: scores.get("memory", 0) * 100,
        t["dim_relationships"]: scores.get("relationships", 0) * 100,
        t["dim_voice"]: scores.get("voice", 0) * 100,
    }, ensure_ascii=False)

    # Emotional triggers
    triggers = emotional.get("triggers", {})
    emo_data = []
    for emo, items in triggers.items():
        if items:
            emo_data.append({"emotion": emo, "triggers": items})
    emo_json = json.dumps(emo_data, ensure_ascii=False)

    # People
    people_list = people.get("people", [])
    people_json = json.dumps(people_list, ensure_ascii=False)

    # Episodic memory
    ep_dir = archive.root / "memory" / "episodic"
    episodes = []
    if ep_dir.exists():
        for f in sorted(ep_dir.glob("*.jsonl"), reverse=True):
            if archive.crypto is not None:
                episodes.extend(archive.crypto.read_sealed_records(f))
            else:
                with open(f, 'r', encoding='utf-8') as fh:
                    for line in fh:
                        try:
                            episodes.append(json.loads(line.strip()))
                        except json.JSONDecodeError:
                            continue
            if len(episodes) >= 20:
                break
    episodes_json = json.dumps(episodes[:20], ensure_ascii=False)

    # MBTI: always infer from full personality data (multi-signal holistic derivation)
    mbti_type, mbti_dims = infer_mbti(ps, emotional, topics_data, episodes)
    mbti_json = json.dumps({"type": mbti_type, "dims": mbti_dims,
                             "note": t.get("mbti_note", ""),
                             "title": t.get("mbti_title", "MBTI")}, ensure_ascii=False)

    # Emotion label map (JS) - includes standard + episodic + custom trigger emotions
    emo_labels_json = json.dumps({
        "joy": t["emo_joy"], "anger": t["emo_anger"],
        "sadness": t["emo_sadness"], "anxiety": t["emo_anxiety"],
        "excitement": t["emo_excitement"], "nostalgia": t["emo_nostalgia"],
        "pride": t["emo_pride"], "gratitude": t["emo_gratitude"],
        "frustration": t["emo_frustration"], "curiosity": t["emo_curiosity"],
        "peace": t["emo_peace"], "guilt": t["emo_guilt"],
        # Custom personality dimensions (emotional patterns)
        "urgency": t["urgency"], "satisfaction": t["satisfaction"],
        # Episodic emotion labels (memory timeline)
        "calm": t["calm"], "clarity": t["clarity"], "focused": t["focused"],
        "relief": t["relief"], "satisfaction": t["satisfaction"],
        "shock_then_urgency": t["shock_then_urgency"],
        "thoughtful": t["thoughtful"],
        # Chinese raw keys from data
        "满意": t.get("满意", t["satisfaction"]),
        "satisfied": t["satisfaction"],  # episodes use 'satisfied' (lowercase)
        "平静": t.get("平静", t["emo_peace"]),
        "好奇": t.get("好奇", t["emo_curiosity"]),
    }, ensure_ascii=False)

    # Identity field label map
    id_fields_json = json.dumps([
        [t["id_name"], "name"], [t["id_nickname"], "nickname"],
        [t["id_age"], "age"], [t["id_gender"], "gender"],
        [t["id_location"], "location"], [t["id_hometown"], "hometown"],
        [t["id_occupation"], "occupation"], [t["id_company"], "company"],
        [t["id_education"], "education"],
    ], ensure_ascii=False)

    # Lifestyle labels
    ls_fields_json = json.dumps([
        [t["ls_routine"], "daily_routine"], [t["ls_sleep"], "sleep_schedule"],
        [t["ls_food"], "food_preferences"], [t["ls_music"], "music_taste"],
        [t["ls_movie"], "movie_taste"], [t["ls_book"], "book_taste"],
        [t["ls_aesthetic"], "aesthetic_style"], [t["ls_spending"], "spending_style"],
        [t["ls_travel"], "travel_preferences"], [t["ls_pet"], "pet_preference"],
    ], ensure_ascii=False)

    # Digital labels
    dg_fields_json = json.dumps([
        [t["dg_apps"], "favorite_apps"], [t["dg_social"], "social_platforms"],
        [t["dg_personas"], "online_personas"], [t["dg_tech"], "tech_proficiency"],
        [t["dg_habits"], "digital_habits"],
    ], ensure_ascii=False)

    # Behavior tags labels
    bh_fields_json = json.dumps([
        [t["ps_risk"], "risk_tolerance"], [t["ps_procrastination"], "procrastination_level"],
        [t["ps_perfectionism"], "perfectionism_level"], [t["ps_planning"], "planning_style"],
        [t["ps_learning"], "learning_style"], [t["ps_work"], "work_style"],
    ], ensure_ascii=False)

    # Social tags labels
    so_fields_json = json.dumps([
        [t["ps_energy"], "social_energy"], [t["ps_role"], "group_role"],
        [t["ps_conflict"], "conflict_approach"], [t["ps_trust"], "trust_building"],
    ], ensure_ascii=False)

    # Style tags labels
    st_fields_json = json.dumps([
        [t["formality"], "formality_level"], [t["verbosity"], "verbosity"],
        [t["humor"], "humor_style"], [t["thinking"], "thinking_expression"],
    ], ensure_ascii=False)

    # Deep lang labels
    dl_fields_json = json.dumps([
        [t["persuasion"], "persuasion_style"], [t["storytelling"], "storytelling_style"],
        [t["question_style"], "question_style"], [t["greeting"], "greeting_style"],
        [t["farewell"], "farewell_style"], [t["typing"], "typing_habits"],
    ], ensure_ascii=False)

    # Separator for arrays (Chinese uses 、, English uses ,)
    arr_sep = "、" if lang == "zh" else ", "

    html = f"""<!DOCTYPE html>
<html lang="{t['html_lang']}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🧬 {t['title'].format(name=name)}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<style>
:root {{
  --bg: #0a0a0f;
  --card: #14141f;
  --card-hover: #1a1a2e;
  --border: #2a2a3e;
  --primary: #7c5bf5;
  --primary-glow: rgba(124, 91, 245, 0.3);
  --accent: #00d4aa;
  --text: #e8e8f0;
  --text-dim: #8888a0;
  --danger: #ff6b6b;
  --warning: #ffd93d;
  --success: #6bcb77;
}}

* {{ margin: 0; padding: 0; box-sizing: border-box; }}

body {{
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
  background: var(--bg);
  color: var(--text);
  min-height: 100vh;
  overflow-x: hidden;
}}

body::before {{
  content: '';
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: radial-gradient(circle at 20% 50%, rgba(124,91,245,0.08) 0%, transparent 50%),
              radial-gradient(circle at 80% 20%, rgba(0,212,170,0.06) 0%, transparent 50%),
              radial-gradient(circle at 50% 80%, rgba(255,107,107,0.05) 0%, transparent 50%);
  pointer-events: none;
  z-index: 0;
}}

.container {{
  max-width: 1100px;
  margin: 0 auto;
  padding: 40px 20px;
  position: relative;
  z-index: 1;
}}

.identity-divider {{
  border: none;
  border-top: 1px solid var(--border);
  margin: 16px 0;
}}

.header {{
  text-align: center;
  margin-bottom: 50px;
}}

.header h1 {{
  font-size: 2.5em;
  background: linear-gradient(135deg, var(--primary), var(--accent));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 10px;
}}

.header .subtitle {{
  color: var(--text-dim);
  font-size: 1.1em;
}}

.completeness-ring {{
  width: 120px; height: 120px;
  margin: 20px auto;
  position: relative;
}}

.completeness-ring svg {{ width: 100%; height: 100%; transform: rotate(-90deg); }}
.completeness-ring .bg {{ fill: none; stroke: var(--border); stroke-width: 8; }}
.completeness-ring .fill {{ fill: none; stroke: var(--primary); stroke-width: 8; stroke-linecap: round;
  stroke-dasharray: 314; stroke-dashoffset: {314 - 314 * completeness}; transition: stroke-dashoffset 1.5s ease; }}
.completeness-ring .label {{
  position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
  font-size: 1.5em; font-weight: 700; color: var(--primary);
}}

.card {{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 28px;
  margin-bottom: 24px;
  transition: all 0.3s ease;
}}
.card:hover {{ background: var(--card-hover); border-color: var(--primary); box-shadow: 0 0 20px var(--primary-glow); }}
.card h2 {{
  font-size: 1.3em;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}}
.card h2 .icon {{ font-size: 1.4em; }}

.grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }}
@media (max-width: 768px) {{ .grid-2 {{ grid-template-columns: 1fr; }} }}

.tag {{
  display: inline-block;
  padding: 5px 14px;
  border-radius: 20px;
  font-size: 0.85em;
  margin: 3px;
  background: rgba(124, 91, 245, 0.15);
  color: var(--primary);
  border: 1px solid rgba(124, 91, 245, 0.3);
}}
.tag.green {{ background: rgba(0, 212, 170, 0.15); color: var(--accent); border-color: rgba(0, 212, 170, 0.3); }}
.tag.red {{ background: rgba(255, 107, 107, 0.15); color: var(--danger); border-color: rgba(255, 107, 107, 0.3); }}
.tag.yellow {{ background: rgba(255, 217, 61, 0.15); color: var(--warning); border-color: rgba(255, 217, 61, 0.3); }}

.progress-item {{ margin-bottom: 12px; }}
.progress-item .label {{ display: flex; justify-content: space-between; margin-bottom: 5px; font-size: 0.9em; }}
.progress-bar {{ height: 8px; background: var(--border); border-radius: 4px; overflow: hidden; }}
.progress-bar .fill {{ height: 100%; border-radius: 4px; transition: width 1s ease;
  background: linear-gradient(90deg, var(--primary), var(--accent)); }}

.quote {{
  padding: 12px 16px;
  border-left: 3px solid var(--primary);
  background: rgba(124, 91, 245, 0.08);
  border-radius: 0 8px 8px 0;
  margin: 8px 0;
  font-style: italic;
  color: var(--text-dim);
}}

.topic-cloud {{ display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }}
.topic-item {{
  padding: 8px 16px; border-radius: 20px; cursor: default;
  transition: all 0.3s; font-weight: 500;
}}
.topic-item:hover {{ transform: scale(1.1); }}

.timeline {{ position: relative; padding-left: 30px; }}
.timeline::before {{ content: ''; position: absolute; left: 10px; top: 0; bottom: 0; width: 2px; background: var(--border); }}
.timeline-item {{
  position: relative; margin-bottom: 20px; padding: 12px 16px;
  background: rgba(124, 91, 245, 0.05); border-radius: 8px;
}}
.timeline-item::before {{
  content: ''; position: absolute; left: -24px; top: 16px;
  width: 10px; height: 10px; border-radius: 50%;
  background: var(--primary); border: 2px solid var(--bg);
}}

.person-card {{
  display: flex; align-items: center; gap: 12px;
  padding: 12px; border-radius: 10px; margin-bottom: 8px;
  background: rgba(0, 212, 170, 0.05); border: 1px solid rgba(0, 212, 170, 0.15);
}}
.person-avatar {{
  width: 40px; height: 40px; border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), var(--accent));
  display: flex; align-items: center; justify-content: center;
  font-size: 1.2em; color: white;
}}

.info-row {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid var(--border); gap: 12px; }}
.info-row:last-child {{ border-bottom: none; }}
.info-row .key {{ color: var(--text-dim); white-space: nowrap; flex-shrink: 0; }}
.info-row .val {{ font-weight: 500; text-align: right; word-break: break-word; }}

.chart-container {{ position: relative; height: 280px; }}

footer {{
  text-align: center;
  padding: 40px 0 20px;
  color: var(--text-dim);
  font-size: 0.85em;
}}
</style>
</head>
<body>

<div class="container">

  <!-- Header -->
  <div class="header">
    <h1>🧬 {t['title'].format(name=name)}</h1>
    <p class="subtitle">{t['subtitle'].format(n=profile.get('total_extractions', 0), date=profile.get('last_updated', 'N/A')[:10])}</p>
    <div class="completeness-ring">
      <svg viewBox="0 0 120 120">
        <circle class="bg" cx="60" cy="60" r="50"/>
        <circle class="fill" cx="60" cy="60" r="50"/>
      </svg>
      <div class="label">{completeness:.0%}</div>
    </div>
    <p class="subtitle" style="font-size:0.9em;">{t['soul_completeness']}</p>
  </div>

  <!-- Dimension Progress -->
  <div class="card">
    <h2><span class="icon">📊</span> {t['dim_completeness']}</h2>
    <div id="dim-progress"></div>
  </div>

  <!-- Identity Card -->
  <div class="card">
    <h2><span class="icon">👤</span> {t['identity']}</h2>
    <div id="identity-basic" style="display:grid;grid-template-columns:1fr 1fr;gap:0 32px;"></div>
    <hr class="identity-divider">
    <div id="identity-extra" style="display:grid;grid-template-columns:1fr 1fr;gap:0 24px;"></div>
  </div>

  <!-- Personality -->
  <div class="card" style="display:flex;flex-direction:column;gap:16px;">
    <h2 style="margin:0;"><span class="icon">💫</span> {t['personality']}</h2>
    <div id="personality-tags"></div>
    <!-- Big Five + MBTI side by side -->
    <div style="display:flex;gap:20px;align-items:flex-start;flex-wrap:wrap;">
      <div class="chart-container" style="flex:1;min-width:200px;margin:0;">
        <canvas id="big5Chart"></canvas>
      </div>
      <div id="mbti-panel" style="flex:1;min-width:200px;">
        <div id="mbti-header"></div>
        <div id="mbti-gauges"></div>
        <div id="mbti-note" style="font-size:0.75em;color:var(--text-dim);margin-top:8px;"></div>
      </div>
    </div>
  </div>

  <!-- Language Style -->
  <div class="card">
    <h2><span class="icon">🗣️</span> {t['language_fp']}</h2>
    <div id="language-section"></div>
  </div>

  <div class="grid-2">
    <!-- Topic Interests -->
    <div class="card">
      <h2><span class="icon">🔥</span> {t['topics']}</h2>
      <div class="topic-cloud" id="topic-cloud"></div>
    </div>

    <!-- Emotional Patterns -->
    <div class="card">
      <h2><span class="icon">❤️</span> {t['emotions']}</h2>
      <div id="emotional-section"></div>
    </div>
  </div>

  <!-- Relationships -->
  <div class="card">
    <h2><span class="icon">🤝</span> {t['relationships']}</h2>
    <div id="people-section"></div>
  </div>

  <!-- Memory Fragments -->
  <div class="card">
    <h2><span class="icon">📝</span> {t['memories']}</h2>
    <div class="timeline" id="episodes-section"></div>
  </div>

  <footer>
    🧬 {t['footer'].format(version=skill_version, time=datetime.now().strftime('%Y-%m-%d %H:%M'))}
  </footer>
</div>

<script>
// ---- Data ----
const basicInfo = {json.dumps(bi, ensure_ascii=False)};
const personality = {json.dumps(ps, ensure_ascii=False)};
const language = {json.dumps(lang_data, ensure_ascii=False)};
const topicsData = {topics_json};
const bigFive = {bf_json};
const mbtiData = {mbti_json};
const dimScores = {dim_json};
const emotionalData = {emo_json};
const peopleData = {people_json};
const episodes = {episodes_json};
const emoLabels = {emo_labels_json};
const arrSep = {json.dumps(arr_sep)};

// Label maps
const idFields = {id_fields_json};
const lsFields = {ls_fields_json};
const dgFields = {dg_fields_json};
const bhFields = {bh_fields_json};
const soFields = {so_fields_json};
const stFields = {st_fields_json};
const dlFields = {dl_fields_json};

// i18n strings
const i18n = {{
  lifestyle: {json.dumps(t['lifestyle'])},
  digital: {json.dumps(t['digital'])},
  decision: {json.dumps(t['ps_decision'])},
  behavior: {json.dumps(t['ps_behavior'])},
  socialStyle: {json.dumps(t['ps_social'])},
  drivers: {json.dumps(t['ps_drivers'])},
  noData: {json.dumps(t['no_data'])},
  noDataChat: {json.dumps(t['no_data_chat'])},
  catchphrases: {json.dumps(t['catchphrases'])},
  sentencePatterns: {json.dumps(t['sentence_patterns'])},
  speechSamples: {json.dumps(t['speech_samples'])},
  fillerWords: {json.dumps(t['filler_words'])},
  dialect: {json.dumps(t['dialect'])},
  agreeExpr: {json.dumps(t['agree_expr'])},
  disagreeExpr: {json.dumps(t['disagree_expr'])},
  deepFp: {json.dumps(t['deep_fp'])},
  noLangData: {json.dumps(t['no_lang_data'])},
  noTopicData: {json.dumps(t['no_topic_data'])},
  noEmotionData: {json.dumps(t['no_emotion_data'])},
  noPeopleData: {json.dumps(t['no_people_data'])},
  noMemoryData: {json.dumps(t['no_memory_data'])},
  idHobbies: {json.dumps(t['id_hobbies'])},
  idMotto: {json.dumps(t['id_motto'])}
}};

// ---- Helpers ----
function getVal(obj, key) {{
  const v = obj[key];
  if (Array.isArray(v)) return v.length ? v.join(arrSep) : null;
  return v || null;
}}

// ---- Dimension Progress Bars ----
const dimEl = document.getElementById('dim-progress');
Object.entries(dimScores).forEach(([name, score]) => {{
  dimEl.innerHTML += `
    <div class="progress-item">
      <div class="label"><span>${{name}}</span><span>${{Math.round(score)}}%</span></div>
      <div class="progress-bar"><div class="fill" style="width:${{score}}%"></div></div>
    </div>`;
}});

// ---- Identity Info ----
const idBasicEl = document.getElementById('identity-basic');
const idExtraEl = document.getElementById('identity-extra');

// Core fields (two-column grid)
idFields.forEach(([label, key]) => {{
  const v = getVal(basicInfo, key);
  if (v) idBasicEl.innerHTML += `<div class="info-row"><span class="key">${{label}}</span><span class="val">${{v}}</span></div>`;
}});

// Hobbies and motto
const hobbies = basicInfo.hobbies?.length ? basicInfo.hobbies.join(arrSep) : null;
if (hobbies) idBasicEl.innerHTML += `<div class="info-row"><span class="key">${{i18n.idHobbies}}</span><span class="val">${{hobbies}}</span></div>`;
const motto = basicInfo.life_motto;
if (motto) idBasicEl.innerHTML += `<div class="info-row"><span class="key">${{i18n.idMotto}}</span><span class="val">${{motto}}</span></div>`;

if (!idBasicEl.innerHTML) idBasicEl.innerHTML = `<p style="color:var(--text-dim)">${{i18n.noDataChat}}</p>`;

// Lifestyle (left column of extra row)
const filledLs = lsFields.filter(([, key]) => getVal(basicInfo, key));
// Digital Identity (right column of extra row)
const filledDg = dgFields.filter(([, key]) => getVal(basicInfo, key));

if (filledLs.length || filledDg.length) {{
  let lsHtml = '';
  if (filledLs.length) {{
    lsHtml += `<div style="margin-bottom:6px;color:var(--accent);font-size:0.9em;font-weight:600;">${{i18n.lifestyle}}</div>`;
    filledLs.forEach(([label, key]) => {{
      lsHtml += `<div class="info-row"><span class="key">${{label}}</span><span class="val">${{getVal(basicInfo, key)}}</span></div>`;
    }});
  }}

  let dgHtml = '';
  if (filledDg.length) {{
    dgHtml += `<div style="margin-bottom:6px;color:var(--accent);font-size:0.9em;font-weight:600;">${{i18n.digital}}</div>`;
    filledDg.forEach(([label, key]) => {{
      dgHtml += `<div class="info-row"><span class="key">${{label}}</span><span class="val">${{getVal(basicInfo, key)}}</span></div>`;
    }});
  }}

  idExtraEl.innerHTML = `<div>${{lsHtml}}</div><div>${{dgHtml}}</div>`;
}}

// ---- Personality Tags ----
const psEl = document.getElementById('personality-tags');
let psHtml = '';
if (personality.mbti) psHtml += `<span class="tag green">${{personality.mbti}}</span>`;
(personality.traits || []).forEach(t => psHtml += `<span class="tag">${{t}}</span>`);
(personality.values || []).forEach(v => psHtml += `<span class="tag yellow">${{v}}</span>`);
if (personality.decision_style) psHtml += `<span class="tag green">${{i18n.decision}}: ${{personality.decision_style}}</span>`;

// Behavior patterns
const filledBh = bhFields.filter(([, key]) => personality[key]);
if (filledBh.length) {{
  psHtml += `<div style="margin:10px 0 6px;color:var(--text-dim);font-size:0.85em;">${{i18n.behavior}}</div>`;
  filledBh.forEach(([label, key]) => psHtml += `<span class="tag green">${{label}}: ${{personality[key]}}</span>`);
}}

// Social style
const filledSo = soFields.filter(([, key]) => personality[key]);
if (filledSo.length) {{
  psHtml += `<div style="margin:10px 0 6px;color:var(--text-dim);font-size:0.85em;">${{i18n.socialStyle}}</div>`;
  filledSo.forEach(([label, key]) => psHtml += `<span class="tag">${{label}}: ${{personality[key]}}</span>`);
}}

// Drivers
if (personality.motivation_drivers?.length) {{
  psHtml += `<div style="margin:10px 0 6px;color:var(--text-dim);font-size:0.85em;">${{i18n.drivers}}</div>`;
  personality.motivation_drivers.forEach(d => psHtml += `<span class="tag red">${{d}}</span>`);
}}

psEl.innerHTML = psHtml || `<p style="color:var(--text-dim)">${{i18n.noData}}</p>`;

// ---- Big Five Radar Chart ----
const bf5 = Object.entries(bigFive);
if (bf5.some(([,v]) => v > 0)) {{
  new Chart(document.getElementById('big5Chart'), {{
    type: 'radar',
    data: {{
      labels: bf5.map(([k]) => k),
      datasets: [{{
        data: bf5.map(([,v]) => v),
        backgroundColor: 'rgba(124, 91, 245, 0.2)',
        borderColor: '#7c5bf5',
        pointBackgroundColor: '#7c5bf5',
        borderWidth: 2
      }}]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{ legend: {{ display: false }} }},
      scales: {{ r: {{
        grid: {{ color: 'rgba(255,255,255,0.08)' }},
        angleLines: {{ color: 'rgba(255,255,255,0.08)' }},
        pointLabels: {{ color: '#e8e8f0', font: {{ size: 13 }} }},
        ticks: {{ display: false }},
        min: 0, max: 100
      }} }}
    }}
  }});
}}

// ---- MBTI Gauge Panel ----
(function() {{
  if (!mbtiData || !mbtiData.type) return;
  const {{type, dims, note, title}} = mbtiData;

  // Header: type badge
  const headerEl = document.getElementById('mbti-header');
  if (headerEl) {{
    headerEl.innerHTML = `<div style="text-align:center;margin-bottom:12px;">
      <span style="font-size:2em;font-weight:700;letter-spacing:0.1em;color:var(--accent);">${{type}}</span>
      <div style="font-size:0.8em;color:var(--text-dim);margin-top:2px;">${{title || 'MBTI'}}</div>
    </div>`;
  }}

  // Dimension gauges
  const gaugesEl = document.getElementById('mbti-gauges');
  if (gaugesEl && dims) {{
    let gaugesHtml = '';
    dims.forEach((d) => {{
      const pct = d.score;  // percentage toward left label
      const dominantColor = 'var(--accent)';
      const recessiveColor = 'rgba(255,255,255,0.15)';
      const leanLeft = pct >= 50;
      const leftColor = leanLeft ? dominantColor : recessiveColor;
      const rightColor = leanLeft ? recessiveColor : dominantColor;
      // Bar: fill from the dominant side
      const barWidth = leanLeft ? pct : (100 - pct);
      const barSide = leanLeft ? 'left:0;border-radius:4px 0 0 4px;' : 'right:0;border-radius:0 4px 4px 0;';
      const displayPct = leanLeft ? pct : (100 - pct);
      gaugesHtml += `<div style="margin-bottom:14px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px;">
          <span style="font-size:0.82em;color:${{leftColor}};font-weight:${{leanLeft?'600':'400'}};">${{d.label}}</span>
          <span style="font-size:0.75em;color:var(--text-dim);">${{d.dim}}</span>
          <span style="font-size:0.82em;color:${{rightColor}};font-weight:${{leanLeft?'400':'600'}};">${{d.other_label}}</span>
        </div>
        <div style="position:relative;height:8px;background:rgba(255,255,255,0.08);border-radius:4px;overflow:hidden;">
          <div style="position:absolute;${{barSide}}top:0;height:100%;width:${{barWidth}}%;background:${{dominantColor}};transition:width 0.6s ease;"></div>
          <div style="position:absolute;left:50%;top:-2px;width:2px;height:12px;background:rgba(255,255,255,0.35);transform:translateX(-50%);border-radius:1px;z-index:1;"></div>
        </div>
        <div style="text-align:center;font-size:0.72em;color:var(--text-dim);margin-top:3px;">${{displayPct}}%</div>
      </div>`;
    }});
    gaugesEl.innerHTML = gaugesHtml;
  }}

  const noteEl = document.getElementById('mbti-note');
  if (noteEl && note) noteEl.textContent = note;
}})();

// ---- Language Fingerprint ----
const langEl = document.getElementById('language-section');
let langHtml = '';
if (language.catchphrases?.length) {{
  langHtml += `<h3 style="margin-bottom:8px;font-size:1em;">${{i18n.catchphrases}}</h3>`;
  language.catchphrases.forEach(p => langHtml += `<span class="tag">"${{p}}"</span>`);
}}
if (language.sentence_patterns?.length) {{
  langHtml += `<h3 style="margin:16px 0 8px;font-size:1em;">${{i18n.sentencePatterns}}</h3>`;
  language.sentence_patterns.forEach(s => langHtml += `<div class="quote">${{s}}</div>`);
}}
if (language.examples?.length) {{
  langHtml += `<h3 style="margin:16px 0 8px;font-size:1em;">${{i18n.speechSamples}}</h3>`;
  language.examples.slice(0, 5).forEach(e => langHtml += `<div class="quote">${{e}}</div>`);
}}
const filledSt = stFields.filter(([, key]) => language[key]);
if (filledSt.length) {{
  langHtml += '<div style="margin-top:12px;">';
  filledSt.forEach(([label, key]) => langHtml += `<span class="tag green">${{label}}: ${{language[key]}}</span>`);
  langHtml += '</div>';
}}

// Deep Language Fingerprint
let deepLangHtml = '';
if (language.filler_words?.length) {{
  deepLangHtml += `<h3 style="margin:16px 0 8px;font-size:1em;">${{i18n.fillerWords}}</h3>`;
  language.filler_words.forEach(w => deepLangHtml += `<span class="tag">${{w}}</span>`);
}}
if (language.dialect_features?.length) {{
  deepLangHtml += `<h3 style="margin:16px 0 8px;font-size:1em;">${{i18n.dialect}}</h3>`;
  language.dialect_features.forEach(f => deepLangHtml += `<span class="tag yellow">${{f}}</span>`);
}}
if (language.agreement_expressions?.length) {{
  deepLangHtml += `<h3 style="margin:16px 0 8px;font-size:1em;">${{i18n.agreeExpr}}</h3>`;
  language.agreement_expressions.forEach(e => deepLangHtml += `<span class="tag green">${{e}}</span>`);
}}
if (language.disagreement_expressions?.length) {{
  deepLangHtml += `<h3 style="margin:16px 0 8px;font-size:1em;">${{i18n.disagreeExpr}}</h3>`;
  language.disagreement_expressions.forEach(e => deepLangHtml += `<span class="tag red">${{e}}</span>`);
}}
const filledDl = dlFields.filter(([, key]) => language[key]);
if (filledDl.length) {{
  deepLangHtml += `<h3 style="margin:16px 0 8px;font-size:1em;">${{i18n.deepFp}}</h3>`;
  filledDl.forEach(([label, key]) => deepLangHtml += `<span class="tag">${{label}}: ${{language[key]}}</span>`);
}}

langHtml += deepLangHtml;
langEl.innerHTML = langHtml || `<p style="color:var(--text-dim)">${{i18n.noLangData}}</p>`;

// ---- Topic Cloud ----
const tcEl = document.getElementById('topic-cloud');
const sentimentColors = {{positive:'green', negative:'red', neutral:'', mixed:'yellow'}};
const maxFreq = Math.max(...topicsData.map(t => t.frequency), 1);
topicsData.forEach(t => {{
  const size = 0.8 + (t.frequency / maxFreq) * 0.8;
  const cls = sentimentColors[t.sentiment] || '';
  tcEl.innerHTML += `<span class="topic-item tag ${{cls}}" style="font-size:${{size}}em">${{t.name}} (${{t.frequency}})</span>`;
}});
if (!topicsData.length) tcEl.innerHTML = `<p style="color:var(--text-dim)">${{i18n.noTopicData}}</p>`;

// ---- Emotional Patterns ----
const emoEl = document.getElementById('emotional-section');
let emoHtml = '';
emotionalData.forEach(e => {{
  const label = emoLabels[e.emotion] || e.emotion;
  emoHtml += `<div style="margin-bottom:12px;"><strong>${{label}}</strong><br>`;
  e.triggers.forEach(t => emoHtml += `<span class="tag" style="margin-top:4px;">${{t}}</span>`);
  emoHtml += '</div>';
}});
emoEl.innerHTML = emoHtml || `<p style="color:var(--text-dim)">${{i18n.noEmotionData}}</p>`;

// ---- Relationships ----
const pplEl = document.getElementById('people-section');
if (peopleData.length) {{
  peopleData.forEach(p => {{
    const initial = (p.name || '?')[0];
    pplEl.innerHTML += `<div class="person-card">
      <div class="person-avatar">${{initial}}</div>
      <div><strong>${{p.name}}</strong>${{p.relationship ? ' · ' + p.relationship : ''}}
      ${{p.description ? '<br><span style="color:var(--text-dim);font-size:0.9em;">' + p.description + '</span>' : ''}}</div>
    </div>`;
  }});
}} else {{
  pplEl.innerHTML = `<p style="color:var(--text-dim)">${{i18n.noPeopleData}}</p>`;
}}

// ---- Memory Fragments ----
const epEl = document.getElementById('episodes-section');
if (episodes.length) {{
  episodes.forEach(ep => {{
    const emoLabel = ep.emotion ? (emoLabels[ep.emotion] || ep.emotion) : '';
    epEl.innerHTML += `<div class="timeline-item">
      <strong>${{ep.event || ''}}</strong>
      ${{emoLabel ? ' <span class="tag" style="font-size:0.8em;">' + emoLabel + '</span>' : ''}}
      ${{ep.context ? '<br><span style="color:var(--text-dim);font-size:0.9em;">' + ep.context + '</span>' : ''}}
    </div>`;
  }});
}} else {{
  epEl.innerHTML = `<p style="color:var(--text-dim)">${{i18n.noMemoryData}}</p>`;
}}
</script>

</body>
</html>"""

    if output_path:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        with open(output, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"✅ Soul report generated ({lang}): {output}")
    else:
        print(html)

    return html


def main():
    default_soul_dir = str(Path.home() / ".skills_data" / "soul-archive")
    parser = argparse.ArgumentParser(description="🧬 Soul Report Generator (Multi-language)")
    parser.add_argument("--soul-dir", default=default_soul_dir,
                        help=f"Soul data directory path (default: {default_soul_dir})")
    parser.add_argument("--output", help="Output HTML file path")
    parser.add_argument("--lang", choices=["zh", "en"], default=None,
                        help="Report language: zh (Chinese) or en (English). "
                             "Auto-detected from user name if not specified.")
    parser.add_argument("--access-key", help="Access key (if data protection is enabled)")

    args = parser.parse_args()
    archive = SoulArchive(args.soul_dir)

    # Read version from SKILL.md front matter
    skill_dir = Path(__file__).parent.parent
    skill_version = "unknown"
    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        try:
            text = skill_md.read_text(encoding="utf-8")
            parts = text.split("---", 2)
            if len(parts) >= 3:
                import re as _re
                m = _re.search(r'version:\s*["\']?([^"\'\n]+)', parts[1])
                if m:
                    skill_version = m.group(1).strip()
        except Exception:
            pass

    if not archive.is_initialized():
        print("❌ Soul archive not initialized. Run soul_init.py first.")
        sys.exit(1)

    # Auto-initialize crypto if data protection is enabled
    config = archive.load_config()
    if config.get("encryption"):
        archive.init_crypto_from_config(password=args.access_key)

    if not args.output:
        print("❌ 请通过 --output 指定报告输出路径（建议输出到工作目录，非数据目录）")
        sys.exit(1)
    output = args.output
    generate_html_report(archive, output, lang=args.lang, skill_version=skill_version)


if __name__ == "__main__":
    main()
