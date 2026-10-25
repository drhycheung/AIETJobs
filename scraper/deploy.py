"""
deploy.py — 发布到 GitHub Pages（gh-pages 分支）。
审查期：PUSH_GITHUB=False，默认不推送，仅打印指引。
启用条件：config.PUSH_GITHUB=True 且提供 GH_TOKEN（repo 权限）、GH_OWNER。
注意：GitHub 写操作建议在云端运行时 / 用户提供的 PAT 下执行，不在沙箱硬跑 OAuth。
"""
from __future__ import annotations

import os
import sys
import subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config


def push() -> bool:
    if not config.PUSH_GITHUB:
        print("[deploy] PUSH_GITHUB=False（审查期）→ 不推送 GitHub，仅本地产出。")
        return False
    if not config.GH_TOKEN or not config.GH_OWNER:
        print("[deploy] 缺少 GH_TOKEN / GH_OWNER，无法推送。请在 config 或环境变量中配置。")
        return False
    # TODO: 实际推送由云端运行时执行：
    #   git add site data && git commit && git subtree push ... gh-pages
    # 此处仅占位，避免沙箱内硬跑 OAuth（见 AGENTS.md §5 坑 #6）。
    print("[deploy] 推送逻辑待在云端运行时执行（GH_TOKEN 已配置）。")
    return False


if __name__ == "__main__":
    push()
