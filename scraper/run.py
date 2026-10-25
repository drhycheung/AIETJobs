"""
run.py — 每日任务入口
流程：抓取官方页 + 搜索发现 → 合规过滤/评分/排序 → 生成 JSON+HTML → （审查期）不推送 GitHub
用法：python -m scraper.run
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pipeline import run as pipeline_run
from generate import generate
from deploy import push as deploy_push


def main():
    print("=== AIETJobs 每日运行开始 ===")
    jobs = pipeline_run()
    generate(jobs)
    deploy_push()
    print("=== 完成 ===")


if __name__ == "__main__":
    main()
