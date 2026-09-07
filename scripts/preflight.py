#!/usr/bin/env python3
"""Read-only runtime check. Does not configure credentials, upload or save drafts."""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


def find_ffprobe(directory: str | None = None) -> str | None:
    binary = "ffprobe.exe" if os.name == "nt" else "ffprobe"
    if directory:
        candidate = Path(directory).expanduser() / binary
        return str(candidate.resolve()) if candidate.is_file() else None
    found = shutil.which("ffprobe")
    if found:
        return found
    if os.name == "nt":
        roaming = Path(os.environ.get("APPDATA", Path.home() / "AppData/Roaming"))
        candidates = [
            roaming / "LobsterAI/tools/ffmpeg/ffmpeg-master-latest-win64-gpl/bin/ffprobe.exe",
            roaming / "TRAE SOLO CN/ModularData/ai-agent/vm/tools/app/ffmpeg/ffprobe.exe",
        ]
        return next((str(p) for p in candidates if p.is_file()), None)
    return None


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ffprobe-dir", help="Use an existing ffprobe installation")
    parser.add_argument("--skip-cli", action="store_true", help="Only inspect local media dependencies")
    args = parser.parse_args()
    probe = find_ffprobe(args.ffprobe_dir)
    cli = shutil.which("yxer")
    pillow = importlib.util.find_spec("PIL") is not None
    result = {"python": sys.executable, "python_ok": sys.version_info >= (3, 10),
              "pillow": pillow, "ffprobe": probe, "yxer": cli,
              "path_prepend": str(Path(probe).parent) if probe else None}
    probe_ok = False
    if probe:
        try:
            check = subprocess.run([probe, "-version"], capture_output=True, timeout=15)
            probe_ok = check.returncode == 0
        except (OSError, subprocess.TimeoutExpired):
            pass
    result["ffprobe_ok"] = probe_ok
    doctor_ok = args.skip_cli
    if not args.skip_cli and cli:
        try:
            process = subprocess.run([cli, "doctor", "--json"], capture_output=True,
                                     encoding="utf-8", errors="replace", timeout=30)
            data = json.loads(process.stdout)
            doctor = data.get("data", {})
            doctor_ok = process.returncode == 0 and data.get("ok") is True and doctor.get("apiKeyPresent") is True
            # Only allowlisted status booleans, never raw configuration or credentials.
            result["doctor"] = {"ok": doctor_ok, "api_key_present": doctor.get("apiKeyPresent") is True,
                                "schema_ready": doctor.get("schemaDirOK") is True,
                                "workflow_ready": doctor.get("workflowsOK") is True}
        except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
            result["doctor"] = {"ok": False, "error_type": type(exc).__name__}
    result["ok"] = bool(result["python_ok"] and pillow and probe_ok and doctor_ok)
    result["note"] = "Prepend path_prepend to PATH in the upload process; this check does not change the parent environment."
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
