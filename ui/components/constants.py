CONFIDENCE_LABELS: dict[str, str] = {
    "observed": "Directly observed",
    "high": "Strongly supported",
    "moderate": "Reasonable interpretation",
    "low": "Tentative possibility",
    "exploratory": "Exploratory hypothesis",
    "insufficient_evidence": "Not enough evidence",
}

SAFETY_DISCLAIMER = (
    "This analysis is based only on the transcript provided. It is not a diagnosis, "
    "legal assessment, or substitute for professional support. Important context such as "
    "tone, body language, history, and safety factors may be missing. Consider professional "
    "help for serious safety concerns."
)
