from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class AgentRunCreate(BaseModel):
    goal: str = Field(..., min_length=3, description="High-level goal for the autonomous agent")

class AgentPlanStep(BaseModel):
    step: int
    tool: str
    description: str
    params: Dict[str, Any] = Field(default_factory=dict)
    status: str = Field(default="pending") # pending, running, completed, failed, skipped
    result_summary: Optional[str] = None

class AgentEventOut(BaseModel):
    id: int
    run_id: int
    event_type: str
    message: str
    tool_name: Optional[str] = None
    structured_data: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime

    class Config:
        from_attributes = True

class AgentRunOut(BaseModel):
    id: int
    user_id: int
    goal: str
    execution_plan: List[Dict[str, Any]] = Field(default_factory=list)
    status: str
    final_summary: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    completed_at: Optional[datetime] = None
    events: Optional[List[AgentEventOut]] = None

    class Config:
        from_attributes = True

class AgentApproveRequest(BaseModel):
    action: Optional[str] = "approve"
    notes: Optional[str] = None
