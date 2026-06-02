from __future__ import annotations

import json
from pathlib import Path

from .six_axes import SixAxisSnapshot


def persist_snapshots(snapshots: list[dict], directory: str | Path) -> list[Path]:
    target_dir = Path(directory)
    target_dir.mkdir(parents=True, exist_ok=True)

    paths: list[Path] = []
    for snapshot in snapshots:
        snapshot_id = str(snapshot.get("snapshot_id", f"snap-{len(paths)}"))
        path = target_dir / f"{snapshot_id}.json"
        path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
        paths.append(path)
    return paths


def load_snapshots(directory: str | Path) -> list[SixAxisSnapshot]:
    target_dir = Path(directory)
    snapshots: list[SixAxisSnapshot] = []
    for path in sorted(target_dir.glob("*.json")):
        snapshots.append(SixAxisSnapshot.from_dict(json.loads(path.read_text(encoding="utf-8"))))
    return snapshots


def replay_snapshots(
    snapshots: list[SixAxisSnapshot],
    start: int = 0,
    stop: int | None = None,
) -> list[dict[str, object]]:
    window = snapshots[start:stop]
    return [
        {
            "snapshot_id": snapshot.snapshot_id,
            "event_id": snapshot.event_id,
            "timestamp": snapshot.timestamp,
            "ranking": list(snapshot.assessment.ranking),
            "commit_domain": snapshot.assessment.commit_domain,
            "notes": list(snapshot.assessment.notes),
        }
        for snapshot in window
    ]
