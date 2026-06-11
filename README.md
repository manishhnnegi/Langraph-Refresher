# Langraph-Refresher
Refresher to Langraph, How it works!


# Create virtual env!
uv init
uv venv --python 3.11

# Ativate env
.venv\Scripts\activate

# Add dependencies
uv add ruff


# run server
uvicorn main:app --reload   ---> chat bot using html jawascript frontend

# agent server
uvicorn twlio_wtsapp_gmail_agent:app --port 5000 ---> agent integrated with whatsapp ( twilio) and gmailapi


# LANGCHAIN BASICS
https://github.com/AnmolTomer/langchain-basics
