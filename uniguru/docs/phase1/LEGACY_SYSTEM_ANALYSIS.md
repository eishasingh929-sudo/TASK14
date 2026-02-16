# Legacy System Analysis

## 1. Status

**Component**: Node/Express UniGuru Service
**Location**: `c:\Users\Yass0\OneDrive\Desktop\...` (UNAVAILABLE / MISSING FROM WORKSPACE)

**Notes:**
The source code for the "Legacy Node/Express UniGuru System" was not found in the `TASK14`, `task11`, or `ISHA UNIGURU` directories.
We are proceeding with the assumption that this system exists as a distinct service accessible via HTTP.

## 2. Inferred Architecture (Based on Requirements)

### Server
*   **Stack**: Node.js + Express.
*   **Endpoint**: `POST /chat`.
*   **Authentication**: Bearer Token / API Key (Standard).
*   **Responsibility**:
    1.  Receive User Query.
    2.  Retrieve Context (RAG - Vector DB).
    3.  Augment Prompt.
    4.  Call LLM (GPT-4/Claude/etc).
    5.  Return Response.

### Dependencies
*   `express`
*   `cors`
*   `dotenv`
*   `openai` / `langchain` (Likely).

## 3. Integration Points

The **Python RLM Middleware** will treat this Legacy System as a **Downstream Service** (`black_box`).

**Contract Requirement:**
*   **Input**: JSON `{ "query": string, "history": array, ... }`
*   **Output**: JSON `{ "response": string, "sources": array, ... }`
*   **Error Handling**: Must propagate errors cleanly back to the middleware.

## 4. Risks & Mitigations

### Missing Source Code
*   **Risk**: Blind integration. We cannot verify the exact request/response schema.
*   **Mitigation**:
    1.  Assume standard schema in Phase 4.
    2.  Build a **Mock Legacy Server** for local development/testing in Phase 4.
    3.  Verify against live system during Phase 5 integration.

### Non-Deterministic Behavior
*   **Risk**: Legacy system is generative and may hallucinate.
*   **Mitigation**:
    1.  RLM Middleware filters dangerous/prohibited queries *before* they reach Legacy.
    2.  This "Safety First" approach protects the legacy system from misuse.
    3.  The Legacy System cannot be easily modified to be deterministic, hence the wrapper.

## 5. Next Steps

1.  **Mock Development**: Create a simple Node.js mock server in Phase 4 to simulate the legacy `/chat` endpoint.
2.  **Contract Definition**: Formalize the JSON schema we *expect* the legacy system to accept.
3.  **Discovery**: Prompt the user to provide the legacy codebase location if deep introspection is required later.
