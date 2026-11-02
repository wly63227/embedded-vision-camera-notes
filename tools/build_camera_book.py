"""Generate one Markdown reader and a source-only downloadable zip."""
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/camera"
ORDER = ["guide", "hardware", "syllabus", "00-start", "01-electricity", "02-c",
         "03-toolchain", "04-gpio-time", "05-pwm", "06-protocol", "07-python-camera",
         "08-vision", "09-control-composition", "10-photography", "11-recognition",
         "12-integration", "13-edge", "labs", "exercises", "answers", "knowledge",
         "project", "troubleshooting", "glossary", "learning-log", "sources"]
LINK = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)")


def rebase(match, source):
    label, target = match.groups()
    if target.startswith(("https://", "http://", "mailto:", "#")):
        return match.group(0)
    path, marker, fragment = target.partition("#")
    relative = (source.parent / path).resolve().relative_to(ROOT).as_posix()
    return f"[{label}]({relative}{marker}{fragment})"


def main():
    pieces = ["# 嵌入式视觉与云台相机系统学习笔记\n\n"
              "> 由 docs/camera/ 正文自动生成。零基础、实操优先；首批预算 300～500 元。\n"]
    for name in ORDER:
        path = SOURCE / f"{name}.md"
        pieces.append(LINK.sub(lambda match: rebase(match, path), path.read_text(encoding="utf-8")))
    book = ROOT / "嵌入式视觉与云台相机学习笔记.md"
    book.write_text("\n\n---\n\n".join(pieces) + "\n", encoding="utf-8")
    output = ROOT / "dist/embedded-vision-camera-notes.zip"
    output.parent.mkdir(exist_ok=True)
    excluded = {".git", ".venv", "build", "dist", "__pycache__", "datasets", "captures"}
    count = 0
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(ROOT.rglob("*")):
            relative = path.relative_to(ROOT)
            if not path.is_file() or any(part in excluded for part in relative.parts):
                continue
            if relative.parts[0] == "results" and path.name not in {"validation.json", "simulation.csv"}:
                continue
            if path.suffix in {".pyc", ".exe", ".o", ".obj"}:
                continue
            archive.write(path, relative.as_posix())
            count += 1
    print(f"Generated {book.name}: {len(ORDER)} sections, {book.stat().st_size} bytes")
    print(f"Packaged {count} source files: {output}")


if __name__ == "__main__":
    main()
