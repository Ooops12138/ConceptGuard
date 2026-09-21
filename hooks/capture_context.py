from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any


def diagnostic_log(path: Path, message: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(f"{message}\n")


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
    event: dict[str, Any]
    try:
        payload = json.load(sys.stdin)
        if not isinstance(payload, dict):
            raise TypeError("hook event must be a JSON object")
        raw_cwd = payload.get("cwd")
        if not isinstance(raw_cwd, str) or not raw_cwd.strip():
            raise ValueError("hook event must contain a non-empty string cwd")
        event = payload
        cwd = Path(raw_cwd).resolve()
    except (json.JSONDecodeError, TypeError, ValueError, OSError) as error:
        print(f"concept-guard: invalid hook input: {error}", file=sys.stderr)
        return 1

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
    try:
        atomic_write(state_dir / "current-context.json", context)

        if session_id and turn_id:
            atomic_write(
                state_dir / "turns" / str(session_id) / f"{turn_id}.json",
                context,
            )
    except (OSError, TypeError, ValueError) as error:
        message = f"concept-guard: failed to write context in {state_dir}: {error}"
        print(message, file=sys.stderr)
        try:
            diagnostic_log(state_dir / "hook.log", message)
        except OSError:
            pass
        return 1

    try:
        diagnostic_log(
            state_dir / "hook.log",
            f"hook={event.get('hook_event_name')} cwd={cwd} "
            f"session_id={session_id} turn_id={turn_id}",
        )
    except OSError as error:
        print(f"concept-guard: failed to write diagnostic log: {error}", file=sys.stderr)

    if event.get("hook_event_name") == "Stop":
        print(json.dumps({"continue": True}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
