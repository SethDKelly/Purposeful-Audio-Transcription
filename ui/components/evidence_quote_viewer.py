import streamlit as st


def build_quotes_index(
    evidence_quotes: list[dict],
    speakers: list[dict] | None = None,
) -> dict[str, dict]:
    speaker_names = {
        speaker["id"]: speaker.get("display_name") or speaker.get("label", "Speaker")
        for speaker in (speakers or [])
    }
    indexed: dict[str, dict] = {}
    for quote in evidence_quotes:
        enriched = dict(quote)
        enriched["speaker_display_name"] = speaker_names.get(
            quote.get("speaker_id"), "Speaker"
        )
        enriched["speaker_label"] = next(
            (
                speaker.get("label")
                for speaker in (speakers or [])
                if speaker.get("id") == quote.get("speaker_id")
            ),
            "Speaker",
        )
        indexed[quote["quote_id"]] = enriched
    return indexed


def render_evidence_quote_viewer(
    quotes_by_id: dict[str, dict],
    *,
    selected_quote_id: str | None = None,
    modules_using: dict[str, list[str]] | None = None,
) -> None:
    if not quotes_by_id:
        st.caption("No evidence quotes available.")
        return

    st.markdown("### Evidence map")
    quote_ids = sorted(quotes_by_id.keys())
    selected = st.selectbox(
        "Select a quote to inspect",
        options=quote_ids,
        index=quote_ids.index(selected_quote_id) if selected_quote_id in quote_ids else 0,
        format_func=lambda quote_id: f"{quote_id} — {quotes_by_id[quote_id].get('text', '')[:80]}",
        key="evidence_quote_selector",
    )

    quote = quotes_by_id.get(selected, {})
    speaker = quote.get("speaker_display_name") or quote.get("speaker_label") or "Unknown"
    turn_index = quote.get("quote_index", "?")

    st.markdown(f"**{selected}** · Turn {turn_index} · {speaker}")
    st.markdown(f"> {quote.get('text', '')}")

    if quote.get("context_before"):
        st.caption(f"Before: {quote['context_before']}")
    if quote.get("context_after"):
        st.caption(f"After: {quote['context_after']}")

    if modules_using and selected in modules_using:
        st.markdown("**Used by modules:** " + ", ".join(modules_using[selected]))


def index_modules_by_quote(module_runs: list[dict]) -> dict[str, list[str]]:
    usage: dict[str, list[str]] = {}
    for module_run in module_runs:
        parsed = module_run.get("parsed_output") or {}
        module_id = parsed.get("module_id") or module_run.get("module_id", "module")
        for finding in parsed.get("findings", []):
            for quote_id in finding.get("evidence_quote_ids", []):
                usage.setdefault(quote_id, [])
                if module_id not in usage[quote_id]:
                    usage[quote_id].append(module_id)
    return usage
