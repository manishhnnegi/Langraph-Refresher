import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from dotenv import load_dotenv

from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model

# Load environment variables
load_dotenv()

app = FastAPI(title="LangGraph Chatbot with Email Approval")
templates = Jinja2Templates(directory="templates")

# Define Tool Logic
@tool
def write_email(to: str, subject: str, content: str) -> str:
    """Write an email and save a copy to a local log file."""
    log_file = "sent_emails.txt"
    email_entry = (
        f"=== NEW EMAIL ===\n"
        f"To: {to}\n"
        f"Subject: {subject}\n"
        f"Content:\n{content}\n"
        f"=================\n\n"
    )
    with open(log_file, "a", encoding="utf-8") as file:
        file.write(email_entry)
    return f"Email successfully saved locally to {log_file} and marked as sent to {to}."

tools = [write_email]
llm = init_chat_model("google_genai:gemini-2.5-flash")
llm_with_tools = llm.bind_tools(tools)

# Define State Schema
class State(MessagesState):
    approved: bool

# Graph Nodes & Routing Functions
def chatbot_node(state: State):
    system_prompt = SystemMessage(content="You are a helpful assistant. Use tools whenever required.")
    messages = [system_prompt] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def route_tools(state: State):
    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        return "approval"
    return "__end__"

def approval_node(state: State):
    last_ai_message = state["messages"][-1]
    tool_call = last_ai_message.tool_calls[0]
    
    # Execution halts here until a payload is passed via graph.stream(Command(resume=...))
    approval = interrupt(
        {
            "question": "Do you approve sending this email?",
            "tool_name": tool_call["name"],
            "tool_args": tool_call["args"]
        }
    )
    return {"approved": approval}

def route_after_approval(state: State):
    if state.get("approved") is True:
        return "tools"
    return "cancel"

def cancel_node(state: State):
    return {"messages": [AIMessage(content="Email sending cancelled.")]}

tool_node = ToolNode(tools)

# Build StateGraph
builder = StateGraph(State)
builder.add_node("chatbot", chatbot_node)
builder.add_node("tools", tool_node)
builder.add_node("approval", approval_node)
builder.add_node("cancel", cancel_node)

builder.add_edge(START, "chatbot")

builder.add_conditional_edges(
    "chatbot",
    route_tools,
    {
        "approval": "approval",
        "__end__": END,
    },
)

builder.add_conditional_edges(
    "approval",
    route_after_approval,
    {
        "tools": "tools",
        "cancel": "cancel"
    }
)

builder.add_edge("tools", "chatbot")
builder.add_edge("cancel", END)

memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

# Input Schemas
class ChatRequest(BaseModel):
    message: str | None = None
    thread_id: str
    action: str | None = None  # "approve" or "cancel"

@app.get("/", response_class=HTMLResponse)
async def get_ui(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/api/chat")
async def chat_endpoint(payload: ChatRequest):
    config = {"configurable": {"thread_id": payload.thread_id}}
    
    try:
        # Scenario A: Processing action inputs from an active human interrupt sequence
        if payload.action in ["approve", "cancel"]:
            is_approved = (payload.action == "approve")
            
            # Resume processing step feeding approval decision back into the graph
            for event in graph.stream(Command(resume=is_approved), config=config, stream_mode="values"):
                pass
                
        # Scenario B: Standard text messaging entry point 
        else:
            if not payload.message or not payload.message.strip():
                raise HTTPException(status_code=400, detail="Message cannot be empty")
            
            for event in graph.stream({"messages": [HumanMessage(content=payload.message)]}, config=config, stream_mode="values"):
                pass

        # Inspect if graph has hit an active interrupt checkpoint block
        snapshot = graph.get_state(config)
        if snapshot.interrupts:
            # CORRECT FIX: Access the first element index from the active interrupts list
            interrupt_data = snapshot.interrupts[0].value
            return {
                "status": "interrupt_required",
                "question": interrupt_data.get("question"),
                "tool_args": interrupt_data.get("tool_args")
            }

        # Otherwise safely grab final response element from messages context array
        bot_reply = snapshot.values["messages"][-1].content
        return {"status": "success", "reply": bot_reply}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
