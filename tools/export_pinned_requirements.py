#!/usr/bin/env python3
"""Export pinned requirements for Raspberry Pi deployment.

Strategy:
- If `pip-compile` is available (pip-tools), use it to compile pyproject/requirements into a pinned file.
- Otherwise, fall back to copying `requirements.txt` to `requirements-pinned.txt` and warn.

Usage: python3 tools/export_pinned_requirements.py --output requirements-pinned.txt
"""
from pathlib import Path
import shutil
import subprocess
import sys


def has_command(cmd: str) -> bool:
    from shutil import which
    return which(cmd) is not None


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', default='requirements-pinned.txt')
    args = ap.parse_args()

    out = Path(args.output)
    # Prefer Poetry export if project uses Poetry
    if Path('pyproject.toml').exists() and has_command('poetry'):
        try:
            subprocess.check_call(['poetry', 'export', '-f', 'requirements.txt', '--output', str(out), '--without-hashes', '--dev'])
            print('Exported pinned requirements via poetry ->', out)
            return 0
        except subprocess.CalledProcessError:
            print('poetry export failed; falling back', file=sys.stderr)

    # Next prefer pip-compile if available
    if has_command('pip-compile'):
        try:
            subprocess.check_call(['pip-compile', '--output-file', str(out), 'requirements.txt'])
            print('Wrote', out)
            return 0
        except subprocess.CalledProcessError:
            print('pip-compile failed; falling back to copy', file=sys.stderr)

    # Fallback: copy existing requirements.txt
    src = Path('requirements.txt')
    if src.exists():
        shutil.copyfile(src, out)
        print('Copied', src, '→', out)
        print('NOTE: This is an unpinned fallback. Install Poetry or pip-tools to produce pinned output.')
        return 0

    print('No requirements.txt found and neither poetry nor pip-compile available. Cannot create pinned requirements.', file=sys.stderr)
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
