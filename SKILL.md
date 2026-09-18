---
name: concept-guard
description: Track high-confidence architecture-level concept proposals and concise provenance when explicitly invoked; exclude ordinary implementation details.
---

# Concept Guard

Use this for the current thread after an explicit `$concept-guard` invocation. Do not create `.concept-guard.json` unless a qualifying concept must be recorded.

## Detect

Record an agent-introduced concept only when **both** conditions hold:

- The agent gives it a reusable, named identity.
- The agent presents it as a proposal intended to shape the solution and, if adopted, it would add or change module boundaries, responsibilities, lifecycle, ownership, or a cross-module contract.

Do not record functions, variables, filenames, local algorithms, one-off implementation choices, ordinary technical terms, or nouns that merely describe current code. When uncertain, do not record it.

Classify a qualifying record as `architecture` only when it adds or changes a durable component, layer, boundary, or cross-module contract; otherwise use `concept`.

## Record

At the start, read `<project-root>/.concept-guard.json` if it exists. Do not create it otherwise. When the first qualifying record is needed, create it with this shape and assign the next `C-###` id:

```json
{
  "concepts": [
    {
      "id": "C-001",
      "name": "...",
      "kind": "concept",
      "status": "proposed",
      "introduced": { "by": "agent", "at": "YYYY-MM-DD / short task", "wording": "..." },
      "established": null,
      "reused_in": [],
      "derived_from": null
    }
  ]
}
```

- Every new agent proposal starts as `proposed`.
- Change `proposed` to `established` only after the user explicitly accepts that record. Set `established` to `{ "by": "user", "at": "YYYY-MM-DD / short task", "wording": "..." }`.
- Never establish a record from agent-authored code, documentation, repetition, or assumed agreement.
- When an existing record is used again in a later task, append one short `{ "at": "YYYY-MM-DD / short task", "wording": "..." }` entry to `reused_in`. Add at most one entry per concept per task.
- Set `derived_from` only when the agent explicitly presents the new record as derived from one existing record. It holds one parent id; never infer it, add relation types, or use multiple parents.
- Do not rename, merge, or create records for user-originated or pre-existing project terms in v0.1.

Before adding an unconfirmed architectural abstraction as a persistent project boundary, present it as a proposal and ask the user for concise confirmation. Do not treat the confirmation as given until the user states it.

## End Of Task

In the final response, include only nonempty sections from this list:

```text
New concepts introduced
- <name> (<status>)

New architectural abstractions
- <name> (<status>)

Unconfirmed concepts later reused
- <name>
```

Do not emit an empty report or any section with no entries.
