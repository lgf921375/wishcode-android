#!/usr/bin/env python3
"""Create an opt-in, pinned compatibility archive for dsh-purge-flash v1.4.0.

This does not alter the DSH host or install/enable any plugin.
It rejects unexpected upstream bytes, unsafe tar members and manifest drift.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import stat
import tarfile

UPSTREAM_COMMIT = "636059f8002b060fb4dca1c1b47c02e1ef2a2f31"
UPSTREAM_REPO = "jadezane6634-ops/dsh-purge-flash"
UPSTREAM_VERSION = "1.4.0"
SOURCE_BLOB_SHA = {
    "lib/skills.js": "5138d8d067c81a49abe431fd9489cc7d4b357eb0",
    "package.json": "616861cf8777a758fcc2a9fb4083a218879cc164",
    "cordis.patch.yml": "8a00b5154b9954bf884b928068c36107a04e1aa7",
}
ANCHOR = b'      name: "armor-playbook",\n      description: DESCRIPTION,\n'
REPLACEMENT = b'      name: "armor-playbook",\n      description: DESCRIPTION,\n      source: "runtime",\n'
MAX_TOTAL_BYTES = 16 * 1024 * 1024
MAX_FILES = 200


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def extract_source(raw_archive: Path) -> dict[str, bytes]:
    result: dict[str, bytes] = {}
    total = 0
    prefix = None
    with tarfile.open(raw_archive, "r:gz") as archive:
        members = archive.getmembers()
        if len(members) > MAX_FILES:
            raise ValueError("unexpected number of upstream archive entries")
        for member in members:
            entry = PurePosixPath(member.name)
            if entry.is_absolute() or ".." in entry.parts or "\\" in member.name:
                raise ValueError("unsafe upstream archive member")
            if not entry.parts:
                continue
            if prefix is None:
                prefix = entry.parts[0]
            if entry.parts[0] != prefix:
                raise ValueError("multiple archive roots")
            # A source archive must not contain device nodes or symbolic/hard links.
            if member.issym() or member.islnk() or not (member.isfile() or member.isdir()):
                raise ValueError("unexpected source member type")
            if member.isdir():
                continue
            if len(entry.parts) < 2:
                raise ValueError("unexpected root file")
            logical = "/".join(entry.parts[1:])
            if logical in result:
                raise ValueError("duplicate source archive member")
            if member.size < 0 or member.size > MAX_TOTAL_BYTES:
                raise ValueError("oversized source member")
            total += member.size
            if total > MAX_TOTAL_BYTES:
                raise ValueError("source archive too large")
            stream = archive.extractfile(member)
            if stream is None:
                raise ValueError("unreadable source archive member")
            data = stream.read(MAX_TOTAL_BYTES + 1)
            if len(data) != member.size:
                raise ValueError("truncated upstream archive member")
            result[logical] = data
    if not result:
        raise ValueError("empty upstream archive")
    return result


def patch_source(files: dict[str, bytes]) -> dict:
    for name, expected_sha in SOURCE_BLOB_SHA.items():
        if name not in files or git_blob_sha(files[name]) != expected_sha:
            raise ValueError("upstream blob SHA mismatch: " + name)
    package = json.loads(files["package.json"])
    if package.get("name") != "dsh-purge-flash" or package.get("version") != UPSTREAM_VERSION:
        raise ValueError("upstream plugin identity mismatch")
    if package.get("dsh", {}).get("bundle", {}).get("patch") != "./cordis.patch.yml":
        raise ValueError("upstream DSH plugin entry mismatch")
    skills = files["lib/skills.js"]
    if skills.count(ANCHOR) != 1:
        raise ValueError("armor-playbook registration anchor drift")
    if b'source: "runtime"' in skills:
        raise ValueError("upstream source already has compatibility fix; review before repackaging")
    fixed = skills.replace(ANCHOR, REPLACEMENT, 1)
    if fixed.count(REPLACEMENT) != 1:
        raise ValueError("compatibility patch failed")
    files["lib/skills.js"] = fixed
    return {
        "project": "WishCode Android",
        "upstream": UPSTREAM_REPO,
        "upstream_commit": UPSTREAM_COMMIT,
        "upstream_version": UPSTREAM_VERSION,
        "patch": "armor-playbook runtime skill source:string",
        "target": "DSH 0.2.1-rc.2",
        "auto_installed": False,
        "auto_enabled": False,
        "verified_on_android": False,
        "patched_file_sha256": hashlib.sha256(fixed).hexdigest(),
    }


def make_archive(files: dict[str, bytes], output: Path) -> str:
    output.parent.mkdir(parents=True, exist_ok=True)
    # Deterministic gzip/tar metadata; prefix required for standard package imports.
    with output.open("wb") as target, gzip.GzipFile(fileobj=target, mode="wb", mtime=0, filename="") as gz:
        with tarfile.open(fileobj=gz, mode="w") as archive:
            for name in sorted(files):
                if name.startswith(".github/") or name.startswith("test/"):
                    continue  # Tests run from an extracted upstream working tree before packaging.
                data = files[name]
                member = tarfile.TarInfo("package/" + name)
                member.size = len(data)
                member.mode = 0o644
                member.mtime = 0
                member.uid = member.gid = 0
                member.uname = member.gname = ""
                archive.addfile(member, io.BytesIO(data))
    return hashlib.sha256(output.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source_tarball", type=Path)
    parser.add_argument("output_tgz", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    files = extract_source(args.source_tarball)
    report = patch_source(files)
    report["archive_sha256"] = make_archive(files, args.output_tgz)
    report["archive_name"] = args.output_tgz.name
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
