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





# MCP server and other server details

1. 'database',
2. 'employee_mcp_server.py'    ----------> these three to understand resources and prompts in MCP server used in 10_mcp_basics.ipynb
3. 'employee_client.py'


1. 'web_time_mcp.py' ---------> used in 10_mcp_basics.ipynb

1. 'session_server.py'----> to understand session used in 'session_client.ipynb'
    


# modification in DIR structure

chat_bkend --> chat backend code main.py
gmail_wtsapp --> all files related to lapp   / previous version in different branch
database --> data
mcp_server --> all server.py files




# docker commands
docker-compose up -d
(Or docker compose up -d depending on your Docker version). The -d flag runs it in the background just like before.
docker compose down

if you want to go inside 
docker exec -it my-postgres-compose psql -U postgres -d my_database
run pgsql commands


