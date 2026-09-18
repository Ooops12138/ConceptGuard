# Concept Guard

In multi-turn collaboration, an agent continually introduces new abstractions, concepts, architectural layers, modules, and design terminology. Many suggestions seem reasonable in isolation, but users may fail to fully understand the conversation—either because they lack relevant domain knowledge or because their attention drifts after many turns (Of course humans can be attention lapses too)—and therefore cannot question or adjust the model’s output in time. The model then often assumes that the user has tacitly accepted the earlier suggestions, causing these concepts to gradually become part of the project. Eventually, concepts may accumulate, the architecture may bloat, and the project may drift from its original goal. Moreover, in long dialogue histories, users may find it hard to trace who introduced a given concept, when it was introduced, and what other concepts it later spawned.

Concept Guard is an Codex Skill for tracking high-confidence design concepts introduced by an agent. It preserves when a potentially durable proposal first enters a project without treating the proposal as an established project fact.

It is intentionally small. Version 0.1 uses one project file, `.concept-guard.json`, only when there is a qualifying concept to record.

## What It Records

A concept is recorded only when the agent gives it a reusable name and presents it as a proposal that, if adopted, would change module boundaries, responsibilities, lifecycle, ownership, or a cross-module contract.

Ordinary functions, variables, filenames, local algorithms, one-off implementation choices, technical terms, and descriptive nouns are excluded. When uncertain, Concept Guard does not record anything.

New agent proposals always start as `proposed`. They become `established` only after the user explicitly accepts them. Agent-authored code, documentation, repetition, or assumed agreement never establish a concept.

## Install

Clone this repository into the local Codex Skills directory as `concept-guard`:

```powershell
git clone https://github.com/Ooops12138/ConceptGuard.git "$env:USERPROFILE\.codex\skills\concept-guard"
```

Restart Codex if it does not discover the new Skill automatically.

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
        "by": "agent",
        "at": "2026-09-18 / payment failure flow",
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

## Non-Goals

Version 0.1 does not judge whether a design is overengineered. It does not use hooks, scripts, MCP, databases, external services, vector search, multi-agent workflows, or automatic evidence-based promotion to `established`.

## License

No license has been selected yet.
