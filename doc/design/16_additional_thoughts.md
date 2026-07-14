# Design principles

Notes that shaped the MVP and remain useful when extending the product.

1. **Keep the domain model smaller than your ambition.** Start with the core objects only: Transcript, Speaker, Turn, Quote, Finding, Evidence, Construct, Confidence, ModuleRun, WorkflowRun, and Synthesis. Everything else can grow from there.

2. **Do not build the full suite first.** Build the narrowest vertical slice: upload transcript → segment speakers → run one analysis module → return structured findings → cite evidence → render report. Once that works end-to-end, adding modules is easier.

3. **Evidence traceability is non-negotiable.** Every claim should point back to transcript quote IDs. That separates the app from a generic chatbot.

4. **Treat prompts as replaceable.** Durable assets are schemas, module specs, workflow definitions, knowledge graph, evaluation tests, and UI patterns. Prompts will evolve constantly.

5. **Progressive disclosure in the UI.** Lead with an executive summary; drill into evidence, module views, confidence, and alternatives. A full suite as one giant report overwhelms.

6. **Careful clinical framing.** Even when exploring attachment, trauma-informed communication, or related lenses, product language should stay exploratory, non-diagnostic, evidence-limited, and not a substitute for professional assessment.
