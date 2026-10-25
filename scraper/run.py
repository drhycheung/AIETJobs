"""
run.py — Daily task entry point
Flow: crawl official pages + search discovery -> compliance filter / scoring / sort
-> generate JSON + HTML -> (review period) do not push to GitHub
Usage: python -m scraper.run
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pipeline import run as pipeline_run
from generate import generate
from deploy import push as deploy_push


def main():
    print("=== AIETJobs daily run started ===")
    jobs = pipeline_run()
    generate(jobs)
    deploy_push()
    print("=== done ===")


if __name__ == "__main__":
    main()
