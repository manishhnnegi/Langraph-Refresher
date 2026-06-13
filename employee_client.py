import asyncio
import json
from typing import TypedDict

from langgraph.graph import (
    StateGraph,
    END
)

# from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_mcp_adapters.client import (
    MultiServerMCPClient
)


import os
from dotenv import load_dotenv
# 1. Load variables from the .env file
load_dotenv()
OLLAMA_API_KEY = os.environ.get("OLLAMA_API_KEY")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")

llm = ChatOllama(
    model="nemotron-3-super:cloud",
    base_url="https://ollama.com",
    client_kwargs={"headers": {"Authorization": f"Bearer {OLLAMA_API_KEY}"}},
    )




class State(TypedDict):
    employee_name: str
    question: str
    answer: str


async def employee_agent(state: State):

    client = MultiServerMCPClient(
        {
            "my_server": {
                "url":
                    "http://localhost:8000/mcp",
                "transport":
                    "streamable_http",
            }
        }
    )

    # Correct way
    async with client.session(
        "my_server"
    ) as session:

        # -------------------
        # READ RESOURCE
        # -------------------
        resource = (
            await session.read_resource(
                "employee://all"
            )
        )

        employees = json.loads(
            resource.contents[0].text
        )

        employee = next(
            (
                emp
                for emp in employees
                if emp["name"].lower()
                == state[
                    "employee_name"
                ].lower()
            ),
            None
        )

        employee_data = (
            json.dumps(employee, indent=2)
            if employee
            else "Not found"
        )

        # -------------------
        # GET PROMPT
        # -------------------
        prompt = (
            await session.get_prompt(
                "employee_hr_prompt",
                arguments={
                    "employee_name":
                        state[
                            "employee_name"
                        ],
                    "employee_data":
                        employee_data,
                    "user_question":
                        state[
                            "question"
                        ]
                }
            )
        )

        prompt_text = (
            prompt.messages[0]
            .content.text
        )


        response = llm.invoke(
            prompt_text
        )

        return {
            "answer":
                response.content
        }


graph = StateGraph(State)

graph.add_node(
    "employee_agent",
    employee_agent
)

graph.set_entry_point(
    "employee_agent"
)

graph.add_edge(
    "employee_agent",
    END
)

app = graph.compile()


async def main():

    result = await app.ainvoke(
        {
            "employee_name":
                "Manish",

            "question":
                "What is his salary?"
        }
    )

    print(result["answer"])


asyncio.run(main())