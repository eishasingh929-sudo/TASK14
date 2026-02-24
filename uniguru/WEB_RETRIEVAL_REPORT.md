# Web Retrieval Engine Report

## Status: FUNCTIONAL (PHASE 5)
The Live Verified Web Retrieval Engine allows UniGuru to access external knowledge while maintaining trust boundaries.

## Verification Logic
The engine implements a strict domain filter:
- **Allowed**: `.edu`, `.gov`, `nature.com`, `science.org`, `britannica.com`, `wikipedia.org`.
- **Rejected**: Personal blogs, anonymous forum posts, and unverified commercial sites.

## Truth Declaration
When information is found but does not meet the "Highly Verified" criteria, UniGuru is forced to declare:
> “This information was found but could not be fully verified. Source: [link]”

## Architecture
- **Location**: `retrieval/web_retriever.py`
- **Method**: Domain-based credibility scoring.

## Integration
The Web Retrieval Engine acts as a secondary layer to the internal KB. If the internal KB has no answer, the Web Engine is consulted. If both fail or provide unverified data, the system defaults to refusal.
