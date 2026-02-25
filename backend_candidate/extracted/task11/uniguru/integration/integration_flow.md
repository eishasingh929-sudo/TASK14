# UniGuru LM → BHIV Core → Bucket Integration Flow

## Overview
This document explains how UniGuru LM outputs flow through BHIV Core,
are logged into BHIV Bucket, and finally returned to the Gurukul UI
without changing the user experience.

## Step-by-Step Flow

1. User submits a query from Gurukul UI.
2. Gurukul backend forwards the query to UniGuru LM.
3. UniGuru LM processes the input using hardened logic
   (ambiguity handling, emotional safety, unsafe request checks).
4. Generated output is passed to BHIV Core.
5. BHIV Core enforces:
   - Policy rules
   - Reasoning boundaries
   - Ethical and learning constraints
6. Finalized output is sent back to Gurukul UI.
7. In parallel, an intelligence event is sent to BHIV Bucket.
8. Bucket stores the event in an append-only manner for auditing.
9. Gurukul UI displays the response exactly as before.

## Failure Handling

- If LM fails → deterministic fallback response is returned.
- If policy violation occurs → refusal message is shown.
- If Bucket logging fails → user response still proceeds (no UX break).

## Key Guarantees

- Gurukul UX remains unchanged.
- All intelligence actions are observable.
- Failures degrade gracefully without silent crashes.
