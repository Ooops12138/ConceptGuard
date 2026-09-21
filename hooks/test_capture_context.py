import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent))
from capture_context import main


class CaptureContextTests(unittest.TestCase):
    def test_writes_current_and_turn_scoped_context(self):
        with tempfile.TemporaryDirectory() as directory:
            event = {
                "cwd": directory,
                "session_id": "session-1",
                "turn_id": "turn-2",
                "hook_event_name": "UserPromptSubmit",
                "transcript_path": "transcript.jsonl",
            }
            with patch("sys.stdin", __import__("io").StringIO(json.dumps(event))):
                self.assertEqual(main(), 0)

            root = Path(directory) / ".codex" / "concept-guard"
            current = json.loads((root / "current-context.json").read_text())
            archived = json.loads(
                (root / "turns" / "session-1" / "turn-2.json").read_text()
            )
            self.assertEqual(current["session_id"], "session-1")
            self.assertEqual(current["turn_id"], "turn-2")
            self.assertEqual(archived, current)

    def test_stop_emits_continue(self):
        with tempfile.TemporaryDirectory() as directory:
            event = {
                "cwd": directory,
                "session_id": "session-1",
                "turn_id": "turn-3",
                "hook_event_name": "Stop",
            }
            with patch("sys.stdin", __import__("io").StringIO(json.dumps(event))):
                self.assertEqual(main(), 0)


if __name__ == "__main__":
    unittest.main()
