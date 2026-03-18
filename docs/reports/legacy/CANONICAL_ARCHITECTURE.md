# CANONICAL_ARCHITECTURE.md

## Purpose

This document defines the **final architecture of Unified UniGuru** after repository consolidation and before middleware bridge implementation.

This architecture represents the system that will connect the reasoning engine to the real UniGuru production system.

---

## High-Level System Goal

All user queries must pass through the UniGuru reasoning system before reaching the legacy UniGuru backend.

Target flow:

User → Bridge → Governance → Reasoning → Retrieval → Legacy UniGuru → Response

This makes UniGuru the **intelligence and safety layer** in front of the production system.

---

## System Components

The canonical UniGuru repository now contains the following core components.

### 1. Bridge Layer (`/bridge`)

Role:
- Public entrypoint of the system
- Accepts HTTP requests from users
- Sends requests to the reasoning engine
- Forwards safe requests to the legacy UniGuru system

This layer acts as middleware between users and the legacy backend.

---

### 2. Core Reasoning Engine (`/core`)

Main file:
core/engine.py

Responsibilities:
- Orchestrates rule evaluation
- Produces deterministic decisions
- Generates execution trace

This is the **brain of UniGuru**.

---

### 3. Governance Layer (`/governance`)

Contains rules that manage user intent and system authority.

Rules include:
- Authority rule
- Delegation rule
- Ambiguity rule
- Emotional rule

Purpose:
Ensure safe and responsible interaction.

---

### 4. Enforcement Layer (`/enforcement`)

Contains safety enforcement logic.

Rule:
- UnsafeRule

Purpose:
Prevent harmful or prohibited requests from reaching the legacy system.

---

### 5. Retrieval Layer (`/retrieval`)

Main file:
retrieval/retriever.py

Responsibilities:
- Load knowledge base files
- Provide deterministic answers from Quantum_KB
- Reduce unnecessary calls to the generative system

---

### 6. Knowledge Base (`/Quantum_KB`)

Contains deterministic knowledge used by the retrieval engine.

This acts as the **ground truth** for factual responses.

---

### 7. Tests (`/tests`)

Contains:
- Rule tests
- Integration tests
- Regression tests

Ensures system reliability.

---

## Request Flow (Technical)

Step-by-step flow:

1. User sends HTTP request to Bridge.
2. Bridge sends message to Rule Engine.
3. Rule Engine evaluates governance and safety rules.
4. Decision is produced:

   - BLOCK → Reject request  
   - ANSWER → Use Retrieval Engine  
   - FORWARD → Call Legacy UniGuru  

5. Legacy UniGuru generates final response (if forwarded).
6. Bridge returns final response to user.

---

## Architectural Principles

The system is built on these principles:

1. Governance before generation  
2. Deterministic reasoning before LLM usage  
3. Knowledge retrieval before forwarding  
4. No direct access to legacy backend  
5. Full request traceability  

---

## Result

UniGuru now operates as a **middleware intelligence layer** in front of the legacy UniGuru system.

This architecture enables safe integration with real user traffic.
