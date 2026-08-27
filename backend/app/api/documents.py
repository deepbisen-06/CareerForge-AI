from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.models.entities import User, Internship, Resume, GeneratedDocument
from app.schemas.schemas import GenerateDocumentRequest, GeneratedDocumentOut
from app.auth.deps import get_current_user
from app.agents.customization_agent import customization_agent

router = APIRouter(prefix="/documents", tags=["Document Customization"])

@router.post("/generate", response_model=GeneratedDocumentOut)
def generate_document(
    req: GenerateDocumentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    internship = db.query(Internship).filter(Internship.id == req.internship_id).first()
    if not internship:
        raise HTTPException(status_code=404, detail="Internship not found")

    user_skills = [{"name": us.skill.name, "proficiency": us.proficiency} for us in current_user.user_skills]
    prof_dict = {
        "full_name": current_user.profile.full_name if current_user.profile else "Aarav Sharma",
        "phone": current_user.profile.phone if current_user.profile else "+91 98765 43210",
        "location": current_user.profile.location if current_user.profile else "Bangalore, India",
        "email": current_user.email,
        "career_objective": current_user.profile.career_objective if current_user.profile else "",
        "skills": user_skills,
        "experiences": [{"company": e.company, "role": e.role, "description": e.description, "start_date": e.start_date, "end_date": e.end_date} for e in current_user.experiences],
        "projects": [{"title": p.title, "description": p.description, "technologies": p.technologies, "project_url": p.project_url} for p in current_user.projects],
        "educations": [{"degree": ed.degree, "institution": ed.institution, "field": ed.field, "start_year": ed.start_year, "end_year": ed.end_year, "cgpa_or_percentage": ed.cgpa_or_percentage} for ed in current_user.educations]
    }
    
    internship_dict = {
        "id": internship.id,
        "company": internship.company,
        "title": internship.title,
        "requirements": internship.requirements or [],
        "preferred_skills": internship.preferred_skills or [],
        "deadline": internship.deadline
    }

    latest_resume = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.created_at.desc()).first()
    raw_resume_text = latest_resume.raw_text if latest_resume else ""

    doc_type = req.document_type.upper()
    if doc_type == "COVER_LETTER":
        doc_res = customization_agent.generate_cover_letter(
            prof_dict, internship_dict, tone=req.tone or "Professional", additional_notes=req.additional_notes
        )
    else:
        doc_res = customization_agent.generate_tailored_resume(prof_dict, raw_resume_text, internship_dict)

    # Save to database
    doc_record = GeneratedDocument(
        user_id=current_user.id,
        internship_id=internship.id,
        document_type=doc_res["document_type"],
        title=doc_res["title"],
        content=doc_res["content"],
        metadata_json=doc_res.get("metadata", {})
    )
    db.add(doc_record)
    db.commit()
    db.refresh(doc_record)

    return GeneratedDocumentOut(
        id=doc_record.id,
        internship_id=doc_record.internship_id,
        document_type=doc_record.document_type,
        title=doc_record.title,
        content=doc_record.content,
        metadata=doc_record.metadata_json or {},
        created_at=doc_record.created_at
    )

@router.get("/list", response_model=List[GeneratedDocumentOut])
def list_user_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    docs = db.query(GeneratedDocument).filter(GeneratedDocument.user_id == current_user.id).order_by(GeneratedDocument.created_at.desc()).all()
    return [
        GeneratedDocumentOut(
            id=d.id,
            internship_id=d.internship_id,
            document_type=d.document_type,
            title=d.title,
            content=d.content,
            metadata=d.metadata_json or {},
            created_at=d.created_at
        )
        for d in docs
    ]
