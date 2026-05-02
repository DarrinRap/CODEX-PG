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
        self.assertIn("Start-Process $Url", script)
        self.assertLess(script.index("if ($IsRunning)"), script.index("if ($NoBrowser)"))
        self.assertLess(script.index("if ($NoBrowser)"), script.index("Start-Process $Url"))

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

        self.assertNotIn('class="panda-step-guide"', html)
        self.assertNotIn('id="pandaStepGuide"', html)
        self.assertIn("function pandaStepGuideState()", html)
        self.assertIn("function renderPandaStepGuide()", html)
        self.assertIn("Register User 1", html)
        self.assertIn("Register User 2", html)
        self.assertIn("Collaborator Hub", html)
        self.assertIn("Start Session", html)
        self.assertIn("Create Handoff", html)
        self.assertIn('class="sequence-arrow" aria-hidden="true">&gt;</span>', html)
        self.assertIn(".sequence-panel.is-current .panel-head", html)
        self.assertIn(".sequence-panel.is-ready .panel-head", html)
        self.assertIn(".sequence-panel.is-pending .panel-head", html)
        self.assertIn("panel.dataset.flowState", html)

    def test_setup_checklist_reveals_steps_progressively(self):
        html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")

        self.assertRegex(html, r"\['user1Ready', 'Register User 1', user1Ready, true\]")
        self.assertRegex(html, r"\['user2Ready', 'Register User 2', user2Ready, user1Ready\]")
        self.assertRegex(html, r"\['allReady', 'Open Collaborator Hub', readiness\.allReady, user1Ready && user2Ready\]")
        self.assertIn("].filter(([, , , visible]) => visible)", html)

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
        self.assertNotIn('<span class="step-num">4</span>', html)

    def test_repository_paths_have_folder_browse_buttons(self):
        html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")
        repo_panel = html.split('class="panel repo-panel"', 1)[1].split('</section>', 1)[0]

        for element_id in ("repoPath", "profileRepoPath", "profileRepoPathUser2"):
            self.assertIn(f'id="{element_id}"', html)
            self.assertIn(f'data-path-picker="{element_id}"', html)
        self.assertEqual(html.count('id="repoPath"'), 1)
        self.assertEqual(html.count('id="scanBtn"'), 1)
        self.assertIn('class="repo-scan-controls"', repo_panel)
        self.assertIn('id="repoPath"', repo_panel)
        self.assertIn('data-path-picker="repoPath"', repo_panel)
        self.assertIn('class="primary" id="scanBtn" type="button">Scan repository</button>', repo_panel)
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
        html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")

        self.assertIn('id="projectFilesDirectory"', html)
        self.assertIn('id="setupProjectFilesDirectory"', html)
        self.assertIn('data-path-picker="projectFilesDirectory"', html)
        self.assertIn('data-path-picker="setupProjectFilesDirectory"', html)
        self.assertIn(r"C:\panda-gallery", html)
        self.assertIn(r"skills\pg-project-sync\MANIFEST.md", html)
        self.assertIn("project_knowledge_sync_YYYY-MM-DD", html)

    def test_setup_has_auto_fill_and_claude_help_action(self):
        html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")

        self.assertIn('id="autoFillSetupBtn"', html)
        self.assertIn("async function autoFillSetup()", html)
        self.assertIn("'/api/setup/autofill'", html)
        self.assertIn("ask_claude: true", html)
        self.assertIn("Claude help request", html)

    def test_switch_user_entry_points_are_visible_and_not_dead_before_setup(self):
        html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")

        self.assertIn('id="switchUserBtn"', html)
        self.assertIn("Collaborator Hub / Handover", html)
        self.assertIn("$('switchUserBtn').addEventListener('click', openSetupWizard)", html)
        self.assertIn("button.disabled = state.busy;", html)
        self.assertIn("HANDOVER TO USER 1", html)
        self.assertIn("HANDOVER TO USER 2", html)
        self.assertIn("function handoverButtonLabel(userId, user)", html)
        self.assertIn("button.textContent = ready ? handoverButtonLabel(button.dataset.switchGo, user)", html)
        self.assertIn(": `SET UP ${button.dataset.switchGo === 'user1' ? 'USER 1' : 'USER 2'}`", html)
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

        self.assertNotIn('<span class="step-num">1</span>', html)
        self.assertNotIn('<span class="step-num">2</span>', html)
        self.assertNotIn('<span class="step-num">3</span>', html)
        self.assertNotIn('class="panda-step-guide"', html)
        self.assertIn('class="sequence-step">1</span>', html)

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

        self.assertRegex(html, r"(?s)\.shell\s*\{.*?grid-template-rows:\s*60px minmax\(0, 1fr\);")
        self.assertRegex(html, r"(?s)header\s*\{.*?display:\s*flex;")
        self.assertRegex(html, r"(?s)\.active-user-banner\s*\{.*?height:\s*38px;")
        self.assertRegex(html, r"(?s)\.active-user-banner\s*\{.*?overflow:\s*hidden;")
        self.assertRegex(html, r"(?s)\.active-user-banner\s*\{.*?grid-template-columns:\s*auto minmax\(120px, 320px\) minmax\(0, 1fr\);")
        self.assertRegex(html, r"(?s)\.active-user-banner small\s*\{.*?text-overflow:\s*ellipsis;")

    def test_information_pills_and_action_buttons_are_visually_distinct(self):
        html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")

        self.assertRegex(html, r"(?s)button\s*\{.*?border-radius:\s*2px;")
        self.assertRegex(html, r"(?s)button\s*\{.*?box-shadow:\s*inset 0 1px 0")
        self.assertRegex(html, r"(?s)button:not\(:disabled\):not\(\.danger\)\s*\{.*?background:\s*linear-gradient\(180deg, #8ccf6f, #6da850\);")
        self.assertRegex(html, r"(?s)button:disabled\s*\{.*?background:\s*linear-gradient\(180deg, #4a4a56, #353542\);")
        self.assertRegex(html, r"(?s)\.view-toggle button\.active:not\(:disabled\).*?\.segmented button\.active:not\(:disabled\)\s*\{.*?background:\s*linear-gradient\(180deg, #8ccf6f, #6da850\);")
        self.assertRegex(html, r"(?s)\.chip\s*\{.*?border-radius:\s*999px;")
        self.assertRegex(html, r"(?s)\.chip\s*\{.*?cursor:\s*default;")
        self.assertRegex(html, r"(?s)\.test-status-pill\s*\{.*?border-radius:\s*999px;")
        self.assertRegex(html, r"(?s)\.test-status-pill\s*\{.*?cursor:\s*default;")
        self.assertRegex(html, r"(?s)\.test-mode-btn\s*\{.*?border-radius:\s*2px;")
        self.assertRegex(html, r"(?s)\.quit-test-btn\s*\{.*?border-radius:\s*2px;")
        self.assertIn("$('testModeBtn').classList.toggle('hidden', state.testMode.active);", html)
        self.assertIn("$('openTestEvidenceBtn').classList.toggle('hidden'", html)
        self.assertIn('class="chip" id="scanTime"', html)

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

    def test_create_safe_handoff_button_is_prominent_and_state_colored(self):
        html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")
        handoff_panel = html.split('data-flow-panel="handoff"', 1)[1].split('</section>', 1)[0]

        self.assertEqual(html.count('id="handoffBtn"'), 1)
        self.assertLess(handoff_panel.index('id="handoffBtn"'), handoff_panel.index('class="handoff-fields"'))
        self.assertIn('class="handoff-primary-action" id="handoffBtn" disabled>Create safe handoff</button>', html)
        self.assertRegex(html, r"(?s)\.handoff-primary-action\s*\{.*?width:\s*100%;")
        self.assertRegex(html, r"(?s)\.handoff-primary-action\s*\{.*?min-height:\s*48px;")
        self.assertRegex(html, r"(?s)\.handoff-primary-action\s*\{.*?background:\s*linear-gradient\(180deg, #8ccf6f, #6da850\);")
        self.assertRegex(html, r"(?s)\.handoff-primary-action:disabled\s*\{.*?background:\s*linear-gradient\(180deg, #4a4a56, #353542\);")

    def test_status_messages_use_one_scroll_container(self):
        html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")

        self.assertRegex(html, r"(?s)\.status-panel \.panel-body\s*\{.*?overflow:\s*hidden;")
        self.assertRegex(html, r"(?s)\.status-window\s*\{.*?height:\s*100%;.*?overflow:\s*auto;.*?scrollbar-gutter:\s*stable;")
        self.assertIn('id="resultBox" class="empty status-window"', html)

    def test_setup_dialog_is_centered_and_shows_side_by_side_registration(self):
        html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")

        self.assertRegex(html, r"(?s)\.setup-dialog\s*\{.*?width:\s*min\(936px, calc\(100vw - 88px\)\);")
        self.assertNotIn("width: min(1560px", html)
        self.assertRegex(html, r"(?s)\.wizard-grid\s*\{.*?grid-template-columns:\s*repeat\(2, minmax\(0, 1fr\)\);")
        self.assertRegex(html, r'(?s)\.wizard-grid\s*\{.*?"project project".*?"hub hub".*?"user1 user2";')
        self.assertRegex(html, r"(?s)\.wizard-grid\s*\{.*?overflow:\s*hidden;")
        self.assertRegex(html, r"(?s)\.setup-project-step \.wizard-step-body\s*\{.*?grid-template-columns:\s*minmax\(0, 1fr\) auto auto;")
        self.assertRegex(html, r"(?s)\.setup-project-step \.identity-note\s*\{.*?grid-column:\s*1 / -1;")
        self.assertIn('class="wizard-step wide setup-project-step"', html)
        self.assertIn('class="setup-dialog-status"', html)
        self.assertIn('class="setup-dialog-actions"', html)
        self.assertNotIn("<h3>Required flow</h3>", html)
        self.assertNotIn('id="registrationProgress"', html)
        self.assertIn(".registration-panel.is-current .wizard-step-head", html)
        self.assertIn(".registration-panel.is-ready .wizard-step-head", html)
        self.assertIn(".registration-panel.is-pending .wizard-step-head", html)
        current_panel_css = html.split(".registration-panel.is-current {", 1)[1].split("}", 1)[0]
        locked_panel_css = html.split(".registration-panel.is-locked .wizard-step-head", 1)[0]
        self.assertNotIn("grid-column: 1 / -1", current_panel_css)
        self.assertNotIn(".registration-panel.is-locked {\n      display: none;", locked_panel_css)
        self.assertNotIn(".registration-panel:not(.is-current) .wizard-step-body", html)
        self.assertIn("panel.dataset.registrationState", html)
        self.assertNotIn('registration-panel hidden" data-registration-stage="user2"', html)
        self.assertNotIn('registration-panel hidden" data-registration-stage="hub"', html)
        self.assertIn("panel.classList.toggle('is-current'", html)
        self.assertIn("panel.classList.toggle('is-locked'", html)
        self.assertIn("panel.classList.toggle('is-collapsed'", html)

    def test_user_registration_stays_on_one_side_by_side_screen(self):
        html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")

        self.assertNotIn('id="user1Transition"', html)
        self.assertNotIn('id="continueUser2Btn"', html)
        self.assertNotIn("user1Complete", html)
        self.assertIn("users: 'REGISTER USERS'", html)
        self.assertIn("setRegistrationStage('users')", html)
        self.assertIn("setupDialog.dataset.registrationStage = stage", html)
        self.assertIn("User 1 saved. User 2 remains visible on the same setup screen.", html)
        self.assertNotIn("setRegistrationStage('user2');\n        showResult('User 1 registered. Now register User 2.')", html)
        self.assertNotIn(".registration-transition", html)
        self.assertRegex(html, r"(?s)\.profile-defaults\s*\{.*?grid-template-columns:\s*repeat\(2, minmax\(0, 1fr\)\);")
        self.assertIn("Accounts, tools, and Git identity", html)
        self.assertIn("registrationCollapsed: {user1: true, user2: true}", html)
        self.assertIn('data-collapse-panel="user1"', html)
        self.assertIn('data-collapse-panel="user2"', html)
        self.assertIn("function toggleRegistrationPanel(userId)", html)
        self.assertIn("toggleRegistrationPanel(button.dataset.collapsePanel)", html)
        self.assertRegex(html, r"(?s)\.registration-panel\.is-collapsed\s*\{.*?grid-template-rows:\s*auto;")
        self.assertRegex(html, r"(?s)\.registration-panel\.is-collapsed \.wizard-step-body\s*\{.*?display:\s*none;")

    def test_user_two_registration_names_missing_fields(self):
        html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")

        self.assertIn("function registrationRequiredFields(userId)", html)
        self.assertIn("function registrationMissingFields(userId)", html)
        self.assertIn("return registrationMissingFields(userId).length === 0", html)
        for field_id in (
            "codexAccountUser2",
            "claudeAccountUser2",
            "claudeDesktopPathUser2",
            "claudeCodePathUser2",
            "gitAuthorNameUser2",
            "gitAuthorEmailUser2",
        ):
            self.assertIn(f"['{field_id}'", html)
        self.assertIn("User 1 needs ${missingUser1.join(', ')}", html)
        self.assertIn("User 2 needs ${missingUser2.join(', ')}", html)
        self.assertIn("$('registerUser2FinishBtn').dataset.missingFields = registrationMissingFields('user2').join(', ');", html)
        self.assertIn("$('registerUser2FinishBtn').disabled = state.busy || !storedUserReady('user1') || !registrationFieldReady('user2');", html)

    def test_main_screen_orders_controls_left_to_right_by_workflow(self):
        html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")
        main = html.split('<main class="workflow-layout">', 1)[1].split('<div class="setup-overlay', 1)[0]

        self.assertIn('class="workflow-row"', main)
        self.assertRegex(
            html,
            r"(?s)\.workflow-row\s*\{.*?grid-template-columns:\s*minmax\(145px, \.55fr\).*?minmax\(540px, 2\.45fr\);",
        )
        self.assertRegex(html, r"(?s)main\s*\{.*?grid-template-rows:\s*minmax\(340px, 1\.22fr\) minmax\(0, \.58fr\);")
        self.assertIn('data-flow-panel="handoff"', main)
        self.assertIn(".sequence-panel.is-locked", html)
        self.assertIn("function updateWorkflowLocks()", html)
        self.assertIn("handoff: handoffStepReady()", html)
        self.assertIn("forbidden.slice(0, 2)", html)
        self.assertIn("more destructive commands blocked", html)

        sequence = [
            "Register User 1",
            "Register User 2",
            "Collaborator Hub / Handover",
            "Start Session",
            "Create Handoff",
        ]
        positions = [main.index(label) for label in sequence]
        self.assertEqual(positions, sorted(positions))
        self.assertLess(main.index('id="startSessionBtn"'), main.index('id="handoffBtn"'))
        self.assertLess(main.index('class="workflow-row"'), main.index('class="support-grid"'))


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
        (self.repo / "tracked.txt").write_text("base\nworking change\n", encoding="utf-8")
        (self.repo / "new-note.md").write_text("# untracked\n", encoding="utf-8")

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
        self.assertTrue((package_dir / "patches" / "unstaged-working-tree.patch").exists())
        self.assertTrue((package_dir / "patches" / "staged-index.patch").exists())
        self.assertTrue((package_dir / "file_copies" / "tracked.txt").exists())
        self.assertTrue((package_dir / "file_copies" / "new-note.md").exists())
        self.assertFalse(manifest["stash_used"])
        self.assertTrue(manifest["committed_protection"]["created_without_checkout"])
        self.assertEqual(manifest["operator_context"]["display_name"], "Darrin")
        self.assertEqual(manifest["operator_context"]["codex_account"], "darrin-codex@example.invalid")
        self.assertEqual(manifest["operator_context"]["claude_desktop_path"], str(self.tmp / "Claude Desktop.exe"))
        self.assertEqual(manifest["operator_context"]["project_files_directory"], str(self.tmp / "panda-gallery"))

        branch = manifest["committed_protection"]["branch"]
        refs = run(["git", "show-ref", "--verify", f"refs/heads/{branch}"], self.repo)
        self.assertIn(branch, refs.stdout)

        status_after = run(["git", "status", "--porcelain=v1", "-uall"], self.repo).stdout
        self.assertIn(" M tracked.txt", status_after)
        self.assertIn("?? new-note.md", status_after)

        loaded = json.loads((package_dir / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(loaded["committed_protection"]["branch"], branch)
        self.assertFalse(loaded["safety_receipt"]["stash_used"])
        self.assertFalse(loaded["safety_receipt"]["restore_or_apply_performed"])

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
        self.assertEqual(len(plan["copy_checks"]), 2)
        self.assertIn("Target repository has uncommitted work; automated restore must stay unavailable.", plan["blockers"])

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


if __name__ == "__main__":
    unittest.main()
