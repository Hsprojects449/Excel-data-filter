"""
Unit tests for the filter engine.
"""

import pytest
import polars as pl
from core.filter_engine import FilterEngine, FilterRule


@pytest.fixture
def sample_dataframe():
    """Create a sample dataframe for testing."""
    return pl.DataFrame(
        {
            "ID": [1, 2, 3, 4, 5],
            "Name": ["Alice", "Bob", "Charlie", "David", "Eve"],
            "Age": [25, 30, 35, 28, 32],
            "City": ["NYC", "LA", "NYC", "Chicago", "NYC"],
        }
    )


def test_filter_engine_creation(sample_dataframe):
    """Test filter engine initialization."""
    engine = FilterEngine(sample_dataframe)
    assert engine.dataframe is not None
    assert len(engine.dataframe) == 5


def test_add_filter(sample_dataframe):
    """Test adding a filter rule."""
    engine = FilterEngine(sample_dataframe)
    rule = FilterRule("City", "equals", "NYC")
    engine.add_filter(rule)
    assert len(engine.applied_filters) == 1


def test_apply_equals_filter(sample_dataframe):
    """Test equals filter."""
    engine = FilterEngine(sample_dataframe)
    rule = FilterRule("City", "equals", "NYC")
    engine.add_filter(rule)
    result = engine.apply_filters()
    assert len(result) == 3


def test_apply_contains_filter(sample_dataframe):
    """Test contains filter."""
    engine = FilterEngine(sample_dataframe)
    rule = FilterRule("Name", "contains", "a")
    engine.add_filter(rule)
    result = engine.apply_filters()
    assert len(result) == 3  # Charlie, David, Alice


def test_apply_numeric_filter(sample_dataframe):
    """Test numeric comparison filter."""
    engine = FilterEngine(sample_dataframe)
    rule = FilterRule("Age", "gt", 30)
    engine.add_filter(rule)
    result = engine.apply_filters()
    assert len(result) == 2  # 35, 32


def test_clear_filters(sample_dataframe):
    """Test clearing filters."""
    engine = FilterEngine(sample_dataframe)
    engine.add_filter(FilterRule("City", "equals", "NYC"))
    engine.apply_filters()
    engine.clear_filters()
    assert len(engine.applied_filters) == 0


def test_multiple_filters(sample_dataframe):
    """Test applying multiple filters."""
    engine = FilterEngine(sample_dataframe)
    engine.add_filter(FilterRule("City", "equals", "NYC"))
    engine.add_filter(FilterRule("Age", "gte", 25))
    result = engine.apply_filters()
    assert len(result) >= 1


def test_statistics(sample_dataframe):
    """Test statistics generation."""
    engine = FilterEngine(sample_dataframe)
    engine.add_filter(FilterRule("City", "equals", "NYC"))
    engine.apply_filters()
    stats = engine.get_statistics()
    assert stats["original_rows"] == 5
    assert stats["filtered_rows"] == 3
