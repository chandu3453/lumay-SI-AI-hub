"""
Summarisation pipeline — condenses complaint and interaction text.

Generates concise summaries of long complaint narratives or
conversation threads for agent dashboards and regulatory reports.
"""

from ai.pipelines.base_pipeline import BasePipeline, PipelineContext, PipelineResult


class SummarisationPipeline(BasePipeline):
    """Text summarisation pipeline.

    Steps:
      1. Document chunking (for long inputs exceeding context window)
      2. Chunk-level summarisation
      3. Hierarchical merge of chunk summaries
      4. Entity-preserving refinement
      5. Length enforcement (target word count / max tokens)
    """

    def __init__(self) -> None:
        super().__init__(name="summarisation_pipeline")

    async def run(self, input_data: dict[str, Any], context: PipelineContext | None = None) -> PipelineResult:
        ...
