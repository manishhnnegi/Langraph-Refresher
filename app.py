from fastapi import FastAPI
from pydantic import BaseModel

from langchain_core.messages import HumanMessage
from langgraph.types import Command
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()


class ChatRequest(BaseModel):
    message: str


class ResumeRequest(BaseModel):
    approved: bool


config = {
    "configurable": {
        "thread_id": "user-1"
    }
}

# Serve CSS and JS files
app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

templates = Jinja2Templates(
    directory="templates"
)


from fastapi import Request

@app.get("/")
def home(request: Request):

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request
        }
    )



@app.post("/chat")
def chat(req: ChatRequest):

    last_state = None

    for state in graph.stream(
        {
            "messages": [
                HumanMessage(content=req.message)
            ]
        },
        config=config,
        stream_mode="values"
    ):
        last_state = state

    snapshot = graph.get_state(config)

    if snapshot.interrupts:

        interrupt_data = snapshot.interrupts[0].value

        return {
            "type": "interrupt",
            "data": interrupt_data
        }

    return {
        "type": "message",
        "message": last_state["messages"][-1].content
    }



@app.post("/resume")
def resume(req: ResumeRequest):

    last_state = None

    for state in graph.stream(
        Command(resume=req.approved),
        config=config,
        stream_mode="values"
    ):
        last_state = state

    return {
        "type": "message",
        "message": last_state["messages"][-1].content
    }


