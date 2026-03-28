import os
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from agent import root_agent

app = FastAPI(title="Question Answering Agent")

APP_NAME = "qa_app"

class QARequest(BaseModel):
    context: str
    question: str

@app.get("/")
def health():
    return {"status": "ok", "agent": "qa_agent"}

@app.post("/ask")
async def ask(request: QARequest):
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
    prompt = f"Context:\n{request.context}\n\nQuestion:\n{request.question}"
    content = types.Content(
        role="user",
        parts=[types.Part(text=prompt)]
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
    return {
        "question": request.question,
        "answer": final_response
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
