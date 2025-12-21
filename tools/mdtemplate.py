from pathlib import Path
from typing import Dict, List
import re


TEMPLATE_ROOT = Path('.specify/templates')
PLACEHOLDER_RE = re.compile(r"\[([A-Z 0-9_\-]+)\]|\{\{\s*([A-Z0-9_\-]+)\s*\}\}", re.I)


def render_template(template_path: Path, values: Dict[str, str]) -> str:
    """Render a markdown template replacing placeholders.

    Placeholders supported:
    - [FEATURE NAME]
    - {{FEATURE_NAME}}
    Values dict keys should match either form (with or without brackets).
    """
    text = template_path.read_text()

    def replace(match):
        key = match.group(1) or match.group(2)
        if not key:
            return match.group(0)
        # normalize keys: allow spaces or underscores
        norm = key.strip().upper().replace(' ', '_')
        # look for exact keys in values (case-insensitive)
        for k, v in values.items():
            if k.upper().replace(' ', '_') == norm:
                return v
        return match.group(0)

    return PLACEHOLDER_RE.sub(replace, text)


def load_template(name: str) -> Path:
    p = TEMPLATE_ROOT / name
    if not p.exists():
        raise FileNotFoundError(p)
    return p


def find_unreplaced_tokens(rendered: str) -> List[str]:
    return list({m.group(0) for m in PLACEHOLDER_RE.finditer(rendered)})


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print('Usage: mdtemplate.py <template-file>')
        sys.exit(1)
    tpl = load_template(sys.argv[1])
    print(render_template(tpl, {}))
