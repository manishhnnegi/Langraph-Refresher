import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import Response
from dotenv import load_dotenv

# Twilio and LangGraph imports
from twilio.twiml.messaging_response import MessagingResponse
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model

load_dotenv()

app = FastAPI(title="WhatsApp LangGraph Email Bot")

# --- 1. DEFINE TOOLS & GRAPH LOOPS (Your Original Logic) ---

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

class State(MessagesState):
    approved: bool

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
    
    # FIX: Get the FIRST tool call out of the list safely
    tool_calls = getattr(last_ai_message, "tool_calls", [])
    if not tool_calls:
        raise ValueError("No tool calls found to approve.")
    
    tool_call = tool_calls[0]
    
    # Execution halts here until Command(resume=...) is passed
    approval = interrupt(
        {
            "question": "Do you approve sending this email?",
            "tool_name": tool_call.get("name"),
            "tool_args": tool_call.get("args")
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
builder.add_conditional_edges("chatbot", route_tools, {"approval": "approval", "__end__": END})
builder.add_conditional_edges("approval", route_after_approval, {"tools": "tools", "cancel": "cancel"})
builder.add_edge("tools", "chatbot")
builder.add_edge("cancel", END)

memory = MemorySaver()
graph = builder.compile(checkpointer=memory)


# --- 2. WHATSAPP WEBHOOK INTEGRATION ---


@app.post("/")  # or "/whatsapp" depending on your path setup
async def whatsapp_webhook(From: str = Form(...), Body: str = Form(...)):
    twiml_response = MessagingResponse()
    config = {"configurable": {"thread_id": From}}
    user_input = Body.strip()
    
    state_info = graph.get_state(config)
    
    if state_info.next and "approval" in state_info.next:
        if user_input.lower() in ["yes", "y", "approve"]:
            events = graph.stream(Command(resume=True), config, stream_mode="values")
        elif user_input.lower() in ["no", "n", "cancel"]:
            events = graph.stream(Command(resume=False), config, stream_mode="values")
        else:
            twiml_response.message("Please reply with 'yes' to send or 'no' to cancel.")
            return Response(content=str(twiml_response), media_type="application/xml")
    else:
        events = graph.stream({"messages": [HumanMessage(content=user_input)]}, config, stream_mode="values")

    final_output = None
    for event in events:
        if "messages" in event and event["messages"]:
            final_output = event["messages"][-1].content

    updated_state = graph.get_state(config)
    if updated_state.next and "approval" in updated_state.next:
        # FIX: LangGraph wraps interrupt list items inside a special structure
        # We need to grab the actual dictionary inside the interrupt value safely
        try:
            raw_interrupts = updated_state.tasks[0].interrupts
            interrupt_data = raw_interrupts[0].value
        except Exception:
            interrupt_data = updated_state.tasks.interrupts.value if hasattr(updated_state.tasks, 'interrupts') else {}
            
        args = interrupt_data.get("tool_args", {})
        
        approval_prompt = (
            f"📧 *Draft Email ready!*\n\n"
            f"*To:* {args.get('to')}\n"
            f"*Subject:* {args.get('subject')}\n"
            f"*Content:* {args.get('content')}\n\n"
            f"Reply *'yes'* to send or *'no'* to cancel."
        )
        twiml_response.message(approval_prompt)
    else:
        twiml_response.message(str(final_output) if final_output else "Processed successfully.")

    return Response(content=str(twiml_response), media_type="application/xml")
