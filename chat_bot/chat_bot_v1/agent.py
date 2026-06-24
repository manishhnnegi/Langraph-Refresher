import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory

load_dotenv()

# Initialize the LLM (Make sure OPENAI_API_KEY is set in your environment variables)
# llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
llm = init_chat_model("ollama:nemotron-3-super:cloud",base_url="https://ollama.com")

# Dictionary to hold chat histories for different sessions
sessions_db = {}

def get_chat_history(session_id: str) -> InMemoryChatMessageHistory:
    """Retrieves or creates a chat history for a specific session."""
    if session_id not in sessions_db:
        history = InMemoryChatMessageHistory()
        history.add_message(SystemMessage(content="You must answer every question with exactly one word."))
        sessions_db[session_id] = history
    return sessions_db[session_id]

def run_agent(user_input: str, session_id: str = "default_user") -> str:
    """Appends user input to history, invokes the LLM, and stores the response."""
    history = get_chat_history(session_id)
    history.add_message(HumanMessage(content=user_input))
    response = llm.invoke(history.messages)
    history.add_message(AIMessage(content=response.content))
    
    return response.content