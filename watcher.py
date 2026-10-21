#!/usr/bin/env python3
"""Наблюдатель папки inbox: для каждого нового видео строит XML-таймлайн для Premiere Pro / DaVinci Resolve.

Исходные файлы не пережимаются, не переименовываются и не удаляются: Auto-Editor только читает видео
и пишет XML в out_xml. Папка inbox в docker-compose смонтирована только для чтения.
Зависимости: auto-editor и ffmpeg в PATH (в контейнере ставятся при сборке образа).
"""
import os
import subprocess
import sys
import time
from pathlib import Path

INBOX = Path(os.environ.get("INBOX", "./inbox"))
OUT_XML = Path(os.environ.get("OUT_XML", "./out_xml"))
MARGIN = os.environ.get("MARGIN", "0.2sec")
EXPORT = os.environ.get("EXPORT", "premiere")          # premiere (Premiere Pro, XML) или resolve (DaVinci Resolve, FCPXML)
THRESHOLD = os.environ.get("THRESHOLD", "4%")          # порог тишины; шумная комната: 8%
EXT = {"premiere": "xml", "resolve": "fcpxml"}.get(EXPORT, "xml")
POLL_SECONDS = float(os.environ.get("POLL_SECONDS", "5"))
EXTS = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v", ".mp3", ".wav", ".m4a"}

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def size_is_stable(path: Path, wait: float = 3.0) -> bool:
    """Файл ещё копируется, пока его размер меняется."""
    try:
        first = path.stat().st_size
        time.sleep(wait)
        return first > 0 and first == path.stat().st_size
    except OSError:
        return False


def process(src: Path) -> bool:
    dst = OUT_XML / f"{src.stem}_cut.{EXT}"
    cmd = ["auto-editor", str(src), "--edit", f"audio:threshold={THRESHOLD}", "--margin", MARGIN, "--export", EXPORT, "-o", str(dst)]
    print(f"[watcher] {src.name} -> {dst.name}", flush=True)
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print(f"[watcher] ОШИБКА auto-editor ({res.returncode}) для {src.name}; исходник не тронут", flush=True)
        return False
    print(f"[watcher] готово: {dst}", flush=True)
    return True


def main() -> None:
    INBOX.mkdir(parents=True, exist_ok=True)
    OUT_XML.mkdir(parents=True, exist_ok=True)
    print(f"[watcher] слежу за {INBOX}, XML кладу в {OUT_XML}, отступ {MARGIN}, порог {THRESHOLD}, экспорт {EXPORT}", flush=True)
    seen: set = set()
    while True:
        for src in sorted(INBOX.iterdir()):
            if not src.is_file() or src.suffix.lower() not in EXTS:
                continue
            key = (src.name, src.stat().st_size)
            if key in seen or (OUT_XML / f"{src.stem}_cut.{EXT}").exists():
                seen.add(key)
                continue
            if not size_is_stable(src):
                continue
            process(src)
            seen.add(key)
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
