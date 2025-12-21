import json
import subprocess
from pathlib import Path

SCRIPT = Path('.specify/scripts/bash/check-prerequisites.sh')


def run_prereqs():
    """Run the repository prerequisites checker and return parsed JSON.

    Returns a dict with keys `FEATURE_DIR` and `AVAILABLE_DOCS` on success.
    Raises RuntimeError on failure with stderr included.
    """
    if not SCRIPT.exists():
        raise RuntimeError(f"Prereq script not found: {SCRIPT}")
    proc = subprocess.run([str(SCRIPT), '--json'], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"Prereq script failed: {proc.stderr.strip()}")
    return json.loads(proc.stdout)


if __name__ == '__main__':
    import sys

    try:
        out = run_prereqs()
        print(json.dumps(out, indent=2))
    except Exception as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)
