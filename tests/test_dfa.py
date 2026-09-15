"""Formal verification tests for the minimized product-code DFA."""

import pytest

from core.dfa_engine import MinimizedDFA
from core.generator import ProductCodeGenerator


@pytest.fixture
def dfa() -> MinimizedDFA:
    return MinimizedDFA()


@pytest.mark.parametrize(
    "code",
    [
        "IT-2026-001",
        "CS-2026-104",
        "HR-2024-999",
        "MK-2023-500",
        "FN-2025-012",
        "QA-2026-789",
        "AC-2021-333",
        "SA-2027-002",
        "OP-2022-841",
        "RD-2026-654",
    ],
)
def test_accepted_product_codes_reach_q11(
    dfa: MinimizedDFA,
    code: str,
) -> None:
    result = dfa.validate(code)

    assert result["is_valid"] is True
    assert result["halt_state"] == "q11"


@pytest.mark.parametrize(
    "code",
    [
        "it-2026-001",
        "I-2026-001",
        "ENG-2026-001",
        "IT 2026 001",
        "IT--2026-001",
        "IT-26-001",
        "IT-2026-01",
        "IT-2026-0001",
        "IT-2026-00A",
        "IT-2026-001#",
    ],
)
def test_rejected_product_codes_reach_trap(
    dfa: MinimizedDFA,
    code: str,
) -> None:
    result = dfa.validate(code)

    assert result["is_valid"] is False
    assert result["halt_state"] == "q_trap"


def test_trap_state_stops_step_logging(dfa: MinimizedDFA) -> None:
    result = dfa.validate("IT-2026-001#trailing")

    assert result["halt_state"] == "q_trap"
    assert len(result["steps"]) == 12
    assert result["steps"][-1]["char"] == "#"
    assert result["steps"][-1]["to_state"] == "q_trap"


def test_transition_topology_is_minimized(dfa: MinimizedDFA) -> None:
    assert dfa.transitions["q0"]["I"] == "q1"
    assert dfa.transitions["q1"]["T"] == "q2"
    assert dfa.transitions["q2"]["-"] == "q3"
    assert dfa.transitions["q7"]["-"] == "q8"
    assert dfa.transitions["q10"]["1"] == "q11"


@pytest.mark.parametrize(
    "corruption_type",
    ["short_prefix", "long_prefix", "bad_year", "bad_serial", "illegal_char"],
)
def test_generator_corruption_modes_are_rejected(
    dfa: MinimizedDFA,
    corruption_type: str,
) -> None:
    code = ProductCodeGenerator().generate_corrupted(corruption_type)

    assert not dfa.validate(code)["is_valid"]
