import asyncio
from typing import Annotated, Sequence
from typing_extensions import TypedDict

from langchain_mcp_adapters.client import MultiServerMCPClient
import os
from langchain_ollama import ChatOllama
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode


import os
from dotenv import load_dotenv
# 1. Load variables from the .env file
load_dotenv()
OLLAMA_API_KEY = os.environ.get("OLLAMA_API_KEY")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")

# can be done with 
from langgraph.graph import MessagesState 
class AgentState(MessagesState):
    pass

# 1. Define the Graph State structure
class AgentState(TypedDict):
    # This automatically appends new messages to the existing list history
    messages: Annotated[Sequence[BaseMessage], add_messages]

async def main():
    # 2. Connect to your MCP Server
    client = MultiServerMCPClient(
    {
        "my_server": {
            "url": "http://localhost:8000/mcp",
            "transport": "streamable_http",
        }
    }
    )
    
    tools = await client.get_tools()
    prompt_messages = await client.get_prompt("my_server", "prompt")
    system_prompt = prompt_messages[0].content

    # 3. Configure your custom ChatOllama instance
    llm = ChatOllama(
    model="nemotron-3-super:cloud",
    base_url="https://ollama.com",
    client_kwargs={"headers": {"Authorization": f"Bearer {OLLAMA_API_KEY}"}},
    )
    
    # Bind the available tools directly into the LLM model instance
    llm_with_tools = llm.bind_tools(tools)

    # 4. Define the Node functions
    async def call_model(state: AgentState):
        """Node function to let the AI think and respond."""
        messages = state["messages"]
        
        # Inject the system prompt rules at the start of the message list
        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + list(messages)
            
        response = await llm_with_tools.ainvoke(messages)
        return {"messages": [response]}

    def should_continue(state: AgentState):
        """Conditional routing logic to check if tools are requested."""
        last_message = state["messages"][-1]
        
        # If the LLM wants to call a tool, route the graph to the tools node
        if getattr(last_message, "tool_calls", None):
            return "tools"
        
        # Otherwise, stop the workflow loop and return the final response
        return END

    # 5. Build the manual StateGraph workflow pipeline
    workflow = StateGraph(AgentState)

    # Add the worker nodes
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", ToolNode(tools))  # Standard node that runs tool code

    # Connect the structural logic wires
    workflow.add_edge(START, "agent")
    
    # Add conditional route logic out of the agent node
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",  # If should_continue returns "tools", go to tools node
            END: END           # If should_continue returns END, stop execution
        }
    )

    # Connect the tools node back to the agent so it can read tool outputs
    workflow.add_edge("tools", "agent")

    # Compile the final application graph
    app = workflow.compile()

    # 6. Run a query through your manual graph
    inputs = {
        "messages": [
            {"role": "user", "content": "What is LangGraph and what tools do you have answer in two lines only"}
        ]
    }
    
    response = await app.ainvoke(inputs)
    
    print("\n--- Final Script Output ---")
    print(response["messages"][-1].content)

if __name__ == "__main__":
    asyncio.run(main())
