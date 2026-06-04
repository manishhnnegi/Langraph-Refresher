from langchain_core.messages import HumanMessage
from langgraph.types import Command

from typing import Annotated

# from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
    AIMessage,
)

from langgraph.graph import (
    StateGraph,
    MessagesState,
    START,
    END,
)
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command
from langchain_core.tools import tool



from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
# 1. Load variables from the .env file
load_dotenv()
OLLAMA_API_KEY = os.environ.get("OLLAMA_API_KEY")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")




# @tool
# def write_email(to: str, subject: str, content: str) -> str:
#     """Write and send an email."""
#     # Placeholder response - in real app would send email
#     return f"Email sent to {to} with subject '{subject}' and content: {content}"




@tool
def write_email(to: str, subject: str, content: str) -> str:
    """Write an email and save a copy to a local log file."""
    log_file = "sent_emails.txt"
    
    # Format the email data for clean visual separation in the file
    email_entry = (
        f"=== NEW EMAIL ===\n"
        f"To: {to}\n"
        f"Subject: {subject}\n"
        f"Content:\n{content}\n"
        f"=================\n\n"
    )
    
    # Append the email data to the local file
    with open(log_file, "a", encoding="utf-8") as file:
        file.write(email_entry)
        
    return f"Email successfully saved locally to {log_file} and marked as sent to {to}."


tools = [write_email]
llm = init_chat_model("google_genai:gemini-2.5-flash")
llm_with_tools = llm.bind_tools(tools)




class State(MessagesState):
    approved: bool

def approval_node(state):
    last_ai_message = state["messages"][-1]
    tool_call = last_ai_message.tool_calls[0]
    approval = interrupt(
        {
            "question": "Do you approve sending this email?",
            "tool_name": tool_call["name"],
            "tool_args": tool_call["args"]
        }
    )
    return {
        "approved": approval
    }


def route_after_approval(state):
    if state["approved"]:
        return "tools"

    return "cancel"

def cancel_node(state):
    return {"messages": [AIMessage(content="Email sending cancelled.")]}


def chatbot_node(state: State):
    messages = [SystemMessage(content="You are a helpful assistant. Use tools whenever required.")] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


def route_tools(state):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "approval"

    return "__end__"


# def route_tools(state):
#     last_message = state["messages"][-1]

#     if hasattr(last_message, "tool_calls") and last_message.tool_calls:
#         return "tools"

#     return "__end__"

tool_node = ToolNode(tools)




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
# display(Image(graph.get_graph().draw_mermaid_png()))



while True:

    user_input = input("\nYou: ")

    if user_input.lower() == "exit":
        break

    last_state = None

    # Run graph
    for state in graph.stream(
        {
            "messages": [
                HumanMessage(content=user_input)
            ]
        },
        config=config,
        stream_mode="values",
    ):
        last_state = state

    # Check for interrupt
    snapshot = graph.get_state(config)

    if snapshot.interrupts:

        interrupt_data = snapshot.interrupts[0].value

        print("\nApproval Required")
        print(interrupt_data)

        answer = input(
            "\nApprove sending email? (yes/no): "
        )

        last_state = None

        # Resume graph
        for state in graph.stream(
            Command(
                resume=answer.lower() == "yes"
            ),
            config=config,
            stream_mode="values",
        ):
            last_state = state

    # Print final assistant response
    if last_state:
        print(
            "\nBot:",
            last_state["messages"][-1].content
        )