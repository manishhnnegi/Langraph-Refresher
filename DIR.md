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


# directory structure

'docker_files' --> all the files for 
                    1. for postgres SQL server 
                    2. for mongo-DB server


'gmail_wtsapp' --> all the files with 
                    1. gmail api integration
                    2. whats app integration



'mcp_servers' --> exploration of mcp server with langraph
                    1. employee client 
                    2. time server 


'notebooks' --> all the exploration done while learning langchain 
                1. langraph basics
                2. email agent exploration
                3.


'official-langraph-basics' --> all the notebooks with notes of the langchain accedemy courses
                                based on 1. langraph
                                         2. langchain-agent
                                         3. email agent 
                                         4. whatsapp agent
                                         5. mcp basics
                                         6. SQL db connection basics
                                         7. agent basics
                                         8. session client of fast api asyinc basics





'studio' --> to run langsmith for analysis


'templates' --> frontend files for chat_bkend chatbot with tool calling with intruption using in notebook 8_interupt



'chat_bkend' --> main.py of fastapi server with agent


'chat_bot' --> simple chat bot from scratch with detailed frontend analysis version by version
                1. version 1 simple chat bot without session
                2. chatbot with session history 


'concurrent_prog' --> kept in git ignore


'database' --> all the data files used stored here in different experiments


