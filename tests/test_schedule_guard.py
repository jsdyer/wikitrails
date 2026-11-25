import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location(
    "schedule_guard", Path(__file__).resolve().parents[1] / "scripts/add_schedule_guard.py"
)
guard = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(guard)


class ScheduleGuardTests(unittest.TestCase):
    def test_explicit_workflows_and_self_with_minimal_permissions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            folder = root / ".github/workflows"
            folder.mkdir(parents=True)
            for name in ("pages.yml", "second.yaml"):
                (folder / name).write_text("on:\n  schedule:\n    - cron: '7 * * * *'\n")
            selected = [".github/workflows/pages.yml", ".github/workflows/second.yaml"]
            paths = guard.add_guard(root, "owner/my-tool", selected)
            text = (root / guard.GUARD).read_text()
            self.assertEqual(set(paths), {*selected, guard.GUARD})
            self.assertIn("permissions: {}", text)
            self.assertIn("    permissions:\n      actions: write", text)
            self.assertIn("github.event.repository.default_branch", text)
            self.assertIn("workflow_dispatch:", text)
            self.assertNotIn("pull_request", text)
            self.assertNotIn("checkout", text)
            self.assertNotIn("contents: write", text)
            guard.add_guard(root, "owner/my-tool", selected)
            self.assertEqual((root / guard.GUARD).read_text(), text)

    def test_invalid_or_missing_paths_do_not_create_workflow(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for paths in ([], ["../outside.yml"], [".github/workflows/missing.yml"], [guard.GUARD]):
                with self.assertRaises(ValueError):
                    guard.add_guard(root, "owner/my-tool", paths)
                self.assertFalse((root / guard.GUARD).exists())

    def test_only_allowed_active_and_inactivity_states_are_renewed(self):
        for state in ("active", "disabled_inactivity", "disabled_manually", "disabled_fork", "deleted"):
            with self.subTest(state=state):
                calls = []

                def api(command, **kwargs):
                    calls.append(command)
                    if "?per_page" in command[2]:
                        return json.dumps([{"workflows": [
                            {"id": 1, "path": guard.GUARD},
                            {"id": 2, "path": ".github/workflows/unrelated.yml"},
                        ]}])
                    if command[2].endswith("/enable"):
                        return ""
                    return json.dumps({"path": guard.GUARD, "state": state})

                with patch.dict(os.environ, {"GITHUB_REPOSITORY": "owner/my-tool", "GUARDED_PATHS": json.dumps([guard.GUARD])}), patch.object(subprocess, "check_output", api):
                    exec(compile(guard.SCRIPT, "guard", "exec"), {})
                updates = [call for call in calls if call[2].endswith("/enable")]
                self.assertEqual(len(updates), int(state in {"active", "disabled_inactivity"}))
                self.assertTrue(all("/2" not in call[2] for call in calls))

    def test_missing_allowlisted_workflow_fails_visibly(self):
        with patch.dict(os.environ, {"GITHUB_REPOSITORY": "owner/my-tool", "GUARDED_PATHS": json.dumps([guard.GUARD])}), patch.object(subprocess, "check_output", return_value='[{"workflows":[]}]'):
            with self.assertRaises(SystemExit) as result:
                exec(compile(guard.SCRIPT, "guard", "exec"), {})
        self.assertEqual(result.exception.code, 1)
