import os
import time
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from .agent import root_agent

app = FastAPI(title="QA Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

APP_NAME = "qa_app"


class QARequest(BaseModel):
    context: str
    question: str


@app.get("/")
def health():
    return {"status": "ok", "agent": "qa_agent"}


@app.get("/examples")
def examples():
    return {
        "examples": [
            {
                "context": (
                    "Metformin is a first-line medication for type 2 diabetes. "
                    "It works by decreasing hepatic glucose production and improving insulin sensitivity. "
                    "Common side effects include nausea and diarrhea, particularly when starting treatment. "
                    "It is contraindicated in patients with severe renal impairment due to the risk of lactic acidosis."
                ),
                "question": "Why is metformin contraindicated in patients with severe renal impairment?",
                "answer": (
                    "Metformin is contraindicated in patients with severe renal impairment because "
                    "of the risk of lactic acidosis."
                ),
            },
            {
                "context": (
                    "The Battle of Hastings took place on 14 October 1066 between the Norman forces "
                    "of William the Conqueror and the English army led by King Harold II. "
                    "Harold was killed during the battle, most likely by an arrow. "
                    "The Norman victory led to the conquest of England and fundamentally changed "
                    "the country's language, culture, and governance."
                ),
                "question": "Who led the English army at the Battle of Hastings?",
                "answer": "The English army at the Battle of Hastings was led by King Harold II.",
            },
            {
                "context": (
                    "In Python, the Global Interpreter Lock (GIL) is a mutex that protects access "
                    "to Python objects, preventing multiple native threads from executing Python bytecodes "
                    "at once. This means that even on multi-core systems, only one thread runs Python code "
                    "at a time. CPU-bound tasks do not benefit from threading in CPython because of the GIL. "
                    "I/O-bound tasks can still benefit because the GIL is released during I/O operations."
                ),
                "question": "Do CPU-bound tasks benefit from threading in CPython?",
                "answer": (
                    "No. CPU-bound tasks do not benefit from threading in CPython because the GIL "
                    "allows only one thread to execute Python bytecodes at a time, even on multi-core systems."
                ),
            },
        ]
    }


@app.post("/ask")
async def ask(request: QARequest):
    context = request.context.strip()
    question = request.question.strip()

    if len(context) < 10:
        return JSONResponse(status_code=400, content={"error": "Context is too short to answer from."})
    if len(question) < 5:
        return JSONResponse(status_code=400, content={"error": "Please provide a complete question."})
    if len(context) > 8000:
        return JSONResponse(status_code=400, content={"error": "Context is too long. Please keep it under 8000 characters."})

    start = time.perf_counter()

    try:
        session_service = InMemorySessionService()
        runner = Runner(
            agent=root_agent,
            app_name=APP_NAME,
            session_service=session_service,
        )
        session = await session_service.create_session(
            app_name=APP_NAME,
            user_id="user1",
        )
        prompt = f"Context:\n{context}\n\nQuestion:\n{question}"
        content = types.Content(
            role="user",
            parts=[types.Part(text=prompt)],
        )
        final_response = ""
        async for event in runner.run_async(
            user_id="user1",
            session_id=session.id,
            new_message=content,
        ):
            if event.is_final_response():
                final_response = event.content.parts[0].text
                break
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

    elapsed_ms = round((time.perf_counter() - start) * 1000)

    return {
        "question": question,
        "answer": final_response,
        "response_time_ms": elapsed_ms,
    }


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
