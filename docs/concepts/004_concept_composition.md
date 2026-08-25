# 004 — Concept Composition

## Purpose

Describe how concepts combine and where tensions appear.

Good concepts are not enough individually. They must compose without producing surprising, unsafe, expensive, or misleading behavior.

---

# Recording + Transcript + Retention Rule

The user uploads or records audio. The system stages the recording, transcribes it, and produces a transcript. The recording is deleted according to the audio retention rule.

## Tension

Recording is useful but highly sensitive.

## Design Resolution

Audio should be ephemeral by default. The transcript, not the recording, becomes the durable artifact if the user chooses retention.

---

# Transcript + Transcript Version + Evidence Quote

The transcript is prepared and analyzed. Evidence quotes are created against a specific transcript version. Later edits create a new version.

## Desired Behavior

```text
Transcript v1
→ Evidence Q001–Q050
→ Report cites v1/Q012

Transcript edited
→ Transcript v2
→ New evidence set
→ Old report still resolves v1/Q012
```

## Design Resolution

Analysis binds to transcript version. Quote IDs are version-scoped.

---

# Lens + Psychological Hypothesis + Non-Diagnostic Discipline

A user may ask whether evidence in a conversation is consistent with a psychological hypothesis.

## Tension

Psychological hypotheses can become labels.

## Design Resolution

Hypotheses must be framed as:

```text
evidence-consistent
evidence-inconsistent
insufficient evidence
alternative explanations
reflection questions
```

Not diagnosis, identity label, or verdict.

---

# Finding + Confidence + Evidence Quote

A finding says something specific and cites evidence.

## Desired Behavior

```text
Finding:
  "The response moves quickly from hurt to global accusation."

Evidence:
  "You always have a reason."

Confidence:
  observed

Limitations:
  single transcript; tone unavailable
```

## Design Resolution

Every finding must include confidence and limitations appropriate to inference depth.

---

# Reflection Point + Safety-Aware Framing

The system gives a user reflection points for improvement.

## Tension

In serious safety contexts, “both people should improve communication” can be unsafe or misleading.

## Design Resolution

Safety-aware framing can suppress ordinary mutual-growth suggestions when coercion, threats, stalking, intimidation, or severe control appear.

---

# Reasoning Graph + Synthesis

Synthesis should be based on structured findings, constructs, and relationships.

## Design Resolution

Synthesis should be a view over structured reasoning, not a free-form second analysis. Graph relationships should include rationale, confidence, and evidence where possible.

---

# Case + Longitudinal Analysis + Privacy Boundary

The user groups transcripts into a case to understand change over time.

## Tension

Longitudinal analysis requires retained sensitive transcripts.

## Design Resolution

Cases are opt-in. Only transcripts explicitly retained or assigned to a case should contribute to longitudinal analysis. Case-level evidence must identify transcript and version.

---

# Cost State + Worker Jobs

The app sleeps when idle to reduce cost, but active jobs should not be corrupted.

## Design Resolution

Shutdown can occur only when there is no authenticated activity, no active jobs, and no wake/shutdown transition in progress. Long jobs require timeout/cancel policy.

---

# Personal Owner + Future Enterprise

The current system is personal and owner-operated. Future enterprise use may involve many users, organizations, roles, and compliance needs.

## Design Resolution

Model enterprise as policy expansion, not current default.

---

# Common Composition Failures

1. Recording becomes durable by accident.
2. Transcript edits invalidate old evidence.
3. Psychological hypotheses become diagnoses.
4. Findings lack evidence.
5. Evidence is too long to be useful.
6. Longitudinal claims are made from one transcript.
7. Safety concerns are mutualized.
8. Cost controls interrupt active work.
9. Enterprise assumptions overcomplicate personal use.
10. Reports become prose detached from structured graph data.
