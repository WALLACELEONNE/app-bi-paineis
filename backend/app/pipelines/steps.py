import yaml
from dataclasses import dataclass, field
from typing import Any
import structlog

logger = structlog.get_logger()


@dataclass
class StepResult:
    step_name: str
    status: str
    rows_affected: int = 0
    error: str | None = None
    output_columns: list[str] = field(default_factory=list)


class Step:
    def execute(self, data: list[dict], context: dict) -> tuple[list[dict], StepResult]:
        raise NotImplementedError


class ValidateStep(Step):
    def __init__(self, config: dict, template_schema: dict):
        self.config = config
        self.schema = template_schema

    def execute(self, data: list[dict], context: dict) -> tuple[list[dict], StepResult]:
        colunas = self.schema.get("colunas", [])
        col_names = {c["nome"] for c in colunas}
        required = {c["nome"] for c in colunas if c.get("obrigatorio")}

        valid_rows = []
        errors = 0
        for row in data:
            valid = True
            for col in colunas:
                name = col["nome"]
                if name not in row and name in required:
                    valid = False
                    break
                if name in row and col["tipo"] == "float":
                    try:
                        row[name] = float(row[name])
                    except (ValueError, TypeError):
                        valid = False
                        break
            if valid:
                valid_rows.append(row)
            else:
                errors += 1

        logger.info(
            "validate_step", total=len(data), valid=len(valid_rows), errors=errors
        )
        return valid_rows, StepResult(
            step_name="validate",
            status="ok",
            rows_affected=len(valid_rows),
            output_columns=list(col_names),
        )


class TransformStep(Step):
    def __init__(self, config: dict):
        self.config = config

    def execute(self, data: list[dict], context: dict) -> tuple[list[dict], StepResult]:
        transforms = (
            self.config.get("transform", self.config)
            if isinstance(self.config, dict)
            else self.config
        )
        for tf in transforms:
            if "add_column" in tf:
                col_name = tf["add_column"]["nome"]
                for row in data:
                    row[col_name] = None
            elif "calcular" in tf:
                col_name = tf["calcular"]["nome"]
                formula = tf["calcular"]["formula"]
                from app.pipelines.expressions import evaluate

                for row in data:
                    try:
                        row[col_name] = evaluate(formula, row)
                    except Exception:
                        row[col_name] = None
        return data, StepResult(
            step_name="transform", status="ok", rows_affected=len(data)
        )


class AggregateStep(Step):
    def __init__(self, config: dict):
        self.config = config

    def execute(self, data: list[dict], context: dict) -> tuple[list[dict], StepResult]:
        aggregates = self.config.get("aggregate", [])
        if not aggregates:
            return data, StepResult(
                step_name="aggregate", status="ok", rows_affected=len(data)
            )

        results = {}
        for agg in aggregates:
            group_by = agg.get("group_by", [])
            aggs = agg.get("aggregations", {})
            for row in data:
                key = tuple(row.get(g, None) for g in group_by)
                if key not in results:
                    results[key] = {g: row.get(g) for g in group_by}
                    for agg_name in aggs:
                        results[key][agg_name] = 0.0
                for agg_name, agg_expr in aggs.items():
                    if agg_expr.startswith("sum("):
                        col = agg_expr[4:-1]
                        results[key][agg_name] += float(row.get(col, 0))
                    elif agg_expr.startswith("avg("):
                        col = agg_expr[4:-1]
                        results[key][agg_name] = results[key].get(
                            f"_avg_{col}_sum", 0
                        ) + float(row.get(col, 0))
                        results[key][f"_avg_{col}_count"] = (
                            results[key].get(f"_avg_{col}_count", 0) + 1
                        )
                        results[key][agg_name] = (
                            results[key][f"_avg_{col}_sum"]
                            / results[key][f"_avg_{col}_count"]
                        )

        aggregated = [
            {k: v for k, v in row.items() if not k.startswith("_avg_")}
            for row in results.values()
        ]
        return aggregated, StepResult(
            step_name="aggregate", status="ok", rows_affected=len(aggregated)
        )
