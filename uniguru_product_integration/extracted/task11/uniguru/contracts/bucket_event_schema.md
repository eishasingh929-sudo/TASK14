# BHIV Bucket Event Schema

## Purpose
This document defines the structure of intelligence events
logged into BHIV Bucket from UniGuru LM.

Bucket is strictly append-only and contains no intelligence logic.

## Event Structure

```json
{
  "event_id": "uuid",
  "timestamp": "ISO-8601",
  "user_id": "string",
  "session_id": "string",
  "lesson_id": "string",
  "source_system": "UniGuru_LM",
  "target_system": "Gurukul_UI",
  "user_input": "string",
  "lm_output": "string",
  "policy_status": "allowed | refused | fallback",
  "notes": "optional metadata"
}
