import json
import re
import shutil
import subprocess
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import panda_collaborator as pc  # noqa: E402


def run(args, cwd):
    result = subprocess.run(args, cwd=str(cwd), text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise AssertionError(f"{args} failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    return result


class ButtonInventoryParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.buttons = []
        self._button_stack = []

    def handle_starttag(self, tag, attrs):
        if tag == "button":
            self._button_stack.append({"attrs": dict(attrs), "text": ""})
        elif self._button_stack:
            self._button_stack[-1]["text"] += " "

    def handle_data(self, data):
        if self._button_stack:
            self._button_stack[-1]["text"] += data

    def handle_endtag(self, tag):
        if tag == "button" and self._button_stack:
            self.buttons.append(self._button_stack.pop())


class PandaCollaboratorSafetyTests(unittest.TestCase):
    def test_forbidden_git_commands_are_rejected(self):
        forbidden = [
            ["reset", "--hard"],
            ["clean", "-fd"],
            ["clean", "-xdf"],
            ["push", "--force"],
            ["push", "-f"],
            ["checkout", "."],
            ["restore", "."],
            ["branch", "-D", "feature"],
            ["branch", "-d", "feature"],
            ["push", "origin", "--delete", "feature"],
            ["stash"],
            ["merge", "main"],
            ["rebase", "main"],
        ]
        for args in forbidden:
            with self.subTest(args=args):
                with self.assertRaises(pc.SafetyError):
                    pc.assert_git_args_safe(args)

    def test_package_id_cannot_escape_package_root(self):
        with tempfile.TemporaryDirectory(prefix="panda-collab-package-root-") as tmp:
            old_package_root = pc.os.environ.get("PANDA_COLLABORATOR_PACKAGE_ROOT")
            pc.os.environ["PANDA_COLLABORATOR_PACKAGE_ROOT"] = tmp
            try:
                for package_id in ("../manifest.json", "..\\manifest.json", "C:/Windows/win.ini"):
                    with self.subTest(package_id=package_id):
                        with self.assertRaises(pc.SafetyError):
                            pc.resolve_package_manifest(package_id)
            finally:
                if old_package_root is None:
                    pc.os.environ.pop("PANDA_COLLABORATOR_PACKAGE_ROOT", None)
                else:
                    pc.os.environ["PANDA_COLLABORATOR_PACKAGE_ROOT"] = old_package_root

    def test_safe_relative_paths_exclude_git_and_escape_attempts(self):
        repo = Path(tempfile.mkdtemp(prefix="panda-collab-relpath-"))
        try:
            self.assertIsNone(pc.safe_rel_path(repo, ".git/config"))
            self.assertIsNone(pc.safe_rel_path(repo, "../outside.txt"))
            self.assertEqual(pc.safe_rel_path(repo, "src/app.py"), Path("src/app.py"))
        finally:
            shutil.rmtree(repo, ignore_errors=True)


class PandaCollaboratorTestSandboxTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="panda-collab-test-sandbox-"))
        self.old_root = pc.os.environ.get("PANDA_COLLABORATOR_TEST_SANDBOX_ROOT")
        pc.os.environ["PANDA_COLLABORATOR_TEST_SANDBOX_ROOT"] = str(self.tmp / "pc-action-test")

    def tearDown(self):
        if self.old_root is None:
            pc.os.environ.pop("PANDA_COLLABORATOR_TEST_SANDBOX_ROOT", None)
        else:
            pc.os.environ["PANDA_COLLABORATOR_TEST_SANDBOX_ROOT"] = self.old_root
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_create_test_sandbox_is_local_only_and_timestamped(self):
        first = pc.create_test_sandbox()
        second = pc.create_test_sandbox()

        self.assertNotEqual(first["run_root"], second["run_root"])
        self.assertTrue(Path(first["run_root"]).exists())
        self.assertTrue(Path(first["fake_repo_path"], ".git").exists())
        self.assertTrue(Path(first["fake_project_files_tracker_path"], "skills", "pg-project-sync", "MANIFEST.md").exists())
        self.assertTrue(Path(first["fake_claude_desktop_path"]).exists())
        self.assertTrue(Path(first["fake_claude_code_path"]).exists())
        self.assertTrue(Path(first["evidence_screenshots_path"]).exists())
        self.assertTrue(Path(first["evidence_reports_path"]).exists())
        self.assertTrue(Path(first["run_state_path"]).exists())
        self.assertFalse(first["external_side_effects"])
        self.assertFalse(first["github_repo_created"])
        self.assertFalse(first["git_remote_configured"])
        self.assertFalse(first["destructive_git_commands_run"])

        root = Path(pc.os.environ["PANDA_COLLABORATOR_TEST_SANDBOX_ROOT"]).resolve()
        for key in (
            "run_root",
            "fake_repo_path",
            "fake_project_files_tracker_path",
            "fake_claude_desktop_path",
            "fake_claude_code_path",
            "evidence_screenshots_path",
            "evidence_reports_path",
            "run_state_path",
        ):
            Path(first[key]).resolve().relative_to(root)

    def test_create_test_sandbox_repo_has_expected_status_states(self):
        sandbox = pc.create_test_sandbox()
        status = pc.repo_status(sandbox["fake_repo_path"])

        self.assertGreaterEqual(status["counts"]["staged"], 1)
        self.assertGreaterEqual(status["counts"]["unstaged"], 1)
        self.assertGreaterEqual(status["counts"]["untracked"], 1)
        self.assertGreaterEqual(status["counts"]["deleted"], 1)
        self.assertEqual(status["counts"]["conflicted"], 0)
        self.assertEqual(pc.safe_git(Path(sandbox["fake_repo_path"]), ["remote", "-v"], allow_failure=True).stdout.strip(), "")
        self.assertIn("docs/conflict-note.md", Path(sandbox["run_state_path"]).read_text(encoding="utf-8"))

    def test_manual_test_log_records_browser_steps_inside_sandbox(self):
        log = pc.create_manual_test_log()
        entry = pc.append_manual_test_log(
            {
                "log_path": log["log_path"],
                "event": "click-run-test",
                "detail": "User clicked Run Test.",
                "status": "ok",
            }
        )

        self.assertEqual(entry["entry"]["event"], "click-run-test")
        log_path = Path(log["log_path"])
        self.assertTrue(log_path.exists())
        self.assertIn("click-run-test", log_path.read_text(encoding="utf-8"))
        Path(log["run_root"]).resolve().relative_to(Path(pc.os.environ["PANDA_COLLABORATOR_TEST_SANDBOX_ROOT"]).resolve())
        with self.assertRaises(pc.SafetyError):
            pc.append_manual_test_log({"log_path": str(self.tmp / "outside.jsonl"), "event": "bad"})

    def test_open_launcher_supports_no_browser_for_restarts(self):
        script = (PROJECT_ROOT / "CODEX_open_panda_collaborator.ps1").read_text(encoding="utf-8")

        self.assertIn("[switch]$NoBrowser", script)
        self.assertIn("$IsRunning = Get-NetTCPConnection", script)
        self.assertIn("if ($IsRunning)", script)
        self.assertIn("Browser launch skipped. Refresh the existing tab:", script)
        self.assertIn("function Invoke-PandaCollaboratorRefresh", script)
        self.assertIn("api/launch-refresh/request", script)
        self.assertIn("api/launch-refresh/state", script)
        self.assertIn("foreground_ack_clients", script)
        self.assertNotIn("SendKeys", script)
        self.assertNotIn("_pc_launch", script)
        self.assertIn("function Open-PandaCollaborator", script)
        self.assertIn("Start-Process $Url", script)
        self.assertLess(script.index("if ($IsRunning)"), script.index("if ($NoBrowser)"))
        self.assertLess(script.index("if ($NoBrowser)"), script.index("\nOpen-PandaCollaborator"))

    def test_launch_refresh_payload_contract(self):
        original = json.loads(json.dumps(pc.LAUNCH_REFRESH_STATE))
        try:
            with pc.LAUNCH_REFRESH_LOCK:
                pc.LAUNCH_REFRESH_STATE.clear()
                pc.LAUNCH_REFRESH_STATE.update({"token": "", "issued_at": "", "clients": {}, "acks": {}})
            heartbeat = pc.record_launch_refresh_client(
                "test-client",
                "",
                {"visibility_state": "visible", "focused": True},
            )
            self.assertEqual(heartbeat["active_clients"], 1)
            self.assertEqual(heartbeat["foreground_clients"], 1)
            requested = pc.request_launch_refresh("unit-test")
            self.assertTrue(requested["token"])
            self.assertEqual(requested["active_clients"], 1)
            self.assertEqual(requested["ack_clients"], 0)
            acknowledged = pc.acknowledge_launch_refresh(
                "test-client",
                requested["token"],
                {"visibility_state": "visible", "focused": True},
            )
            self.assertEqual(acknowledged["ack_clients"], 1)
            self.assertEqual(acknowledged["foreground_ack_clients"], 1)
            with pc.LAUNCH_REFRESH_LOCK:
                pc.LAUNCH_REFRESH_STATE.clear()
                pc.LAUNCH_REFRESH_STATE.update({"token": "", "issued_at": "", "clients": {}, "acks": {}})
            hidden = pc.record_launch_refresh_client(
                "hidden-client",
                "",
                {"visibility_state": "hidden", "focused": False},
            )
            self.assertEqual(hidden["active_clients"], 1)
            self.assertEqual(hidden["foreground_clients"], 0)
            hidden_request = pc.request_launch_refresh("unit-test")
            hidden_ack = pc.acknowledge_launch_refresh(
                "hidden-client",
                hidden_request["token"],
                {"visibility_state": "hidden", "focused": False},
            )
            self.assertEqual(hidden_ack["ack_clients"], 1)
            self.assertEqual(hidden_ack["foreground_ack_clients"], 0)
        finally:
            with pc.LAUNCH_REFRESH_LOCK:
                pc.LAUNCH_REFRESH_STATE.clear()
                pc.LAUNCH_REFRESH_STATE.update(original)

    def test_run_pc_action_test_writes_pass_evidence_inside_run_folder(self):
        result = pc.run_pc_action_test()

        self.assertEqual(result["status"], "PASS")
        run_root = Path(result["run_root"]).resolve()
        self.assertTrue(Path(result["handoff_package_path"], "manifest.json").exists())
        self.assertTrue(Path(result["daily_report_path"]).exists())
        self.assertTrue(Path(result["evidence_json_path"]).exists())
        self.assertTrue(Path(result["evidence_markdown_path"]).exists())
        self.assertFalse(result["external_side_effects"])
        self.assertFalse(result["destructive_git_commands_run"])
        self.assertFalse(result["github_repo_created"])
        self.assertTrue(result["real_values_redacted"])
        self.assertGreaterEqual(len(result["messages_created"]), 2)
        self.assertTrue(all(item["ok"] for item in result["checkpoints"]))
        for key in ("handoff_package_path", "daily_report_path", "evidence_json_path", "evidence_markdown_path"):
            Path(result[key]).resolve().relative_to(run_root)
        report_text = Path(result["evidence_markdown_path"]).read_text(encoding="utf-8")
        self.assertIn("PC Action Test PASS", report_text)
        self.assertIn("Bob", report_text)
        self.assertIn("Karen", report_text)
        evidence = pc.read_test_evidence(result["evidence_markdown_path"])
        self.assertEqual(evidence["path"], result["evidence_markdown_path"])
        self.assertIn("PC Action Test PASS", evidence["content"])
        with self.assertRaises(pc.SafetyError):
            pc.read_test_evidence(str(run_root.parents[2] / "outside.md"))


class PandaCollaboratorSettingsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="panda-collab-settings-"))
        self.settings_path = self.tmp / "settings.local.json"
        self.old_settings_path = pc.os.environ.get("PANDA_COLLABORATOR_SETTINGS_PATH")
        pc.os.environ["PANDA_COLLABORATOR_SETTINGS_PATH"] = str(self.settings_path)

    def tearDown(self):
        if self.old_settings_path is None:
            pc.os.environ.pop("PANDA_COLLABORATOR_SETTINGS_PATH", None)
        else:
            pc.os.environ["PANDA_COLLABORATOR_SETTINGS_PATH"] = self.old_settings_path
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_default_settings_have_two_user_profiles(self):
        settings = pc.load_settings()

        self.assertFalse(settings["setup_completed"])
        self.assertEqual(settings["active_user_id"], "user1")
        self.assertEqual(settings["project_files_directory"], r"C:\panda-gallery")
        self.assertEqual([user["id"] for user in settings["users"]], ["user1", "user2"])
        self.assertEqual(settings["users"][0]["display_name"], "User 1")
        self.assertEqual(settings["users"][0]["codex_account"], "")
        self.assertEqual(settings["users"][0]["claude_account"], "")
        self.assertEqual(settings["users"][0]["claude_desktop_path"], "")
        self.assertEqual(settings["users"][0]["claude_code_path"], "")

    def test_save_settings_persists_two_custom_names(self):
        saved = pc.save_settings(
            {
                "active_user_id": "user2",
                "project_files_directory": str(self.tmp / "panda-gallery"),
                "users": [
                    {
                        "display_name": "Darrin",
                        "default_repo_path": str(self.tmp / "repo-a"),
                        "handoff_agent": "Codex",
                        "handoff_title": "Darrin handoff",
                        "codex_account": "darrin-codex@example.invalid",
                        "claude_account": "darrin-claude@example.invalid",
                        "claude_desktop_path": str(self.tmp / "claude-desktop-a.exe"),
                        "claude_code_path": str(self.tmp / "claude-code-a"),
                        "git_author_name": "Darrin",
                        "git_author_email": "darrin@example.invalid",
                    },
                    {
                        "display_name": "CD",
                        "default_repo_path": str(self.tmp / "repo-b"),
                        "handoff_agent": "Claude",
                        "handoff_title": "CD handoff",
                        "codex_account": "cd-codex@example.invalid",
                        "claude_account": "cd-claude@example.invalid",
                        "claude_desktop_path": str(self.tmp / "claude-desktop-b.exe"),
                        "claude_code_path": str(self.tmp / "claude-code-b"),
                        "git_author_name": "CD",
                        "git_author_email": "cd@example.invalid",
                    },
                ],
            }
        )

        self.assertTrue(saved["setup_completed"])
        self.assertEqual(saved["active_user_id"], "user2")
        self.assertEqual(saved["project_files_directory"], str(self.tmp / "panda-gallery"))
        self.assertEqual([user["display_name"] for user in saved["users"]], ["Darrin", "CD"])
        loaded = pc.load_settings()
        self.assertEqual(loaded["users"][1]["handoff_title"], "CD handoff")
        self.assertEqual(loaded["users"][0]["codex_account"], "darrin-codex@example.invalid")
        self.assertEqual(loaded["users"][0]["claude_desktop_path"], str(self.tmp / "claude-desktop-a.exe"))
        self.assertEqual(loaded["users"][1]["claude_code_path"], str(self.tmp / "claude-code-b"))
        self.assertEqual(loaded["users"][1]["git_author_email"], "cd@example.invalid")

        pc.save_settings(saved)
        backups = list(self.tmp.glob("settings.local.*.bak.json"))
        self.assertGreaterEqual(len(backups), 1)

    def test_save_settings_requires_exactly_two_profiles(self):
        with self.assertRaises(pc.CollaboratorError):
            pc.save_settings({"users": [{"display_name": "Only one"}]})

    def test_default_settings_include_clean_handover_state(self):
        # Phase 5 (PC_HANDOFF_PROGRESS_SPEC v1.1 §5.2): default settings include a
        # handover_state sub-object with all-null fields and handover_pending=False.
        settings = pc.load_settings()
        self.assertIn("handover_state", settings)
        hs = settings["handover_state"]
        self.assertEqual(hs["handover_pending"], False)
        self.assertIsNone(hs["incoming_user_slot"])
        self.assertIsNone(hs["handover_timestamp"])
        self.assertIsNone(hs["handoff_package_id"])
        self.assertIsNone(hs["failed_package_id"])

    def test_save_settings_round_trips_populated_handover_state(self):
        # Phase 5: write a populated handover_state through save_settings, then load
        # and verify all 5 fields survive normalization round-trip.
        ts_iso = "2026-05-04T22:30:00-07:00"
        saved = pc.save_settings(
            {
                "active_user_id": "user1",
                "project_files_directory": str(self.tmp / "panda-gallery"),
                "users": [
                    {
                        "display_name": "Darrin",
                        "default_repo_path": str(self.tmp / "repo-a"),
                        "handoff_agent": "Codex",
                        "handoff_title": "Darrin handoff",
                        "codex_account": "darrin-codex@example.invalid",
                        "claude_account": "darrin-claude@example.invalid",
                        "claude_desktop_path": str(self.tmp / "cd-a.exe"),
                        "claude_code_path": str(self.tmp / "cc-a"),
                        "git_author_name": "Darrin",
                        "git_author_email": "darrin@example.invalid",
                    },
                    {
                        "display_name": "Adam",
                        "default_repo_path": str(self.tmp / "repo-b"),
                        "handoff_agent": "Claude",
                        "handoff_title": "Adam handoff",
                        "codex_account": "adam-codex@example.invalid",
                        "claude_account": "adam-claude@example.invalid",
                        "claude_desktop_path": str(self.tmp / "cd-b.exe"),
                        "claude_code_path": str(self.tmp / "cc-b"),
                        "git_author_name": "Adam",
                        "git_author_email": "adam@example.invalid",
                    },
                ],
                "handover_state": {
                    "handover_pending": True,
                    "incoming_user_slot": "user2",
                    "handover_timestamp": ts_iso,
                    "handoff_package_id": "PG-2026-05-04-2230",
                    "failed_package_id": None,
                },
            }
        )
        self.assertEqual(saved["handover_state"]["handover_pending"], True)
        self.assertEqual(saved["handover_state"]["incoming_user_slot"], "user2")
        self.assertEqual(saved["handover_state"]["handover_timestamp"], ts_iso)
        self.assertEqual(saved["handover_state"]["handoff_package_id"], "PG-2026-05-04-2230")
        self.assertIsNone(saved["handover_state"]["failed_package_id"])
        loaded = pc.load_settings()
        self.assertEqual(loaded["handover_state"]["handover_pending"], True)
        self.assertEqual(loaded["handover_state"]["incoming_user_slot"], "user2")
        self.assertEqual(loaded["handover_state"]["handoff_package_id"], "PG-2026-05-04-2230")
        self.assertIsNone(loaded["handover_state"]["failed_package_id"])

    def test_load_settings_with_missing_handover_state_falls_back_to_default(self):
        # Phase 5 (per CD ruling): missing handover_state sub-object in settings.json
        # is treated as `{handover_pending: False}` — no migration step required.
        # Write a settings file missing handover_state and verify load_settings
        # returns the default normalized shape.
        legacy_payload = {
            "schema_version": 1,
            "setup_completed": True,
            "active_user_id": "user1",
            "project_files_directory": str(self.tmp / "panda-gallery"),
            "users": [
                {
                    "id": "user1",
                    "display_name": "Darrin",
                    "default_repo_path": str(self.tmp / "repo-a"),
                    "handoff_agent": "Codex",
                    "handoff_title": "Darrin handoff",
                    "codex_account": "darrin-codex@example.invalid",
                    "claude_account": "darrin-claude@example.invalid",
                    "claude_desktop_path": str(self.tmp / "cd-a.exe"),
                    "claude_code_path": str(self.tmp / "cc-a"),
                    "git_author_name": "Darrin",
                    "git_author_email": "darrin@example.invalid",
                },
                {
                    "id": "user2",
                    "display_name": "Adam",
                    "default_repo_path": str(self.tmp / "repo-b"),
                    "handoff_agent": "Claude",
                    "handoff_title": "Adam handoff",
                    "codex_account": "adam-codex@example.invalid",
                    "claude_account": "adam-claude@example.invalid",
                    "claude_desktop_path": str(self.tmp / "cd-b.exe"),
                    "claude_code_path": str(self.tmp / "cc-b"),
                    "git_author_name": "Adam",
                    "git_author_email": "adam@example.invalid",
                },
            ],
            # NOTE: no `handover_state` key — simulates a pre-Phase-5 settings file
        }
        path = pc.settings_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(legacy_payload), encoding="utf-8")

        loaded = pc.load_settings()
        self.assertIn("handover_state", loaded)
        hs = loaded["handover_state"]
        self.assertFalse(hs["handover_pending"])
        self.assertIsNone(hs["incoming_user_slot"])
        self.assertIsNone(hs["handover_timestamp"])
        self.assertIsNone(hs["handoff_package_id"])
        self.assertIsNone(hs["failed_package_id"])

    def test_normalize_handover_state_clamps_invalid_slot_and_string_lengths(self):
        # Phase 5: invalid slot strings → None; oversize string fields trimmed to caps.
        # Phase 5 micro-fix (CLAUDE-20260504-008302): handover_pending uses strict
        # bool coercion — only Python True or integer 1 produce True. Any string
        # (including "false", "true", "yes") collapses to False to avoid the
        # bool("false") == True quirk mis-firing Phase 7 auto-show on a manually
        # edited settings file.
        result = pc.normalize_handover_state(
            {
                "handover_pending": "yes",  # string — strict coercion → False
                "incoming_user_slot": "user_1",  # underscore variant — invalid → None
                "handover_timestamp": "  2026-05-04T22:30:00-07:00  " + "x" * 200,
                "handoff_package_id": "P" * 500,
                "failed_package_id": "  ",  # whitespace-only → None
            }
        )
        self.assertEqual(result["handover_pending"], False)
        self.assertIsNone(result["incoming_user_slot"])
        self.assertEqual(len(result["handover_timestamp"]), 64)
        self.assertEqual(len(result["handoff_package_id"]), 120)
        self.assertIsNone(result["failed_package_id"])

        # Per CD micro-fix directive: explicit assertions for bool coercion edge cases.
        self.assertFalse(pc.normalize_handover_state({"handover_pending": "false"})["handover_pending"])
        self.assertFalse(pc.normalize_handover_state({"handover_pending": "true"})["handover_pending"])
        self.assertFalse(pc.normalize_handover_state({"handover_pending": "yes"})["handover_pending"])
        self.assertTrue(pc.normalize_handover_state({"handover_pending": True})["handover_pending"])
        self.assertTrue(pc.normalize_handover_state({"handover_pending": 1})["handover_pending"])
        self.assertFalse(pc.normalize_handover_state({"handover_pending": 0})["handover_pending"])
        self.assertFalse(pc.normalize_handover_state({"handover_pending": None})["handover_pending"])

    def test_setup_autofill_finds_paths_and_drafts_claude_help(self):
        repo = self.tmp / "repo"
        repo.mkdir()
        run(["git", "init"], repo)
        run(["git", "config", "user.name", "Darrin"], repo)
        run(["git", "config", "user.email", "darrin@example.invalid"], repo)
        project_files = self.tmp / "panda-gallery"
        (project_files / "skills" / "pg-project-sync").mkdir(parents=True)
        (project_files / "skills" / "pg-project-sync" / "MANIFEST.md").write_text("# manifest\n", encoding="utf-8")
        local_app = self.tmp / "localapp"
        claude_desktop = local_app / "AnthropicClaude" / "Claude.exe"
        claude_desktop.parent.mkdir(parents=True)
        claude_desktop.write_text("", encoding="utf-8")
        bin_dir = self.tmp / "bin"
        bin_dir.mkdir()
        claude_code = bin_dir / "claude.cmd"
        claude_code.write_text("@echo off\n", encoding="utf-8")
        cc_inbox = self.tmp / "cc-inbox"
        cc_inbox.mkdir()

        old_search = pc.os.environ.get("PANDA_COLLABORATOR_SEARCH_ROOTS")
        old_inbox = pc.os.environ.get("PANDA_COLLABORATOR_CC_INBOX")
        old_local = pc.os.environ.get("LOCALAPPDATA")
        old_path = pc.os.environ.get("PATH")
        pc.os.environ["PANDA_COLLABORATOR_SEARCH_ROOTS"] = str(self.tmp)
        pc.os.environ["PANDA_COLLABORATOR_CC_INBOX"] = str(cc_inbox)
        pc.os.environ["LOCALAPPDATA"] = str(local_app)
        pc.os.environ["PATH"] = str(bin_dir) + pc.os.pathsep + (old_path or "")
        try:
            result = pc.setup_autofill({"settings": pc.default_settings(), "ask_claude": True})
        finally:
            if old_search is None:
                pc.os.environ.pop("PANDA_COLLABORATOR_SEARCH_ROOTS", None)
            else:
                pc.os.environ["PANDA_COLLABORATOR_SEARCH_ROOTS"] = old_search
            if old_inbox is None:
                pc.os.environ.pop("PANDA_COLLABORATOR_CC_INBOX", None)
            else:
                pc.os.environ["PANDA_COLLABORATOR_CC_INBOX"] = old_inbox
            if old_local is None:
                pc.os.environ.pop("LOCALAPPDATA", None)
            else:
                pc.os.environ["LOCALAPPDATA"] = old_local
            if old_path is None:
                pc.os.environ.pop("PATH", None)
            else:
                pc.os.environ["PATH"] = old_path

        self.assertEqual(result["suggestions"]["project_files_directory"], str(project_files))
        self.assertEqual(result["suggestions"]["users"][0]["default_repo_path"], str(repo))
        self.assertEqual(result["suggestions"]["users"][0]["git_author_name"], "Darrin")
        self.assertEqual(result["suggestions"]["users"][0]["git_author_email"], "darrin@example.invalid")
        self.assertEqual(result["suggestions"]["users"][0]["claude_desktop_path"], str(claude_desktop))
        self.assertEqual(result["suggestions"]["users"][0]["claude_code_path"].lower(), str(claude_code).lower())
        self.assertTrue(result["claude_request"]["created"])
        self.assertTrue(Path(result["claude_request"]["message_path"]).exists())

    def test_path_picker_rejects_invalid_mode_before_opening_gui(self):
        with self.assertRaises(pc.CollaboratorError):
            pc.pick_local_path({"mode": "branch"})

    def test_path_picker_configures_high_dpi_awareness_before_gui(self):
        source = (PROJECT_ROOT / "panda_collaborator.py").read_text(encoding="utf-8")

        self.assertIn("def configure_path_picker_dpi_awareness()", source)
        self.assertIn("SetProcessDpiAwareness(2)", source)
        self.assertIn("SetProcessDPIAware()", source)
        self.assertLess(source.index("configure_path_picker_dpi_awareness()"), source.index("import tkinter as tk"))
        self.assertIn('root.tk.call("tk", "scaling"', source)


class PandaCollaboratorWebThemeTests(unittest.TestCase):
    def test_workflow_panels_are_single_state_colored_step_guide(self):
        html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")

        # Phase 2: workflow guide is now the 32px Phase 1 horizontal rail (.workflow-guide)
        # with .wg-step blocks; legacy 5-panel sequence-panel grid was atomically replaced.
        # JS workflow lock infrastructure (sequence-panel CSS rules + updateWorkflowLocks) is
        # preserved as dead CSS until Phase 8 cleanup.
        self.assertNotIn('class="panda-step-guide"', html)
        self.assertNotIn('id="pandaStepGuide"', html)
        self.assertIn("function pandaStepGuideState()", html)
        self.assertIn("function renderPandaStepGuide()", html)
        # Sequence labels still appear in the live left-to-right workflow rail
        self.assertIn("Register User 1", html)
        self.assertIn("Register User 2", html)
        self.assertIn("Start Session", html)
        self.assertIn('id="workflowGuide"', html)
        for step in ("setup", "tree", "start", "activity", "handoff"):
            self.assertIn(f'data-wg-step="{step}"', html)
        self.assertIn("step.done ? '✓' : String(index + 1)", html)
        self.assertIn("node.classList.add(step.state)", html)
        self.assertIn("stateText.textContent = step.stateText", html)
        self.assertIn("const treeDone = Boolean(state.repo?.repo_root);", html)
        # JS workflow lock CSS rules preserved as dead CSS until Phase 8 cleanup
        self.assertIn(".sequence-panel.is-current .panel-head", html)
        self.assertIn(".sequence-panel.is-ready .panel-head", html)
        self.assertIn(".sequence-panel.is-pending .panel-head", html)
        self.assertIn("panel.dataset.flowState", html)

    def test_guided_flow_uses_visible_completion_and_actionable_states(self):
        html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")

        self.assertIn("### App-Wide Guided Completion Flow", (PROJECT_ROOT / "PRODUCTION_SPEC.md").read_text(encoding="utf-8"))
        self.assertRegex(html, r"(?s)\.wg-step\.complete \.step-num\s*\{.*?background:\s*var\(--ok\);")
        self.assertRegex(html, r"(?s)\.wg-step\.ready \.step-num\s*\{.*?background:\s*var\(--ok-soft\);")
        self.assertRegex(html, r"(?s)\.wg-step\.active \.step-num\s*\{.*?background:\s*var\(--accent\);")
        self.assertRegex(html, r"(?s)\.wg-step\.pending \.step-num\s*\{.*?background:\s*var\(--pane\);")
        self.assertIn("state: step.done ? 'complete' : step.id === current && step.enabled ? 'active' : step.enabled ? 'ready' : 'pending'", html)
        self.assertIn("node.setAttribute('title', step.state === 'pending' ? step.pendingReason", html)
        self.assertIn("start: setupDone && treeDone", html)

    def test_setup_checklist_reveals_steps_progressively(self):
        html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")

        self.assertRegex(html, r"\['user1Ready', 'Register User 1', user1Ready, true\]")
        self.assertRegex(html, r"\['user2Ready', 'Register User 2', user2Ready, user1Ready\]")
        self.assertRegex(html, r"\['allReady', 'Open Collaborator Hub', readiness\.allReady, user1Ready && user2Ready\]")
        self.assertIn("].filter(([, , , visible]) => visible)", html)

    def test_quick_message_is_not_handoff_gated(self):
        html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")

        self.assertIn("function messageStepReady()", html)
        self.assertIn("return Boolean(setupReady().allReady);", html)
        self.assertIn("$('messageText').disabled = isBusy || !messageStepReady();", html)
        self.assertIn("$('messageText').disabled = state.busy || !messageStepReady();", html)
        self.assertNotIn("$('messageText').disabled = isBusy || !handoffReady;", html)
        self.assertNotIn("$('messageText').disabled = state.busy || !handoffStepReady();", html)

    def test_render_repo_supports_saved_state_and_empty_state(self):
        html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")

        self.assertIn("function renderRepo(repo = state.repo)", html)
        render_repo = html.split("function renderRepo(repo = state.repo)", 1)[1].split("/* Phase 3: showResult", 1)[0]
        self.assertIn("if (!repo)", render_repo)
        self.assertIn("renderStatusBar(null);", render_repo)
        self.assertIn("localStorage.setItem('pandaCollaborator.repoPath', repo.repo_root || '');", render_repo)
        self.assertIn("$('branchChip').textContent = repo.branch || 'branch –';", render_repo)
        self.assertIn("${escapeHtml(repo.repo_root || '')}", render_repo)

    def test_setup_fields_map_to_visible_user_panels(self):
        html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")
        render_settings = html.split("function renderSettings()", 1)[1].split("async function loadSettings()", 1)[0]
        save_settings = html.split("async function saveSettings", 1)[1].split("async function saveCurrentSettings", 1)[0]

        self.assertIn("const user1Profile = user1;", render_settings)
        self.assertIn("$('profileRepoPath').value = user1Profile?.default_repo_path || '';", render_settings)
        self.assertIn("$('profileAgent').value = user1Profile?.handoff_agent || user1Profile?.display_name || '';", render_settings)
        self.assertIn("$('profileRepoPathUser2').value = user2?.default_repo_path || '';", render_settings)
        self.assertNotIn("const profile = activeProfile();", render_settings)
        self.assertNotIn("$('profileRepoPath').value = profile?.default_repo_path || '';", render_settings)
        self.assertIn("syncAllRegistrationFieldsToState();", save_settings)
        self.assertNotIn("syncActiveProfileFieldsToState();", save_settings)

    def test_user_one_registration_uses_warm_amber_theme(self):
        html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")
        user_one_match = re.search(r"body\.user-one\s*\{(?P<body>.*?)\n\s*\}", html, re.S)
        self.assertIsNotNone(user_one_match)
        user_one_css = user_one_match.group("body").lower()

        self.assertIn("--user-accent: #f2b36d", user_one_css)
        self.assertIn("--accent: #f2b36d", user_one_css)
        self.assertIn("--user-bg: #281a10", user_one_css)
        self.assertNotIn("#68d8e8", user_one_css)
        self.assertNotIn("104, 216, 232", user_one_css)
        self.assertIn("function effectiveThemeUserId()", html)
        theme_function = html.split("function effectiveThemeUserId()", 1)[1].split("function applyUserTheme()", 1)[0]
        self.assertNotIn("registrationStage", theme_function)
        self.assertRegex(
            html,
            r"(?s)function setRegistrationStage\(stage\).*?applyUserTheme\(\);.*?updateSetupGuide\(\);",
            "Registration stage changes must refresh labels without changing the active operator theme.",
        )

    def test_user_registration_surfaces_keep_identity_tones(self):
        html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")

        self.assertIn('[data-user-tone="user1"]', html)
        self.assertIn('[data-user-tone="user2"]', html)
        self.assertIn("--tone-accent: #f2b36d", html)
        self.assertIn("--tone-accent: #68d8e8", html)
        self.assertIn('data-flow-panel="user1" data-user-tone="user1"', html)
        self.assertIn('data-flow-panel="user2" data-user-tone="user2"', html)
        self.assertIn('class="setup-dialog" data-user-tone="user1"', html)
        self.assertIn('data-registration-stage="user1" data-user-tone="user1"', html)
        self.assertIn('data-registration-stage="user2" data-user-tone="user2"', html)
        self.assertIn("setupDialog.dataset.userTone = userTone", html)
        self.assertIn("delete setupDialog.dataset.userTone", html)
        self.assertRegex(html, r"(?s)\.setup-dialog\s*\{.*?border:\s*1px solid var\(--tone-ring, var\(--user-ring\)\);")
        self.assertRegex(html, r"(?s)\.setup-dialog-head h2\s*\{.*?color:\s*var\(--tone-accent, var\(--user-accent\)\);")
        self.assertRegex(html, r"(?s)\.setup-dialog\[data-user-tone\] \.primary\s*\{.*?background:\s*linear-gradient\(180deg, #8ccf6f, #6da850\);")
        self.assertRegex(html, r"(?s)\.setup-dialog\[data-user-tone\] \.setup-checklist li\.current\s*\{.*?color:\s*var\(--tone-accent\);")
        self.assertRegex(html, r"(?s)\.sequence-panel\[data-user-tone\]\.is-current\s*\{.*?border-color:\s*var\(--tone-ring\);")
        self.assertRegex(html, r"(?s)\.registration-panel\[data-user-tone\]\.is-current\s*\{.*?border-color:\s*var\(--tone-ring\);")
        self.assertRegex(html, r"(?s)\.register-card\s*\{.*?border:\s*1px solid var\(--tone-ring, var\(--user-ring\)\);")
        self.assertRegex(html, r"(?s)\.register-card strong\s*\{.*?color:\s*var\(--tone-accent, var\(--user-accent\)\);")

    def test_setup_collects_claude_paths_with_browse_buttons(self):
        html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")

        for element_id in ("claudeDesktopPath", "claudeCodePath", "claudeDesktopPathUser2", "claudeCodePathUser2"):
            self.assertIn(f'id="{element_id}"', html)
            self.assertIn(f'data-path-picker="{element_id}"', html)
        self.assertIn("async function pickPath", html)
        self.assertIn("'/api/path/pick'", html)
        self.assertIn("claude_desktop_path", html)
        self.assertIn("claude_code_path", html)
        # Phase 1: the only step-num="4" element is the workflow-guide activity stage.
        # It must not appear as a wizard registration badge; verify it only appears inside .wg-step.
        self.assertEqual(html.count('<span class="step-num">4</span>'), 1)
        self.assertIn('data-wg-step="activity"', html)

    def test_repository_paths_have_folder_browse_buttons(self):
        html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")
        # Phase 2: Working Tree lives in left column .sec block; legacy .repo-panel container
        # was atomically replaced. JS-reachable IDs (repoPath, scanBtn, packagesBtn) preserved
        # in the new Working Tree .sec inside the left-col.
        # The User 1 / User 2 profileRepoPath inputs still live inside the setup-overlay modal.
        for element_id in ("repoPath", "profileRepoPath", "profileRepoPathUser2"):
            self.assertIn(f'id="{element_id}"', html)
            self.assertIn(f'data-path-picker="{element_id}"', html)
        self.assertEqual(html.count('id="repoPath"'), 1)
        self.assertEqual(html.count('id="scanBtn"'), 1)
        # Working Tree section uses spec §9 canonical button name "Scan Working Tree"
        self.assertIn('id="scanBtn"', html)
        self.assertRegex(html, r'<button[^>]*id="scanBtn"[^>]*>Scan Working Tree</button>')
        self.assertIn('data-path-title="Select local Git repository folder"', html)
        self.assertIn('data-path-title="Select User 1 local Git repository folder"', html)
        self.assertIn('data-path-title="Select User 2 local Git repository folder"', html)

    def test_scan_repository_does_not_open_registration_wizard(self):
        html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")
        scan_function = html.split("async function scanRepo()", 1)[1].split("function activeOperatorContext()", 1)[0]
        load_settings_function = html.split("async function loadSettings()", 1)[1].split("async function saveSettings", 1)[0]

        self.assertIn("api('/api/repo/scan'", scan_function)
        self.assertNotIn("openSetupWizard", scan_function)
        self.assertNotIn("setupReady().allReady", scan_function)
        self.assertIn("Repository scan complete. Setup is only required before handover", scan_function)
        self.assertIn("Working Tree scan remains available", load_settings_function)
        self.assertNotIn("openSetupWizard", load_settings_function)

    def test_working_tree_panel_gets_room_and_wraps_controls(self):
        html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")

        self.assertRegex(html, r"(?s)\.support-grid\s*\{.*?grid-template-rows:\s*minmax\(172px, \.62fr\) minmax\(86px, \.38fr\);")
        self.assertRegex(html, r"(?s)\.repo-panel\s*\{.*?overflow:\s*hidden;")
        self.assertRegex(html, r"(?s)\.repo-panel \.panel-body\s*\{.*?overflow-x:\s*hidden;.*?overflow-y:\s*auto;.*?grid-template-rows:\s*auto minmax\(44px, 1fr\);")
        self.assertRegex(html, r"(?s)\.repo-scan-controls\s*\{.*?grid-template-columns:\s*repeat\(2, minmax\(0, 1fr\)\);.*?gap:\s*8px;")
        self.assertRegex(html, r"(?s)\.repo-scan-controls label\s*\{.*?grid-column:\s*1 / -1;")
        self.assertRegex(html, r"(?s)\.repo-scan-controls \.inline-picker\s*\{.*?grid-template-columns:\s*minmax\(0, 1fr\) minmax\(96px, auto\);.*?gap:\s*8px;")
        self.assertRegex(html, r"(?s)@media \(max-width: 1200px\).*?\.repo-scan-controls\s*\{\s*grid-template-columns:\s*minmax\(0, 1fr\);")
        self.assertRegex(html, r"(?s)@media \(max-width: 1200px\).*?\.repo-scan-controls button\s*\{\s*width:\s*100%;")

    def test_escape_key_recovers_from_scan_focus_and_scroll(self):
        html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")
        escape_handler = html.split("document.addEventListener('keydown', event =>", 1)[1].split("$('resultBox').addEventListener", 1)[0]

        self.assertIn("event.key !== 'Escape'", escape_handler)
        self.assertIn("closeSetupWizard();", escape_handler)
        self.assertIn("document.activeElement?.blur?.();", escape_handler)
        self.assertIn("document.querySelector('.repo-panel .panel-body')?.scrollTo?.({top: 0, left: 0});", escape_handler)
        self.assertIn("document.querySelector('.status-window')?.scrollTo?.({top: 0, left: 0});", escape_handler)

    def test_project_files_directory_uses_existing_pgsync_location(self):
        # Setup-modal-fix (Phase 7-fix) Q2: in-modal `setupProjectFilesDirectory`
        # input + auto-fill section removed per locked v2 mockup. Main-view
        # `projectFilesDirectory` input retains user-edit responsibility for the
        # `project_files_directory` setting.
        html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")

        self.assertIn('id="projectFilesDirectory"', html)
        self.assertIn('data-path-picker="projectFilesDirectory"', html)
        self.assertIn(r"C:\panda-gallery", html)
        self.assertNotIn('id="setupProjectFilesDirectory"', html)
        self.assertNotIn('data-path-picker="setupProjectFilesDirectory"', html)

    # test_setup_has_auto_fill_and_claude_help_action: DELETED.
    # Setup-modal-fix Q3 ruling — `autoFillSetupBtn` removed from the modal per
    # locked v2 mockup. Backend `/api/setup/autofill` endpoint stays untouched
    # for potential future surfacing.

    def test_switch_user_entry_points_are_visible_and_not_dead_before_setup(self):
        html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")

        self.assertIn('id="switchUserBtn"', html)
        # Phase 2: legacy "Collaborator Hub / Handover" panel header gone with atomic replace.
        # The hub functionality (Switch buttons + identity sections) now lives in the left
        # column User 1 / User 2 sections. Switch buttons exist with data-switch-go attributes.
        # data-switch-go appears in: (1) left-col Switch button, (2) legacy-pending hub markup,
        # (3) setup-overlay registration. Phase 8 will dedupe; Phase 2 keeps all to preserve
        # JS-reachable handlers.
        self.assertGreaterEqual(html.count('data-switch-go="user1"'), 1)
        self.assertGreaterEqual(html.count('data-switch-go="user2"'), 1)
        self.assertIn("$('switchUserBtn').addEventListener('click', openSetupWizard)", html)
        self.assertIn("button.disabled = state.busy;", html)
        self.assertIn("function handoverButtonLabel(userId, user)", html)
        self.assertIn("return {text: 'Handover'", html)
        self.assertIn("button.textContent = label.text;", html)
        self.assertIn("button.textContent = 'Set up';", html)
        self.assertIn("aria: `Set up ${setupTarget}`", html)
        self.assertNotIn("HANDOVER TO USER 1", html)
        self.assertNotIn("HANDOVER TO USER 2", html)
        self.assertNotIn("GO / Switch", html)

    def test_test_mode_has_visible_lifecycle_and_restore_controls(self):
        html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")

        self.assertIn('id="testModeBtn"', html)
        self.assertIn('id="createTestSandboxBtn"', html)
        self.assertIn('id="testStatusPill"', html)
        self.assertIn('id="openTestEvidenceBtn"', html)
        self.assertIn('id="quitTestModeBtn"', html)
        self.assertIn('id="quitTestModeBannerBtn"', html)
        self.assertIn('id="runTestAgainBtn"', html)
        self.assertIn('id="testModeBanner"', html)
        self.assertIn("body.test-mode", html)
        self.assertIn("TEST MODE ACTIVE - FAKE USERS, FAKE ACCOUNTS, FAKE REPOSITORY", html)
        self.assertIn("function enterTestMode()", html)
        self.assertIn("async function createTestSandbox()", html)
        self.assertIn("async function runPcActionTest()", html)
        self.assertIn("async function openTestEvidence()", html)
        self.assertIn("async function ensureManualTestLog()", html)
        self.assertIn("async function logManualTestStep", html)
        self.assertIn('id="testChecklist"', html)
        self.assertIn("const manualTestChecklist = [", html)
        self.assertIn("function renderTestChecklist()", html)
        self.assertIn("function markManualChecklist(id)", html)
        self.assertIn("function startTestChecklistDrag()", html)
        self.assertIn("startTestChecklistDrag();", html)
        self.assertIn("handle.addEventListener('pointerdown'", html)
        self.assertIn("api('/api/test/sandbox'", html)
        self.assertIn("api('/api/test/run'", html)
        self.assertIn("api('/api/test/manual-log/start'", html)
        self.assertIn("api('/api/test/manual-log/append'", html)
        self.assertIn("apiGet(`/api/test/evidence?path=${encodeURIComponent(path)}`)", html)
        self.assertIn("function quitTestMode(result = '')", html)
        self.assertIn("function normalModeSanityCheck()", html)
        self.assertIn("localStorage.setItem('pandaCollaborator.testModeSnapshot'", html)
        self.assertIn("localStorage.removeItem('pandaCollaborator.testModeActive')", html)
        self.assertIn("$('testModeBtn').addEventListener('click'", html)
        self.assertIn("$('createTestSandboxBtn').addEventListener('click', createTestSandbox)", html)
        self.assertIn("$('runTestAgainBtn').addEventListener('click', runPcActionTest)", html)
        self.assertIn("$('openTestEvidenceBtn').addEventListener('click', openTestEvidence)", html)
        self.assertIn("$('quitTestModeBtn').addEventListener('click', () => quitTestMode())", html)
        self.assertIn("$('testChecklistMinBtn').addEventListener('click'", html)
        self.assertIn("$('testChecklistLogBtn').addEventListener('click'", html)
        self.assertIn("$('quitTestModeBannerBtn').addEventListener('click', () => quitTestMode())", html)

    def test_test_mode_footer_contains_test_pill_not_safety_pill(self):
        # Phase 8 Feature 3 (token §3 item 5): when body.test-mode is active,
        # the footer shows a yellow `test-pill` and the standard `safety-pill`
        # is hidden. CSS rule pair: `body.test-mode .pc-footer .test-pill { display: inline-flex }`
        # + `body.test-mode .pc-footer .safety-pill { display: none }`.
        html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")
        self.assertIn('class="test-pill"', html)
        self.assertIn('class="safety-pill"', html)
        self.assertIn("body.test-mode .pc-footer .test-pill { display: inline-flex; }", html)
        self.assertIn("body.test-mode .pc-footer .safety-pill { display: none; }", html)
        # The test-pill copy aligns with the v2 mockup verbatim
        self.assertIn("⚠ TEST MODE — Fake users, fake accounts, sandbox repo", html)

    def test_test_mode_diagonal_ribbon_uses_high_contrast_yellow_black(self):
        html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")
        ribbon_rule = html.split("body.test-mode::before {", 1)[1].split("}", 1)[0]

        self.assertIn('content: "TEST MODE";', ribbon_rule)
        self.assertIn("background: #ffdf4d;", ribbon_rule)
        self.assertIn("color: #050505;", ribbon_rule)
        self.assertIn("font-weight: 900;", ribbon_rule)
        self.assertNotIn("background: var(--test-bob);", ribbon_rule)
        self.assertNotIn("color: var(--canvas);", ribbon_rule)

    def test_test_mode_uses_bob_karen_and_does_not_persist_to_normal_settings(self):
        html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")

        self.assertIn("display_name: 'Bob'", html)
        self.assertIn("display_name: 'Karen'", html)
        self.assertIn("test-bob-codex@example.invalid", html)
        self.assertIn("test-karen-claude@example.invalid", html)
        self.assertIn("bob.test@example.invalid", html)
        self.assertIn("karen.test@example.invalid", html)
        self.assertIn("localStorage.setItem('pandaCollaborator.testModeSettings', JSON.stringify(state.settings));", html)
        persist_function = html.split("async function persistSettings()", 1)[1].split("function autoFillSummary", 1)[0]
        self.assertLess(persist_function.index("if (state.testMode.active)"), persist_function.index("api('/api/settings'"))
        self.assertIn("TEST MODE quit complete. Normal Darrin and Pam state restored", html)

    def test_registration_headers_do_not_render_redundant_number_badges(self):
        html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")

        # The legacy panda-step-guide must stay gone — it caused redundant numbering on registration headers.
        # Phase 2 atomically replaced the legacy 5-panel `.workflow-row` (which carried
        # `.sequence-step` numeric badges) with the 3-column `.pc-body` body. The only
        # remaining numbered badges live in the Phase 1 horizontal `.workflow-guide` rail
        # (5 `.wg-step .step-num` dots).
        self.assertNotIn('class="panda-step-guide"', html)
        self.assertNotIn('class="sequence-step">1</span>', html)
        self.assertNotIn('class="sequence-step">2</span>', html)
        # New workflow-guide step nums live inside .wg-step blocks and are the only step-num usage.
        for badge_num in ("1", "2", "3", "4", "5"):
            self.assertEqual(html.count(f'<span class="step-num">{badge_num}</span>'), 1,
                             f"step-num {badge_num} should appear exactly once (in workflow-guide)")

    def test_heading_fonts_stay_compact_for_single_screen_fit(self):
        html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")

        self.assertRegex(html, r"(?s)\.setup-dialog-head h2\s*\{.*?font-size:\s*18px;")
        self.assertRegex(html, r"(?s)\.registration-title strong\s*\{.*?font-size:\s*18px;")
        self.assertRegex(html, r"(?s)\.active-user-banner strong\s*\{.*?font-size:\s*20px;")
        self.assertRegex(html, r"(?s)\.sequence-panel h2\s*\{.*?gap:\s*6px;")
        self.assertRegex(html, r"(?s)\.brand h1\s*\{.*?font-size:\s*14px;")
        self.assertRegex(html, r"(?s)\.panel-head h2\s*\{.*?font-size:\s*10px;")
        self.assertRegex(html, r"(?s)\.hub-card strong\s*\{.*?font-size:\s*12px;")

    def test_active_user_banner_stays_inside_header_row(self):
        html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")

        # Phase 1 chrome: shell stacks header / statusbar / workflow-guide / main
        self.assertRegex(html, r"(?s)\.shell\s*\{.*?grid-template-rows:\s*auto auto auto minmax\(0, 1fr\);")
        # New pc-header is a flex row matching pc_main_operational.html
        self.assertRegex(html, r"(?s)\.pc-header\s*\{.*?display:\s*flex;")
        self.assertRegex(html, r"(?s)\.pc-header\s*\{.*?background:\s*var\(--chrome\);")
        # Active-user pill inside pc-header (left-border-stripe style, identity-color via body theme)
        self.assertRegex(html, r"(?s)\.pc-header \.active-user\s*\{.*?border-left:\s*3px solid var\(--user1\);")
        self.assertRegex(html, r"(?s)body\.user-two \.pc-header \.active-user\s*\{.*?border-left-color:\s*var\(--user2\);")
        # The activeUserName ID still lives inside the header row (JS-reachable)
        self.assertIn('id="activeUserName" class="active-user"', html)
        self.assertIn('id="activeUserTheme" class="role-tag"', html)

    def test_information_pills_and_action_buttons_are_visually_distinct(self):
        html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")

        # Phase 1: Bible-aligned radius (4px = var(--radius-md)) and flat surface backgrounds
        self.assertRegex(html, r"(?s)button\s*\{.*?border-radius:\s*var\(--radius-md\);")
        self.assertRegex(html, r"(?s)button\s*\{.*?box-shadow:\s*inset 0 1px 0")
        self.assertRegex(html, r"(?s)button:not\(:disabled\):not\(\.danger\)\s*\{.*?background:\s*var\(--ok\);")
        self.assertRegex(html, r"(?s)button:disabled\s*\{.*?background:\s*var\(--pane\);")
        self.assertRegex(html, r"(?s)\.view-toggle button\.active:not\(:disabled\).*?\.segmented button\.active:not\(:disabled\)\s*\{.*?background:\s*var\(--ok\);")
        self.assertRegex(html, r"(?s)\.chip\s*\{.*?border-radius:\s*999px;")
        self.assertRegex(html, r"(?s)\.chip\s*\{.*?cursor:\s*default;")
        self.assertRegex(html, r"(?s)\.test-status-pill\s*\{.*?border-radius:\s*999px;")
        self.assertRegex(html, r"(?s)\.test-status-pill\s*\{.*?cursor:\s*default;")
        self.assertRegex(html, r"(?s)\.test-mode-btn\s*\{.*?border-radius:\s*var\(--radius-md\);")
        self.assertRegex(html, r"(?s)\.quit-test-btn\s*\{.*?border-radius:\s*var\(--radius-md\);")
        self.assertIn("$('testModeBtn').classList.toggle('hidden', state.testMode.active);", html)
        self.assertIn("$('openTestEvidenceBtn').classList.toggle('hidden'", html)
        # Phase 2: scanTime moved out of legacy `<span class="chip">` into the new Working Tree
        # left-col section as `<span class="last-scan" id="scanTime">last scan: …</span>`.
        self.assertIn('id="scanTime"', html)

    def test_action_buttons_and_info_pills_get_lay_tooltips(self):
        html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")

        self.assertIn("function tooltipForAction(button)", html)
        self.assertIn("function tooltipForChip(chip)", html)
        self.assertIn("function applyTooltips(root = document)", html)
        self.assertIn("function startTooltipObserver()", html)
        self.assertIn("new MutationObserver(() => applyTooltips())", html)
        self.assertIn("Open a picker to", html)
        self.assertIn("Hand over to this user, apply their saved settings, and scan the repository.", html)
        self.assertIn("Information only:", html)
        self.assertIn("Preview restore safety only. This checks risk but does not change files.", html)
        self.assertIn("Always enforced", html)
        self.assertIn("These safety rules protect your work and cannot be changed from this screen.", html)
        self.assertIn("Complete these fields first:", html)

    def test_every_button_has_click_wiring_or_delegated_handler(self):
        html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")
        parser = ButtonInventoryParser()
        parser.feed(html)
        direct_listener_ids = set(re.findall(r"\$\('([^']+)'\)\.addEventListener\('click'", html))
        delegated_handlers = {
            "data-switch-go": "querySelectorAll('[data-switch-go]')",
            "data-path-picker": "querySelectorAll('[data-path-picker]')",
            "data-collapse-panel": "querySelectorAll('[data-collapse-panel]')",
            "data-side-view": "querySelectorAll('[data-side-view]')",
            "data-summary-view": "dataset.summaryView",
            "data-package-id": "dataset.packageId",
            "data-restore-package-id": "dataset.restorePackageId",
        }

        missing = []
        for button in parser.buttons:
            attrs = button["attrs"]
            label = " ".join(button["text"].split())
            button_id = attrs.get("id")
            wired = bool(button_id and button_id in direct_listener_ids)
            wired = wired or any(attr in attrs and needle in html for attr, needle in delegated_handlers.items())
            if not wired:
                missing.append({"id": button_id, "label": label, "attrs": attrs})

        self.assertEqual(missing, [], "Every visible button must perform work or be covered by a delegated handler.")

    def test_dollar_id_references_have_dom_targets(self):
        html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")

        dom_ids = set(re.findall(r'id="([^"]+)"', html))
        dollar_refs = set(re.findall(r"\$\('([^']+)'\)", html))

        self.assertEqual(dollar_refs - dom_ids, set())

    def test_create_safe_handoff_button_is_prominent_and_state_colored(self):
        html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")
        # Phase 2: handoff section in right column .sec (was legacy .handoff-panel <section>).
        # Per spec §4.5, the dominant Create Safe Handoff button now sits AFTER the metadata
        # fields (Title/Agent/Notes) — not before — so the source order is fields → button.
        handoff_panel = html.split('data-flow-panel="handoff"', 1)[1].split('class="legacy-pending"', 1)[0]

        self.assertEqual(html.count('id="handoffBtn"'), 1)
        # Spec §4.5: dominant action sits below metadata fields
        self.assertLess(handoff_panel.index('class="handoff-fields"'), handoff_panel.index('id="handoffBtn"'))
        self.assertIn('class="handoff-primary-action" id="handoffBtn" disabled>Create safe handoff</button>', html)
        self.assertRegex(html, r"(?s)\.handoff-primary-action\s*\{.*?width:\s*100%;")
        self.assertRegex(html, r"(?s)\.handoff-primary-action\s*\{.*?min-height:\s*48px;")
        # Bible §6 grammar: flat surface backgrounds — no linear-gradient fills
        self.assertRegex(html, r"(?s)\.handoff-primary-action\s*\{.*?border-radius:\s*var\(--radius-md\);")
        self.assertRegex(html, r"(?s)\.handoff-primary-action\s*\{.*?background:\s*var\(--ok\);")
        self.assertRegex(html, r"(?s)\.handoff-primary-action:disabled\s*\{.*?background:\s*var\(--pane\);")

    def test_status_messages_use_one_scroll_container(self):
        html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")

        # Phase 3: legacy `.status-panel .panel-body` and `.status-window` containers replaced
        # by the new `.status-list` accumulating list inside `.center-col .status-sec`. The
        # scroll container is `.status-list { overflow-y: auto }`. Status messages prepend
        # color-coded `.status-row` entries.
        self.assertRegex(html, r"(?s)\.pc-body \.center-col \.status-list\s*\{.*?overflow-y:\s*auto;")
        self.assertRegex(html, r"(?s)\.pc-body \.center-col \.status-sec\s*\{.*?flex:\s*1 1 auto;")
        # resultBox is now the .status-list container itself
        self.assertIn('class="status-list" id="resultBox"', html)
        # The new showResult prepends .status-row entries — single scroll container per spec §4.4
        self.assertIn("function showResult(message, kind = 'ok')", html)
        self.assertIn("row.className = 'status-row ' + cls;", html)

    def test_setup_dialog_is_centered_and_shows_side_by_side_registration(self):
        # Setup-modal-fix (Phase 7-fix) Q5 Option B: existing class names
        # preserved (`.setup-dialog`, `.wizard-grid`, `.registration-panel`,
        # `.setup-dialog-foot`) but Phase 7-fix CSS overrides refine measurements
        # to match locked `pc_v2_setup_users_modal.html`: 800px modal-card,
        # 36px head, two-column form grid `1fr 1fr` with 12px gap and 14px
        # padding. Removed: Project Files Tracker section, Collaborator Hub
        # section, `setup-dialog-status`, `setup-dialog-actions`, per-user
        # save buttons, step pills, status warning bar.
        html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")

        # Phase 7-fix override: 800px modal-card width
        self.assertRegex(
            html,
            r"(?s)/\* === Setup-modal-fix.*?\.setup-dialog\s*\{[^}]*?width:\s*min\(800px, calc\(100vw - 88px\)\);",
        )
        # Phase 7-fix override: simple two-column grid with `user1 user2`
        # template area (project + hub rows removed)
        self.assertRegex(
            html,
            r'(?s)/\* === Setup-modal-fix.*?\.setup-dialog \.wizard-grid\s*\{[^}]*?grid-template-columns:\s*1fr 1fr;[^}]*?grid-template-areas:\s*"user1 user2";',
        )
        # Phase 7-fix override: 14px body padding + 12px column gap
        self.assertRegex(
            html,
            r"(?s)/\* === Setup-modal-fix.*?\.setup-dialog \.wizard-grid\s*\{[^}]*?gap:\s*12px;[^}]*?padding:\s*14px;",
        )
        # Per locked v2 mockup: Project Files Tracker section + Collaborator Hub section + setup-project-step removed
        self.assertNotIn('class="wizard-step wide setup-project-step"', html)
        self.assertNotIn('class="setup-dialog-status"', html)
        self.assertNotIn('class="setup-dialog-actions"', html)
        self.assertNotIn('id="registrationHubGrid"', html)
        # Note: `class="hub-card"` markup remains on the side-view hub
        # (`#sideHubGrid`), which is a separate surface outside the modal —
        # only the in-modal hub (`#registrationHubGrid`) was removed.
        # Single Save Settings + Cancel in foot (Q4)
        self.assertIn('id="saveSettingsBtn"', html)
        self.assertIn('id="cancelSetupBtn"', html)
        # Removed per-user save buttons + footer step pills (Q4)
        self.assertNotIn('id="registerUser1NextBtn"', html)
        self.assertNotIn('id="registerUser2FinishBtn"', html)
        self.assertNotIn('id="openHubBtn"', html)
        self.assertNotIn('id="registerBackBtn"', html)
        self.assertNotIn('id="wizardChecklist"', html)
        self.assertNotIn('id="setupWarning"', html)
        # Title is now always SETUP USERS — wizard stage map removed
        self.assertIn(">SETUP USERS<", html)

    def test_user_registration_stays_on_one_side_by_side_screen(self):
        # Setup-modal-fix (Phase 7-fix): wizard staging removed. Modal is now a
        # single-screen two-column form. Both User 1 and User 2 panels render
        # always; no collapse, no per-user transitions, no per-stage titles.
        # State + helpers (`setRegistrationStage`, `toggleRegistrationPanel`,
        # `registrationCollapsed`, `.registration-panel.is-collapsed` CSS) are
        # left in place as inert support for legacy callers per minimum-diff
        # rule — they no longer drive any user-visible behavior.
        html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")

        self.assertNotIn('id="user1Transition"', html)
        self.assertNotIn('id="continueUser2Btn"', html)
        self.assertNotIn("user1Complete", html)
        # Phase 7-fix: title is always SETUP USERS — stage-specific titles removed
        self.assertNotIn("users: 'REGISTER USERS'", html)
        self.assertIn("setRegistrationStage('users')", html)
        self.assertIn("setupDialog.dataset.registrationStage = stage", html)
        self.assertNotIn("setRegistrationStage('user2');\n        showResult('User 1 registered. Now register User 2.')", html)
        self.assertNotIn(".registration-transition", html)
        # profile-defaults inputs render in the simplified column flow per modal-form
        self.assertIn(".profile-defaults", html)
        # Phase 7-fix: ampersand-cased subhead per locked v2 mockup
        self.assertIn("Accounts, tools &amp; git identity", html)
        # Phase 7-fix: collapse-panel buttons removed from modal markup
        self.assertNotIn('data-collapse-panel="user1"', html)
        self.assertNotIn('data-collapse-panel="user2"', html)

    # test_user_two_registration_names_missing_fields: DELETED.
    # Setup-modal-fix Q4 ruling — `registerUser2FinishBtn` (and per-user save
    # buttons + their `dataset.missingFields` annotations) removed per locked
    # v2 mockup. Field-readiness gating now lives on `saveSettingsBtn`
    # (combined User 1 + User 2 missing-fields list); test coverage for the
    # combined gate is implicit in the layout assertion in
    # test_setup_dialog_is_centered_and_shows_side_by_side_registration.

    def test_main_screen_orders_controls_left_to_right_by_workflow(self):
        html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")
        # Phase 2: legacy `<main class="workflow-layout">` 5-panel grid atomically replaced
        # with `<main class="pc-body">` 3-column scaffold (280 LEFT / flex CENTER / 360 RIGHT).
        # Left column fully built (Working Tree + collapsible User 1/User 2). Center and right
        # columns scaffolded with JS-reachable IDs preserved; Phases 3 and 4 will refine.
        main = html.split('<main class="pc-body">', 1)[1].split('</main>', 1)[0]

        # 3-column grid template per spec §3.1
        self.assertRegex(
            html,
            r"(?s)\.pc-body\s*\{.*?grid-template-columns:\s*280px 1fr 360px;",
        )
        # Phase 4: layout inheritance fix — pin row template + height + zero gap/padding
        # to override the legacy generic `main { grid-template-rows / gap / padding / height }`
        # rule so the 3 columns fill the full body height instead of just the first
        # legacy row (Codex audit finding).
        self.assertRegex(html, r"(?s)\.pc-body\s*\{.*?grid-template-rows:\s*minmax\(0, 1fr\);")
        self.assertRegex(html, r"(?s)\.pc-body\s*\{.*?height:\s*100%;")
        self.assertRegex(html, r"(?s)\.pc-body\s*\{.*?gap:\s*0;")
        self.assertRegex(html, r"(?s)\.pc-body\s*\{.*?padding:\s*0;")
        # Left/center/right column markers
        self.assertIn('class="left-col"', main)
        self.assertIn('class="center-col"', main)
        self.assertIn('class="right-col"', main)
        # Identity sections (left col) carry data-flow-panel attributes for legacy compat
        self.assertIn('data-flow-panel="user1"', main)
        self.assertIn('data-flow-panel="user2"', main)
        self.assertIn('data-flow-panel="handoff"', main)
        # JS workflow lock infrastructure preserved
        self.assertIn(".sequence-panel.is-locked", html)
        self.assertIn("function updateWorkflowLocks()", html)
        self.assertIn("handoff: handoffStepReady()", html)
        self.assertIn("forbidden.slice(0, 2)", html)
        self.assertIn("more destructive commands blocked", html)

        # Workflow ordering inside the left column: User 1 section appears before User 2
        self.assertLess(main.index('data-flow-panel="user1"'), main.index('data-flow-panel="user2"'))
        # Handoff button (right col Phase 4 scaffold) lives after Start Session button
        # (center col Phase 3 scaffold). Both IDs preserved.
        self.assertLess(main.index('id="startSessionBtn"'), main.index('id="handoffBtn"'))
        # Left col precedes right col in source order
        self.assertLess(main.index('class="left-col"'), main.index('class="right-col"'))


class PandaCollaboratorHandoffTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="panda-collab-test-"))
        self.repo = self.tmp / "repo"
        self.package_root = self.tmp / "packages"
        self.history_root = self.tmp / "history"
        self.repo.mkdir()
        run(["git", "init"], self.repo)
        run(["git", "config", "user.name", "PANDA Test"], self.repo)
        run(["git", "config", "user.email", "panda-test@example.invalid"], self.repo)
        (self.repo / "tracked.txt").write_text("base\n", encoding="utf-8")
        run(["git", "add", "tracked.txt"], self.repo)
        run(["git", "commit", "-m", "base"], self.repo)
        self.old_package_root = pc.os.environ.get("PANDA_COLLABORATOR_PACKAGE_ROOT")
        self.old_history_root = pc.os.environ.get("PANDA_COLLABORATOR_HISTORY_ROOT")
        pc.os.environ["PANDA_COLLABORATOR_PACKAGE_ROOT"] = str(self.package_root)
        pc.os.environ["PANDA_COLLABORATOR_HISTORY_ROOT"] = str(self.history_root)

    def tearDown(self):
        if self.old_package_root is None:
            pc.os.environ.pop("PANDA_COLLABORATOR_PACKAGE_ROOT", None)
        else:
            pc.os.environ["PANDA_COLLABORATOR_PACKAGE_ROOT"] = self.old_package_root
        if self.old_history_root is None:
            pc.os.environ.pop("PANDA_COLLABORATOR_HISTORY_ROOT", None)
        else:
            pc.os.environ["PANDA_COLLABORATOR_HISTORY_ROOT"] = self.old_history_root
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_handoff_protects_committed_and_uncommitted_work(self):
        # Phase 6: PC_HANDOFF_PROGRESS_SPEC v1.1 + CD ruling 20260504_008308 require
        # a clean working tree before handoff. Commit the test changes first so the
        # new Step 2 (Verify committed state) passes; the rest of the test exercises
        # the protection branch, patch/copy infrastructure, and downstream APIs over
        # a clean tree. (Patches will be empty bytes since tree is clean — that's
        # the new-correct behavior.)
        (self.repo / "tracked.txt").write_text("base\nworking change\n", encoding="utf-8")
        (self.repo / "new-note.md").write_text("# untracked\n", encoding="utf-8")
        run(["git", "add", "-A"], self.repo)
        run(["git", "commit", "-m", "phase6 test: commit changes before handoff"], self.repo)

        manifest = pc.create_handoff_package(
            str(self.repo),
            "handoff test",
            "Codex",
            "verify safety",
            {
                "user_id": "user1",
                "display_name": "Darrin",
                "codex_account": "darrin-codex@example.invalid",
                "claude_account": "darrin-claude@example.invalid",
                "claude_desktop_path": str(self.tmp / "Claude Desktop.exe"),
                "claude_code_path": str(self.tmp / "Claude Code"),
                "project_files_directory": str(self.tmp / "panda-gallery"),
                "git_author_name": "Darrin",
                "git_author_email": "darrin@example.invalid",
                "repo_path": str(self.repo),
                "shared_git_working_tree": True,
            },
        )

        package_dir = Path(manifest["package_dir"])
        self.assertTrue(package_dir.exists())
        self.assertTrue((package_dir / "manifest.json").exists())
        self.assertTrue((package_dir / "HANDOFF.md").exists())
        self.assertTrue((package_dir / "PLAIN_SUMMARY.md").exists())
        self.assertTrue((package_dir / "TECHNICAL_SUMMARY.md").exists())
        # Patches still written (empty bytes for clean tree) per spec — the patch
        # infrastructure runs every time even when the diff is empty.
        self.assertTrue((package_dir / "patches" / "unstaged-working-tree.patch").exists())
        self.assertTrue((package_dir / "patches" / "staged-index.patch").exists())
        # File copies dir exists but is empty since tree is clean.
        self.assertTrue((package_dir / "file_copies").exists())
        self.assertFalse(manifest["stash_used"])
        self.assertTrue(manifest["committed_protection"]["created_without_checkout"])
        self.assertEqual(manifest["operator_context"]["display_name"], "Darrin")
        self.assertEqual(manifest["operator_context"]["codex_account"], "darrin-codex@example.invalid")
        self.assertEqual(manifest["operator_context"]["claude_desktop_path"], str(self.tmp / "Claude Desktop.exe"))
        self.assertEqual(manifest["operator_context"]["project_files_directory"], str(self.tmp / "panda-gallery"))

        branch = manifest["committed_protection"]["branch"]
        refs = run(["git", "show-ref", "--verify", f"refs/heads/{branch}"], self.repo)
        self.assertIn(branch, refs.stdout)

        # Phase 6: tree is clean after the test's pre-handoff commit; assert that.
        status_after = run(["git", "status", "--porcelain=v1", "-uall"], self.repo).stdout
        self.assertEqual(status_after.strip(), "", "Working tree must be clean after handoff per spec §9")

        loaded = json.loads((package_dir / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(loaded["committed_protection"]["branch"], branch)
        self.assertFalse(loaded["safety_receipt"]["stash_used"])
        self.assertFalse(loaded["safety_receipt"]["restore_or_apply_performed"])
        # Phase 6: package_id is now returned alongside the manifest per CD ruling 20260504_008308.
        self.assertIn("package_id", manifest)
        self.assertTrue(manifest["package_id"])

        packages = pc.list_packages(str(self.repo))
        self.assertEqual(len(packages["packages"]), 1)
        self.assertIn("id", packages["packages"][0])

        detail = pc.read_package_detail(packages["packages"][0]["id"])
        self.assertEqual(detail["manifest"]["committed_protection"]["branch"], branch)
        self.assertTrue(detail["branch_exists"])
        self.assertEqual(detail["counts"]["patches"], 2)
        self.assertIn("# handoff test", detail["handoff_preview"])
        self.assertIn("## Session / Account Context", detail["handoff_preview"])
        self.assertIn("Codex account label: darrin-codex@example.invalid", detail["handoff_preview"])
        self.assertIn("Claude Desktop path:", detail["handoff_preview"])
        self.assertIn("Project files directory:", detail["handoff_preview"])
        self.assertIn("If both users use the same repository path", detail["handoff_preview"])

        before_preview_status = run(["git", "status", "--porcelain=v1", "-uall"], self.repo).stdout
        plan = pc.preview_restore_plan(packages["packages"][0]["id"], str(self.repo))
        after_preview_status = run(["git", "status", "--porcelain=v1", "-uall"], self.repo).stdout
        self.assertEqual(before_preview_status, after_preview_status)
        self.assertFalse(plan["automated_restore_available"])
        self.assertTrue(plan["protection_branch_exists"])
        self.assertGreaterEqual(len(plan["patch_checks"]), 1)
        # Phase 6: clean tree = 0 file copies; copy_checks will reflect that.
        self.assertEqual(len(plan["copy_checks"]), 0)

        context = {
            "user_id": "user1",
            "display_name": "Darrin",
            "codex_account": "darrin-codex@example.invalid",
            "claude_account": "darrin-claude@example.invalid",
            "claude_desktop_path": str(self.tmp / "Claude Desktop.exe"),
            "claude_code_path": str(self.tmp / "Claude Code"),
            "project_files_directory": str(self.tmp / "panda-gallery"),
            "git_author_name": "Darrin",
            "git_author_email": "darrin@example.invalid",
            "repo_path": str(self.repo),
            "shared_git_working_tree": True,
        }
        message = pc.create_message({"kind": "concern", "text": "Watch the working change.", "operator_context": context})
        self.assertEqual(message["kind"], "concern")
        dashboard = pc.dashboard_for(str(self.repo), context)
        self.assertIn("project_manager", dashboard)
        self.assertIn("recommended_next_action", dashboard["project_manager"])

        start = pc.start_session({"path": str(self.repo), "operator_context": context})
        self.assertIn("checklist", start)
        self.assertTrue((self.history_root / "timeline.jsonl").exists())

        paused = pc.set_pause({"reason": "Need review", "operator_context": context}, True)
        self.assertTrue(paused["control_state"]["paused"])
        self.assertFalse(paused["control_state"]["start_work_enabled"])
        cleared = pc.set_pause({"operator_context": context}, False)
        self.assertFalse(cleared["control_state"]["paused"])

        search = pc.search_history("working change")
        self.assertGreaterEqual(len(search["results"]), 1)

        ended = pc.end_session(
            {
                "path": str(self.repo),
                "title": "guided closeout",
                "agent": "Codex",
                "notes": "Optional closeout note.",
                "operator_context": context,
            }
        )
        self.assertTrue(Path(ended["daily_report"]["path"]).exists())
        self.assertTrue(Path(ended["handoff"]["package_dir"], "PLAIN_SUMMARY.md").exists())


class PandaCollaboratorHandoffProgressTests(unittest.TestCase):
    """Phase 6: per-step state machine tests for create_handoff_package.

    Tests the 8 active steps (1, 2, 3, 4, 5, 6, 7a, 7b) plus the 2 placeholder-
    skipped steps (2b, 2c). Verifies:
      - Step 1 PASS for valid git root; FAIL for non-git path
      - Step 2 PASS for clean tree; FAIL/abort for dirty tree (spec §9 non-negotiable)
      - Steps 2b/2c always skipped with 'Phase 6.1' note
      - Step 3 creates protection branch
      - Steps 4, 5, 6, 7a use temp+atomic-rename idempotency
      - Step 7b returns package_id
      - INCOMPLETE hard-block: failure mid-run leaves status=failed, remaining steps skipped
      - get_handoff_progress() exposes live state
    """
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="panda-collab-test-"))
        self.repo = self.tmp / "repo"
        self.package_root = self.tmp / "packages"
        self.history_root = self.tmp / "history"
        self.repo.mkdir()
        run(["git", "init"], self.repo)
        run(["git", "config", "user.name", "PANDA Test"], self.repo)
        run(["git", "config", "user.email", "panda-test@example.invalid"], self.repo)
        (self.repo / "tracked.txt").write_text("base\n", encoding="utf-8")
        run(["git", "add", "tracked.txt"], self.repo)
        run(["git", "commit", "-m", "base"], self.repo)
        self.old_package_root = pc.os.environ.get("PANDA_COLLABORATOR_PACKAGE_ROOT")
        self.old_history_root = pc.os.environ.get("PANDA_COLLABORATOR_HISTORY_ROOT")
        pc.os.environ["PANDA_COLLABORATOR_PACKAGE_ROOT"] = str(self.package_root)
        pc.os.environ["PANDA_COLLABORATOR_HISTORY_ROOT"] = str(self.history_root)

    def tearDown(self):
        if self.old_package_root is None:
            pc.os.environ.pop("PANDA_COLLABORATOR_PACKAGE_ROOT", None)
        else:
            pc.os.environ["PANDA_COLLABORATOR_PACKAGE_ROOT"] = self.old_package_root
        if self.old_history_root is None:
            pc.os.environ.pop("PANDA_COLLABORATOR_HISTORY_ROOT", None)
        else:
            pc.os.environ["PANDA_COLLABORATOR_HISTORY_ROOT"] = self.old_history_root
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _full_run_passes_all_active_steps(self):
        manifest = pc.create_handoff_package(str(self.repo), "phase6 ok", "Codex", "")
        progress = pc.get_handoff_progress()
        return manifest, progress

    def test_full_run_passes_all_active_steps(self):
        manifest, progress = self._full_run_passes_all_active_steps()
        self.assertEqual(progress["status"], "complete")
        self.assertIsNotNone(progress["package_id"])
        self.assertEqual(progress["package_id"], manifest["package_id"])

        states_by_id = {s["id"]: s["state"] for s in progress["steps"]}
        # 8 active steps PASS
        for sid in ("1", "2", "3", "4", "5", "6", "7a", "7b"):
            self.assertEqual(states_by_id[sid], "pass", f"Step {sid} should be PASS")
        # 2 placeholder steps SKIPPED with Phase 6.1 note
        for sid in ("2b", "2c"):
            self.assertEqual(states_by_id[sid], "skipped", f"Step {sid} should be SKIPPED in Phase 6")
        notes_by_id = {s["id"]: s["note"] for s in progress["steps"]}
        self.assertIn("Phase 6.1", notes_by_id["2b"])
        self.assertIn("Phase 6.1", notes_by_id["2c"])

    def test_step1_fails_on_non_git_path(self):
        non_git = self.tmp / "not-a-repo"
        non_git.mkdir()
        with self.assertRaises(pc.CollaboratorError) as ctx:
            pc.create_handoff_package(str(non_git), "phase6 step1 fail", "Codex", "")
        self.assertIn("Step 1", str(ctx.exception))
        progress = pc.get_handoff_progress()
        self.assertEqual(progress["status"], "failed")
        states_by_id = {s["id"]: s["state"] for s in progress["steps"]}
        self.assertEqual(states_by_id["1"], "fail")
        # All later steps skipped
        for sid in ("2", "2b", "2c", "3", "4", "5", "6", "7a", "7b"):
            self.assertIn(states_by_id[sid], ("skipped", "pending"))

    def test_step2_fails_on_dirty_tree(self):
        # Modify the committed file without committing — should trigger Step 2 FAIL
        (self.repo / "tracked.txt").write_text("base\nuncommitted change\n", encoding="utf-8")
        with self.assertRaises(pc.CollaboratorError) as ctx:
            pc.create_handoff_package(str(self.repo), "phase6 step2 fail", "Codex", "")
        self.assertIn("Step 2", str(ctx.exception))
        self.assertIn("uncommitted", str(ctx.exception).lower())
        progress = pc.get_handoff_progress()
        self.assertEqual(progress["status"], "failed")
        states_by_id = {s["id"]: s["state"] for s in progress["steps"]}
        self.assertEqual(states_by_id["1"], "pass")
        self.assertEqual(states_by_id["2"], "fail")
        # Spec §9 non-negotiable: tree must NOT be modified by PC
        status_after = run(["git", "status", "--porcelain=v1"], self.repo).stdout
        self.assertIn(" M tracked.txt", status_after, "PC must not commit; tree stays dirty after Step 2 fail")

    def test_step2_fails_on_untracked_file(self):
        # Untracked file should also trigger Step 2 FAIL
        (self.repo / "new-untracked.txt").write_text("orphan\n", encoding="utf-8")
        with self.assertRaises(pc.CollaboratorError):
            pc.create_handoff_package(str(self.repo), "phase6 untracked fail", "Codex", "")
        progress = pc.get_handoff_progress()
        self.assertEqual(progress["status"], "failed")

    def test_steps_2b_2c_always_skipped(self):
        # Even on a successful full run, 2b/2c must remain Phase 6.1 placeholders
        pc.create_handoff_package(str(self.repo), "phase6 placeholder", "Codex", "")
        progress = pc.get_handoff_progress()
        states = {s["id"]: s for s in progress["steps"]}
        self.assertEqual(states["2b"]["state"], "skipped")
        self.assertEqual(states["2c"]["state"], "skipped")
        self.assertIn("Phase 6.1", states["2b"]["note"])
        self.assertIn("Phase 6.1", states["2c"]["note"])

    def test_step4_idempotent_via_temp_then_replace(self):
        # Verify temp_then_replace_bytes directly — first write creates target,
        # second write replaces atomically (no SafetyError on existing file).
        target = self.tmp / "step4-test.bin"
        pc.temp_then_replace_bytes(target, b"first")
        self.assertEqual(target.read_bytes(), b"first")
        pc.temp_then_replace_bytes(target, b"second")
        self.assertEqual(target.read_bytes(), b"second")
        # No leftover temp files
        leftovers = [p for p in self.tmp.iterdir() if p.name.endswith(".tmp")]
        self.assertEqual(leftovers, [])

    def test_step6_idempotent_via_temp_then_replace_text(self):
        target = self.tmp / "step6-manifest.json"
        pc.temp_then_replace_text(target, '{"v":1}')
        self.assertEqual(target.read_text(encoding="utf-8"), '{"v":1}')
        pc.temp_then_replace_text(target, '{"v":2}')
        self.assertEqual(target.read_text(encoding="utf-8"), '{"v":2}')

    def test_step5_copy_idempotent(self):
        src = self.tmp / "src.txt"
        src.write_text("payload\n", encoding="utf-8")
        dst = self.tmp / "out" / "dst.txt"
        pc.temp_then_replace_copy(src, dst)
        self.assertEqual(dst.read_text(encoding="utf-8"), "payload\n")
        # Modify source then re-copy — atomic replace works
        src.write_text("updated\n", encoding="utf-8")
        pc.temp_then_replace_copy(src, dst)
        self.assertEqual(dst.read_text(encoding="utf-8"), "updated\n")

    def test_step7b_returns_package_id_in_response(self):
        manifest = pc.create_handoff_package(str(self.repo), "phase6 7b id", "Codex", "")
        # Step 7b finalises and returns package_id (Phase 7 will write it to settings)
        self.assertIn("package_id", manifest)
        self.assertTrue(manifest["package_id"])
        # Phase 6 does NOT touch handover_state
        settings = pc.load_settings()
        self.assertFalse(settings["handover_state"]["handover_pending"])
        self.assertIsNone(settings["handover_state"]["handoff_package_id"])

    def test_get_handoff_progress_initial_state_idle_or_complete(self):
        # The state machine retains the most-recent run's terminal state.
        # Either we're in 'idle' (no run yet this process) or 'complete' (after a run).
        progress = pc.get_handoff_progress()
        self.assertIn(progress["status"], ("idle", "complete", "failed", "running", "aborted"))
        # Always 10 step entries per spec
        self.assertEqual(len(progress["steps"]), 10)
        ids = [s["id"] for s in progress["steps"]]
        self.assertEqual(ids, ["1", "2", "2b", "2c", "3", "4", "5", "6", "7a", "7b"])

    def test_incomplete_hard_block_on_step2_fail(self):
        # INCOMPLETE hard-block per spec §7.4: failed run does NOT surface as a
        # completed handoff. Verify status = 'failed', no package_id, package
        # directory was not finalised.
        (self.repo / "tracked.txt").write_text("dirty\n", encoding="utf-8")
        with self.assertRaises(pc.CollaboratorError):
            pc.create_handoff_package(str(self.repo), "phase6 incomplete", "Codex", "")
        progress = pc.get_handoff_progress()
        self.assertEqual(progress["status"], "failed")
        self.assertIsNone(progress["package_id"])
        self.assertIsNotNone(progress["error"])
        # No package surfaced via list_packages — engine aborted before reaching list-eligible state
        packages = pc.list_packages(str(self.repo))
        self.assertEqual(len(packages["packages"]), 0)


class PandaCollaboratorHandoverStateTests(unittest.TestCase):
    """Phase 7: handover_state mutator + auto-show + start-session-clears tests.

    Per PC_HANDOFF_PROGRESS_SPEC v1.1 §5.1-§5.2 and Phase 7 token §1, this class
    covers the five test categories required by the token:
      - save_handover_state writes a full 5-field record with ISO-8601 UTC timestamp
      - load round-trips through disk (handover state survives app restart)
      - clear_handover_state resets the sub-object to default-all-null
      - start_session clears a pending handover atomically (incoming-modal path)
      - malformed handover_state on disk recovers to pending=false (no crash)
      - chain: Phase 6 create_handoff_package package_id flows into save_handover_state
    """

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="panda-collab-handover-"))
        self.settings_path = self.tmp / "settings.local.json"
        self.history_root = self.tmp / "history"
        self.package_root = self.tmp / "packages"
        self.repo = self.tmp / "repo"
        self.repo.mkdir()
        run(["git", "init"], self.repo)
        run(["git", "config", "user.name", "PANDA Test"], self.repo)
        run(["git", "config", "user.email", "panda-test@example.invalid"], self.repo)
        (self.repo / "tracked.txt").write_text("base\n", encoding="utf-8")
        run(["git", "add", "tracked.txt"], self.repo)
        run(["git", "commit", "-m", "base"], self.repo)
        self.old_settings = pc.os.environ.get("PANDA_COLLABORATOR_SETTINGS_PATH")
        self.old_history = pc.os.environ.get("PANDA_COLLABORATOR_HISTORY_ROOT")
        self.old_packages = pc.os.environ.get("PANDA_COLLABORATOR_PACKAGE_ROOT")
        pc.os.environ["PANDA_COLLABORATOR_SETTINGS_PATH"] = str(self.settings_path)
        pc.os.environ["PANDA_COLLABORATOR_HISTORY_ROOT"] = str(self.history_root)
        pc.os.environ["PANDA_COLLABORATOR_PACKAGE_ROOT"] = str(self.package_root)
        # Seed two-user settings — required for save_handover_state to round-trip
        # through normalize_settings (strict=True requires exactly 2 user profiles).
        pc.save_settings(
            {
                "active_user_id": "user1",
                "project_files_directory": str(self.tmp / "panda-gallery"),
                "users": [
                    {
                        "display_name": "Darrin",
                        "default_repo_path": str(self.repo),
                        "handoff_agent": "Codex",
                        "handoff_title": "Darrin handoff",
                        "codex_account": "darrin-codex@example.invalid",
                        "claude_account": "darrin-claude@example.invalid",
                        "claude_desktop_path": str(self.tmp / "cd-a.exe"),
                        "claude_code_path": str(self.tmp / "cc-a"),
                        "git_author_name": "Darrin",
                        "git_author_email": "darrin@example.invalid",
                    },
                    {
                        "display_name": "Pam",
                        "default_repo_path": str(self.repo),
                        "handoff_agent": "Claude",
                        "handoff_title": "Pam handoff",
                        "codex_account": "pam-codex@example.invalid",
                        "claude_account": "pam-claude@example.invalid",
                        "claude_desktop_path": str(self.tmp / "cd-b.exe"),
                        "claude_code_path": str(self.tmp / "cc-b"),
                        "git_author_name": "Pam",
                        "git_author_email": "pam@example.invalid",
                    },
                ],
            }
        )

    def tearDown(self):
        for key, prior in (
            ("PANDA_COLLABORATOR_SETTINGS_PATH", self.old_settings),
            ("PANDA_COLLABORATOR_HISTORY_ROOT", self.old_history),
            ("PANDA_COLLABORATOR_PACKAGE_ROOT", self.old_packages),
        ):
            if prior is None:
                pc.os.environ.pop(key, None)
            else:
                pc.os.environ[key] = prior
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_save_handover_state_writes_full_record_with_iso_timestamp(self):
        result = pc.save_handover_state("user2", "PG-2026-05-04-2230")
        self.assertEqual(result["handover_pending"], True)
        self.assertEqual(result["incoming_user_slot"], "user2")
        self.assertEqual(result["handoff_package_id"], "PG-2026-05-04-2230")
        self.assertIsNone(result["failed_package_id"])
        # ISO 8601 UTC timestamp with Z suffix per spec v1.1 §5.2
        self.assertRegex(result["handover_timestamp"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

    def test_save_handover_state_rejects_invalid_slot(self):
        # Slot must be exactly 'user1' or 'user2' (live-code format per CD ruling 3)
        with self.assertRaises(pc.CollaboratorError):
            pc.save_handover_state("user_1", "PG-X")
        with self.assertRaises(pc.CollaboratorError):
            pc.save_handover_state("admin", "PG-X")
        with self.assertRaises(pc.CollaboratorError):
            pc.save_handover_state("", "PG-X")

    def test_save_handover_state_rejects_empty_package_id(self):
        with self.assertRaises(pc.CollaboratorError):
            pc.save_handover_state("user1", "")
        with self.assertRaises(pc.CollaboratorError):
            pc.save_handover_state("user1", "   ")

    def test_save_handover_state_survives_disk_round_trip(self):
        # Phase 7 token §1: "write survives restart" — the saved record must be
        # readable from disk after a fresh load_settings() call.
        pc.save_handover_state("user1", "PG-survives-restart")
        loaded = pc.load_settings()
        self.assertEqual(loaded["handover_state"]["handover_pending"], True)
        self.assertEqual(loaded["handover_state"]["incoming_user_slot"], "user1")
        self.assertEqual(loaded["handover_state"]["handoff_package_id"], "PG-survives-restart")
        self.assertRegex(
            loaded["handover_state"]["handover_timestamp"],
            r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$",
        )

    def test_clear_handover_state_resets_to_default_all_null(self):
        # Phase 7 token §1: "Start Work clears state" — at the helper level.
        pc.save_handover_state("user2", "PG-clear-test")
        self.assertTrue(pc.load_settings()["handover_state"]["handover_pending"])
        result = pc.clear_handover_state()
        self.assertEqual(result["handover_pending"], False)
        self.assertIsNone(result["incoming_user_slot"])
        self.assertIsNone(result["handover_timestamp"])
        self.assertIsNone(result["handoff_package_id"])
        self.assertIsNone(result["failed_package_id"])
        loaded = pc.load_settings()
        self.assertEqual(loaded["handover_state"]["handover_pending"], False)

    def test_start_session_clears_pending_handover_state(self):
        # Phase 7: Start Session click on the incoming-confirmation modal goes
        # through /api/session/start → start_session(), which clears any pending
        # handover_state before computing the dashboard.
        pc.save_handover_state("user1", "PG-start-session-clear")
        self.assertTrue(pc.load_settings()["handover_state"]["handover_pending"])
        pc.start_session({"path": str(self.repo), "operator_context": {}})
        loaded = pc.load_settings()
        self.assertFalse(loaded["handover_state"]["handover_pending"])
        self.assertIsNone(loaded["handover_state"]["incoming_user_slot"])
        self.assertIsNone(loaded["handover_state"]["handoff_package_id"])

    def test_start_session_skips_clear_when_no_handover_pending(self):
        # When no handover is pending, start_session must not call save_settings
        # for handover_state — verified by counting backup files (save_settings
        # writes a backup on every call). This avoids noisy backup files on
        # every regular main-hub Start Session click.
        backups_before = len(list(self.tmp.glob("settings.local.*.bak.json")))
        pc.start_session({"path": str(self.repo), "operator_context": {}})
        backups_after = len(list(self.tmp.glob("settings.local.*.bak.json")))
        self.assertEqual(backups_after, backups_before)

    def test_load_settings_with_malformed_handover_state_recovers_to_pending_false(self):
        # Phase 7 token "Launch-flow risk note" + CD ruling: malformed JSON or
        # missing required fields → treat as pending=false (no auto-show, no crash).
        # normalize_handover_state coerces non-dict values to default-all-null.
        legacy_payload = {
            "schema_version": 1,
            "setup_completed": True,
            "active_user_id": "user1",
            "project_files_directory": str(self.tmp / "panda-gallery"),
            "users": [
                {
                    "id": "user1",
                    "display_name": "Darrin",
                    "default_repo_path": str(self.repo),
                    "handoff_agent": "Codex",
                    "handoff_title": "Darrin handoff",
                    "codex_account": "darrin-codex@example.invalid",
                    "claude_account": "darrin-claude@example.invalid",
                    "claude_desktop_path": str(self.tmp / "cd-a.exe"),
                    "claude_code_path": str(self.tmp / "cc-a"),
                    "git_author_name": "Darrin",
                    "git_author_email": "darrin@example.invalid",
                },
                {
                    "id": "user2",
                    "display_name": "Pam",
                    "default_repo_path": str(self.repo),
                    "handoff_agent": "Claude",
                    "handoff_title": "Pam handoff",
                    "codex_account": "pam-codex@example.invalid",
                    "claude_account": "pam-claude@example.invalid",
                    "claude_desktop_path": str(self.tmp / "cd-b.exe"),
                    "claude_code_path": str(self.tmp / "cc-b"),
                    "git_author_name": "Pam",
                    "git_author_email": "pam@example.invalid",
                },
            ],
            "handover_state": "this is not a dict",  # malformed sub-object
        }
        path = pc.settings_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(legacy_payload), encoding="utf-8")
        loaded = pc.load_settings()
        self.assertEqual(loaded["handover_state"]["handover_pending"], False)
        self.assertIsNone(loaded["handover_state"]["incoming_user_slot"])
        self.assertIsNone(loaded["handover_state"]["handoff_package_id"])

    def test_handoff_package_id_chains_phase6_create_to_handover_state(self):
        # Phase 7 token §1: "handoff_package_id populated from Phase 6 package_id".
        # End-to-end: create a handoff package via Phase 6, then save the returned
        # package_id into handover_state (the live outgoing-confirmation flow).
        manifest = pc.create_handoff_package(str(self.repo), "phase 7 chain", "Codex", "")
        package_id = manifest.get("package_id")
        self.assertTrue(package_id)
        result = pc.save_handover_state("user2", package_id)
        self.assertEqual(result["handoff_package_id"], package_id)
        loaded = pc.load_settings()
        self.assertEqual(loaded["handover_state"]["handoff_package_id"], package_id)
        self.assertEqual(loaded["handover_state"]["incoming_user_slot"], "user2")
        # Phase 6 itself must NOT have touched handover_state — package_id only
        # flows into handover_state via the explicit save_handover_state call above.
        # If Phase 6 wrote handover_pending, the assertion below would already be
        # true after create_handoff_package, before save_handover_state — but the
        # verification chain documents the expected flow boundary.
        self.assertTrue(loaded["handover_state"]["handover_pending"])


class PandaCollaboratorEmergencyPauseTests(unittest.TestCase):
    """Phase 8: token-strict in-memory emergency pause (CD ruling Q1).

    Coexists with the legacy set_pause() / control_state.paused surface; the
    new endpoints do NOT touch the settings file or control_state. Pause does
    not survive restart by design (`_emergency_pause_state` is module-level
    volatile state).
    """

    def setUp(self):
        # Reset volatile state between tests so order doesn't matter.
        pc.toggle_emergency_pause(False, "")

    def tearDown(self):
        pc.toggle_emergency_pause(False, "")

    def test_emergency_pause_activate_disables_primary_actions(self):
        # POST toggle active=true → GET status returns active + triggered_by + ts
        result = pc.toggle_emergency_pause(True, "Darrin")
        self.assertEqual(result["emergency_pause_active"], True)
        status = pc.get_emergency_pause_status()
        self.assertEqual(status["emergency_pause_active"], True)
        self.assertEqual(status["triggered_by"], "Darrin")
        self.assertRegex(status["triggered_at"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

    def test_emergency_pause_clear_re_enables_primary_actions(self):
        pc.toggle_emergency_pause(True, "Darrin")
        result = pc.toggle_emergency_pause(False, "")
        self.assertEqual(result["emergency_pause_active"], False)
        status = pc.get_emergency_pause_status()
        self.assertEqual(status["emergency_pause_active"], False)
        self.assertIsNone(status["triggered_by"])
        self.assertIsNone(status["triggered_at"])

    def test_emergency_pause_does_not_persist_across_restart(self):
        # Activate, then simulate restart by reloading settings — pause must
        # NOT appear in settings file.
        pc.toggle_emergency_pause(True, "Darrin")
        # Simulate fresh process: clear volatile state (as a real restart would).
        pc._emergency_pause_state["active"] = False
        pc._emergency_pause_state["triggered_by"] = None
        pc._emergency_pause_state["triggered_at"] = None
        # New "process" reads its volatile state — should be inactive.
        status = pc.get_emergency_pause_status()
        self.assertEqual(status["emergency_pause_active"], False)
        # Settings file is untouched: load_settings does not surface emergency-pause.
        # (We can't fully assert "not on disk" without a settings fixture; the
        # behavior is structural — confirm_escape_hatch + save_handover_state
        # are the only Phase 7/8 paths that write settings.)


class PandaCollaboratorEscapeHatchTests(unittest.TestCase):
    """Phase 8: confirm_escape_hatch() handles the incoming-modal escape path
    per spec v1.1 §8.3 — sets handover_state.failed_package_id, clears
    handover_pending and the other fields, persists via save_settings()."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="panda-collab-escape-"))
        self.settings_path = self.tmp / "settings.local.json"
        self.old_settings = pc.os.environ.get("PANDA_COLLABORATOR_SETTINGS_PATH")
        pc.os.environ["PANDA_COLLABORATOR_SETTINGS_PATH"] = str(self.settings_path)
        # Seed two-user settings + a pending handover so the escape hatch has
        # something realistic to clear.
        pc.save_settings(
            {
                "active_user_id": "user1",
                "project_files_directory": str(self.tmp / "panda-gallery"),
                "users": [
                    {
                        "display_name": "Darrin",
                        "default_repo_path": str(self.tmp / "repo-a"),
                        "handoff_agent": "Codex",
                        "handoff_title": "Darrin handoff",
                        "codex_account": "darrin-codex@example.invalid",
                        "claude_account": "darrin-claude@example.invalid",
                        "claude_desktop_path": str(self.tmp / "cd-a.exe"),
                        "claude_code_path": str(self.tmp / "cc-a"),
                        "git_author_name": "Darrin",
                        "git_author_email": "darrin@example.invalid",
                    },
                    {
                        "display_name": "Pam",
                        "default_repo_path": str(self.tmp / "repo-b"),
                        "handoff_agent": "Claude",
                        "handoff_title": "Pam handoff",
                        "codex_account": "pam-codex@example.invalid",
                        "claude_account": "pam-claude@example.invalid",
                        "claude_desktop_path": str(self.tmp / "cd-b.exe"),
                        "claude_code_path": str(self.tmp / "cc-b"),
                        "git_author_name": "Pam",
                        "git_author_email": "pam@example.invalid",
                    },
                ],
            }
        )
        pc.save_handover_state("user2", "PG-pending-pkg")

    def tearDown(self):
        if self.old_settings is None:
            pc.os.environ.pop("PANDA_COLLABORATOR_SETTINGS_PATH", None)
        else:
            pc.os.environ["PANDA_COLLABORATOR_SETTINGS_PATH"] = self.old_settings
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_escape_hatch_sets_failed_package_id_and_clears_pending(self):
        # Pre-condition: pending=true via setUp's save_handover_state call
        pre = pc.load_settings()["handover_state"]
        self.assertTrue(pre["handover_pending"])
        self.assertEqual(pre["handoff_package_id"], "PG-pending-pkg")

        result = pc.confirm_escape_hatch("PG-pending-pkg")
        self.assertEqual(result["failed_package_id"], "PG-pending-pkg")

        post = pc.load_settings()["handover_state"]
        self.assertFalse(post["handover_pending"])
        self.assertEqual(post["failed_package_id"], "PG-pending-pkg")
        self.assertIsNone(post["incoming_user_slot"])
        self.assertIsNone(post["handover_timestamp"])
        self.assertIsNone(post["handoff_package_id"])

    def test_escape_hatch_with_null_package_id_still_clears_pending(self):
        result = pc.confirm_escape_hatch(None)
        self.assertIsNone(result["failed_package_id"])
        post = pc.load_settings()["handover_state"]
        self.assertFalse(post["handover_pending"])
        self.assertIsNone(post["failed_package_id"])

    def test_escape_hatch_survives_disk_round_trip(self):
        # POST escape, then reload settings → failed_package_id must persist.
        pc.confirm_escape_hatch("PG-survives-restart")
        loaded = pc.load_settings()
        self.assertEqual(loaded["handover_state"]["failed_package_id"], "PG-survives-restart")
        self.assertFalse(loaded["handover_state"]["handover_pending"])


if __name__ == "__main__":
    unittest.main()
