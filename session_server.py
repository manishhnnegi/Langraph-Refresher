from fastapi import FastAPI, Response, Cookie
from typing import Optional

app = FastAPI()

# 1. The Login: The server creates the "session"
@app.post("/login")
def login(username: str, response: Response):
    # In a real app, you'd verify the password here.
    # We fake a "Session ID" and hand it to the client as a cookie.
    session_id = f"secret_session_for_{username}"
    
    response.set_cookie(key="session_id", value=session_id)
    return {"message": f"Logged in successfully as {username}!"}

# 2. The Follow-up: The server recognizes the client via the session cookie
@app.get("/profile")
def get_profile(session_id: Optional[str] = Cookie(None)):
    if not session_id:
        return {"error": "Not logged in! No session found."}
    
    # The server reads the cookie and remembers who you are
    username = session_id.replace("secret_session_for_", "")
    return {"message": f"Welcome back to your profile, {username}!"}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("session_server:app", host="127.0.0.1", port=8080, reload=True)
