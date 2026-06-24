import os
import sqlite3
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import START, MessagesState, StateGraph

load_dotenv()

# 1. Initialize the LLM (Using your configured setup)
llm = init_chat_model("ollama:nemotron-3-super:cloud", base_url="https://ollama.com")

# 2. Setup SQLite persistence database
DB_DIR = "database"
os.makedirs(DB_DIR, exist_ok=True)
DB_FILE = os.path.join(DB_DIR, "sessions.db")

# Establish a connection and use SqliteSaver as our memory checkpointer
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
memory = SqliteSaver(conn)

# 3. Define the LangGraph Node function
def call_model(state: MessagesState):
    """
    The main node processing user input.
    If the history is empty, it injects the strict one-word instruction.
    """
    messages = state["messages"]
    
    # Check if a system instruction is already in this thread's history
    has_system_msg = any(isinstance(m, SystemMessage) for m in messages)
    if not has_system_msg:
        messages = [SystemMessage(content="You must answer every question with exactly one word.")] + messages
        
    response = llm.invoke(messages)
    return {"messages": [response]}

# 4. Build the State Graph workflow
workflow = StateGraph(MessagesState)
workflow.add_node("chatbot", call_model)
workflow.add_edge(START, "chatbot")

# Compile the graph together with our SQLite memory manager
graph = workflow.compile(checkpointer=memory)

# --- UTILITIES FOR YOUR FASTAPI APP ---

def get_all_sessions() -> list:
    """Queries the SQLite backend directly to pull all active unique thread IDs."""
    try:
        cursor = conn.cursor()
        # LangGraph stores checkpointer IDs in the checkpoints table under 'thread_id'
        cursor.execute("SELECT DISTINCT thread_id FROM checkpoints")
        rows = cursor.fetchall()
        return [row[0] for row in rows]
    except sqlite3.OperationalError:
        # Table doesn't exist yet if no messages have been sent
        return []

def get_chat_history_messages(session_id: str) -> list:
    """Fetches the state directly from the LangGraph checkpointer storage."""
    config = {"configurable": {"thread_id": session_id}}
    state = graph.get_state(config)
    if state and "messages" in state.values:
        return state.values["messages"]
    return []

def run_agent(user_input: str, session_id: str) -> str:
    """
    Streams the user input through the LangGraph runtime graph.
    The graph automatically saves history to SQLite after completion.
    """
    config = {"configurable": {"thread_id": session_id}}
    
    # Send input into the state graph
    events = graph.stream(
        {"messages": [HumanMessage(content=user_input)]}, 
        config, 
        stream_mode="values"
    )
    
    # Iterate to get the last compiled state response
    last_event = None
    for event in events:
        last_event = event
        
    if last_event and "messages" in last_event:
        return last_event["messages"][-1].content
    return "Error generating response."