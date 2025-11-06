"""
Employee data tools - INTENTIONALLY VULNERABLE (Lab 4: IDOR)
"""
from langchain_core.tools import tool
import httpx
import logging

logger = logging.getLogger(__name__)


@tool
def get_employee_info(employee_id: str) -> str:
    """
    Get employee information including salary and PTO balance.

    ⚠️ INTENTIONALLY VULNERABLE (Lab 4: IDOR) ⚠️
    This tool accepts any employee ID without validating authorization.
    A secure implementation would check if the requester is authorized to view the requested employee's data.

    Args:
        employee_id: The employee ID to look up (e.g., "E1001", "E1002", etc.)

    Returns:
        Employee information including name, salary, PTO balance, and department.

    Examples:
        - get_employee_info("E1001") - Get info for employee E1001
        - get_employee_info("E1003") - Get info for employee E1003
    """
    try:
        logger.info(f"[LAB 4 IDOR TOOL] Getting employee info for: {employee_id}")

        # Call the internal API endpoint
        # VULNERABILITY: No authorization check - accepts any employee_id!
        response = httpx.get(f"http://localhost:8000/api/employee/{employee_id}", timeout=5.0)

        if response.status_code == 404:
            return f"Employee {employee_id} not found in the system."

        response.raise_for_status()
        data = response.json()

        employee = data.get("employee", {})

        # Format the response
        result = f"""Employee Information Retrieved:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Employee ID: {employee.get('employee_id')}
Name: {employee.get('name')}
Email: {employee.get('email')}
Department: {employee.get('department')}
Salary: {employee.get('salary')}
PTO Balance: {employee.get('pto_balance')} days
Hire Date: {employee.get('hire_date')}
Manager: {employee.get('manager')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

        if data.get("lab_message"):
            result += f"\n\n{data['lab_message']}"
            logger.warning(f"[LAB 4 IDOR TOOL] ⚠️ UNAUTHORIZED ACCESS: {employee.get('name')} ({employee_id}) data exposed!")

        return result

    except httpx.HTTPError as e:
        logger.error(f"[LAB 4 IDOR TOOL] HTTP error: {e}")
        return f"Error retrieving employee information: {str(e)}"
    except Exception as e:
        logger.error(f"[LAB 4 IDOR TOOL] Unexpected error: {e}")
        return f"Unexpected error: {str(e)}"
