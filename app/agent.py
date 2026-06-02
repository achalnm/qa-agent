from google.adk.agents import LlmAgent

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="qa_agent",
    instruction=(
        "Answer the question using only the information in the provided context. "
        "If the answer is not present in the context, respond with: "
        "\"The answer is not available in the provided context.\""
    ),
)
