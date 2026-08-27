from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.entities import User, Profile, Notification
from app.schemas.schemas import UserRegister, UserLogin, Token, UserOut
from app.auth.security import get_password_hash, verify_password, create_access_token
from app.auth.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists"
        )
    
    hashed_pwd = get_password_hash(user_in.password)
    user = User(email=user_in.email, password_hash=hashed_pwd)
    db.add(user)
    db.flush()

    # Create associated profile
    profile = Profile(
        user_id=user.id,
        full_name=user_in.full_name or "Student",
        preferred_domains=["AI/ML", "Software Development"],
        preferred_locations=["Bangalore, India", "Remote"],
        preferred_work_mode="Any"
    )
    db.add(profile)

    # Welcome notification
    db.add(Notification(
        user_id=user.id,
        type="SYSTEM",
        title="Welcome to CareerBridge AI!",
        message="Complete your student profile or upload your resume to unlock AI matching."
    ))

    db.commit()

    token = create_access_token(subject=user.id)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email,
        "full_name": profile.full_name
    }

@router.post("/login", response_model=Token)
def login(login_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_in.email).first()
    if not user or not verify_password(login_in.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = create_access_token(subject=user.id)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email,
        "full_name": user.profile.full_name if user.profile else "Student"
    }

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/logout")
def logout():
    return {"message": "Logged out successfully"}
