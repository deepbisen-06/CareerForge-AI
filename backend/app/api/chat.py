from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.models.entities import User, ChatSession, ChatMessage
from app.schemas.schemas import ChatMessageIn, ChatMessageOut, ChatSessionOut
from app.auth.deps import get_current_user
from app.agents.career_assistant import career_assistant_agent

router = APIRouter(prefix="/chat", tags=["Conversational Career Assistant"])

@router.post("/message", response_model=ChatMessageOut)
def send_chat_message(
    chat_in: ChatMessageIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = None
    if chat_in.session_id:
        session = db.query(ChatSession).filter(ChatSession.id == chat_in.session_id, ChatSession.user_id == current_user.id).first()

    if not session:
        # Create new chat session
        first_few_words = " ".join(chat_in.message.split()[:5])
        session = ChatSession(
            user_id=current_user.id,
            title=f"Chat: {first_few_words}..."
        )
        db.add(session)
        db.flush()

    # Save User message
    user_msg = ChatMessage(
        session_id=session.id,
        role="user",
        content=chat_in.message
    )
    db.add(user_msg)
    db.flush()

    # Get conversation history
    past_messages = db.query(ChatMessage).filter(ChatMessage.session_id == session.id).order_by(ChatMessage.created_at.asc()).all()
    history_tuples = [{"role": m.role, "content": m.content} for m in past_messages]

    # Process via CareerAssistantAgent
    assistant_output = career_assistant_agent.process_message(
        db=db,
        user_id=current_user.id,
        user_message=chat_in.message,
        conversation_history=history_tuples
    )

    # Save Assistant message
    assistant_msg = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=assistant_output["response"],
        tool_calls=assistant_output.get("tool_calls", [])
    )
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)

    return ChatMessageOut(
        id=assistant_msg.id,
        role=assistant_msg.role,
        content=assistant_msg.content,
        tool_calls=assistant_msg.tool_calls or [],
        created_at=assistant_msg.created_at
    )

@router.get("/sessions", response_model=List[ChatSessionOut])
def get_user_chat_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sessions = db.query(ChatSession).filter(ChatSession.user_id == current_user.id).order_by(ChatSession.updated_at.desc()).all()
    return sessions

@router.get("/session/{id}", response_model=ChatSessionOut)
def get_chat_session(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = db.query(ChatSession).filter(ChatSession.id == id, ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return session
