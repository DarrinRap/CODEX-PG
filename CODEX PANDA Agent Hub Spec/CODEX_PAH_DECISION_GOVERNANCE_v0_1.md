# PANDA Agent Hub Decision Governance v0.1

Generated: 2026-04-26 19:15:00 -07:00
Status: Darrin direction accepted

## Core Rule

Darrin does not want to be the decision maker for implementation-detail questions where Codex, Claude Desktop, and Claude Code / CC are better qualified.

For technical architecture, schemas, lint rules, routing, safety mechanics, bridge mechanics, and implementation sequencing, PAH should collect agent opinions and produce a recommendation. Darrin will generally follow the recommendation.

## Decisions Agents Should Vote/Recommend On

Codex, Claude Desktop, and Claude Code / CC should decide or recommend:

- message schema fields
- route/inbox naming
- thread status model
- lint integration strategy
- atomic write mechanics
- idempotency mechanics
- watcher implementation
- headless Claude Code safety mechanics
- hook rollout sequence
- direct API adapter sequencing
- validation rules
- implementation roadmap ordering
- code organization
- test strategy

For these topics, PAH should not block waiting for Darrin unless:

- the agents disagree and cannot converge
- the decision changes product behavior Darrin will experience
- the decision creates new cost, privacy, or safety exposure
- the decision authorizes a protected action

## Decisions Darrin Must Be Consulted On

Darrin must be consulted on:

- UX appearance
- UX functionality
- workflow feel
- what the app should make easy or hard
- what deserves phone/SMS interruption
- dental terminology
- dental workflow assumptions
- clinical/dental correctness
- whether a feature is actually useful
- any action involving PHI or patient data
- any action involving external communication
- any write to `C:\panda-gallery`
- any commit/push or publishing action
- any paid API or SMS provider setup

## Recommended Agent Voting Model

For technical decisions, use this model:

1. Codex states a proposed decision.
2. Claude Desktop reviews for product/process/design-system coherence.
3. Claude Code / CC reviews for implementation practicality and repo/tooling risk.
4. If all three agree, PAH marks the recommendation as accepted.
5. If two agree and one dissents, PAH records the dissent and either:
   - follows the majority for low-risk technical decisions, or
   - escalates to Darrin if the dissent involves UX, dental, safety, cost, or protected actions.
6. If all three disagree or the decision affects Darrin-facing workflow, escalate to Darrin with options and a recommendation.

## Darrin Decision Queue Rule

PAH should keep Darrin's decision queue focused on questions only Darrin can answer.

Do not put purely technical questions in Darrin's queue if the agents can decide them.

Do put questions in Darrin's queue when they involve:

- UX appearance/functionality
- dental/product judgment
- safety boundary
- cost or credentials
- external communication
- write/publish approval

## Practical Consequence For Current PAH Decisions

The following current PAH questions should be agent-decided unless they create safety exposure:

- schema additions from CC
- Claude Code inbox final name
- atomic write design
- lint integration mode
- idempotency design
- quarantine behavior
- route table implementation

The following require Darrin consultation:

- what phone/SMS events are worth interrupting him
- whether PAH should feel like a dense developer cockpit or a simpler command center
- any dental workflow language or assumptions
- any future UI appearance/functionality decisions
- any permission to let PAH or Claude Code write to `C:\panda-gallery`
