from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any


def atomic_write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main() -> int:
    try:
        event = json.load(sys.stdin)
        cwd = Path(event["cwd"]).resolve()
    except (json.JSONDecodeError, KeyError, TypeError, OSError) as error:
        print(f"concept-guard: invalid hook input: {error}", file=sys.stderr)
        return 0

    session_id = event.get("session_id")
    turn_id = event.get("turn_id")
    context = {
        "session_id": session_id,
        "turn_id": turn_id,
        "hook_event_name": event.get("hook_event_name"),
        "transcript_path": event.get("transcript_path"),
        "cwd": str(cwd),
    }
    state_dir = cwd / ".codex" / "concept-guard"
    atomic_write(state_dir / "current-context.json", context)

    if session_id and turn_id:
        atomic_write(
            state_dir / "turns" / str(session_id) / f"{turn_id}.json",
            context,
        )

    if event.get("hook_event_name") == "Stop":
        print(json.dumps({"continue": True}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
