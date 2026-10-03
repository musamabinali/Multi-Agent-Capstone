"""Generate the multi-page MAKPA sample PDF for RAG ingestion.

Produces a 15-page PDF (~45 chunks at 1000/200 split) with five distinct
topic clusters so MMR re-ranking is meaningfully exercised:
  pages 1-3:   LangGraph agents and supervision
  pages 4-6:   Vector stores and embeddings
  pages 7-9:   RAG retrieval and MMR ranking
  pages 10-12: GitHub workflows and pull requests
  pages 13-15: Google Workspace scheduling and email

Usage: python scripts/generate_sample_pdf.py [--output data/sample.pdf]
"""

from __future__ import annotations

import argparse
import os

PARA = (
    "This section expands on the chapter topic with concrete implementation detail, "
    "operational guidance, and worked examples drawn from production deployments. "
    "Readers should pay attention to configuration defaults, failure modes, and the "
    "observability hooks that make the system debuggable under load. Each subsection "
    "closes with a checklist that teams can adopt directly in code review. "
)

TOPICS: list[tuple[str, list[str]]] = [
    (
        "LangGraph Agents and Supervision",
        [
            "The supervisor pattern routes each user query to a specialized sub-agent "
            "using a Pydantic intent classifier, then aggregates partial answers into a "
            "single grounded response with LangGraph Send parallelism.",
            "Sub-agent state schemas stay isolated per domain so the RAG, GitHub, and "
            "Google graphs can evolve independently and be wrapped by the supervisor "
            "without modification to their nodes or edges.",
            "Checkpointers keyed by deterministic thread identifiers give every run "
            "replayable state, which is required for interrupt based human in the loop "
            "confirmations on mutating operations.",
        ],
    ),
    (
        "Vector Stores and Embeddings",
        [
            "Pinecone serverless indexes host high dimensional embeddings with cosine "
            "similarity, while Chroma HTTP serves teams that prefer a self hosted "
            "collection behind a simple REST deployment on their own cluster.",
            "Qdrant Cloud collections store payload metadata beside each point so that "
            "source, page, and chunk filters can narrow retrieval before ranking runs.",
            "HuggingFace sentence transformers run locally on CPU for zero key demos, "
            "and Gemini text embeddings remain an opt in upgrade for hosted quality.",
        ],
    ),
    (
        "RAG Retrieval and MMR Ranking",
        [
            "Maximum marginal relevance balances query similarity against diversity so "
            "that near duplicate chunks do not crowd out complementary evidence from "
            "other pages of the same document collection.",
            "The fetch_k candidate pool feeds the MMR selector, and lambda_mult tunes "
            "the trade off: values near one behave like pure similarity search while "
            "values near zero force maximally diverse coverage of the corpus.",
            "Every retrieved chunk carries source, page, chunk index, and document id "
            "metadata, and the faithfulness guard appends a citation line whenever the "
            "draft answer omits one.",
        ],
    ),
    (
        "GitHub Workflows and Pull Requests",
        [
            "Pull request review starts with listing open PRs by state, reading the "
            "changed files and comments, and checking commit history on the branch "
            "before approving or requesting changes.",
            "Issue triage labels incoming reports by area and severity, and creating "
            "an issue always requires explicit human confirmation because it mutates "
            "shared project state visible to the whole team.",
            "Code search across repositories locates call sites quickly, and reading a "
            "file at a pinned ref keeps review comments anchored to exact content.",
        ],
    ),
    (
        "Google Workspace Scheduling and Email",
        [
            "Calendar scheduling begins with a free busy availability check, presents "
            "the proposed event for human confirmation, and only then creates the "
            "meeting on the selected calendar.",
            "Gmail drafting composes a message from meeting context, shows the full "
            "payload in a second confirmation gate, and sends only after approval so "
            "no external mail leaves without review.",
            "OAuth tokens are cached locally and refreshed automatically, with a "
            "reauthentication URL printed whenever the refresh token expires.",
        ],
    ),
]


def build_pages() -> list[tuple[str, str]]:
    """Expand the five topic clusters into fifteen full pages of prose."""
    pages: list[tuple[str, str]] = []
    for topic_title, bullets in TOPICS:
        for part in range(3):
            heading = f"{topic_title} — Part {part + 1}"
            body_parts = [
                f"Chapter overview: {bullets[part % len(bullets)]}",
                PARA * 3,
                f"Key practice: {bullets[(part + 1) % len(bullets)]}",
                PARA * 3,
                f"Review checklist: {bullets[(part + 2) % len(bullets)]}",
                PARA * 2,
            ]
            pages.append((heading, "\n\n".join(body_parts)))
    return pages


def generate(output: str) -> tuple[str, int]:
    """Render the PDF and return (path, page_count)."""
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

    styles = getSampleStyleSheet()
    story = []
    pages = build_pages()
    for i, (heading, body) in enumerate(pages):
        story.append(Paragraph(heading, styles["Heading1"]))
        story.append(Spacer(1, 12))
        for para in body.split("\n\n"):
            story.append(Paragraph(para.replace("&", "&amp;"), styles["Normal"]))
            story.append(Spacer(1, 6))
        if i < len(pages) - 1:
            story.append(PageBreak())
    os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)
    SimpleDocTemplate(output, pagesize=letter).build(story)
    return output, len(pages)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate MAKPA sample PDF")
    parser.add_argument("--output", default="data/sample.pdf")
    args = parser.parse_args()
    path, count = generate(args.output)
    print(f"Wrote {count} pages to {path}")


if __name__ == "__main__":
    main()
