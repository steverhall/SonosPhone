from pathlib import Path

from tools.validate_tasks_format import validate_file


def test_validator_accepts_good_tasks(tmp_path):
    p = tmp_path / 'tasks.md'
    p.write_text('- [ ] T100 [US1] Do something in src/foo.py\n')
    assert validate_file(p)


def test_validator_rejects_bad_tasks(tmp_path):
    p = tmp_path / 'tasks.md'
    p.write_text('This is not a task\n- [ ] T100 Do something\n- [ ] T099 Duplicate\n')
    assert not validate_file(p)
