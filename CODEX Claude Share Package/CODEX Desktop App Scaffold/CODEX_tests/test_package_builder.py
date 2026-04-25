from __future__ import annotations

import shutil
import unittest
from pathlib import Path

from CODEX_pg_audit.package_builder import BuildContext, build_package
from CODEX_pg_audit.validation import validate_manifest


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


if __name__ == "__main__":
    unittest.main()
