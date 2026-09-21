根据目前官方 Codex Hooks 档，`UserPromptSubmit` 和 `Stop` 都明确提供 `turn_id`，所以你的 Concept Guard 可以使用 `session_id + turn_id` 作为 provenance 定位。每个 command hook 都通过 stdin 接收 JSON；Hook 运行时的工作目录是该 session 的 `cwd`。

```text
hooks.json
```

负责告诉 Codex “什么时候运行 Hook”。

```text
hooks/concept_context.py
```

负责读取 Codex 给它的事件 JSON，然后把 `session_id` / `turn_id` 保存下来。

```text
current-context.json
```

是一个临时 sidecar，供 Concept Guard Skill 读取。

### 1. hooks.json

你的 Windows 项目可以先写成：

```json
{
  "description": "Concept Guard runtime context",
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python \"$(git rev-parse --show-toplevel)/.codex/hooks/concept_context.py\""
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python \"$(git rev-parse --show-toplevel)/.codex/hooks/concept_context.py\""
          }
        ]
      }
    ]
  }
}
```

不过这里有一个 Windows 兼容性问题：官方支持专门的 `commandWindows` 覆盖项。([OpenAI Developers][2])

所以如果你的 Codex 环境对上面这个 shell 命令解析不理想，我更建议明确写 Windows 版本，例如：

```json
{
  "description": "Concept Guard runtime context",
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python \".codex/hooks/concept_context.py\"",
            "commandWindows": "python \".codex/hooks/concept_context.py\""
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python \".codex/hooks/concept_context.py\"",
            "commandWindows": "python \".codex/hooks/concept_context.py\""
          }
        ]
      }
    ]
  }
}
```

实际上，如果 Hook 总是在 session `cwd` 中执行，那么这个相对路径就可以工作；官方文档也说明命令以 session 的 `cwd` 作为工作目录。只是如果 Codex 从子目录启动，你要注意 Hook 文件路径是否稳定。官方推荐 Git-root 路径就是为了避免这个问题。([OpenAI Developers][1])

### 2. concept_context.py

代码其实非常简单：

```python
from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> None:
    event = json.load(sys.stdin)

    cwd = Path(event["cwd"])
    codex_dir = cwd / ".codex"
    context_file = codex_dir / "current-context.json"

    codex_dir.mkdir(parents=True, exist_ok=True)

    context = {
        "session_id": event.get("session_id"),
        "turn_id": event.get("turn_id"),
        "hook_event_name": event.get("hook_event_name"),
        "transcript_path": event.get("transcript_path"),
    }

    context_file.write_text(
        json.dumps(context, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    event_name = event.get("hook_event_name")

    # Stop hook requires JSON output.
    if event_name == "Stop":
        print(json.dumps({"continue": True}))


if __name__ == "__main__":
    main()
```

这里最重要的是：

```python
event = json.load(sys.stdin)
```

这就是前面说的“事件 JSON”。

例如 Codex 在 `UserPromptSubmit` 时可能把：

```json
{
  "session_id": "abc123",
  "turn_id": "turn456",
  "cwd": "D:\\Annotation",
  "hook_event_name": "UserPromptSubmit",
  "prompt": "$concept-guard ..."
}
```

传给这个 Python 程序。

你的脚本取出：

```python
event["session_id"]
event["turn_id"]
event["cwd"]
```

然后写到：

```text
current-context.json
```

### 3. current-context.json

运行之后就会得到：

```json
{
  "session_id": "abc123",
  "turn_id": "turn456",
  "hook_event_name": "UserPromptSubmit",
  "transcript_path": "..."
}
```

于是 Skill 不需要“知道 Codex 的内部变量”，它只需要读取：

```text
.codex/current-context.json
```

然后：

```json
{
  "introduced": {
    "session_id": "abc123",
    "turn_id": "turn456",
    "wording": "..."
  }
}
```

### 4. Concept Guard 的职责

这样之后，你的 Skill 就不要再关心“Codex 怎么获得 ID”。

这样职责非常干净：

```text
Codex
  │
  │ event JSON
  ▼
Hook
  │
  │ session_id / turn_id
  ▼
.codex/current-context.json
  │
  │ read by Skill
  ▼
Concept Guard
  │
  ▼
.concept-guard.json
```
