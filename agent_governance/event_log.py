"""JSONL helpers for sandbox agent traces."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .schemas import AgentEvent, AgentTrace


def events_to_jsonl(events: Iterable[AgentEvent]) -> str:
    return "\n".join(json.dumps(event.as_dict(), ensure_ascii=False, sort_keys=True) for event in events)


def events_from_jsonl(text: str) -> list[AgentEvent]:
    events: list[AgentEvent] = []
    for line in text.splitlines():
        if line.strip():
            events.append(AgentEvent.from_dict(json.loads(line)))
    return events


def write_trace_jsonl(trace: AgentTrace, path: str | Path) -> None:
    Path(path).write_text(events_to_jsonl(trace.events) + "\n", encoding="utf-8")


def read_trace_jsonl(trace_id: str, description: str, path: str | Path) -> AgentTrace:
    return AgentTrace(
        trace_id=trace_id,
        description=description,
        events=events_from_jsonl(Path(path).read_text(encoding="utf-8")),
    )
