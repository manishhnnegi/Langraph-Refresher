from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uuid

import agent

app = FastAPI()

app.mount("/static", StaticFiles(directory="templates"), name="static")
templates = Jinja2Templates(directory="templates")

class ChatRequest(BaseModel):
    message: str
    session_id: str

@app.get("/", response_class=HTMLResponse)
async def get_chat_page(request: Request, session_id: str = None):
    """
    Serves the interface. 
    If a specific session_id is provided in the URL query string, it reuses it.
    Otherwise, it initiates a fresh session ID.
    """
    if not session_id:
        session_id = str(uuid.uuid4())
        
    # Gather existing chats to show in the left-hand sidebar
    history_list = agent.get_all_sessions()
    
    return templates.TemplateResponse(
        request=request,
        name="index.html", 
        context={"session_id": session_id, "history_list": history_list}
    )

@app.get("/history/{session_id}")
async def get_raw_history(session_id: str):
    """API endpoint to fetch past chat messages for a specific session to load into the UI."""
    messages = agent.get_chat_history_messages(session_id)
    
    # Format messages nicely for the frontend JavaScript
    formatted_messages = []
    for msg in messages:
        if msg.type == "human":
            formatted_messages.append({"sender": "user", "text": msg.content})
        elif msg.type == "ai":
            formatted_messages.append({"sender": "bot", "text": msg.content})
            
    return JSONResponse(content={"messages": formatted_messages})

@app.post("/chat")
async def chat_endpoint(data: ChatRequest):
    try:
        bot_response = agent.run_agent(user_input=data.message, session_id=data.session_id)
        return JSONResponse(content={"response": bot_response})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)