---
date: 2026-02-13
topic: kai-agentic-context-platform
status: approved
---

# KAI Agentic Context Platform

## What We're Building
Build KAI v1 as an agentic context platform for analyst teams, inspired by NAO's context-first model and grounded in KAI's existing agent stack. The product focus is a shared, versioned context layer that combines business rules, semantic metadata, verified SQL, mission playbooks, and evaluation cases as reusable assets.

This context layer powers both CLI and UI from day one with full parity. Analysts can run full-autopilot analysis missions that proactively explore hypotheses, execute multi-step analytics, and produce reusable artifacts (verified SQL and notebook outputs) that feed future runs.

## Why This Approach
Approach C was selected because the target outcomes are reliability and reuse, not only richer agent behavior. KAI already has strong primitives (memory, verified SQL tooling, notebooks, streaming agent execution, audit logs), but they are not yet unified into a single analyst-facing context operating model.

A context-platform-first direction creates a stable base for proactive autonomy while preserving trust. It also aligns with the NAO pattern where context quality and testability are first-class, allowing proactive analysis to scale without drifting behavior.

## Key Decisions
- **Chosen direction:** Approach C (Full Agentic Context Platform), not a narrow feature patch.
- **Primary user:** Data analyst teams as the first-class operator persona.
- **Primary success metrics:** `>=90%` pass rate on curated analyst evaluation suites and `>=70%` reuse of agent outputs (verified SQL and notebooks).
- **Surface area:** Full CLI and UI parity in v1 rather than CLI-first rollout.
- **Default autonomy:** Full autopilot by default for multi-step analyst missions.
- **Core product shape:** "Context as assets" is the center; proactive missions are built on top of it.

## Open Questions
- What is the canonical context asset structure in KAI (folders, schemas, ownership model)?
- What exact event defines "reuse" for KPI tracking (copy, rerun, reference, or approved publish)?
- What guardrails are mandatory for full autopilot in production analyst workflows?
- What is the minimum gold evaluation corpus needed to make `>=90%` meaningful?
- How should context updates be reviewed and promoted (draft, verified, published)?

## Next Steps
→ Run `/workflows:plan` to define implementation phases, delivery slices, and verification gates.
