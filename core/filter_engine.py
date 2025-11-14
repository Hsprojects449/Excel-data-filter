"""
Core filtering engine.
Provides advanced filtering capabilities using Polars.
Supports column-based filters, regex, numeric ranges, and date ranges.
"""

from typing import Any, List, Optional, Dict
import polars as pl
from datetime import datetime
import re
from loguru import logger


class FilterRule:
    """Represents a single filter rule."""

    def __init__(
        self,
        column: str,
        operator: str,
        value: Any,
        is_regex: bool = False,
    ):
        self.column = column
        self.operator = operator
        self.value = value
        self.is_regex = is_regex


class FilterEngine:
    """Applies filters to Polars DataFrames."""

    def __init__(self, dataframe: pl.DataFrame):
        self.dataframe = dataframe
        self.filtered_df = dataframe.clone()
        self.applied_filters: List[FilterRule] = []
        self.filter_logic = "AND"  # AND or OR

    def add_filter(self, rule: FilterRule) -> None:
        """Add a filter rule."""
        self.applied_filters.append(rule)
        logger.debug(f"Added filter: {rule.column} {rule.operator} {rule.value}")

    def clear_filters(self) -> None:
        """Clear all filters and reset to original dataframe."""
        self.applied_filters = []
        self.filtered_df = self.dataframe.clone()
        logger.debug("Cleared all filters")

    def set_filter_logic(self, logic: str) -> None:
        """Set filter logic (AND or OR)."""
        self.filter_logic = logic.upper()

    def apply_filters(self, logic: str = "AND") -> pl.DataFrame:
        """Apply all filters and return the filtered dataframe."""
        if not self.applied_filters:
            self.filtered_df = self.dataframe.clone()
            return self.filtered_df

        self.filter_logic = logic.upper()
        result_df = self.dataframe.clone()

        # Build filter expressions
        filter_expressions = []
        for rule in self.applied_filters:
            expr = self._build_filter_expression(rule)
            if expr is not None:
                filter_expressions.append(expr)

        if not filter_expressions:
            self.filtered_df = result_df
            return result_df

        # Combine expressions based on logic
        if self.filter_logic == "AND":
            combined_expr = filter_expressions[0]
            for expr in filter_expressions[1:]:
                combined_expr = combined_expr & expr
        else:  # OR
            combined_expr = filter_expressions[0]
            for expr in filter_expressions[1:]:
                combined_expr = combined_expr | expr

        try:
            result_df = result_df.filter(combined_expr)
        except Exception as e:
            logger.error(f"Error applying filter expression: {e}")

        self.filtered_df = result_df
        logger.info(
            f"Applied {len(self.applied_filters)} filters with {self.filter_logic}. "
            f"Result: {len(result_df)} rows"
        )
        return result_df

    def _build_filter_expression(self, rule: FilterRule):
        """Build a Polars filter expression from a rule."""
        if rule.column not in self.dataframe.columns:
            logger.warning(f"Column '{rule.column}' not found in dataframe")
            return None

        try:
            col = pl.col(rule.column)

            if rule.operator == "equals":
                return col.cast(pl.Utf8).str.to_lowercase() == str(rule.value).lower()

            elif rule.operator == "not_equals":
                return col.cast(pl.Utf8).str.to_lowercase() != str(rule.value).lower()

            elif rule.operator == "contains":
                return col.cast(pl.Utf8).str.to_lowercase().str.contains(str(rule.value).lower(), literal=False)

            elif rule.operator == "not_contains":
                return ~col.cast(pl.Utf8).str.to_lowercase().str.contains(str(rule.value).lower(), literal=False)

            elif rule.operator == "starts_with":
                return col.cast(pl.Utf8).str.to_lowercase().str.starts_with(str(rule.value).lower())

            elif rule.operator == "ends_with":
                return col.cast(pl.Utf8).str.to_lowercase().str.ends_with(str(rule.value).lower())

            elif rule.operator == "regex":
                return col.cast(pl.Utf8).str.contains(rule.value)

            elif rule.operator == "gt":
                try:
                    return col > float(rule.value)
                except ValueError:
                    return col > int(rule.value)

            elif rule.operator == "lt":
                try:
                    return col < float(rule.value)
                except ValueError:
                    return col < int(rule.value)

            elif rule.operator == "gte":
                try:
                    return col >= float(rule.value)
                except ValueError:
                    return col >= int(rule.value)

            elif rule.operator == "lte":
                try:
                    return col <= float(rule.value)
                except ValueError:
                    return col <= int(rule.value)

            elif rule.operator == "between":
                parts = str(rule.value).split(",")
                if len(parts) == 2:
                    try:
                        start = float(parts[0].strip())
                        end = float(parts[1].strip())
                    except ValueError:
                        start = int(parts[0].strip())
                        end = int(parts[1].strip())
                    return (col >= start) & (col <= end)

            elif rule.operator == "not_null":
                return col.is_not_null()

            elif rule.operator == "is_null":
                return col.is_null()

            else:
                logger.warning(f"Unknown operator: {rule.operator}")
                return None

        except Exception as e:
            logger.error(f"Error building filter expression: {e}")
            return None

    def get_filtered_data(self) -> pl.DataFrame:
        """Get the current filtered dataframe."""
        return self.filtered_df.clone()

    def get_statistics(self) -> dict:
        """Get statistics about filtering result."""
        return {
            "original_rows": len(self.dataframe),
            "filtered_rows": len(self.filtered_df),
            "rows_removed": len(self.dataframe) - len(self.filtered_df),
            "filter_count": len(self.applied_filters),
            "reduction_percent": (
                (len(self.dataframe) - len(self.filtered_df))
                / len(self.dataframe)
                * 100
                if len(self.dataframe) > 0
                else 0
            ),
        }
        result_df = self.dataframe.clone()

        for rule in self.applied_filters:
            result_df = self._apply_single_filter(result_df, rule)

        self.filtered_df = result_df
        logger.info(
            f"Applied {len(self.applied_filters)} filters. Result: {len(result_df)} rows"
        )
        return result_df

    def _apply_single_filter(
        self, df: pl.DataFrame, rule: FilterRule
    ) -> pl.DataFrame:
        """Apply a single filter rule to a dataframe."""
        if rule.column not in df.columns:
            logger.warning(f"Column '{rule.column}' not found in dataframe")
            return df

        try:
            if rule.operator == "equals":
                return df.filter(pl.col(rule.column) == rule.value)

            elif rule.operator == "contains":
                return df.filter(pl.col(rule.column).str.contains(str(rule.value)))

            elif rule.operator == "regex":
                return df.filter(pl.col(rule.column).str.contains(rule.value))

            elif rule.operator == "gt":
                return df.filter(pl.col(rule.column) > rule.value)

            elif rule.operator == "lt":
                return df.filter(pl.col(rule.column) < rule.value)

            elif rule.operator == "gte":
                return df.filter(pl.col(rule.column) >= rule.value)

            elif rule.operator == "lte":
                return df.filter(pl.col(rule.column) <= rule.value)

            elif rule.operator == "between":
                if isinstance(rule.value, (list, tuple)) and len(rule.value) == 2:
                    start, end = rule.value
                    return df.filter(
                        (pl.col(rule.column) >= start) & (pl.col(rule.column) <= end)
                    )

            elif rule.operator == "not_null":
                return df.filter(pl.col(rule.column).is_not_null())

            elif rule.operator == "is_null":
                return df.filter(pl.col(rule.column).is_null())

            else:
                logger.warning(f"Unknown operator: {rule.operator}")
                return df

        except Exception as e:
            logger.error(f"Error applying filter: {e}")
            return df

    def get_filtered_data(self) -> pl.DataFrame:
        """Get the current filtered dataframe."""
        return self.filtered_df.clone()

    def get_statistics(self) -> dict:
        """Get statistics about filtering result."""
        return {
            "original_rows": len(self.dataframe),
            "filtered_rows": len(self.filtered_df),
            "rows_removed": len(self.dataframe) - len(self.filtered_df),
            "filter_count": len(self.applied_filters),
            "reduction_percent": (
                (len(self.dataframe) - len(self.filtered_df)) / len(self.dataframe) * 100
                if len(self.dataframe) > 0
                else 0
            ),
        }
