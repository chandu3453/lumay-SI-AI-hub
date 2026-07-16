"""
Classification pipeline — multi-label complaint classification.

Assigns one or more category labels to complaint text using
few-shot classification with label descriptions.
"""

from ai.pipelines.base_pipeline import BasePipeline, PipelineContext, PipelineResult


class ClassificationPipeline(BasePipeline):
    """Multi-label classification pipeline.

    Steps:
      1. Category prediction (primary category + confidence)
      2. Sub-category assignment
      3. Issue type identification
      4. Regulatory tagging (applicable regulations)
      5. Confidence calibration
    """

    def __init__(self) -> None:
        super().__init__(name="classification_pipeline")

    async def run(self, input_data: dict[str, Any], context: PipelineContext | None = None) -> PipelineResult:
        ...
