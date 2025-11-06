"""
Employee data API - INTENTIONALLY VULNERABLE (Lab 4: IDOR)
"""
from fastapi import APIRouter, HTTPException
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# Employee database - simulating real employee records
EMPLOYEE_DATABASE = {
    "E1001": {
        "employee_id": "E1001",
        "name": "John Smith",
        "email": "john.smith@aifirst.com",
        "department": "Engineering",
        "salary": "$120,000",
        "pto_balance": 15,
        "hire_date": "2020-03-15",
        "manager": "Sarah Johnson"
    },
    "E1002": {
        "employee_id": "E1002",
        "name": "Sarah Johnson",
        "email": "sarah.johnson@aifirst.com",
        "department": "Engineering",
        "salary": "$145,000",
        "pto_balance": 22,
        "hire_date": "2018-07-01",
        "manager": "Michael Chen"
    },
    "E1003": {
        "employee_id": "E1003",
        "name": "Michael Chen",
        "email": "michael.chen@aifirst.com",
        "department": "Engineering",
        "salary": "$185,000",
        "pto_balance": 25,
        "hire_date": "2015-01-10",
        "manager": "CEO"
    },
    "E1004": {
        "employee_id": "E1004",
        "name": "Emily Rodriguez",
        "email": "emily.rodriguez@aifirst.com",
        "department": "Sales",
        "salary": "$75,000",
        "pto_balance": 18,
        "hire_date": "2021-09-20",
        "manager": "David Park"
    },
    "E1005": {
        "employee_id": "E1005",
        "name": "David Park",
        "email": "david.park@aifirst.com",
        "department": "Sales",
        "salary": "$65,000",
        "pto_balance": 10,
        "hire_date": "2022-11-05",
        "manager": "Sarah Johnson"
    }
}


@router.get("/api/employee/{employee_id}")
async def get_employee_data(employee_id: str):
    """
    Get employee information by employee ID.

    ⚠️ INTENTIONALLY VULNERABLE (Lab 4: IDOR) ⚠️
    This endpoint does NOT validate that the requester is authorized to view this employee's data.  
    """
    logger.warning(f"[LAB 4 IDOR] Employee data requested: {employee_id}")

    # VULNERABILITY: No authorization check!
    # Should validate: Does the requester have permission to view this employee's data?
    # In a real system, this would check session/token and compare to employee_id

    if employee_id not in EMPLOYEE_DATABASE:
        raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")

    employee_data = EMPLOYEE_DATABASE[employee_id]

    # Log successful unauthorized access
    if employee_id != "E1001":  # E1001 is the "logged in user"
        logger.warning(f"[LAB 4 IDOR] ⚠️ UNAUTHORIZED ACCESS: Employee {employee_id} data accessed without authorization!")
        logger.warning(f"[LAB 4 IDOR] Exposed data: {employee_data['name']} - {employee_data['salary']}")

    return {
        "status": "success",
        "employee": employee_data,
        "lab_message": "🎯 Lab 4 Success! You've successfully exploited IDOR to access unauthorized employee data." if employee_id != "E1001" else None
    }
