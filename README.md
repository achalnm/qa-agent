# QA Agent

A question answering agent built with Google ADK and Gemini 2.5 Flash, served via FastAPI and deployed on Google Cloud Run.

## What it does

The agent accepts a context passage and a question, then answers the question using only the information present in the context. If the answer cannot be found in the context, it explicitly says so rather than guessing.

## Tech Stack

- Google ADK (Agent Development Kit) 1.0.0
- Gemini 2.5 Flash (via Google GenAI)
- FastAPI
- Uvicorn
- Docker
- Google Cloud Run

## Project Structure

```
qa-agent/
├── agent.py           # Defines the LlmAgent with its instruction prompt
├── main.py            # FastAPI app with /ask endpoint and ADK runner logic
├── requirements.txt   # Python dependencies
└── Dockerfile         # Container setup using python:3.11-slim
```

## API Endpoints

### GET /
Health check. Returns the agent status.

```json
{ "status": "ok", "agent": "qa_agent" }
```

### POST /ask
Accepts a context and a question, returns the agent's answer.

Request body:
```json
{
  "context": "Your context passage here.",
  "question": "Your question here."
}
```

Response:
```json
{
  "question": "Your question here.",
  "answer": "The agent's answer based on the context."
}
```

## How it works

1. The FastAPI app receives a POST request to `/ask` with a context and question.
2. A new ADK session is created using `InMemorySessionService` for each request.
3. The context and question are combined into a single prompt and passed to the `LlmAgent` backed by Gemini 2.5 Flash.
4. The runner streams events asynchronously and extracts the final response.
5. The answer is returned in the response body alongside the original question.

## Running locally

Install dependencies:
```bash
pip install -r requirements.txt
```

Run the server:
```bash
uvicorn main:app --host 0.0.0.0 --port 8080
```

## Running with Docker

Build the image:
```bash
docker build -t qa-agent .
```

Run the container:
```bash
docker run -e PORT=8080 -p 8080:8080 qa-agent
```

## Deployment

This project is deployed on Google Cloud Run. The container reads the `PORT` environment variable at startup, which Cloud Run sets automatically.

## Notes

- Sessions are in-memory and not persisted between requests.
- The agent is strictly grounded to the provided context and will not answer from general knowledge.
