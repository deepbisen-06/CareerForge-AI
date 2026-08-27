from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.entities import User, Profile, Skill, UserSkill, Education, Experience, Project
from app.schemas.schemas import ProfileOut, ProfileUpdate, EducationSchema, ExperienceSchema, ProjectSchema
from app.auth.deps import get_current_user

router = APIRouter(prefix="/profile", tags=["Student Profile"])

def calculate_completion(user: User) -> int:
    score = 20 # baseline registration
    if user.profile:
        if user.profile.full_name and user.profile.phone and user.profile.location:
            score += 15
        if user.profile.preferred_domains and len(user.profile.preferred_domains) > 0:
            score += 15
    if user.educations and len(user.educations) > 0:
        score += 15
    if user.user_skills and len(user.user_skills) >= 3:
        score += 15
    if user.projects and len(user.projects) > 0:
        score += 10
    if user.experiences and len(user.experiences) > 0:
        score += 10
    return min(100, score)

@router.get("/me", response_model=ProfileOut)
def get_my_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = current_user.profile
    if not profile:
        profile = Profile(user_id=current_user.id, full_name="Student")
        db.add(profile)
        db.commit()
        db.refresh(profile)

    skills_data = [{"name": us.skill.name, "proficiency": us.proficiency, "category": us.skill.category} for us in current_user.user_skills]
    educations_data = [EducationSchema(
        id=e.id, degree=e.degree, institution=e.institution, field=e.field,
        start_year=e.start_year, end_year=e.end_year, cgpa_or_percentage=e.cgpa_or_percentage
    ) for e in current_user.educations]
    
    experiences_data = [ExperienceSchema(
        id=e.id, company=e.company, role=e.role, description=e.description,
        start_date=e.start_date, end_date=e.end_date
    ) for e in current_user.experiences]
    
    projects_data = [ProjectSchema(
        id=p.id, title=p.title, description=p.description,
        technologies=p.technologies or [], project_url=p.project_url
    ) for p in current_user.projects]

    completion = calculate_completion(current_user)

    return ProfileOut(
        id=profile.id,
        user_id=current_user.id,
        full_name=profile.full_name,
        phone=profile.phone,
        location=profile.location,
        career_objective=profile.career_objective,
        preferred_domains=profile.preferred_domains or [],
        preferred_locations=profile.preferred_locations or [],
        preferred_work_mode=profile.preferred_work_mode or "Any",
        preferred_stipend=profile.preferred_stipend or "Any",
        preferred_duration=profile.preferred_duration or "Any",
        skills=skills_data,
        educations=educations_data,
        experiences=experiences_data,
        projects=projects_data,
        completion_percentage=completion
    )

@router.put("/update", response_model=ProfileOut)
def update_profile(
    profile_in: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = current_user.profile
    if not profile:
        profile = Profile(user_id=current_user.id)
        db.add(profile)
        db.flush()

    if profile_in.full_name is not None:
        profile.full_name = profile_in.full_name
    if profile_in.phone is not None:
        profile.phone = profile_in.phone
    if profile_in.location is not None:
        profile.location = profile_in.location
    if profile_in.career_objective is not None:
        profile.career_objective = profile_in.career_objective
    if profile_in.preferred_domains is not None:
        profile.preferred_domains = profile_in.preferred_domains
    if profile_in.preferred_locations is not None:
        profile.preferred_locations = profile_in.preferred_locations
    if profile_in.preferred_work_mode is not None:
        profile.preferred_work_mode = profile_in.preferred_work_mode
    if profile_in.preferred_stipend is not None:
        profile.preferred_stipend = profile_in.preferred_stipend
    if profile_in.preferred_duration is not None:
        profile.preferred_duration = profile_in.preferred_duration

    # Update Skills
    if profile_in.skills is not None:
        db.query(UserSkill).filter(UserSkill.user_id == current_user.id).delete()
        for sk in profile_in.skills:
            s_name = sk.get("name") if isinstance(sk, dict) else sk
            prof = sk.get("proficiency", "Intermediate") if isinstance(sk, dict) else "Intermediate"
            if s_name:
                skill_obj = db.query(Skill).filter(Skill.name == s_name).first()
                if not skill_obj:
                    skill_obj = Skill(name=s_name, category="General")
                    db.add(skill_obj)
                    db.flush()
                db.add(UserSkill(user_id=current_user.id, skill_id=skill_obj.id, proficiency=prof, source="profile"))

    # Update Educations
    if profile_in.educations is not None:
        db.query(Education).filter(Education.user_id == current_user.id).delete()
        for edu in profile_in.educations:
            db.add(Education(
                user_id=current_user.id,
                degree=edu.degree,
                institution=edu.institution,
                field=edu.field,
                start_year=edu.start_year,
                end_year=edu.end_year,
                cgpa_or_percentage=edu.cgpa_or_percentage
            ))

    # Update Experiences
    if profile_in.experiences is not None:
        db.query(Experience).filter(Experience.user_id == current_user.id).delete()
        for exp in profile_in.experiences:
            db.add(Experience(
                user_id=current_user.id,
                company=exp.company,
                role=exp.role,
                description=exp.description,
                start_date=exp.start_date,
                end_date=exp.end_date
            ))

    # Update Projects
    if profile_in.projects is not None:
        db.query(Project).filter(Project.user_id == current_user.id).delete()
        for proj in profile_in.projects:
            db.add(Project(
                user_id=current_user.id,
                title=proj.title,
                description=proj.description,
                technologies=proj.technologies or [],
                project_url=proj.project_url
            ))

    db.commit()
    db.refresh(current_user)
    return get_my_profile(current_user=current_user, db=db)
