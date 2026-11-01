#!/usr/bin/env python3
"""Pre-generate spoken audio for every question in index.html using the TTS_ka CLI.

Writes audio/<TEST>-<id>.mp3 (e.g. audio/AQ-1.mp3), which the page plays locally,
so visitors' browsers never contact a speech service.

Only clips whose spoken text or voice changed are regenerated (tracked in
audio/manifest.json); clips for questions that no longer exist are deleted.

Usage:  python3 build_audio.py            # build missing/changed clips
        python3 build_audio.py --force    # rebuild everything
Needs:  tts-ka on PATH and an internet connection (TTS_ka uses Microsoft's Edge neural voices).
"""
import hashlib
import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "audio"
MANIFEST = OUT / "manifest.json"
LANG = "en"  # TTS_ka's "en" = British English (en-GB-SoniaNeural), matching the site's spelling
WORKERS = 4

# Written shorthand that a voice would read awkwardly ("s slash he").
SPEECH_FIXES = [
    (r"\bs/he\b", "he or she"),
    (r"\bhim/herself\b", "himself or herself"),
    (r"\bhim/her\b", "him or her"),
    (r"\bhis/her\b", "his or her"),
    (r"\be\.g\.,?", "for example,"),
]


def speech_text(text: str) -> str:
    for pattern, repl in SPEECH_FIXES:
        text = re.sub(pattern, repl, text, flags=re.I)
    return re.sub(r"\s+", " ", text).strip()


def load_questions() -> dict:
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    m = re.search(r'<script type="application/json" id="questions-data">(.*?)</script>', html, re.S)
    if not m:
        sys.exit("Could not find the questions-data block in index.html")
    return json.loads(m.group(1))


def main() -> None:
    force = "--force" in sys.argv
    OUT.mkdir(exist_ok=True)
    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() and not force else {}

    jobs = {}
    for test, questions in load_questions().items():
        for q in questions:
            text = speech_text(q["text"])
            jobs[f"{test}-{q['id']}.mp3"] = (text, hashlib.sha1(f"{LANG}|{text}".encode()).hexdigest()[:16])

    todo = [name for name, (_, h) in jobs.items() if force or manifest.get(name) != h or not (OUT / name).exists()]

    def build(name: str) -> tuple[str, str | None]:
        text, _ = jobs[name]
        r = subprocess.run(["tts-ka", "-l", LANG, "-n", "--force", "-o", str(OUT / name), text],
                           capture_output=True, text=True, cwd=OUT)
        ok = r.returncode == 0 and (OUT / name).exists() and (OUT / name).stat().st_size > 0
        return name, None if ok else (r.stderr or r.stdout).strip()[-300:]

    failed = []
    with ThreadPoolExecutor(WORKERS) as pool:
        for i, (name, err) in enumerate(pool.map(build, todo), 1):
            if err is None:
                manifest[name] = jobs[name][1]
            else:
                failed.append(name)
                print(f"  FAILED {name}: {err}", file=sys.stderr)
            print(f"\r{i}/{len(todo)} built", end="", flush=True)
    if todo:
        print()

    stale = [p for p in OUT.glob("*.mp3") if p.name not in jobs]
    for p in stale:
        p.unlink()
        manifest.pop(p.name, None)

    MANIFEST.write_text(json.dumps(dict(sorted(manifest.items())), indent=1) + "\n")
    print(f"{len(jobs)} clips total · {len(todo) - len(failed)} built · {len(jobs) - len(todo)} unchanged · "
          f"{len(stale)} stale removed · {len(failed)} failed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
