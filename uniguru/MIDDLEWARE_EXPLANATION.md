# UniGuru as Deterministic Middleware

## 1. What is Middleware?
In backend engineering, **Middleware** is software that sits between the raw network request and the final application logic. It intercepts the incoming data, performs a transformation or validation, and either passes the request onward or terminates it (blocks).

## 2. Where UniGuru Sits
UniGuru is **"Reasoning Middleware."** It does not store user data; it validates the *intent* and *safety* of a request before it reaches a deeper system (like an LLM or a Database).

### Lifecycle Analogies
*   **NodeJS/Express**: Like a `router.use((req, res, next) => { ... })` function that checks for a valid header before allowing access to a route.
*   **FastAPI**: Like a `Depends()` dependency or a `BaseHTTPMiddleware` that wraps every endpoint.

## 3. The UniGuru Bridge
UniGuru acts as a bridge between a **Stochastic Client** (User) and a **Production Core**. It ensures that no matter how unstructured or dangerous the user's message is, the output delivered to the production environment is:
1.  **Audited** (Governance)
2.  **Classified** (Reasoning)
3.  **Grounded** (Retrieval)

## 4. Deterministic Requirement
Middleware in high-security systems **must** be deterministic. If a bridge operates on "probabilities" (like an LLM), it introduces non-deterministic security holes. By making UniGuru deterministic, we guarantee that the "Security Gate" never sleeps and never guesses.
