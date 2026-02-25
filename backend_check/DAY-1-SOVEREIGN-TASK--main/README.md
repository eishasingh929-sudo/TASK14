# Day 1 – Deterministic Answer Pipeline

This project implements a fixed, deterministic pipeline for answering queries.

## Pipeline Stages
1. Input Normalization – cleans user input
2. Knowledge Lookup – searches local knowledge base
3. Validation – checks if data exists
4. Confidence Evaluation – verifies certainty
5. Classification – decides answer or refusal
6. Response Shaping – formats final response

Each stage logs entry and exit to ensure traceability.

## Overview
This project implements a deterministic, stage-based answer pipeline.
The goal is to ensure that every input follows a fixed sequence of steps
and always produces the same output for the same input.

The system focuses on correctness, traceability, and controlled behavior.
No external APIs, UI changes, or assumptions about users are used.

---

## Objective
- Convert the answer flow into a strict, ordered pipeline
- Ensure determinism (same input → same output)
- Log every decision stage clearly
- Prepare a base system for refusal and consistency checks in later days

---

## Pipeline Architecture

The pipeline is executed in the following fixed order:

1. **Input Normalization**
   - Cleans user input
   - Removes extra spaces
   - Converts input to lowercase
   - Ensures consistent input format

2. **Knowledge Lookup**
   - Searches a local, predefined knowledge base
   - No external sources or APIs are used

3. **Validation**
   - Checks whether relevant data exists
   - Prevents proceeding with missing information

4. **Confidence Evaluation**
   - Evaluates confidence score of the data
   - Ensures minimum certainty threshold is met

5. **Classification**
   - Decides whether the system should ANSWER or REFUSE
   - Based strictly on validation and confidence results

6. **Response Shaping**
   - Produces the final output
   - Returns either a factual answer or a neutral refusal message

---

## Design Principles
- Deterministic logic only
- Each stage implemented as a separate function
- Clear console logs for entry and exit of every stage
- No randomness or hidden behavior
- Refusal preferred over uncertain answers

---

## Logging
Each pipeline stage logs:
- Entry into the stage
- Exit from the stage
- Key decision points where applicable

This ensures transparency and easy debugging.

---

## Files Included
- `pipeline.js` – Contains the complete deterministic pipeline
- `README.md` – Documentation explaining pipeline structure and behavior

---

## Status
Day 1 implementation complete.
The pipeline is ready for failure enforcement and consistency testing in the next phases.
