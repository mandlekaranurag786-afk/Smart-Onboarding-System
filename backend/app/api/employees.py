"""
Employee Directory API endpoints
Provides search and profile access for employees/stakeholders
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from app.database import get_db
from app.models.stakeholder import Stakeholder

router = APIRouter()

# Pydantic Schemas
class EmployeeResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    department: Optional[str]
    is_available: bool
    on_leave_until: Optional[str]

class EmployeeDetailResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    department: Optional[str]
    is_available: bool
    on_leave_until: Optional[str]
    fallback_stakeholder_id: Optional[str]
    created_at: str
    updated_at: str

@router.get("/", response_model=List[EmployeeResponse])
async def search_employees(
    search: Optional[str] = Query(None, description="Search by name, email, or role"),
    department: Optional[str] = Query(None, description="Filter by department"),
    role: Optional[str] = Query(None, description="Filter by role"),
    available_only: bool = Query(False, description="Show only available employees"),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    db: Session = Depends(get_db)
):
    """
    Search and filter employees/stakeholders
    Supports filtering by name, email, role, department, and availability
    """
    query = db.query(Stakeholder)
    
    # Apply search filter
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Stakeholder.name.like(search_pattern)) |
            (Stakeholder.email.like(search_pattern)) |
            (Stakeholder.role.like(search_pattern))
        )
    
    # Apply department filter
    if department:
        query = query.filter(Stakeholder.department == department)
    
    # Apply role filter
    if role:
        query = query.filter(Stakeholder.role == role)
    
    # Apply availability filter
    if available_only:
        query = query.filter(Stakeholder.is_available == True)
    
    # Get total count before pagination
    total = query.count()
    
    # Apply pagination
    employees = query.offset(offset).limit(limit).all()
    
    return [
        EmployeeResponse(
            id=emp.id,
            name=emp.name,
            email=emp.email,
            role=emp.role,
            department=emp.department,
            is_available=emp.is_available,
            on_leave_until=emp.on_leave_until
        )
        for emp in employees
    ]

@router.get("/{employee_id}", response_model=EmployeeDetailResponse)
async def get_employee_profile(
    employee_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed employee profile by ID
    """
    employee = db.query(Stakeholder).filter_by(id=employee_id).first()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    return EmployeeDetailResponse(
        id=employee.id,
        name=employee.name,
        email=employee.email,
        role=employee.role,
        department=employee.department,
        is_available=employee.is_available,
        on_leave_until=employee.on_leave_until,
        fallback_stakeholder_id=employee.fallback_stakeholder_id,
        created_at=employee.created_at.isoformat(),
        updated_at=employee.updated_at.isoformat()
    )

@router.get("/departments/list")
async def get_departments(db: Session = Depends(get_db)):
    """
    Get list of all departments
    """
    departments = db.query(Stakeholder.department).distinct().filter(
        Stakeholder.department.isnot(None)
    ).all()
    
    return {
        "departments": [dept[0] for dept in departments if dept[0]]
    }

@router.get("/roles/list")
async def get_roles(db: Session = Depends(get_db)):
    """
    Get list of all roles
    """
    roles = db.query(Stakeholder.role).distinct().all()
    
    return {
        "roles": [role[0] for role in roles if role[0]]
    }
