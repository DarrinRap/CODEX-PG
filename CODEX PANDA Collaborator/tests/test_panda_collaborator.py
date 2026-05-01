import json
import re
import shutil
import subprocess
import tempfile
import unittest
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


class PandaCollaboratorWebThemeTests(unittest.TestCase):
    def test_header_uses_large_arrow_step_guide(self):
        html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")

        self.assertIn('class="panda-step-guide"', html)
        self.assertIn('id="pandaStepGuide"', html)
        self.assertIn("function pandaStepGuideState()", html)
        self.assertIn("function renderPandaStepGuide()", html)
        self.assertIn("Register User 1", html)
        self.assertIn("Register User 2", html)
        self.assertIn("Collaborator Hub", html)
        self.assertIn("Start Session", html)
        self.assertIn("Create Handoff", html)
        self.assertIn("arrow: index === rows.length - 1 ? '' : '>'", html)
        self.assertIn(".panda-step.current", html)
        self.assertIn(".panda-step.done", html)

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
        self.assertIn("if (setupOpen && ['user1', 'user2'].includes(state.registrationStage))", html)
        self.assertRegex(
            html,
            r"(?s)function setRegistrationStage\(stage\).*?applyUserTheme\(\);.*?updateSetupGuide\(\);",
            "Registration stage changes must immediately retheme the wizard.",
        )

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

        for element_id in ("repoPath", "profileRepoPath", "profileRepoPathUser2"):
            self.assertIn(f'id="{element_id}"', html)
            self.assertIn(f'data-path-picker="{element_id}"', html)
        self.assertIn('data-path-title="Select local Git repository folder"', html)
        self.assertIn('data-path-title="Select User 1 local Git repository folder"', html)
        self.assertIn('data-path-title="Select User 2 local Git repository folder"', html)

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
        self.assertIn("Collaborator Hub / Switch Users", html)
        self.assertIn("$('switchUserBtn').addEventListener('click', openSetupWizard)", html)
        self.assertIn("button.disabled = state.busy;", html)
        self.assertIn("button.textContent = ready ? `GO / Switch to", html)
        self.assertIn(": `Setup ${user?.display_name", html)

    def test_registration_headers_do_not_render_redundant_number_badges(self):
        html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")

        self.assertNotIn('<span class="step-num">1</span>', html)
        self.assertNotIn('<span class="step-num">2</span>', html)
        self.assertNotIn('<span class="step-num">3</span>', html)
        self.assertIn('class="panda-step-guide"', html)

    def test_heading_fonts_stay_compact_for_single_screen_fit(self):
        html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")

        self.assertRegex(html, r"(?s)\.setup-dialog-head h2\s*\{.*?font-size:\s*18px;")
        self.assertRegex(html, r"(?s)\.registration-title strong\s*\{.*?font-size:\s*18px;")
        self.assertRegex(html, r"(?s)\.active-user-banner strong\s*\{.*?font-size:\s*20px;")
        self.assertRegex(html, r"(?s)\.panda-step\s*\{.*?font-size:\s*11px;")
        self.assertRegex(html, r"(?s)\.brand h1\s*\{.*?font-size:\s*14px;")
        self.assertRegex(html, r"(?s)\.panel-head h2\s*\{.*?font-size:\s*10px;")
        self.assertRegex(html, r"(?s)\.hub-card strong\s*\{.*?font-size:\s*12px;")

    def test_active_user_banner_stays_inside_header_row(self):
        html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")

        self.assertRegex(html, r"(?s)\.shell\s*\{.*?grid-template-rows:\s*92px minmax\(0, 1fr\);")
        self.assertRegex(html, r"(?s)header\s*\{.*?grid-template-rows:\s*44px 32px;")
        self.assertRegex(html, r"(?s)\.active-user-banner\s*\{.*?height:\s*38px;")
        self.assertRegex(html, r"(?s)\.active-user-banner\s*\{.*?overflow:\s*hidden;")
        self.assertRegex(html, r"(?s)\.active-user-banner\s*\{.*?grid-template-columns:\s*auto minmax\(120px, 320px\) minmax\(0, 1fr\);")
        self.assertRegex(html, r"(?s)\.active-user-banner small\s*\{.*?text-overflow:\s*ellipsis;")

    def test_information_pills_and_action_buttons_are_visually_distinct(self):
        html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")

        self.assertRegex(html, r"(?s)button\s*\{.*?border-radius:\s*2px;")
        self.assertRegex(html, r"(?s)button\s*\{.*?box-shadow:\s*inset 0 1px 0")
        self.assertRegex(html, r"(?s)\.chip\s*\{.*?border-radius:\s*999px;")
        self.assertRegex(html, r"(?s)\.chip\s*\{.*?cursor:\s*default;")
        self.assertIn('class="chip" id="scanTime"', html)

    def test_action_buttons_and_info_pills_get_lay_tooltips(self):
        html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")

        self.assertIn("function tooltipForAction(button)", html)
        self.assertIn("function tooltipForChip(chip)", html)
        self.assertIn("function applyTooltips(root = document)", html)
        self.assertIn("function startTooltipObserver()", html)
        self.assertIn("new MutationObserver(() => applyTooltips())", html)
        self.assertIn("Open a picker to", html)
        self.assertIn("Switch to this user, apply their saved settings, and scan the repository.", html)
        self.assertIn("Information only:", html)
        self.assertIn("Preview restore safety only. This checks risk but does not change files.", html)

    def test_setup_dialog_is_centered_and_shows_three_setup_columns(self):
        html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")

        self.assertRegex(html, r"(?s)\.setup-dialog\s*\{.*?width:\s*min\(1380px, calc\(100vw - 96px\)\);")
        self.assertRegex(html, r"(?s)\.wizard-grid\s*\{.*?grid-template-columns:\s*repeat\(3, minmax\(0, 1fr\)\);")
        self.assertNotIn('registration-panel hidden" data-registration-stage="user2"', html)
        self.assertNotIn('registration-panel hidden" data-registration-stage="hub"', html)
        self.assertIn("panel.classList.toggle('is-current'", html)
        self.assertIn("panel.classList.toggle('is-locked'", html)

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
            "Collaborator Hub / Switch Users",
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
