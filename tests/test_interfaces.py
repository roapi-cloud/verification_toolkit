import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from verification_toolkit.interfaces import EvaluationResult


def test_evaluation_result_defaults():
    result = EvaluationResult(success=True, details="done")
    assert result.success is True
    assert result.details == "done"
    assert result.artifacts is None
