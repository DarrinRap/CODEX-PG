from __future__ import annotations

import argparse
import json
from pathlib import Path

from .package_builder import BuildContext, build_package
from .validation import validate_manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Build and validate a local PG Audit session package.")
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    package_dir = build_package(BuildContext(source_dir=args.source.resolve(), output_root=args.out.resolve(), overwrite=args.overwrite))
    report = validate_manifest(package_dir / "session_package_manifest.json")
    print(json.dumps({"package_dir": str(package_dir), "validation": report.as_dict()}, indent=2))
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
