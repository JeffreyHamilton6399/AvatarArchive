"""
Avatar Caption Renamer - Fixed
================================
Cleans up ALL naming variations:
  - "Avatar The Last Airbender - S03E14 - The ..."  -> S3E14.en.srt
  - "The Legend of Korra - S01E01 - Welcome ..."    -> S1E1.en.srt
  - "Avatar The Last Airbender - 3x01 - ..."        -> S3E1.en.srt
  - S3E2.en (already correct, skipped)

Also renames folders to atla-season1, korra-season1, etc.

Usage:
    python rename_captions.py "D:\\TheAvatarHub\\captions"
"""

import os
import re
import sys

# Matches: 3x01, S03E01, S3E1, etc.
_EP_RE = re.compile(r'[Ss]?0*(\d+)[xXeE]0*(\d+)', re.IGNORECASE)


def parse_season_episode(filename):
    m = _EP_RE.search(filename)
    if m:
        return int(m.group(1)), int(m.group(2))
    return None


def detect_show(name):
    nl = name.lower()
    if 'korra' in nl:
        return 'korra'
    if 'airbender' in nl or 'avatar' in nl or 'atla' in nl:
        return 'atla'
    return None


def process_folder(folder):
    srt_files = [f for f in os.listdir(folder) if f.lower().endswith('.srt')]
    if not srt_files:
        print(f"  [SKIP] No .srt files found.")
        return

    seen = set()
    renamed = 0
    skipped = 0

    for fname in sorted(srt_files):
        se = parse_season_episode(fname)
        if se is None:
            print(f"  [WARN] Can't parse episode number: {fname}")
            skipped += 1
            continue

        season, episode = se
        new_name = f"S{season}E{episode}.en.srt"

        if se in seen:
            # Delete the duplicate instead of leaving it
            dup_path = os.path.join(folder, fname)
            os.remove(dup_path)
            print(f"  [DEL ] Duplicate removed: {fname}")
            skipped += 1
            continue
        seen.add(se)

        old_path = os.path.join(folder, fname)
        new_path = os.path.join(folder, new_name)

        if fname == new_name:
            print(f"  [OK]  {fname}")
            continue

        # If target already exists and it's a different file, remove the old one
        if os.path.exists(new_path):
            os.remove(old_path)
            print(f"  [DEL ] Removed (target exists): {fname}")
            skipped += 1
            continue

        os.rename(old_path, new_path)
        print(f"  {fname} -> {new_name}")
        renamed += 1

    print(f"  Done: {renamed} renamed, {skipped} skipped")


def main():
    if len(sys.argv) < 2:
        print('Usage: python rename_captions.py "D:\\TheAvatarHub\\captions"')
        sys.exit(1)

    captions_folder = sys.argv[1]

    if not os.path.isdir(captions_folder):
        print(f"Error: '{captions_folder}' is not a folder.")
        sys.exit(1)

    subfolders = sorted(
        d for d in os.listdir(captions_folder)
        if os.path.isdir(os.path.join(captions_folder, d))
    )

    for folder_name in subfolders:
        folder_path = os.path.join(captions_folder, folder_name)
        show = detect_show(folder_name)

        if show is None:
            print(f"\n[SKIP] Can't detect show from: {folder_name}")
            continue

        season_match = re.search(r'(\d+)', folder_name)
        season_num = int(season_match.group(1)) if season_match else None

        if season_num is None:
            print(f"\n[SKIP] Can't detect season number from: {folder_name}")
            continue

        new_folder_name = f"{show}-season{season_num}"
        new_folder_path = os.path.join(captions_folder, new_folder_name)

        print(f"\n{folder_name} -> {new_folder_name}")

        process_folder(folder_path)

        if folder_path != new_folder_path:
            if os.path.exists(new_folder_path):
                print(f"  [SKIP] Folder already exists: {new_folder_name}")
            else:
                os.rename(folder_path, new_folder_path)
                print(f"  Folder renamed to: {new_folder_name}")

    print("\nAll done!")


if __name__ == '__main__':
    main()
