"""Public evaluator construction must distinguish boolean and numeric criteria."""

import pytest

from maxim.evaluators import BaseEvaluator
from maxim.models.evaluator import (
    PassFailCriteria,
    PassFailCriteriaForTestrunOverall,
    PassFailCriteriaOnEachEntry,
)


class _Evaluator(BaseEvaluator):
    def evaluate(self, result, data):
        return {}


def _create_evaluator(operator, value):
    return _Evaluator(
        {
            "check": PassFailCriteria(
                on_each_entry_pass_if=PassFailCriteriaOnEachEntry(operator, value),
                for_testrun_overall_pass_if=PassFailCriteriaForTestrunOverall(
                    ">=", 80, "percentageOfPassedResults"
                ),
            )
        }
    )


@pytest.mark.parametrize("value", [True, False])
@pytest.mark.parametrize("operator", [">", ">=", "<", "<="])
def test_boolean_criteria_reject_ordering(operator, value):
    with pytest.raises(Exception, match="Invalid operator for scoreShouldBe"):
        _create_evaluator(operator, value)


@pytest.mark.parametrize("value", [True, False])
@pytest.mark.parametrize("operator", ["=", "!="])
def test_boolean_criteria_accept_equality(operator, value):
    evaluator = _create_evaluator(operator, value)
    assert evaluator.names == ["check"]
    assert evaluator.pass_fail_criteria["check"].on_each_entry.value is value


@pytest.mark.parametrize("value", [-1, 0, 0.5, 1])
@pytest.mark.parametrize("operator", [">", ">=", "<", "<=", "=", "!="])
def test_numeric_criteria_keep_all_comparison_operators(operator, value):
    evaluator = _create_evaluator(operator, value)
    assert evaluator.pass_fail_criteria["check"].on_each_entry.value == value


@pytest.mark.parametrize("value", [True, False, 0, 0.5])
def test_unknown_operator_still_rejected(value):
    with pytest.raises(Exception, match="Invalid operator for scoreShouldBe"):
        _create_evaluator("contains", value)


@pytest.mark.parametrize("value", [None, "yes"])
def test_invalid_criteria_type_still_rejected(value):
    with pytest.raises(Exception, match="Invalid type for onEachEntry.value"):
        _create_evaluator("=", value)
