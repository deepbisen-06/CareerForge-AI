from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone

from app.database.session import get_db
from app.models.entities import User, AgentRun, AgentEvent
from app.schemas.agent import AgentRunCreate, AgentRunOut, AgentEventOut, AgentApproveRequest
from app.auth.deps import get_current_user
from app.agents.orchestrator import orchestrator

router = APIRouter(prefix="/agent", tags=["CareerForge Autonomous Agent"])

@router.post("/runs", response_model=AgentRunOut)
def create_and_execute_agent_run(
    payload: AgentRunCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Spawns and executes an autonomous CareerForge AI agent run for the given user goal.
    Executes multi-step planning, tool selection, evaluation, and persists events.
    """
    agent_run = AgentRun(
        user_id=current_user.id,
        goal=payload.goal.strip(),
        status="PENDING",
        created_at=datetime.now(timezone.utc)
    )
    db.add(agent_run)
    db.commit()
    db.refresh(agent_run)

    # Execute orchestrator loop
    try:
        completed_run = orchestrator.execute_run(run_id=agent_run.id, db=db)
        return completed_run
    except Exception as e:
        agent_run.status = "FAILED"
        agent_run.final_summary = {"error": str(e)}
        db.commit()
        db.refresh(agent_run)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent execution encountered an unhandled error: {str(e)}"
        )


@router.get("/runs", response_model=List[AgentRunOut])
def list_agent_runs(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lists historical agent runs for the authenticated user.
    """
    runs = db.query(AgentRun).filter(
        AgentRun.user_id == current_user.id
    ).order_by(AgentRun.created_at.desc()).limit(limit).all()
    return runs


@router.get("/runs/{run_id}", response_model=AgentRunOut)
def get_agent_run(
    run_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves details and status of a specific agent run.
    """
    run = db.query(AgentRun).filter(
        AgentRun.id == run_id,
        AgentRun.user_id == current_user.id
    ).first()
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent run not found")
    return run


@router.get("/runs/{run_id}/events", response_model=List[AgentEventOut])
def get_agent_run_events(
    run_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns real-time execution events for an agent run.
    """
    run = db.query(AgentRun).filter(
        AgentRun.id == run_id,
        AgentRun.user_id == current_user.id
    ).first()
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent run not found")

    events = db.query(AgentEvent).filter(
        AgentEvent.run_id == run_id
    ).order_by(AgentEvent.created_at.asc()).all()
    return events


@router.post("/runs/{run_id}/approve", response_model=AgentRunOut)
def approve_agent_run(
    run_id: int,
    payload: AgentApproveRequest = AgentApproveRequest(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Human-in-the-Loop approval gate: approves drafted materials and moves status to COMPLETED.
    """
    try:
        updated_run = orchestrator.approve_run(
            run_id=run_id,
            user_id=current_user.id,
            db=db,
            notes=payload.notes
        )
        return updated_run
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/runs/{run_id}/cancel", response_model=AgentRunOut)
def cancel_agent_run(
    run_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancels an active or pending agent run.
    """
    try:
        updated_run = orchestrator.cancel_run(
            run_id=run_id,
            user_id=current_user.id,
            db=db
        )
        return updated_run
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
