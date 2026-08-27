from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from app.database.session import get_db
from app.models.entities import User, Resume, ResumeVersion, Skill, UserSkill, Notification
from app.schemas.schemas import ResumeAnalysisOut, ResumeVersionOut, ResumeVersionCreate
from app.auth.deps import get_current_user
from app.agents.resume_agent import resume_agent

router = APIRouter(prefix="/resume", tags=["Resume Intelligence"])

@router.post("/upload", response_model=ResumeAnalysisOut)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    filename = file.filename or "resume.pdf"
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    # File size limit check (5MB)
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds 5MB limit")

    # Extract text & parse
    raw_text = resume_agent.extract_text(content, filename)
    if not raw_text or len(raw_text.strip()) < 20:
        raise HTTPException(
            status_code=400,
            detail="Unable to extract meaningful text from the uploaded file. Please ensure it is not an image-only scan."
        )

    parsed_data = resume_agent.parse_resume(raw_text)
    ats_score, strengths, weaknesses, missing_sections, recommendations = resume_agent.analyze_resume_intelligence(
        raw_text, parsed_data
    )

    # Save Resume record (Preserve original resume)
    resume_record = Resume(
        user_id=current_user.id,
        file_name=filename,
        raw_text=raw_text,
        parsed_data=parsed_data,
        resume_score=ats_score,
        strengths=strengths,
        weaknesses=weaknesses,
        missing_sections=missing_sections,
        recommendations=recommendations
    )
    db.add(resume_record)
    db.flush()

    # Automatically create Base Resume Version v1
    v1 = ResumeVersion(
        user_id=current_user.id,
        original_resume_id=resume_record.id,
        version_number=1,
        title=f"Base Upload ({filename})",
        document_type="OPTIMIZED_BASE",
        content_markdown=raw_text,
        metadata_json={"ats_score": ats_score, "source": "direct_upload"}
    )
    db.add(v1)

    # Auto-sync detected skills into UserSkill if not already present
    for s_name in parsed_data.get("skills", []):
        existing_skill = db.query(Skill).filter(Skill.name == s_name).first()
        if not existing_skill:
            existing_skill = Skill(name=s_name, category="General")
            db.add(existing_skill)
            db.flush()

        has_user_skill = db.query(UserSkill).filter(
            UserSkill.user_id == current_user.id,
            UserSkill.skill_id == existing_skill.id
        ).first()

        if not has_user_skill:
            db.add(UserSkill(
                user_id=current_user.id,
                skill_id=existing_skill.id,
                proficiency="Intermediate",
                source="resume"
            ))

    # Notification
    db.add(Notification(
        user_id=current_user.id,
        type="MATCH",
        title="Resume Analyzed Successfully",
        message=f"Your resume {filename} scored {ats_score}/100 ATS compatibility. {len(parsed_data.get('skills', []))} skills extracted."
    ))

    db.commit()
    db.refresh(resume_record)

    versions = db.query(ResumeVersion).filter(ResumeVersion.original_resume_id == resume_record.id).all()

    return ResumeAnalysisOut(
        id=resume_record.id,
        file_name=resume_record.file_name,
        resume_score=resume_record.resume_score,
        ats_score=resume_record.resume_score,
        parsed_data=resume_record.parsed_data,
        strengths=resume_record.strengths or [],
        weaknesses=resume_record.weaknesses or [],
        missing_sections=missing_sections,
        recommendations=resume_record.recommendations or [],
        versions=versions,
        created_at=resume_record.created_at
    )

@router.get("/latest", response_model=ResumeAnalysisOut)
def get_latest_resume(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    resume = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.created_at.desc()).first()
    if not resume:
        raise HTTPException(status_code=404, detail="No resume uploaded yet")

    _, strengths, weaknesses, missing_sections, recommendations = resume_agent.analyze_resume_intelligence(
        resume.raw_text, resume.parsed_data or {}
    )

    versions = db.query(ResumeVersion).filter(ResumeVersion.user_id == current_user.id).order_by(ResumeVersion.created_at.desc()).all()

    return ResumeAnalysisOut(
        id=resume.id,
        file_name=resume.file_name,
        resume_score=resume.resume_score,
        ats_score=resume.resume_score,
        parsed_data=resume.parsed_data or {},
        strengths=resume.strengths or strengths,
        weaknesses=resume.weaknesses or weaknesses,
        missing_sections=resume.missing_sections or missing_sections,
        recommendations=resume.recommendations or recommendations,
        versions=versions,
        created_at=resume.created_at
    )

@router.get("/versions", response_model=List[ResumeVersionOut])
def get_resume_versions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(ResumeVersion).filter(ResumeVersion.user_id == current_user.id).order_by(ResumeVersion.created_at.desc()).all()

@router.post("/versions", response_model=ResumeVersionOut)
def save_resume_version(
    payload: ResumeVersionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    latest_resume = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.created_at.desc()).first()
    count = db.query(ResumeVersion).filter(ResumeVersion.user_id == current_user.id).count()

    new_v = ResumeVersion(
        user_id=current_user.id,
        original_resume_id=latest_resume.id if latest_resume else None,
        target_internship_id=payload.target_internship_id,
        version_number=count + 1,
        title=payload.title,
        document_type=payload.document_type,
        content_markdown=payload.content_markdown,
        metadata_json=payload.metadata_json or {}
    )
    db.add(new_v)
    db.commit()
    db.refresh(new_v)
    return new_v

@router.delete("/versions/{version_id}")
def delete_resume_version(
    version_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    v = db.query(ResumeVersion).filter(ResumeVersion.id == version_id, ResumeVersion.user_id == current_user.id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Version not found")
    db.delete(v)
    db.commit()
    return {"status": "deleted", "message": f"Resume version #{version_id} deleted"}
