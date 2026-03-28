from google.adk.agents import LlmAgent

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="qa_agent",
    description="An agent that answers questions based on provided context",
    instruction="""
    You are a precise question answering assistant.
    The user will provide a context passage and a question.
    Answer the question using ONLY the information in the context.
    If the answer is not found in the context, say "The answer is not available in the provided context."
    Keep your answer concise and direct.
    """,
)
