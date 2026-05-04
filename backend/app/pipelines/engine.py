import yaml
from typing import Any
from app.pipelines.steps import ValidateStep, TransformStep, AggregateStep, StepResult
import structlog

logger = structlog.get_logger()


class PipelineEngine:
    def __init__(self, pipeline_yaml: str, template_schema: dict):
        self.pipeline_config = yaml.safe_load(pipeline_yaml)
        self.template_schema = template_schema
        self.results: list[StepResult] = []

    def execute(self, raw_data: list[dict]) -> tuple[list[dict], list[StepResult]]:
        data = raw_data
        context = {}

        for pipeline_name, pipeline_def in self.pipeline_config.items():
            steps = pipeline_def.get("steps", [])
            for step_config in steps:
                step_type = list(step_config.keys())[0]
                step_detail = step_config[step_type]

                if step_type == "validate":
                    step = ValidateStep(step_detail, self.template_schema)
                elif step_type == "transform":
                    step = TransformStep(step_detail)
                elif step_type == "aggregate":
                    step = AggregateStep(step_detail)
                else:
                    logger.warning("step_unknown", type=step_type)
                    continue

                try:
                    data, result = step.execute(data, context)
                    self.results.append(result)
                    logger.info(
                        "step_executado", step=step_type, rows=result.rows_affected
                    )
                except Exception as e:
                    err_result = StepResult(
                        step_name=step_type, status="error", error=str(e)
                    )
                    self.results.append(err_result)
                    logger.error("step_falhou", step=step_type, error=str(e))
                    raise

        return data, self.results
