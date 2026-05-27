#!/usr/bin/env python3
"""
🧬 Soul Archive — Unified CLI Entry (v3.0)

统一的子命令路由，让你少记 6 个脚本名。

用法：
  soul init                          # 初始化
  soul status                        # 查看灵魂存档状态
  soul extract --input "..."         # 从对话中提取信息
  soul chat [--mode prompt|summary|json]
  soul report [--lang zh|en] [--output /path/to.html]
  soul reflect --mode status         # AI 自我改进状态
  soul context [--format md|json]    # 注入用人格摘要
  soul recall --task "..."           # 跨会话召回相关 pattern/correction
  soul warn --task "..."             # 失败模式预警
  soul distill [--pretend|--commit] # 行为模式蒸馏

也可直接调用底层脚本：
  python3 soul_extract.py --mode status
"""

import os
import sys
from pathlib import Path

HERE = Path(__file__).parent


SCRIPTS = {
    "init":    "soul_init.py",
    "extract": "soul_extract.py",
    "chat":    "soul_chat.py",
    "report":  "soul_report.py",
    "reflect": "soul_reflect.py",
    "context": "soul_context.py",
    "status":  ("soul_extract.py", ["--mode", "status"]),
    # agent_memory 子命令
    "recall":  ("soul_agent_memory.py", ["recall"]),
    "warn":    ("soul_agent_memory.py", ["warn"]),
    "distill": ("soul_agent_memory.py", ["distill"]),
    "session-start": ("soul_agent_memory.py", ["session-start"]),
}


HELP = """🧬 Soul Archive — Unified CLI (v3.0)

子命令：
  init               初始化灵魂存档
  status             查看完整度状态（= extract --mode status）
  extract            从对话提取信息（--input "..." [--mode auto|manual]）
  chat               生成角色扮演 prompt（--mode prompt|summary|json）
  report             生成 HTML 灵魂画像报告（--lang zh|en --output 路径）
  reflect            AI 自我改进引擎（写入侧；--mode status|patterns|reflect|critique|learn）
  context            输出精简的人格摘要（用于 system prompt 注入）
  recall             跨会话召回相关行为模式 / 用户纠正 / 反思（--task "..."）
  warn               失败模式预警：检测当前任务是否匹配过去坑（--task "..."）
  distill            行为模式蒸馏（--pretend 预览 / --commit "<pattern json>" 写回）
  session-start      会话开始综合简报：recall + warn + distill（--task "..."）

通用参数（所有子命令）：
  --soul-dir <path>  自定义灵魂数据目录（默认 ~/.skills_data/soul-archive）
"""


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help", "help"):
        print(HELP)
        sys.exit(0)

    sub = args[0]
    rest = args[1:]
    if sub not in SCRIPTS:
        print(f"❌ 未知子命令：{sub}\n", file=sys.stderr)
        print(HELP, file=sys.stderr)
        sys.exit(1)

    entry = SCRIPTS[sub]
    if isinstance(entry, tuple):
        script, prefix = entry
    else:
        script, prefix = entry, []

    target = HERE / script
    if not target.exists():
        print(f"❌ 缺少脚本：{target}", file=sys.stderr)
        sys.exit(1)

    cmd = [sys.executable, str(target)] + prefix + rest
    os.execvp(cmd[0], cmd)


if __name__ == "__main__":
    main()
