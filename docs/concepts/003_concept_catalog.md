# 003 — Concept Catalog

## Purpose

Define the initial concept catalog for the conversation analysis application.

This catalog is a starting point. Concepts should be refined through use, challenge, and composition analysis.

---

# Recording

## Purpose

Capture raw conversation input that may be converted into a transcript.

## Operational Principle

The user provides a recording. The system stages it long enough to transcribe it. After transcription, the recording is deleted according to the retention rule unless the user explicitly chooses otherwise.

## Invariants

- Recording is not the durable product center.
- Recording must not be retained silently.
- Recording must not appear in logs.
- Recording retention must be visible to the user.

---

# Transcript

## Purpose

Represent the conversation in text form for analysis, reflection, evidence, and longitudinal use.

## Operational Principle

The system creates or accepts a transcript, segments it into speakers and turns, and allows the user to review and correct it before analysis.

## Invariants

- Transcript text is sensitive.
- Transcript should be encrypted when retained.
- Transcript should be owner-scoped.
- Transcript should be editable before analysis.
- Analysis should bind to a transcript version.

---

# Transcript Version

## Purpose

Preserve evidence integrity when transcripts change.

## Operational Principle

When a transcript is analyzed, that analysis binds to a specific transcript version. Later edits create a new version rather than mutating the evidence basis of old reports.

## Invariants

- Old reports must resolve old evidence.
- Quote IDs are scoped to a transcript version.
- Version changes must be visible to the user.

---

# Evidence Quote

## Purpose

Connect findings to exact transcript text.

## Operational Principle

A finding cites concise quote spans from a transcript version. The user can expand the evidence to see surrounding context.

## Invariants

- Evidence should be concise by default.
- Evidence must reference transcript version.
- Evidence should preserve speaker identity.
- Evidence must not silently drift after edits.

---

# Reflection Run

## Purpose

Generate structured reflection from a transcript using one or more analysis lenses.

## Operational Principle

The user selects a transcript and analysis depth. The system runs selected lenses and produces findings, confidence levels, evidence links, and a synthesis.

## Invariants

- Run must bind to transcript version.
- Run must preserve module/lens provenance.
- Run should not be executed twice accidentally.

---

# Lens

## Purpose

Apply a particular analytical perspective to a transcript.

## Operational Principle

A lens examines transcript evidence through a bounded framework such as communication analysis, CBT-style cognitive reflection, DBT-style emotion regulation reflection, behavior analysis, mediation, NVC, systems thinking, attachment-informed interaction, or safety-aware review.

## Invariants

- Lens must declare its purpose.
- Lens must declare inference limits.
- Lens must avoid diagnosis.
- Lens output must cite evidence.
- Lens output must preserve confidence.

---

# Psychological Hypothesis

## Purpose

Allow a user or analysis lens to consider possible psychological explanations without diagnosing.

## Operational Principle

A hypothesis is treated as a reflection context. The system examines whether transcript evidence is consistent with, inconsistent with, or insufficient for that hypothesis.

## Examples

- avoidant withdrawal
- emotional dysregulation
- fear of abandonment
- fear of engulfment
- splitting-like language
- narcissistic injury hypothesis
- schizoid distancing hypothesis
- trauma-related reactivity hypothesis
- cognitive distortion hypothesis

## Invariants

- A hypothesis is not a diagnosis.
- A hypothesis must be evidence-limited.
- A hypothesis should invite reflection, not label a person.
- A hypothesis must include alternatives where possible.

---

# Finding

## Purpose

State one evidence-backed insight.

## Operational Principle

A finding summarizes a pattern, event, behavior, or reflection point and links to concise evidence, confidence, lens source, and limitations.

## Invariants

- Finding must cite evidence unless explicitly a limitation or uncertainty.
- Finding must include confidence.
- Finding must avoid diagnostic certainty.
- Finding should be inspectable and reviewable.

---

# Confidence

## Purpose

Indicate how strongly a claim is supported.

## Operational Principle

Every finding and major graph relationship receives a confidence level based on evidence strength, specificity, repetition, and inference depth.

## Suggested Levels

- observed
- likely
- possible
- insufficient evidence
- contraindicated

## Invariants

- High confidence requires direct evidence.
- Psychological interpretation should usually be lower confidence.
- Diagnostic claims are not allowed regardless of confidence.

---

# Reflection Point

## Purpose

Identify a place where the user may consider changing, clarifying, repairing, regulating, or further exploring behavior.

## Operational Principle

A reflection point converts evidence-backed findings into non-prescriptive self-review prompts.

## Invariants

- Reflection points are not commands.
- Reflection points are not clinical treatment instructions.
- Reflection points should link to findings/evidence.
- Reflection points should be framed for self-awareness.

---

# Reasoning Graph

## Purpose

Represent relationships between findings, constructs, evidence, lenses, hypotheses, and reflection points.

## Operational Principle

The system creates structured nodes and typed edges so synthesis is based on inspectable relationships rather than unstructured prose.

## Invariants

- Nodes should be evidence-backed where possible.
- Edges should have rationale and confidence.
- Graph relationships must not overstate causality.
- Graph should support longitudinal comparison.

---

# Case

## Purpose

Group related transcripts for longitudinal reflection.

## Operational Principle

The user explicitly assigns transcripts to a case. The system compares evidence-backed patterns over time while preserving transcript/version identity.

## Invariants

- Case is opt-in.
- Case evidence must identify source transcript and version.
- Recurrence claims require more than one transcript.
- Case should support deletion/export.

---

# Retention Rule

## Purpose

Control what data is kept, for how long, and why.

## Operational Principle

Each artifact has a retention policy. Audio is short-lived by default. Transcripts and reports are retained only according to user choice, case membership, or explicit settings.

## Invariants

- Retention should be visible.
- Deletion should be supported.
- Sensitive data should not persist accidentally.
- Longitudinal value must be balanced against minimization.

---

# Privacy Boundary

## Purpose

Define who or what can access sensitive content.

## Operational Principle

The application treats recordings, transcripts, evidence, analysis outputs, cases, and exports as private by default. Access requires authentication and ownership.

## Invariants

- Logs must not contain transcript bodies.
- Frontend must not contain secrets.
- Internal services should have least privilege.
- Exports should be deliberate user actions.

---

# Cost State

## Purpose

Keep personal operating cost minimal while preserving the ability to wake and use the system.

## Operational Principle

The system has explicit availability states: asleep, waking, active, idle pending, and shutting down. Personal mode aggressively sleeps. Enterprise mode may later change the availability policy.

## Invariants

- Sleep/wake should not corrupt jobs.
- User should understand when the system is waking.
- Cost controls should not be mixed with analysis logic.
- Availability policy should be configurable by deployment mode.
