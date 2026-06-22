from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uuid

from agent import run_agent

app = FastAPI()

# Mount the templates directory to serve the static CSS file
app.mount("/static", StaticFiles(directory="templates"), name="static")
templates = Jinja2Templates(directory="templates")

# Pydantic model for JSON requests
class ChatRequest(BaseModel):
    message: str
    session_id: str


@app.get("/", response_class=HTMLResponse)
async def get_chat_page(request: Request):
    """Serves the main chat interface and generates a unique session ID."""
    unique_session_id = str(uuid.uuid4())
    
    # FIX: Explicitly pass the 'request' object as the first argument
    return templates.TemplateResponse(
        request=request,
        name="index.html", 
        context={"session_id": unique_session_id}
    )


@app.post("/chat")
async def chat_endpoint(data: ChatRequest):
    """API Endpoint that the frontend calls to get bot responses."""
    try:
        bot_response = run_agent(user_input=data.message, session_id=data.session_id)
        return JSONResponse(content={"response": bot_response})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)