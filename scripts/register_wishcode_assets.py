#!/usr/bin/env python3
"""Explicitly register two reviewed WishCode APK assets in DSHA's strict allowlist.

No wildcard exclusions, no source repository changes and no runtime permission changes.
Run after both tgz packages are built and BEFORE assembleStandardDebug.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ASSETS = (
    "wishcode/dsh-purge-flash-v1.4.0-compat.tgz",
    "wishcode/dsh-wishcode-dnf-dev-0.1.0.tgz",
)
JAVA_READER = "app/src/main/java/com/deepseekharness/app/ui/WishCodeHomeActivity.java"
READER_METHOD = "assets.open(ARMOR_ARCHIVE_ASSET / DNF_ARCHIVE_ASSET)"
MANIFEST = "tools/asset-deployment.json"


def sha256_file(path: Path) -> str:
    with path.open("rb") as fh:
        digest = hashlib.file_digest(fh, "sha256")
    return digest.hexdigest()


def register(source: Path, *, armor_report: Path, dnf_report: Path) -> dict:
    source = Path(source).resolve()
    manifest_path = source / MANIFEST
    reader = source / JAVA_READER
    if not manifest_path.is_file() or manifest_path.is_symlink():
        raise ValueError("upstream explicit asset manifest unavailable")
    if not reader.is_file() or reader.is_symlink():
        raise ValueError("new WishCodeHomeActivity.java reader unavailable")
    content = reader.read_text(encoding="utf-8")
    # These are compile-time Java constants used by the explicit native export UI.
    for name, const in zip(ASSETS, ("ARMOR_ARCHIVE_ASSET", "DNF_ARCHIVE_ASSET")):
        literal = '"'+name+'"'
        if content.count(literal) != 1 or const not in content:
            raise ValueError("native asset reader anchor drift: " + name)

    armor = json.loads(armor_report.read_text(encoding="utf-8"))
    dnf = json.loads(dnf_report.read_text(encoding="utf-8"))
    if armor.get("upstream_commit") != "636059f8002b060fb4dca1c1b47c02e1ef2a2f31":
        raise ValueError("unpinned Flash input")
    if dnf.get("name") != "dsh-wishcode-dnf-dev" or dnf.get("version") != "0.1.0":
        raise ValueError("DNF plugin identity mismatch")
    expected = (armor.get("archive_sha256"), dnf.get("sha256"))
    result = {}
    for name, sha in zip(ASSETS, expected):
        path = source / "app/src/main/assets" / name
        if not path.is_file() or path.is_symlink():
            raise ValueError("missing approved archive: " + name)
        if not isinstance(sha, str) or len(sha) != 64 or sha256_file(path) != sha:
            raise ValueError("archive checksum mismatch: " + name)
        result[name] = sha

    doc = json.loads(manifest_path.read_text(encoding="utf-8"))
    if doc.get("schema") != 1 or not isinstance(doc.get("packagedFiles"), list) or not isinstance(doc.get("dynamicReaders"), list):
        raise ValueError("unrecognized upstream asset deployment schema")
    if any(name in doc["packagedFiles"] for name in ASSETS):
        raise ValueError("review: plugin asset already exists in upstream manifest")
    if any(row.get("source") == JAVA_READER for row in doc["dynamicReaders"]):
        raise ValueError("review: new reader already exists in upstream manifest")
    # Preserve upstream asset allowlist as-is: append only two exact extra paths.
    doc["packagedFiles"].extend(ASSETS)
    doc["dynamicReaders"].append({
        "source": JAVA_READER,
        "method": READER_METHOD,
        "contract": "Two explicitly user-exportable WishCode plugin archives. No automatic install.",
        "assets": list(ASSETS),
    })
    serialized = json.dumps(doc, ensure_ascii=False, indent=2) + "\n"
    manifest_path.write_text(serialized, encoding="utf-8")
    return {"registered": result, "reader": JAVA_READER,
            "manifest_sha256": sha256_file(manifest_path),
            "auto_installed": False}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", type=Path)
    ap.add_argument("--armor-report", type=Path, required=True)
    ap.add_argument("--dnf-report", type=Path, required=True)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    report = register(args.source, armor_report=args.armor_report,
                      dnf_report=args.dnf_report)
    report_json = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(report_json, encoding="utf-8")
    print(report_json)


if __name__ == "__main__":
    main()
