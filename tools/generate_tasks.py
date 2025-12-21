#!/usr/bin/env python3
"""Minimal tasks.md generator for speckit feature.

Usage: tools/generate_tasks.py --feature specs/001-generate-tasks [--dry-run]
"""
import argparse
from pathlib import Path
import re
from tools.mdtemplate import load_template, render_template, find_unreplaced_tokens


FEATURE_RE = re.compile(r"specs/(\d{3}-[\w-]+)")


def parse_spec(spec_path: Path):
    text = spec_path.read_text()
    stories = []
    for line in text.splitlines():
        line = line.strip()
        m = re.match(r"^P(\d):\s*(.+)$", line)
        if m:
            priority = int(m.group(1))
            title = m.group(2).strip()
            stories.append((priority, title))
    # sort by priority
    return sorted(stories, key=lambda s: s[0])


def build_story_section(stories, start_id=100):
    out = '\n\n<!-- Generated story list -->\n'
    for i, (priority, title) in enumerate(stories, start=1):
        task_id = start_id + i
        out += f"\n## [US{i}] P{priority} - {title}\n\n- [ ] T{task_id} [US{i}] Implement story: {title}\n"
    return out


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--feature', required=True)
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--open', action='store_true', help='print output to stdout')
    args = ap.parse_args()

    feature = args.feature
    m = FEATURE_RE.search(feature)
    if not m:
        print('Feature path must be like specs/001-name')
        return 2
    feature_dir = Path(feature)
    plan = feature_dir / 'plan.md'
    spec = feature_dir / 'spec.md'
    template = Path('.specify/templates/tasks-template.md')
    if not plan.exists() or not spec.exists():
        print('Required design docs missing in', feature_dir)
        return 2
    stories = parse_spec(spec)
    values = {
        'FEATURE NAME': feature_dir.name,
    }
    tpl = load_template('tasks-template.md')
    out = render_template(tpl, values)
    out += build_story_section(stories)

    tokens = find_unreplaced_tokens(out)
    if tokens:
        print('Warning: unreplaced template tokens detected:', tokens)

    target = feature_dir / 'tasks.md'
    if args.dry_run or args.open:
        print(out)
    if not args.dry_run:
        target.write_text(out)
        print('Wrote', target)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
