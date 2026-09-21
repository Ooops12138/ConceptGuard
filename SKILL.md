
---
name: concept-guard
description: Track high-confidence architecture-level and reusable user-facing concept proposals, with concise provenance, when explicitly invoked; exclude ordinary implementation details.
---
# Concept Guard

Use this for the current thread after an explicit `$concept-guard` invocation. Do not create `.concept-guard.json` unless a qualifying concept must be recorded.

## Detect

Record an agent-introduced concept only when **both** conditions hold:

- The agent gives it a reusable, named identity.
- The agent presents it as a proposal intended to shape the solution and, if adopted, it would establish or change at least one durable project concern:

  - module boundaries, responsibilities, lifecycle, ownership, or a cross-module contract;
  - a user-facing interaction model or recurring workflow;
  - domain vocabulary or a stable user-visible behavior contract.

Do not record implementation details merely because they are named or reusable,
including functions, variables, flags, prompts, filenames, and one-off choices.

Named classes, models, DTOs, schemas, and query/filter objects qualify only when
the agent presents them as durable domain concepts or cross-module contracts.

Only agent-introduced concepts are eligible. Do not infer concepts retrospectively or create names the agent did not use.

## Self-Audit

**Mandatory before every final response.**

Review the agent-authored content of the current turn and ask:

1. Did I introduce any new named, reusable concept?
2. Does it satisfy both `Detect` conditions?
3. Did I meaningfully reuse an existing concept?

Record or update the registry before sending the final response.

If nothing qualifies, do nothing.

## Record

If you need to record or update a concept, read `<project-root>/.concept-guard.json` if it exists. Do not create it otherwise. When the first qualifying record is needed, create it with this shape and assign the next `C-###` id:

```json
{
  "concepts": [
    {
      "id": "C-001",
      "name": "...",
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
- The recorded concept name must be directly grounded in the agent's wording; do not invent or retrospectively abstract a concept name that the agent did not propose.
- Change `proposed` to `established` only after the user explicitly accepts that record. Set `established` to `{ "by": "user", "at": "YYYY-MM-DD / short task", "wording": "..." }`.
- When an existing record is used again in a later task, append one short `{ "at": "YYYY-MM-DD / short task", "wording": "..." }` entry to `reused_in`. Add at most one entry per concept per task.
- Set `derived_from` only when the agent explicitly presents the new record as derived from one existing record. It holds one parent id; never infer it, add relation types, or use multiple parents.
- Never establish, merge, rename, or infer concepts from repetition or assumed agreement.

## End Of Task

In the final response, include only nonempty sections from this list:

```text
New concepts introduced
- <name> (<status>)

Unconfirmed concepts later reused
- <name>
```

If this task created or reused any concept record, the final response must include every applicable nonempty section below. Never omit applicable reports when a record was created or reused.
