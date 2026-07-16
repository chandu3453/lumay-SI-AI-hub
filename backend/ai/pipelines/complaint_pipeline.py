"""
Complaint intelligence pipeline — classification, sentiment, and triage.

End-to-end pipeline that processes insurance complaints through
classification, sentiment analysis, severity scoring, and entity extraction.
"""

from ai.pipelines.base_pipeline import BasePipeline, PipelineContext, PipelineResult


class ComplaintPipeline(BasePipeline):
    """Complaint intelligence pipeline.

    Steps:
      1. PII redaction (input guard)
      2. Complaint classification (category, sub-category, issue type)
      3. Sentiment analysis (positive, negative, neutral + intensity)
      4. Severity scoring (urgency, financial impact, regulatory risk)
      5. Entity extraction (policy numbers, claim IDs, dates, parties)
      6. Content safety check (output guard)
      7. Evaluation (correctness, relevance)
    """

    def __init__(self) -> None:
        super().__init__(name="complaint_pipeline")

    async def run(self, input_data: dict[str, Any], context: PipelineContext | None = None) -> PipelineResult:
        ...
