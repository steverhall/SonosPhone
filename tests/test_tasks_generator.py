from pathlib import Path
from tools.generate_tasks import parse_spec


def test_parse_spec():
    spec = Path('specs/001-generate-tasks/spec.md')
    stories = parse_spec(spec)
    assert len(stories) >= 1
    assert stories[0][0] == 1


def test_generate_and_validate(tmp_path, monkeypatch):
    # copy feature files to tmp_path
    src = Path('specs/001-generate-tasks')
    dst = tmp_path / 'specs' / '001-generate-tasks'
    dst.mkdir(parents=True)
    for f in ['plan.md', 'spec.md']:
        (dst / f).write_text((src / f).read_text())
    # run generator as module
    import subprocess, sys
    res = subprocess.run([sys.executable, '-m', 'tools.generate_tasks', '--feature', str(dst)], capture_output=True)
    assert res.returncode == 0, res.stderr.decode() + '\n' + res.stdout.decode()
    # validate with validator
    tasks = dst / 'tasks.md'
    assert tasks.exists()
    res2 = subprocess.run([sys.executable, 'tools/validate_tasks_format.py', str(tasks)], capture_output=True)
    assert res2.returncode == 0, res2.stderr.decode() + '\n' + res2.stdout.decode()
