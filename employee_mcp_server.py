import json
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("mcp_server")


# -----------------------------
# RESOURCE
# -----------------------------
@mcp.resource("employee://all")
def get_employee_data():
    """Read employee data"""

    with open(
        r"C:\E_DRIVE\Langraph-Refresher\database\EMPLOYEE.json",
        "r"
    ) as f:
        data = json.load(f)

    return json.dumps(data)


# --------------------------------------
# New added
# -----------------------------------------
# Helper function to avoid duplicating file-reading logic
def _load_all_employees():
    with open(
        r"C:\E_DRIVE\Langraph-Refresher\database\EMPLOYEE.json",
        "r"
    ) as f:
        return json.load(f)



@mcp.resource("employee://{employee_id}")
def get_employee_by_id(employee_id: str) -> str:
    """Read a specific employee data by their ID"""
    employees = _load_all_employees()
    # FastMCP routes path variables as string arguments.
    # If your JSON IDs are integers, we convert them during the search.
    employee = next(
        (emp for emp in employees if str(emp.get("id")) == employee_id), 
        None
    )
    
    if not employee:
        return json.dumps({"error": f"Employee with ID {employee_id} not found"})
        
    return json.dumps(employee, indent=2)

# -----------------------------
# PROMPT
# -----------------------------
@mcp.prompt()
def employee_hr_prompt(
    employee_name: str,
    employee_data: str,
    user_question: str
):
    return f"""
You are an HR assistant.

Answer employee-related questions
strictly based on employee data.

Employee Name:
{employee_name}

Employee Data:
{employee_data}

User Question:
{user_question}

Rules:
- Do not hallucinate
- If employee missing,
  say 'Employee not found'
"""


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http"
    )