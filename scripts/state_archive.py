#!/usr/bin/env python3
"""Inspect and prepare non-destructive state-archive operations."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import shutil
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


DEFAULT_LINE_THRESHOLD = 2_000
DEFAULT_BYTE_THRESHOLD = 256 * 1024
DEFAULT_GROWTH_PERCENT = 25
ARCHIVE_STATUS = re.compile(r"^\s*archive_status:\s*(\w+)\s*$", re.MULTILINE)
WORK_STATUS = re.compile(r"^\s*work_status:\s*(\w+)\s*$", re.MULTILINE)
TASK_HEADING = re.compile(r"^###\s+Task\s+([A-Za-z0-9][A-Za-z0-9._-]*)", re.MULTILINE)
RETENTION_FIELD = re.compile(r"^\s*(reviewed_bytes|reviewed_lines):\s*(\d+)\s*$", re.MULTILINE)


@dataclass
class Counts:
    files: int
    lines: int
    bytes: int


@dataclass
class RetentionState:
    threshold_lines: int
    threshold_bytes: int
    archive: Counts
    threshold_reached: bool
    review_required: bool
    reviewed_bytes: int | None
    reviewed_lines: int | None
    reason: str


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def count_files(paths: list[Path]) -> Counts:
    lines = byte_count = files = 0
    for path in paths:
        if not path.is_file():
            continue
        data = path.read_bytes()
        files += 1
        byte_count += len(data)
        lines += data.count(b"\n") + (1 if data and not data.endswith(b"\n") else 0)
    return Counts(files=files, lines=lines, bytes=byte_count)


def regular_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(path for path in root.rglob("*") if path.is_file())


def read_retention(archive_root: Path) -> tuple[int | None, int | None]:
    marker = archive_root / "retention.md"
    if not marker.is_file():
        return None, None
    values = {name: int(value) for name, value in RETENTION_FIELD.findall(marker.read_text(encoding="utf-8"))}
    return values.get("reviewed_bytes"), values.get("reviewed_lines")


def retention_state(
    archive_root: Path,
    line_threshold: int = DEFAULT_LINE_THRESHOLD,
    byte_threshold: int = DEFAULT_BYTE_THRESHOLD,
    growth_percent: int = DEFAULT_GROWTH_PERCENT,
) -> RetentionState:
    archive_files = [
        path
        for path in regular_files(archive_root)
        if path.resolve() != (archive_root / "retention.md").resolve()
    ]
    archive = count_files(archive_files)
    reached = archive.lines >= line_threshold or archive.bytes >= byte_threshold
    reviewed_bytes, reviewed_lines = read_retention(archive_root)
    if archive.files == 0:
        return RetentionState(line_threshold, byte_threshold, archive, False, False, reviewed_bytes, reviewed_lines, "archive-empty")
    if not reached:
        return RetentionState(line_threshold, byte_threshold, archive, False, False, reviewed_bytes, reviewed_lines, "below-threshold")
    if reviewed_bytes is None or reviewed_lines is None:
        return RetentionState(line_threshold, byte_threshold, archive, True, True, reviewed_bytes, reviewed_lines, "threshold-first-reached")
    growth_factor = 1 + growth_percent / 100
    due = archive.bytes >= reviewed_bytes * growth_factor or archive.lines >= reviewed_lines * growth_factor
    return RetentionState(
        line_threshold,
        byte_threshold,
        archive,
        True,
        due,
        reviewed_bytes,
        reviewed_lines,
        "growth-since-review" if due else "reviewed-watermark-current",
    )


def task_records(todo_path: Path) -> list[dict[str, str]]:
    if not todo_path.is_file():
        return []
    text = todo_path.read_text(encoding="utf-8")
    headings = list(TASK_HEADING.finditer(text))
    records: list[dict[str, str]] = []
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        block = text[heading.start():end]
        work = WORK_STATUS.search(block)
        archive = ARCHIVE_STATUS.search(block)
        records.append(
            {
                "task_id": heading.group(1),
                "work_status": work.group(1) if work else "missing",
                "archive_status": archive.group(1) if archive else "missing",
            }
        )
    return records


def pending_reviews(todo_path: Path) -> list[dict[str, str]]:
    return [
        record
        for record in task_records(todo_path)
        if record["work_status"] == "completed" and record["archive_status"] == "pending_review"
    ]


def collect_inventory(root: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for path in regular_files(root):
        relative = path.relative_to(root)
        text = path.read_text(encoding="utf-8", errors="replace")
        headings = []
        offset = 0
        for line_number, line in enumerate(text.splitlines(), start=1):
            if re.match(r"^#{1,4}\s+", line):
                headings.append({"line": line_number, "text": line})
            offset += len(line) + 1
        records.append(
            {
                "path": str(relative),
                "bytes": path.stat().st_size,
                "lines": text.count("\n") + (1 if text and not text.endswith("\n") else 0),
                "sha256": sha256(path),
                "headings": headings,
            }
        )
    return records


def prepare_session(
    session_id: str,
    source: Path,
    archive_root: Path,
    apply: bool,
    confirmation: str | None,
) -> dict[str, object]:
    if not re.fullmatch(r"[A-Za-z0-9._-]+", session_id):
        raise ValueError("session-id may contain only letters, digits, dot, underscore, and hyphen")
    files = regular_files(source)
    if not files:
        raise ValueError(f"source contains no regular files: {source}")
    destination = archive_root / dt.date.today().strftime("%Y-%m") / session_id
    if destination.exists():
        raise ValueError(f"archive destination already exists: {destination}")
    entries = [
        {
            "source": str(path),
            "archive": str(destination / "snapshot" / path.relative_to(source)),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for path in files
    ]
    result: dict[str, object] = {
        "dry_run": not apply,
        "session_id": session_id,
        "source": str(source),
        "destination": str(destination),
        "files": entries,
        "deletes_source": False,
    }
    if not apply:
        return result
    if confirmation != session_id:
        raise ValueError("applying requires --confirm-session with the exact session-id")
    snapshot = destination / "snapshot"
    snapshot.mkdir(parents=True)
    for path in files:
        target = snapshot / path.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    manifest_lines = [
        f"# Archive Manifest — {session_id}",
        "",
        f"- Created: {dt.datetime.now().astimezone().isoformat(timespec='seconds')}",
        f"- Source: `{source}`",
        f"- Archive: `{destination}`",
        "- Deletes source: `no`",
        "",
        "## Files",
        "",
        "| Source | Archive | Bytes | SHA-256 |",
        "|---|---|---:|---|",
    ]
    for entry in entries:
        manifest_lines.append(
            f"| `{entry['source']}` | `{entry['archive']}` | {entry['bytes']} | `{entry['sha256']}` |"
        )
    (destination / "manifest.md").write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")
    result["manifest"] = str(destination / "manifest.md")
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".agent", help="agent state root (default: .agent)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    status = subparsers.add_parser("status", help="report hot/archive metrics and retention state")
    status.add_argument("--json", action="store_true")
    status.add_argument("--line-threshold", type=int, default=DEFAULT_LINE_THRESHOLD)
    status.add_argument("--byte-threshold", type=int, default=DEFAULT_BYTE_THRESHOLD)
    status.add_argument("--growth-percent", type=int, default=DEFAULT_GROWTH_PERCENT)

    inventory = subparsers.add_parser("inventory", help="print a read-only state inventory")
    inventory.add_argument("--json", action="store_true")
    inventory.add_argument("--output", help="write JSON inventory to this path")

    check_todo = subparsers.add_parser("check-todo", help="report explicit archive-state fields and pending reviews")
    check_todo.add_argument("--json", action="store_true")

    prepare = subparsers.add_parser("prepare-session", help="plan or copy a reviewed session into the archive")
    prepare.add_argument("--session-id", required=True)
    prepare.add_argument("--source", default=".agent/state")
    prepare.add_argument("--archive-root", default=".agent/archive")
    prepare.add_argument("--apply", action="store_true")
    prepare.add_argument("--confirm-session")
    prepare.add_argument("--json", action="store_true")
    return parser


def print_json(value: object) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.root)
    hot = count_files(regular_files(root / "state"))
    archive_root = root / "archive"

    if args.command == "status":
        retention = retention_state(
            archive_root,
            line_threshold=args.line_threshold,
            byte_threshold=args.byte_threshold,
            growth_percent=args.growth_percent,
        )
        result = {
            "hot_state": asdict(hot),
            "archive": asdict(retention.archive),
            "pending_reviews": pending_reviews(root / "state" / "todo.md"),
            "retention": asdict(retention),
        }
        if args.json:
            print_json(result)
        else:
            print(f"hot_state files={hot.files} lines={hot.lines} bytes={hot.bytes}")
            print(
                f"archive files={retention.archive.files} lines={retention.archive.lines} "
                f"bytes={retention.archive.bytes}"
            )
            print(f"pending_reviews={len(result['pending_reviews'])}")
            print(
                f"retention threshold_lines={retention.threshold_lines} "
                f"threshold_bytes={retention.threshold_bytes} reached={retention.threshold_reached} "
                f"review_required={retention.review_required} reason={retention.reason}"
            )
        return 0

    if args.command == "inventory":
        records = collect_inventory(root)
        payload = {"root": str(root), "files": records}
        if args.output:
            destination = Path(args.output)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if args.json or not args.output:
            print_json(payload)
        else:
            print(f"inventory_files={len(records)} output={args.output}")
        return 0

    if args.command == "check-todo":
        records = task_records(root / "state" / "todo.md")
        reviews = [r for r in records if r["work_status"] == "completed" and r["archive_status"] == "pending_review"]
        missing = [r for r in records if "missing" in (r["work_status"], r["archive_status"])]
        payload = {"tasks": records, "pending_reviews": reviews, "records_with_missing_fields": missing}
        if args.json:
            print_json(payload)
        else:
            print(f"tasks={len(records)} pending_reviews={len(reviews)} missing_fields={len(missing)}")
            for record in reviews:
                print(f"pending_review {record['task_id']}")
        return 0

    if args.command == "prepare-session":
        result = prepare_session(
            args.session_id,
            Path(args.source),
            Path(args.archive_root),
            args.apply,
            args.confirm_session,
        )
        if args.json:
            print_json(result)
        else:
            print(f"dry_run={result['dry_run']} session={result['session_id']} files={len(result['files'])}")
            print(f"source={result['source']}")
            print(f"destination={result['destination']}")
            print("deletes_source=false")
            if "manifest" in result:
                print(f"manifest={result['manifest']}")
        return 0

    return 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(2)
