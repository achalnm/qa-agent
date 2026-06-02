# QA Agent

This is a context-grounded question answering API built with Google ADK and Gemini 2.5 Flash, served via FastAPI and deployed on Google Cloud Run. It was built as a learning project during the Google Cloud Gen AI Academy APAC 2026 programme to get hands-on experience with the Google Agent Development Kit and the full loop of building and deploying an AI agent to Cloud Run. You send it a passage of text and a question, and it answers the question using only what is in that passage.

## Project structure

```text
qa-agent/
├── app/
│   ├── __init__.py
│   ├── agent.py        # LlmAgent definition and instruction prompt
│   └── main.py         # FastAPI app, routes, and ADK runner logic
├── .gitignore
├── Dockerfile
├── README.md
└── requirements.txt
```

## How it works

1. A POST request arrives at `/ask` with a `context` string and a `question` string. The server validates both fields for length before doing anything else.
2. A new `InMemorySessionService` is created for the request. This is ADK's in-process session store, which holds conversational state in memory for the lifetime of the object. There is no database and no state shared between requests.
3. An ADK `Runner` is instantiated with the `LlmAgent` defined in `app/agent.py`. The runner formats the context and question into a single prompt and calls `runner.run_async`, which streams events back from the Gemini API via the ADK event loop.
4. The runner emits events as the model generates output. The code listens for `is_final_response()` to be true, extracts the text from the first part of the response content, and returns it. The agent's instruction explicitly tells it to refuse any question that cannot be answered from the provided context, so it will not fall back to general knowledge.

## API

Live URL: Previously deployed on Google Cloud Run during the Google Cloud Gen AI Academy APAC 2026 programme. The deployment has since been taken down as the programme concluded and billing was closed. To run the API yourself, follow the local setup instructions below.

### GET /

Health check.

```bash
curl https://YOUR_CLOUD_RUN_URL/
```

Response:

```json
{ "status": "ok", "agent": "qa_agent" }
```

### POST /ask

Accepts a context passage and a question. Returns the agent's answer and how long the agent took to respond.

```bash
curl -X POST https://YOUR_CLOUD_RUN_URL/ask \
  -H "Content-Type: application/json" \
  -d '{
    "context": "The Eiffel Tower was completed in 1889 and stands 330 metres tall.",
    "question": "How tall is the Eiffel Tower?"
  }'
```

Response:

```json
{
  "question": "How tall is the Eiffel Tower?",
  "answer": "The Eiffel Tower stands 330 metres tall.",
  "response_time_ms": 1423
}
```

Validation rules:

- `context` must be between 10 and 8000 characters
- `question` must be at least 5 characters

Errors return HTTP 400 with an `error` field explaining what is wrong.

### GET /examples

Returns three hardcoded examples showing what the agent can do. Useful for testing and for reading the API docs.

```bash
curl https://YOUR_CLOUD_RUN_URL/examples
```

Response includes a medical example, a historical example, and a technical example, each with a context, question, and sample answer.

## Running locally

Set your API key:

```bash
export GOOGLE_API_KEY=your_key_here
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the server:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

The server will be available at `http://localhost:8080`.

## Running with Docker

Build the image:

```bash
docker build -t qa-agent .
```

Run the container:

```bash
docker run -e GOOGLE_API_KEY=your_key_here -e PORT=8080 -p 8080:8080 qa-agent
```

## Design decisions

**Why InMemorySessionService instead of a persistent session store.** Each request creates a fresh session and discards it when the response is returned. This is appropriate here because the agent does not need to remember anything across requests. The context is always provided inline by the caller. Using a persistent store would add infrastructure complexity with no benefit for this use case.

**Why the agent refuses to answer outside the context.** The instruction prompt tells the agent to respond with a fixed message if the answer is not in the context, rather than drawing on general knowledge. This is a deliberate constraint. The point of this API is to let callers ground the model to their own material. If the model fell back to general knowledge silently, callers would have no way to tell whether the answer came from their text or from the model's training data.

**Why a new session is created per request instead of reusing sessions.** ADK sessions are designed to carry multi-turn conversation history. Reusing a session across unrelated requests would cause the model to see previous context and question pairs when answering the current one, which would produce incorrect or confusing answers. Starting fresh each time keeps each request independent.

## Tech stack

| Component | Details |
| --- | --- |
| Agent framework | Google ADK 1.0.0 |
| Model | Gemini 2.5 Flash via google-genai |
| API server | FastAPI 0.136.3 + Uvicorn 0.48.0 |
| Runtime | Python 3.11 |
| Container | Docker on python:3.11-slim |
| Hosting | Google Cloud Run |

## Limitations

Sessions are not persisted, so there is no conversation history across requests. Each call is stateless.

The agent does not indicate which sentence or part of the context it used to form its answer. The answer is grounded to the context but the source within the context is not cited.

Input is capped at 8000 characters of context per request. Long documents need to be chunked before being sent.
