import re
import sys
from pathlib import Path
from typing import List

TASK_LINE_RE = re.compile(r"^- \[ \] (T(\d{3,}|XXX))(?: \[P\])?(?: \[US(\d+)\])?\s+(.+)$")


def extract_task_lines(text: str) -> List[str]:
    return [l for l in text.splitlines() if l.strip().startswith('- [ ]')]


def validate_file(path: Path) -> bool:
    text = path.read_text()
    lines = extract_task_lines(text)
    task_ids = []
    nums = []
    ok = True
    for i, line in enumerate(lines, start=1):
        m = TASK_LINE_RE.match(line)
        if not m:
            print(f'Line {i}: invalid task format: {line}')
            ok = False
            continue
        task_id = m.group(1)
        task_ids.append(task_id)
        num_part = m.group(2)
        if num_part and num_part != 'XXX':
            nums.append(int(num_part))
        # check if path exists at end of line
        desc = m.group(4)
        # heuristically find a path-like fragment
        path_like = None
        for part in desc.split():
            if '/' in part or part.endswith('.py') or part.endswith('.md'):
                path_like = part.strip('(),')
                break
        if path_like:
            # skip existence check for placeholder-like fragments
            if any(tok in path_like for tok in ('[', ']', '{', '}', '_[', 'NAME', 'name', 'entity', 'endpoint')):
                # placeholder path - warn but don't fail
                print(f'Line {i}: referenced placeholder path (ignored existence check): {path_like}')
            else:
                p = Path(path_like)
                if not p.exists():
                    print(f'Line {i}: referenced path not found (may be created later): {path_like}')
    # Check ascending and duplicates
    if nums:
        if nums != sorted(nums):
            print('Task IDs not in ascending order')
            ok = False
        if len(set(nums)) != len(nums):
            print('Duplicate Task IDs found')
            ok = False
    return ok


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: validate_tasks_format.py <path-to-tasks.md>')
        sys.exit(2)
    p = Path(sys.argv[1])
    if not p.exists():
        print('File not found:', p)
        sys.exit(2)
    ok = validate_file(p)
    if not ok:
        print('Validation failed')
        sys.exit(1)
    print('Validation passed')
    sys.exit(0)
