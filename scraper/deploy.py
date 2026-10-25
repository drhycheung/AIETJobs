"""
deploy.py — Publish to GitHub Pages (gh-pages branch).
Review period: PUSH_GITHUB=False, so by default it does not push and only prints guidance.
Enabled when: config.PUSH_GITHUB=True and GH_TOKEN (repo scope) and GH_OWNER are provided.
Note: GitHub write operations should run in the cloud runtime / with a user-provided PAT,
not by forcing OAuth inside the sandbox.
"""
from __future__ import annotations

import os
import sys
import subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config


def push() -> bool:
    if not config.PUSH_GITHUB:
        print("[deploy] PUSH_GITHUB=False (review period) -> not pushing to GitHub; local output only.")
        return False
    if not config.GH_TOKEN or not config.GH_OWNER:
        print("[deploy] Missing GH_TOKEN / GH_OWNER; cannot push. Configure them in config or env vars.")
        return False
    # TODO: actual push is performed by the cloud runtime:
    #   git add site data && git commit && git subtree push ... gh-pages
    # This is only a placeholder, to avoid forcing OAuth inside the sandbox
    # (see AGENTS.md section 5, pitfall #6).
    print("[deploy] Push logic to be executed by the cloud runtime (GH_TOKEN configured).")
    return False


if __name__ == "__main__":
    push()
