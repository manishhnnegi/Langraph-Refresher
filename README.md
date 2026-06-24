# 🚀 AI Agent & LangGraph Learning Repository

This repository contains all experiments, projects, learning materials, and implementations related to **LangChain**, **LangGraph**, **MCP Servers**, **FastAPI**, **WhatsApp/Gmail Integrations**, and **AI Agent Development**.

---

# 📂 Project Structure

```text
.
├── docker_files/
├── gmail_wtsapp/
├── mcp_servers/
├── notebooks/
├── official-langraph-basics/
├── studio/
├── templates/
├── chat_bkend/
├── chat_bot/
├── concurrent_prog/
└── database/
```

---

# 📁 Directory Details

## 1. docker_files/

Contains Docker configurations and setup files for database services.

### Contents

* PostgreSQL Server setup
* MongoDB Server setup
* Docker Compose configurations
* Environment configuration files

### Purpose

Used for quickly provisioning local database environments required by agents and applications.

---

## 2. gmail_wtsapp/

Contains integrations with communication platforms.

### Features

#### Gmail API Integration

* Read emails
* Send emails
* Email agent experimentation
* Gmail authentication and token management

#### WhatsApp Integration

* WhatsApp messaging workflows
* Twilio integration
* WhatsApp Agent experiments

### Purpose

Used for building AI agents capable of email and messaging interactions.

---

## 3. mcp_servers/

Exploration and implementation of MCP (Model Context Protocol) servers with LangGraph.

### Implementations

#### Employee MCP Server

* Employee data retrieval
* Resource exposure
* MCP client-server communication

#### Time MCP Server

* Time-related tools
* Date and timezone utilities
* MCP server experimentation

### Purpose

Understanding MCP architecture and integrating external resources with agents.

---

## 4. notebooks/

Contains exploratory Jupyter notebooks created during learning and experimentation.

### Topics Covered

* LangGraph basics
* LangChain fundamentals
* Email Agent exploration
* WhatsApp Agent exploration
* Tool Calling
* Memory management
* FastAPI integration
* Agent orchestration experiments

### Purpose

Personal learning notes, prototypes, and proof-of-concept implementations.

---

## 5. official-langraph-basics/

Contains notes and implementations based on LangChain Academy courses.

### Learning Modules

#### LangGraph

* State management
* Nodes and edges
* Graph orchestration

#### LangChain Agents

* Agent creation
* Tool integration
* Memory

#### Email Agent

* Gmail integration
* Email workflows

#### WhatsApp Agent

* Messaging automation
* Agent workflows

#### MCP Basics

* MCP concepts
* MCP servers
* MCP clients

#### SQL Database Connections

* Database integrations
* Query execution
* Agent database access

#### Agent Basics

* ReAct pattern
* Tool calling
* Structured outputs

#### FastAPI Async Session Client

* Async programming
* Session handling
* API integrations

### Purpose

Structured learning material and reference implementations.

---

## 6. studio/

Contains configurations and files related to LangSmith Studio.

### Usage

* Agent tracing
* Workflow debugging
* Performance analysis
* Execution monitoring

### Purpose

Observability and debugging of LangGraph/LangChain applications.

---

## 7. templates/

Frontend templates used by chatbot applications.

### Features

* Chat UI
* Tool-calling support
* Human interruption workflows
* LangGraph integration examples

### Reference

Used heavily in:

```text
notebooks/8_interrupt
```

### Purpose

Frontend experimentation and reusable UI components.

---

## 8. chat_bkend/

Main FastAPI backend application.

### Components

* FastAPI server
* LangGraph agent integration
* Tool execution
* Session management
* API endpoints

### Entry Point

```python
main.py
```

### Purpose

Production-style backend implementation for AI agents.

---

## 9. chat_bot/

Step-by-step chatbot implementations built from scratch.

### Versions

#### Version 1

* Basic chatbot
* No session management

#### Version 2

* Session history support
* Persistent conversations

### Purpose

Understanding chatbot architecture evolution through incremental development.

---

## 10. concurrent_prog/

Contains concurrency and parallel programming experiments.

### Notes

* Included in `.gitignore`
* Used for local experimentation
* Not part of repository commits

### Topics

* Async programming
* Parallel execution
* Performance testing

---

## 11. database/

Central storage location for datasets and experiment files.

### Contents

* JSON files
* SQLite databases
* CSV files
* Sample datasets
* Agent testing data

### Purpose

Maintains all data assets used across projects and experiments.

---

# 🛠 Technology Stack

### AI Frameworks

* LangChain
* LangGraph
* MCP (Model Context Protocol)

### Backend

* FastAPI
* Python

### Databases

* PostgreSQL
* MongoDB
* SQLite

### Communication

* Gmail API
* Twilio WhatsApp API

### DevOps

* Docker
* Docker Compose

### Observability

* LangSmith

---

# 🎯 Repository Goals

This repository serves as a:

* Learning hub for LangChain and LangGraph
* Agent development playground
* MCP experimentation environment
* FastAPI backend reference
* Communication agent framework
* Collection of reusable AI agent components

---

# 📌 Notes

This repository is organized to separate:

* Learning materials
* Experiments
* Production-ready implementations
* Backend services
* Frontend templates
* Database resources

making it easier to navigate, maintain, and extend future AI agent projects.

