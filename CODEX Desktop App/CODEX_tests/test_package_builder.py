from __future__ import annotations

import shutil
import json
import unittest
from pathlib import Path

from CODEX_pg_audit.issue_extraction import build_mock_issue_extraction
from CODEX_pg_audit.package_builder import BuildContext, build_package
from CODEX_pg_audit.review_records import create_local_review_records, search_archive_records, validate_review_record_chain
from CODEX_pg_audit.validation import validate_issue_extraction, validate_manifest


class PackageBuilderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app_root = Path(__file__).resolve().parents[1]
        self.repo_root = self.app_root.parent
        self.test_output = self.app_root / "CODEX_test_output"
        if self.test_output.exists():
            shutil.rmtree(self.test_output)
        self.test_output.mkdir(parents=True)

    def tearDown(self) -> None:
        if self.test_output.exists():
            shutil.rmtree(self.test_output)

    def test_builds_and_validates_sample_package(self) -> None:
        source = self.repo_root / "CODEX Audit MVP Starter Pack" / "CODEX samples" / "sample_source_session"
        out = self.test_output / "CODEX Output"
        package_dir = build_package(BuildContext(source_dir=source, output_root=out, overwrite=True))
        manifest_path = package_dir / "session_package_manifest.json"
        report = validate_manifest(manifest_path)
        self.assertTrue(report.ok, report.as_dict())
        self.assertTrue((package_dir / "derived" / "ai_extraction_input_v1.json").exists())
        self.assertTrue((package_dir / "derived" / "package_summary.md").exists())

    def test_missing_results_blocks_build(self) -> None:
        source = self.test_output / "CODEX Source"
        out = self.test_output / "CODEX Output"
        source.mkdir()
        with self.assertRaises(FileNotFoundError):
            build_package(BuildContext(source_dir=source, output_root=out))

    def test_builds_live_style_repo_relative_screenshot_paths(self) -> None:
        pg_root = self.test_output / "CODEX PG Root"
        workflows = pg_root / "workflows"
        screenshot_dir = workflows / "screenshots" / "run_one"
        screenshot_dir.mkdir(parents=True)
        (screenshot_dir / "step_2.png").write_bytes(b"fakepng")
        results = {
            "schema_version": 1,
            "run_id": "2026-04-24T20-01-30--130-Phase-4-verification",
            "title": "Live shape",
            "results": [
                {
                    "step_n": 2,
                    "kind": "checklist",
                    "title": "Toast wording",
                    "outcome": "PASS",
                    "screenshot": "workflows/screenshots/run_one/step_2.png",
                    "manual_screenshots": [],
                }
            ],
        }
        (workflows / "results_latest.json").write_text(json.dumps(results), encoding="utf-8")
        package_dir = build_package(BuildContext(source_dir=workflows, output_root=self.test_output / "CODEX Output"))
        report = validate_manifest(package_dir / "session_package_manifest.json")
        self.assertTrue(report.ok, report.as_dict())
        manifest = json.loads((package_dir / "session_package_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["session_id"], "2026-04-24T20-01-30--130-Phase-4-verification")
        self.assertEqual(manifest["evidence"][0]["kind"], "step_auto_screenshot")

    def test_missing_optional_metadata_and_transcript_still_validates(self) -> None:
        source = self.test_output / "CODEX Source"
        source.mkdir()
        results = {
            "run_id": "run_without_optional_sources",
            "results": [
                {"step_n": 1, "title": "No evidence", "outcome": "PASS", "manual_screenshots": []}
            ],
        }
        (source / "results_latest.json").write_text(json.dumps(results), encoding="utf-8")
        package_dir = build_package(BuildContext(source_dir=source, output_root=self.test_output / "CODEX Output"))
        report = validate_manifest(package_dir / "session_package_manifest.json")
        self.assertTrue(report.ok, report.as_dict())

    def test_missing_screenshot_is_recorded_without_breaking_validation(self) -> None:
        source = self.test_output / "CODEX Source"
        source.mkdir()
        results = {
            "run_id": "run_missing_screenshot",
            "results": [
                {
                    "step_n": 1,
                    "title": "Missing evidence",
                    "outcome": "FAIL",
                    "manual_screenshots": ["screenshots/missing.png"],
                }
            ],
        }
        (source / "results_latest.json").write_text(json.dumps(results), encoding="utf-8")
        package_dir = build_package(BuildContext(source_dir=source, output_root=self.test_output / "CODEX Output"))
        report = validate_manifest(package_dir / "session_package_manifest.json")
        self.assertTrue(report.ok, report.as_dict())
        manifest = json.loads((package_dir / "session_package_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["missing_sources"][0]["kind"], "region_screenshot")

    def test_mock_issue_extraction_references_manifest_evidence(self) -> None:
        source = self.repo_root / "CODEX Audit MVP Starter Pack" / "CODEX samples" / "sample_source_session"
        package_dir = build_package(BuildContext(source_dir=source, output_root=self.test_output / "CODEX Output"))
        manifest_path = package_dir / "session_package_manifest.json"
        issue_path = build_mock_issue_extraction(manifest_path)
        report = validate_issue_extraction(issue_path, manifest_path)
        self.assertTrue(report.ok, report.as_dict())
        extraction = json.loads(issue_path.read_text(encoding="utf-8"))
        self.assertEqual(extraction["created_by"]["type"], "local_fixture")
        self.assertTrue(extraction["issues"][0]["evidence_ids"])

    def test_issue_validation_blocks_unknown_evidence_ids(self) -> None:
        source = self.repo_root / "CODEX Audit MVP Starter Pack" / "CODEX samples" / "sample_source_session"
        package_dir = build_package(BuildContext(source_dir=source, output_root=self.test_output / "CODEX Output"))
        manifest_path = package_dir / "session_package_manifest.json"
        issue_path = build_mock_issue_extraction(manifest_path)
        extraction = json.loads(issue_path.read_text(encoding="utf-8"))
        extraction["issues"][0]["evidence_ids"] = ["ev_region_9999"]
        issue_path.write_text(json.dumps(extraction), encoding="utf-8")
        report = validate_issue_extraction(issue_path, manifest_path)
        self.assertFalse(report.ok)
        self.assertTrue(any("unknown evidence_id" in error for error in report.errors))

    def test_review_records_are_local_draft_only_and_archived(self) -> None:
        source = self.repo_root / "CODEX Audit MVP Starter Pack" / "CODEX samples" / "sample_source_session"
        package_dir = build_package(BuildContext(source_dir=source, output_root=self.test_output / "CODEX Output"))
        issue_path = build_mock_issue_extraction(package_dir / "session_package_manifest.json")
        report = validate_issue_extraction(issue_path, package_dir / "session_package_manifest.json")
        self.assertTrue(report.ok, report.as_dict())
        records = create_local_review_records(package_dir)
        approval = json.loads(Path(records["approval_record"]).read_text(encoding="utf-8"))
        email = json.loads(Path(records["email_draft_record"]).read_text(encoding="utf-8"))
        archive_lines = Path(records["archive_jsonl"]).read_text(encoding="utf-8").splitlines()
        archive = json.loads(archive_lines[0])
        self.assertEqual(email["state"], "draft_only")
        self.assertEqual(email["provider"], "not_configured_local_prototype")
        self.assertEqual(approval["issue_id"], email["issue_id"])
        self.assertEqual(archive["status"], "archived")
        self.assertTrue(archive["immutability"]["record_sha256"])
        errors = validate_review_record_chain(Path(records["approval_record"]), Path(records["email_draft_record"]), Path(records["archive_jsonl"]))
        self.assertEqual(errors, [])
        search_results = search_archive_records(Path(records["archive_jsonl"]), "mock extraction")
        self.assertEqual(len(search_results), 1)


if __name__ == "__main__":
    unittest.main()
