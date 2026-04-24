"""
AvatarArchive — Korra SRT merge + renumber script
Run this from inside your `main/captions/` folder:
    python merge_korra.py

Korra Season 1: merges 1 + 1.5 into ep1, rest renumbered 1:1
All other Korra seasons: just renumbered 1, 2, 3 ...
Outputs into korra-seasonX-merged/ folders, originals untouched.
"""

import re
from pathlib import Path

# -- Edit these if your folder names differ -----------------------------------
KORRA_SEASONS = ['kora-season1', 'kora-season2', 'kora-season3', 'kora-season4']


# -- SRT helpers --------------------------------------------------------------

TIME_RE = re.compile(
    r'(\d{2}):(\d{2}):(\d{2}),(\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2}),(\d{3})'
)

def to_ms(h, m, s, ms):
    return int(h)*3600000 + int(m)*60000 + int(s)*1000 + int(ms)

def from_ms(total):
    ms  = total % 1000;  total //= 1000
    s   = total % 60;    total //= 60
    m   = total % 60;    h = total // 60
    return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'

def parse_srt(text):
    cues = []
    blocks = re.split(r'\n{2,}', text.strip())
    for block in blocks:
        lines = block.strip().splitlines()
        if len(lines) < 2:
            continue
        m = TIME_RE.match(lines[1].strip()) if len(lines) > 1 else None
        if not m:
            m = TIME_RE.match(lines[0].strip())
            if not m:
                continue
            body = '\n'.join(lines[1:])
        else:
            body = '\n'.join(lines[2:])
        g = m.groups()
        start = to_ms(g[0],g[1],g[2],g[3])
        end   = to_ms(g[4],g[5],g[6],g[7])
        if end - start < 100 and start < 5000 and re.search(r'www\.|font color', body, re.I):
            continue
        cues.append((start, end, body))
    return cues

def render_srt(cues):
    parts = []
    for i, (s, e, body) in enumerate(cues, 1):
        parts.append(f'{i}\n{from_ms(s)} --> {from_ms(e)}\n{body}')
    return '\n\n'.join(parts) + '\n'

def read(path):
    return parse_srt(Path(path).read_text(encoding='utf-8-sig', errors='replace'))

def merge(cues_a, cues_b):
    offset = cues_a[-1][1] if cues_a else 0
    shifted = [(s + offset, e + offset, body) for s, e, body in cues_b]
    return cues_a + shifted

def write(path, cues):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(render_srt(cues), encoding='utf-8')
    print(f'  wrote {Path(path).name}  ({len(cues)} cues)')

def stem_sort_key(p):
    try:
        return float(p.stem)
    except ValueError:
        return 9999.0

def process_season(src_dir):
    src = Path(src_dir)
    if not src.exists():
        print(f'  SKIP — folder not found: {src.resolve()}')
        return

    out_dir = Path(str(src) + '-merged')
    all_srts = sorted(src.glob('*.srt'), key=stem_sort_key)

    seen = set()
    out_ep = 1
    mapping = []

    for p in all_srts:
        stem = p.stem
        if stem in seen:
            continue
        seen.add(stem)

        # if it's a .5 file and we get here unseen, treat standalone
        if '.' in stem:
            mapping.append((out_ep, [p]))
            out_ep += 1
            continue

        half_path = src / f'{stem}.5.srt'
        if half_path.exists():
            seen.add(f'{stem}.5')
            mapping.append((out_ep, [p, half_path]))
        else:
            mapping.append((out_ep, [p]))
        out_ep += 1

    print(f'\n{src_dir}  ->  {out_dir.name}  ({len(mapping)} episodes)')
    for ep, paths in mapping:
        cues = []
        for p in paths:
            cues = merge(cues, read(p))
        write(out_dir / f'{ep}.srt', cues)


if __name__ == '__main__':
    print('Korra SRT merge + renumber')
    print('==========================')
    for folder in KORRA_SEASONS:
        process_season(folder)
    print('\nDone! Check the -merged folders, then swap them in.')
