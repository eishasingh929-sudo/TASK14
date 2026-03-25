# UniGuru System Explanation

1. A user asks a question in the app or through the API.
2. UniGuru first checks whether the question looks like a knowledge question, a general chat question, a workflow request, or a system command.
3. If it is a knowledge question, the system searches the local knowledge base first.
4. If the knowledge base finds a strong match, UniGuru gives a verified answer from the local data.
5. If the local data is not enough, UniGuru sends the question to the live LLM endpoint and returns a real model answer.
6. If the question is a system command, UniGuru blocks it for safety.
7. If something fails, the API still returns a safe, non-empty response so the demo does not break.
8. The system also writes logs, routes, and timing information so we can explain what happened after each request.

## Short Version

UniGuru tries local knowledge first, then uses the live LLM if needed, and falls back to a safe answer if anything goes wrong.

## Route Meanings

- `ROUTE_UNIGURU`: Answer came from the local knowledge base.
- `ROUTE_LLM`: Answer came from the live language model.
- `ROUTE_WORKFLOW`: The request was handed to a workflow action.
- `ROUTE_SYSTEM`: The request was blocked because it looked unsafe.

## If Asked "What Happens When It Fails?"

The system does not return an empty page. It gives a safe fallback answer, keeps the request logged, and stays available for the next question.
