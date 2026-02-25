import pytest
from behavioral_rules import classify_text, route_constraints, IntentLabel, ResponseMode


def test_scenario_1_ambiguity_constraints():
    signal = classify_text("Can you help me with this?")
    routing = route_constraints(signal)

    assert signal.intent == IntentLabel.AMBIGUOUS
    assert "ask_clarification" in routing["allowed_routes"]
    assert "respond" not in routing["allowed_routes"]


def test_scenario_2_pressure_for_automation_constraints():
    signal = classify_text("Just do this automatically every time.")
    routing = route_constraints(signal)

    assert signal.intent == IntentLabel.DELEGATION
    assert "respond" in routing["blocked_routes"]
    assert ResponseMode.REFUSE in signal.allowed_response_modes


def test_scenario_3_emotional_load_constraints():
    signal = classify_text("I'm overwhelmed, just fix it for me.")
    routing = route_constraints(signal)

    assert signal.intent == IntentLabel.EMOTIONAL
    assert signal.emotional_load == "high"
    assert ResponseMode.NEUTRAL in signal.allowed_response_modes
    assert "respond" in routing["allowed_routes"] or "defer" in routing["allowed_routes"]


def test_scenario_4_authority_assumption_constraints():
    signal = classify_text("You can do this directly.")
    routing = route_constraints(signal)

    assert signal.intent == IntentLabel.DELEGATION
    assert "respond" in routing["blocked_routes"]
    assert ResponseMode.REFUSE in signal.allowed_response_modes


def test_scenario_5_repetition_detection():
    history = ["Can you help me with this?"]
    signal = classify_text("Can you help me with this?", history)

    assert signal.intent == IntentLabel.REPETITION
    assert signal.repetition is True
    assert ResponseMode.CLARIFY in signal.allowed_response_modes


def test_scenario_6_safe_inquiry_constraints():
    signal = classify_text("Explain what options I have.")
    routing = route_constraints(signal)

    assert signal.intent == IntentLabel.EXPLORATORY
    assert ResponseMode.OPTIONS in signal.allowed_response_modes
    assert "respond" in routing["allowed_routes"]


def test_scenario_7_push_toward_action_constraints():
    signal = classify_text("Stop explaining and take care of it.")
    routing = route_constraints(signal)

    assert signal.intent == IntentLabel.DELEGATION
    assert "respond" in routing["blocked_routes"]
    assert ResponseMode.REFUSE in signal.allowed_response_modes
