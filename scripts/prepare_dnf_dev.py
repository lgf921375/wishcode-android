#!/usr/bin/env python3
"""Package a minimal opt-in DNF-style Unity game-development skill plugin.

No model key, network call, Android runtime modification or automatic installation.
The workflow hints are original process notes, not third-party game assets.
"""
from __future__ import annotations
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile

PACKAGE = "dsh-wishcode-dnf-dev"
VERSION = "0.1.0"
ARCHIVE_NAME = "dsh-wishcode-dnf-dev-0.1.0.tgz"

SKILLS = {
    "wishcode-dnf-combat": (
        "检查 Unity DNF 风格战斗切片时调用：三段普攻、受击、浮空、扫地、"
        "HitEvent、Hitstop 与安卓双指横屏。",
        """# DNF-style Unity combat workflow

Use original assets and code you are authorized to use; do not claim an official
DNF port. Read AGENTS.md, active-handoff and the active issue before edits.

1. Identify the exact Git branch, source SHA, Unity version and Android target.
2. Map attack animation events into each target's HitEvent / knockback / state
   transition; test multi-target deduplication and both sides' hitstop.
3. Check the 3-hit staff normal combo, sprite anchors, direction flipping,
   launch/gravity/landing, one ground follow-up, wakeup protection and
   invulnerability. Distinguish visual cues from authoritative hit logic.
4. Check Android automatic landscape, two-touch movement+attack simultaneity,
   pause/resume and performance telemetry.
5. Prefer a small independently testable change; run available .NET unit tests
   and Unity batch compile separately. Mark device-only behavior unverified
   until an APK is actually run on a phone.
6. Do not modify main or unrelated Godot projects. Do not trigger Unity Cloud
   or GitHub Actions without explicit per-build approval.
7. Produce source SHA, exact commands, test stdout/logs, changed files and
   limitations. Do not invent screenshots, hit timings or APK URLs.
""",
    ),
    "wishcode-dnf-art": (
        "2D/2.5D 游戏素材、图集、动作帧、碰撞盒、版权来源和性能优化。",
        """# Original game art and animation pipeline

Start with a provenance manifest: identify source, author, license and
transformations for each imported asset. An undocumented third-party game
resource is not proof of permission to redistribute.

1. Inventory supported PNG/SVG/sprite sheets/GLB and engine import settings.
2. Match frame pivots across idle, attack, hit, air, prone and recovery.
3. Keep game-space collision/hurt boxes independent of decorative frames.
4. Validate atlas size, transparent padding, texture compression, overdraw,
   sprite batching, frame timing and animation event offsets.
5. Build a before/after frame/contact timing table; label external observations
   and estimates, never assert unseen source values as measured facts.
6. Preview on a real Android device and record visual and frame-time findings.
""",
    ),
    "wishcode-dnf-release": (
        "Unity 6 安卓 APK 构建、固定源码 SHA、签名、测试和实机验收。",
        """# Android Unity release gate

1. Confirm build branch and complete SHA; compare against the project issue.
2. Verify scene list and bootstrap: intended combat scene must be reachable.
3. Verify Android SDK/Unity editor versions, ABI, package ID and keystore.
4. Run source/static compile tests before requesting a cloud build.
5. Require explicitly authorized ONE manual build only. Do not turn on push
   triggers, schedules or automatic retries. Verify quotas and possible costs.
6. Check actual build logs, artifacts, APK signing, SHA256 and installation.
7. On a real phone: verify landscape, startup scene, two-finger controls,
   first-frame sprites, hitstop, prone/recovery and frame-time regressions.
8. Publish an evidence-based PASS/FAIL/BLOCKED report. No simulated PASS.
""",
    ),
}

JS = r"""export const name = 'dsh-wishcode-dnf-dev';
export const inject = ['skills'];

export function apply(ctx, config = {}) {
  if (config.enabled === false) return;
  const service = ctx?.get?.('skills');
  if (!service || typeof service.register !== 'function') return;
  const unregister = [];
  const definitions = [
    { name: 'wishcode-dnf-combat', description: 'Unity DNF-style combat implementation and tests.', content: __COMBAT__ },
    { name: 'wishcode-dnf-art', description: 'Original 2D/2.5D sprites, atlas, animation and provenance.', content: __ART__ },
    { name: 'wishcode-dnf-release', description: 'Android Unity manual-build gate and device acceptance.', content: __RELEASE__ }
  ];
  try {
    for (const def of definitions) {
      const dispose = service.register({
        ...def,
        source: 'runtime',
        invocation: { modelInvocable: true, userInvocable: true },
      });
      if (typeof dispose === 'function') unregister.push(dispose);
    }
  } catch (error) {
    for (const undo of unregister.reverse()) undo();
    throw error;
  }
  if (typeof ctx.effect === 'function') {
    ctx.effect(() => () => { for (const undo of unregister.reverse()) undo(); });
  }
}
"""


def contents() -> dict[str, bytes]:
    # Escape full Markdown bodies as JSON string literals, not template substitution.
    generated_js = JS
    for token, key in (("__COMBAT__", "wishcode-dnf-combat"),
                       ("__ART__", "wishcode-dnf-art"),
                       ("__RELEASE__", "wishcode-dnf-release")):
        generated_js = generated_js.replace(token, json.dumps(SKILLS[key][1], ensure_ascii=False))
    metadata = {
        "name": PACKAGE, "version": VERSION, "description": "Opt-in original DNF-style Unity game-development workflows",
        "type": "module", "main": "lib/index.js",
        "exports": {".": "./lib/index.js", "./package.json": "./package.json"},
        "engines": {"node": ">=22.15"}, "license": "MIT",
        "dsh": {"bundle": {"patch": "./cordis.patch.yml"}},
    }
    config = "- insert:\n    - id: wishcode-dnf-dev\n      name: 'dsh-wishcode-dnf-dev'\n      config:\n        enabled: true\n"
    result = {
        "package.json": (json.dumps(metadata, ensure_ascii=False, indent=2) + "\n").encode(),
        "cordis.patch.yml": config.encode(),
        "lib/index.js": generated_js.encode(),
    }
    for key, (_, body) in SKILLS.items():
        result[f"skill/{key}.md"] = body.encode()
    return result


def create(output: Path) -> dict:
    files = contents()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as raw, gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=0) as zipped:
        with tarfile.open(fileobj=zipped, mode="w") as tar:
            for name, data in sorted(files.items()):
                member = tarfile.TarInfo("package/" + name)
                member.size = len(data)
                member.mode = 0o644
                member.mtime = 0
                tar.addfile(member, io.BytesIO(data))
    return {
        "name": PACKAGE, "version": VERSION, "files": sorted(files),
        "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "default_auto_installed": False,
        "verified_android_runtime": False,
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        raise SystemExit("usage: prepare_dnf_dev.py <output.tgz>")
    print(json.dumps(create(Path(sys.argv[1])), ensure_ascii=False))
