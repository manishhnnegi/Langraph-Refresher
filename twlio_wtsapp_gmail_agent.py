import os
import base64
import smtplib
from email.mime.text import MIMEText
from fastapi import FastAPI, Request, Form
from fastapi.responses import Response
from dotenv import load_dotenv

# Google Auth imports
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

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

app = FastAPI(title="WhatsApp LangGraph Real Email Bot")

# --- 1. GMAIL OAUTH2 SETUP ---
SCOPES = ["https://google.com"]
SENDER_EMAIL = "xyz@gmail.com"  # Your sender Gmail address

def get_gmail_credentials():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(GoogleRequest())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
            creds = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(creds.to_json())
    return creds


# --- 2. UPDATED LANGCHAIN EMAIL TOOL ---
@tool
def write_email(to: str, subject: str, content: str) -> str:
    """Send an actual email using the Google Gmail API via OAuth2."""
    try:
        # Get active Google credentials
        creds = get_gmail_credentials()
        access_token = creds.token

        # Create the email content
        msg = MIMEText(content)
        msg["Subject"] = subject
        msg["From"] = SENDER_EMAIL
        msg["To"] = to

        # 2. FIX: Use the correct smtp address string instead of "://gmail.com"
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.ehlo()

        auth_string = f"user={SENDER_EMAIL}\x01auth=Bearer {access_token}\x01\x01"
        auth_bytes = base64.b64encode(auth_string.encode()).decode()
        server.docmd("AUTH", "XOAUTH2 " + auth_bytes)

        # Send the actual email
        server.send_message(msg)
        server.quit()
        
        return f"Success! The email has been successfully sent to {to}."
    except Exception as e:
        return f"Failed to send email to {to}. Error details: {str(e)}"
    
# --- 3. LANGGRAPH AGENT FLOW (Same Logic) ---
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
    
    # 1. Grab the list of tool calls safely
    tool_calls = getattr(last_ai_message, "tool_calls", [])
    
    if not tool_calls:
        raise ValueError("No tool calls found to approve.")
        
    # 2. Extract the FIRST tool call dictionary from the list
    tool_call = tool_calls[0] # Added [0] here!
    
    # 3. Pass the actual clean dictionary into the interrupt
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
    return {"messages": [AIMessage(content="Email sending cancelled by user.")]}

tool_node = ToolNode(tools)

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

# --- 4. WHATSAPP WEBHOOK ROUTE ---
@app.post("/")
async def whatsapp_webhook(From: str = Form(...), Body: str = Form(...)):
    twiml_response = MessagingResponse()
    config = {"configurable": {"thread_id": From}}
    user_input = Body.strip()
    
    state_info = graph.get_state(config)
    
    # Process approval or regular chat text
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

    # Read output
    final_output = None
    for event in events:
        if "messages" in event and event["messages"]:
            final_output = event["messages"][-1].content

    # Prepare response for WhatsApp
    # Prepare response for WhatsApp
    updated_state = graph.get_state(config)
    if updated_state.next and "approval" in updated_state.next:
        
        # FIX: Extract the dictionary out of the LangGraph interrupt list safely
        interrupt_data = {}
        if updated_state.tasks:
            # Look inside the current active task for the interrupt value
            active_task = updated_state.tasks[0]
            if hasattr(active_task, 'interrupts') and active_task.interrupts:
                interrupt_data = active_task.interrupts[0].value # Grab the first interrupt's payload
            elif hasattr(updated_state.tasks, 'value'):
                interrupt_data = updated_state.tasks.value
                
        # Get the email tool arguments
        args = interrupt_data.get("tool_args", {})
        
        approval_prompt = (
            f"📧 *Draft Email ready!*\n\n"
            f"*To:* {args.get('to', 'Missing email')}\n"
            f"*Subject:* {args.get('subject', 'No Subject')}\n"
            f"*Content:* {args.get('content', 'No Content')}\n\n"
            f"Reply *'yes'* to send or *'no'* to cancel."
        )
        twiml_response.message(approval_prompt)
    else:
        twiml_response.message(str(final_output) if final_output else "Processed successfully.")

    return Response(content=str(twiml_response), media_type="application/xml")
