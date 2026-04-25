from __future__ import annotations

import argparse
import json
from pathlib import Path

from .issue_extraction import build_mock_issue_extraction
from .package_builder import BuildContext, build_package
from .review_records import create_local_review_records
from .validation import validate_issue_extraction, validate_manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Build and validate a local PG Audit session package.")
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--mock-issues", action="store_true", help="Generate and validate a local mock issue extraction file.")
    parser.add_argument("--review-records", action="store_true", help="Generate local approval, draft-only email, and archive records. Requires --mock-issues.")
    args = parser.parse_args()
    package_dir = build_package(BuildContext(source_dir=args.source.resolve(), output_root=args.out.resolve(), overwrite=args.overwrite))
    manifest_path = package_dir / "session_package_manifest.json"
    report = validate_manifest(manifest_path)
    result = {"package_dir": str(package_dir), "validation": report.as_dict()}
    if args.mock_issues and report.ok:
        issue_path = build_mock_issue_extraction(manifest_path)
        issue_report = validate_issue_extraction(issue_path, manifest_path)
        result["mock_issue_extraction"] = str(issue_path)
        result["issue_validation"] = issue_report.as_dict()
        report = issue_report
        if args.review_records and report.ok:
            result["review_records"] = create_local_review_records(package_dir)
    elif args.review_records:
        result["review_records_error"] = "--review-records requires --mock-issues"
        report.errors.append("--review-records requires --mock-issues")
    print(json.dumps(result, indent=2))
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
