import asyncio
import sys
from langchain_mcp_adapters.client import MultiServerMCPClient

# 1. Apply the Windows subprocess async patch 
# This must happen at the very top level of the script
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

async def main():
    print("Connecting to the Time MCP Server via uvx...")
    
    # 2. Define the Multi-Server client configuration
    client = MultiServerMCPClient(
        {
            "time": {
                "transport": "stdio",
                "command": "uvx",
                "args": [
                    "mcp-server-time",
                    "--local-timezone=America/New_York"
                ]
            }
        }
    )

    try:
        # 3. Fetch the tools from the active server instance
        tools = await client.get_tools()
        
        print(f"\n✅ Successfully connected! Loaded {len(tools)} tools:")
        for tool in tools:
            print(f" - Tool Name: {tool.name}")
            print(f"   Description: {tool.description}\n")
            
    except Exception as e:
        print(f"\n❌ Failed to load tools: {str(e)}")
        print("Make sure you can run 'uvx --version' directly in your command prompt.")

# 4. Entry point to execute the asynchronous main loop safely
if __name__ == "__main__":
    asyncio.run(main())

