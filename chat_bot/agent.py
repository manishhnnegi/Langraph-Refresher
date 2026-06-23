import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, messages_to_dict, messages_from_dict
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory

load_dotenv()

# Initialize the LLM (Make sure OPENAI_API_KEY is set in your environment variables)
# llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
llm = init_chat_model("ollama:nemotron-3-super:cloud",base_url="https://ollama.com")


DB_FILE = "database/sessions.json"

def load_db() -> dict:
    """Reads the JSON database file."""
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({}, f)
        return {}
    
    with open(DB_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_db(data: dict):
    """Writes the updated session records to the JSON database file."""
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_chat_history_messages(session_id: str) -> list:
    """Retrieves LangChain message objects for a session from the JSON file."""
    db = load_db()
    
    if session_id not in db:
        # Create a new session history initialization with our system instruction
        initial_messages = [SystemMessage(content="You must answer every question with exactly one word.")]
        db[session_id] = messages_to_dict(initial_messages)
        save_db(db)
        return initial_messages
    
    # Reconstruct LangChain objects from raw JSON data
    return messages_from_dict(db[session_id])

def save_chat_history_messages(session_id: str, messages: list):
    """Converts LangChain message objects to JSON and saves them."""
    db = load_db()
    db[session_id] = messages_to_dict(messages)
    save_db(db)

def get_all_sessions() -> list:
    """Returns a list of all active session IDs for the sidebar layout."""
    return list(load_db().keys())

def run_agent(user_input: str, session_id: str) -> str:
    """Loads history from JSON, runs the model, updates history, and resaves."""
    messages = get_chat_history_messages(session_id)
    
    # 1. Append new user message
    messages.append(HumanMessage(content=user_input))
    
    # 2. Invoke LLM
    response = llm.invoke(messages)
    
    # 3. Append bot response
    messages.append(AIMessage(content=response.content))
    
    # 4. Commit everything to JSON file
    save_chat_history_messages(session_id, messages)
    
    return response.content