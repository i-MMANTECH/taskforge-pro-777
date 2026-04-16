from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List

class UserSchema(BaseModel):
    id: int
    username: str

class TeamSchema(BaseModel):
    id: int
    name: str
    description: Optional[str]

class ProjectIn(BaseModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    team_id: Optional[int] = None

class ProjectOut(BaseModel):  # For response
    id: int
    name: str
    description: Optional[str]
    start_date: date
    end_date: Optional[date]
    owner: UserSchema
    team: Optional[TeamSchema]

class TaskIn(BaseModel):
    title: str = Field(..., min_length=1)
    description: Optional[str] = None
    status: str = Field(default='TODO', pattern='^(TODO|IN_PROGRESS|DONE)$')
    priority: int = Field(default=1, ge=1, le=3)
    due_date: Optional[date] = None
    project_id: int
    assigned_to_id: Optional[int] = None

class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    priority: int
    due_date: Optional[date]
    project: ProjectOut
    assigned_to: Optional[UserSchema]