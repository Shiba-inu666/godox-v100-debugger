#!/usr/bin/env python3
"""Check public docs, model identities and saved evidence without firmware I/O.

Uses Git's tracked and non-ignored file list. This is a repository consistency
check, not a firmware test, a comprehensive Markdown parser or a secret scanner.
"""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    errors: list[str] = []
    raw = subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
    )
    files = sorted({name.decode("utf-8") for name in raw.split(b"\0") if name})
    published = set(files)
    link_count = 0
    hash_count = 0
    for name in files:
        path = ROOT / name
        if not path.is_file():
            errors.append(f"Missing public file: {name}")
            continue
        try:
            if path.suffix == ".json":
                json.loads(path.read_text(encoding="utf-8"))
            elif path.suffix == ".py":
                ast.parse(path.read_text(encoding="utf-8"), filename=name)
            elif path.suffix == ".md":
                text = path.read_text(encoding="utf-8")
                # Inline local links used by this repository, excluding code fences.
                text = re.sub(r"```[^\n]*\n.*?```", "", text, flags=re.S)
                for target in re.findall(r"!?\[[^\]]*\]\(([^\s)]+)\)", text):
                    parts = urlsplit(target.strip("<>"))
                    if parts.scheme or parts.netloc or not parts.path:
                        continue
                    resolved = (path.parent / unquote(parts.path)).resolve()
                    link_count += 1
                    if not resolved.is_relative_to(ROOT):
                        errors.append(f"Local link leaves repository: {name}: {target}")
                        continue
                    relative = resolved.relative_to(ROOT).as_posix()
                    public_target = relative in published or any(
                        entry.startswith(relative.rstrip("/") + "/") for entry in files
                    )
                    if not resolved.exists() or not public_target:
                        errors.append(f"Missing public link target: {name}: {target}")
        except (ValueError, SyntaxError, UnicodeError) as exc:
            errors.append(f"Invalid {name}: {exc}")

    catalog = json.loads((ROOT / "docs/devices/catalog.json").read_text())
    for device in catalog["devices"]:
        model = device["model"]
        package = ROOT / device["source_directory"]
        spec = json.loads((ROOT / device["patch_record"]).read_text())
        for key in ("model", "firmware_version", "original_sha256", "modified_sha256"):
            if device[key] != spec[key]:
                errors.append(f"Catalog/patch mismatch for {model}: {key}")
        if device["bytes"] != spec.get("size", spec.get("bytes")):
            errors.append(f"Catalog/patch size mismatch for {model}")
        if device["model_guide"] not in published:
            errors.append(f"Model guide is not public: {model}")
        evidence = package / "evidence/PUBLIC_LAB_RESULTS.json"
        saved = json.loads(evidence.read_text())
        if saved["candidate_sha256"] != device["modified_sha256"]:
            errors.append(f"Catalog/evidence candidate mismatch: {model}")
        checks = [(package / rel, sha) for rel, sha in saved["source_sha256"].items()]
        checks += [(evidence.parent / s["result"], s["result_sha256"])
                   for s in saved["suites"].values()]
        for target, expected in checks:
            hash_count += 1
            if not target.is_file() or digest(target) != expected:
                errors.append(f"Saved evidence hash mismatch: {target.relative_to(ROOT)}")

    if errors:
        print("FAIL\n" + "\n".join(errors), file=sys.stderr)
        return 1
    print(f"PASS: {len(files)} public files; {link_count} local links; "
          f"{len(catalog['devices'])} model identities; {hash_count} evidence/source hashes")
    print("No firmware was read, generated, downloaded or written to hardware.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
