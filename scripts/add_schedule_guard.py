#!/usr/bin/env python3
"""Opt in to schedule protection after adding a scheduled data collector."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import textwrap

ROOT = Path(__file__).resolve().parents[1]

GUARD = ".github/workflows/schedule-guard.yml"

SCRIPT = '''import json, os, subprocess, sys

repo = os.environ["GITHUB_REPOSITORY"]
wanted = set(json.loads(os.environ["GUARDED_PATHS"]))
seen, failures = set(), []

def api(path, *flags):
    return subprocess.check_output(
        ["gh", "api", path, *flags], text=True, timeout=45
    )

pages = json.loads(api(
    f"repos/{repo}/actions/workflows?per_page=100",
    "--paginate", "--slurp"
))
for page in pages:
    for listed in page["workflows"]:
        path = listed["path"]
        if path not in wanted:
            continue
        seen.add(path)
        endpoint = f"repos/{repo}/actions/workflows/{listed['id']}"
        try:
            current = json.loads(api(endpoint))
            if current["path"] != path:
                raise RuntimeError("Workflow path changed")
            if current["state"] not in {"active", "disabled_inactivity"}:
                print(f"Preserved {path}: {current['state']}")
                continue
            api(endpoint + "/enable", "--method", "PUT")
            print(f"Renewed {path}")
        except Exception as error:
            failures.append(path)
            print(f"Failed {path}: {type(error).__name__}")

failures.extend(sorted(wanted - seen))
if failures:
    print("Needs attention:", ", ".join(failures))
    sys.exit(1)
'''

def render(repository, paths):
    digest = hashlib.sha256(repository.encode()).digest()
    cron = f"{7 + digest[0] % 50} {digest[1] % 24} * * {digest[2] % 7}"
    header = f'''name: Keep refresh schedules active

on:
  schedule:
    - cron: '{cron}'
  workflow_dispatch:
  push:
    paths:
      - '{GUARD}'

permissions: {{}}

concurrency:
  group: refresh-schedule-guard
  cancel-in-progress: false

jobs:
  renew:
    if: github.ref == format('refs/heads/{{0}}', github.event.repository.default_branch)
    runs-on: ubuntu-latest
    timeout-minutes: 5
    permissions:
      actions: write
    env:
      GH_TOKEN: ${{{{ github.token }}}}
      GUARDED_PATHS: '{json.dumps(paths, separators=(',', ':'))}'
    steps:
      - name: Renew explicitly managed schedules
        shell: bash
        run: |
          python3 - <<'PY'
'''
    return header + textwrap.indent(SCRIPT, "          ") + "          PY\n"


def add_guard(root, repository, paths):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]*/[A-Za-z0-9._-]+", repository):
        raise ValueError("Repository must use owner/name format")
    selected = sorted(set(paths))
    if not selected:
        raise ValueError("Name at least one scheduled refresh workflow")
    for name in selected:
        if not re.fullmatch(r"\.github/workflows/[A-Za-z0-9._-]+\.ya?ml", name) or name == GUARD:
            raise ValueError(f"Expected an existing refresh workflow path: {name}")
        if not (root / name).is_file():
            raise ValueError(f"Workflow does not exist: {name}")
    managed = sorted(set(selected) | {GUARD})
    (root / GUARD).write_text(render(repository, managed), encoding="utf-8")
    return managed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", required=True, help="GitHub owner/name")
    parser.add_argument("workflows", nargs="+", help="Explicit scheduled collector paths")
    args = parser.parse_args()
    try:
        paths = add_guard(ROOT, args.repository, args.workflows)
    except ValueError as error:
        parser.error(str(error))
    print("Created " + GUARD + " for " + ", ".join(paths))
    print("Review the allowlist, commit the workflow, and verify its first push run.")
    print("Register new collectors with the independent server scheduler as well.")


if __name__ == "__main__":
    main()
