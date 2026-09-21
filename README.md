# Concept Guard

In multi-turn collaboration, an agent continually introduces new abstractions, concepts, architectural layers, modules, and design terminology. Many suggestions seem reasonable in isolation, but users may fail to fully understand the conversation—either because they lack relevant domain knowledge or because their attention drifts after many turns (Of course humans can be attention lapses too)—and therefore cannot question or adjust the model’s output in time. The model then often assumes that the user has tacitly accepted the earlier suggestions, causing these concepts to gradually become part of the project. Eventually, concepts may accumulate, the architecture may bloat, and the project may drift from its original goal. Moreover, in long dialogue histories, users may find it hard to trace who introduced a given concept, when it was introduced, and what other concepts it later spawned.

Concept Guard is a Codex plugin containing a skill for tracking high-confidence design concepts introduced by an agent. It preserves when a potentially durable proposal first enters a project without treating the proposal as an established project fact.

## What It Records

A concept is recorded only when the agent gives it a reusable name and presents it as a proposal that, if adopted, would change module boundaries, responsibilities, lifecycle, ownership, or a cross-module contract.

Ordinary functions, variables, filenames, local algorithms, one-off implementation choices, technical terms, and descriptive nouns are excluded. When uncertain, Concept Guard does not record anything.

New agent proposals always start as `proposed`. They become `established` only after the user explicitly accepts them. Agent-authored code, documentation, repetition, or assumed agreement never establish a concept.

## Install

### For Users

Install Concept Guard from its GitHub marketplace repository:

```powershell
codex plugin marketplace add Ooops12138/ConceptGuard
codex plugin add concept-guard@concept-guard
```

The first command adds this GitHub repository as the `concept-guard`
marketplace. The second command installs the `concept-guard` plugin from that
marketplace.

### For Local Development

When editing this plugin locally, use the personal marketplace entry that points
to the local plugin source:

```powershell
codex plugin add concept-guard@personal
```

In the current local setup, that entry points to
`%USERPROFILE%\plugins\concept-guard`.

After either installation path, restart Codex or start a new thread so it
discovers the plugin's skill and hook.

The plugin bundles one skill and its lifecycle hook:

```text
skills/concept-guard/SKILL.md
hooks/hooks.json
hooks/capture_context.py
```

The hook writes:

```text
.codex/concept-guard/current-context.json
.codex/concept-guard/turns/<session_id>/<turn_id>.json
```

The second path is an immutable-by-convention archive for the turn, while the first path is the convenience file used by the skill. These files are project runtime state and should normally be added to `.gitignore`:

```gitignore
.codex/concept-guard/
.concept-guard.json
```

## Use

Invoke it explicitly at the start of work you want to supervise:

```text
$concept-guard Implement the payment failure flow. Present persistent architecture proposals for confirmation.
```

For example, an agent proposal named `Retry Policy` may be recorded immediately as `proposed` if it defines a reusable cross-module policy. Whether it is later reused is recorded separately; reuse is not required for its first appearance to be preserved.

When the user explicitly accepts it, Concept Guard updates only its status and `established` metadata. On a later task, a single concise reference is added to `reused_in` for that concept. A derived concept can name one explicit parent through `derived_from`.

At the end of a task, Concept Guard reports only nonempty sections for new concepts, new architectural abstractions, and unconfirmed concepts later reused.

## Project File

The first qualifying record creates `<project-root>/.concept-guard.json`:

```json
{
  "concepts": [
    {
      "id": "C-001",
      "name": "Retry Policy",
      "kind": "architecture",
      "status": "proposed",
      "introduced": {
        "session_id": "...",
        "turn_id": "...",
        "wording": "Introduce a Retry Policy for payment retries."
      },
      "established": null,
      "reused_in": [],
      "derived_from": null
    }
  ]
}
```

Concept Guard does not copy chat transcripts. The short `wording` fields preserve only the original proposal, explicit acceptance, or later-use reference needed for tracing.

## Hook contract

The hook does not infer or generate IDs. It reads the JSON event from stdin and
persists the IDs supplied by Codex. `turn_id` is available on turn-scoped hook
events; if an event does not contain it, the hook still writes the current
context but skips the turn archive.

For diagnostics, the hook also appends one line per invocation to
`.codex/concept-guard/hook.log`. Each line includes the hook event name, the
resolved `cwd`, and the supplied IDs. Invalid input or a write failure is
reported on stderr and returns a nonzero exit code, so a missing
`current-context.json` is no longer silently treated as success. The file is
always written under the event's `cwd`; inspect `hook.log` there first when
debugging a missing context file.

Concept Guard does not judge whether a design is overengineered. It does not
use external services, databases, vector search, or automatic evidence-based
promotion to `established`.

## License

MIT. See [LICENSE](LICENSE).
