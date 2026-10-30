#!/usr/bin/env python3
"""Check repository-relative Markdown links and local anchors without networking."""
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit
from catalogue import ROOT


def anchors(text):
    found = set(re.findall(r'<a\s+id="([^"]+)"', text))
    counts = {}
    for heading in re.findall(r'^#{1,6}\s+(.+)$', text, re.M):
        base = re.sub(r'[^\w\- ]', '', heading.lower()).replace(' ', '-')
        number = counts.get(base, 0)
        found.add(base + (f'-{number}' if number else ''))
        counts[base] = number + 1
    return found


def check(root=ROOT):
    errors=[]
    paths=[p for p in Path(root).rglob('*.md') if not any(part in {'.git','.venv'} for part in p.relative_to(root).parts)]
    for path in paths:
        content=path.read_text(encoding='utf-8')
        for target in re.findall(r'(?<!!)\[[^\]\n]*\]\(([^)\s]+)\)', content):
            parsed=urlsplit(target)
            if parsed.scheme or parsed.netloc:
                continue
            local=(path.parent/unquote(parsed.path)).resolve() if parsed.path else path
            if not local.is_relative_to(Path(root).resolve()):
                errors.append(f'{path.relative_to(root)}: link escapes repository: {target}')
            elif not local.exists():
                errors.append(f'{path.relative_to(root)}: missing target: {target}')
            elif parsed.fragment and local.suffix=='.md' and unquote(parsed.fragment) not in anchors(local.read_text(encoding='utf-8')):
                errors.append(f'{path.relative_to(root)}: missing anchor: {target}')
    return sorted(set(errors))


if __name__=='__main__':
    errors=check()
    if errors:
        print('\n'.join(errors),file=sys.stderr)
        sys.exit(1)
    print('Local Markdown links and anchors passed.')
