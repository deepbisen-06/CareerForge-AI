import json
import os
import sys
from datetime import datetime, timezone

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.session import engine, Base, SessionLocal
from app.models.entities import (
    User, Profile, Skill, UserSkill, Education, Experience, Project,
    Internship, InternshipSkill, Application, SavedJob, SkillGap, GeneratedDocument,
    InterviewSession, InterviewQuestion, ChatSession, ChatMessage, Notification
)
from app.auth.security import get_password_hash
from app.rag.vector_store import rag_store
from seed_generator import generate_internships

TAXONOMY_SKILLS = [
    # Programming
    ("Python", "Programming"), ("JavaScript", "Programming"), ("TypeScript", "Programming"),
    ("Java", "Programming"), ("C++", "Programming"), ("C", "Programming"), ("Go", "Programming"),
    ("Rust", "Programming"), ("Kotlin", "Programming"), ("Swift", "Programming"), ("Dart", "Programming"),
    ("SQL", "Programming"), ("Bash Scripting", "Programming"),
    # AI/ML & Data
    ("Machine Learning", "AI/ML"), ("Deep Learning", "AI/ML"), ("PyTorch", "AI/ML"),
    ("TensorFlow", "AI/ML"), ("NLP", "AI/ML"), ("Computer Vision", "AI/ML"), ("LLMs", "AI/ML"),
    ("RAG", "AI/ML"), ("LangChain", "AI/ML"), ("Transformers", "AI/ML"), ("Scikit-Learn", "AI/ML"),
    ("OpenCV", "AI/ML"), ("Pandas", "Data Science"), ("NumPy", "Data Science"), ("Spark", "Data Science"),
    ("Airflow", "Data Science"), ("Tableau", "Data Science"), ("PowerBI", "Data Science"), ("Snowflake", "Data Science"),
    # Web & Fullstack
    ("React", "Web"), ("Next.js", "Web"), ("Vue.js", "Web"), ("HTML5", "Web"), ("CSS3", "Web"),
    ("Tailwind CSS", "Web"), ("FastAPI", "Web"), ("Flask", "Web"), ("Django", "Web"),
    ("Node.js", "Web"), ("Express", "Web"), ("Spring Boot", "Web"), ("GraphQL", "Web"),
    ("REST APIs", "Web"), ("PostgreSQL", "Database"), ("MySQL", "Database"), ("MongoDB", "Database"),
    ("Redis", "Database"),
    # Cloud & DevOps
    ("Docker", "Cloud/DevOps"), ("Kubernetes", "Cloud/DevOps"), ("AWS", "Cloud/DevOps"),
    ("GCP", "Cloud/DevOps"), ("Azure", "Cloud/DevOps"), ("Terraform", "Cloud/DevOps"),
    ("CI/CD", "Cloud/DevOps"), ("GitHub Actions", "Cloud/DevOps"), ("Linux", "Cloud/DevOps"),
    ("Microservices", "Architecture"), ("System Design", "Architecture"), ("Data Structures", "Computer Science"),
    ("Algorithms", "Computer Science"),
    # Cybersecurity
    ("Network Security", "Cybersecurity"), ("Penetration Testing", "Cybersecurity"),
    ("OWASP Top 10", "Cybersecurity"), ("Cryptography", "Cybersecurity"), ("Threat Intelligence", "Cybersecurity"),
    ("Burp Suite", "Cybersecurity"), ("SIEM", "Cybersecurity"), ("SOC Operations", "Cybersecurity"),
    # Mobile & IoT
    ("Flutter", "Mobile"), ("React Native", "Mobile"), ("Android", "Mobile"), ("iOS", "Mobile"),
    ("Jetpack Compose", "Mobile"), ("SwiftUI", "Mobile"), ("Embedded C", "Robotics/IoT"),
    ("ROS2", "Robotics/IoT"), ("RTOS", "Robotics/IoT"), ("Microcontrollers", "Robotics/IoT"),
    ("Robotics Kinematics", "Robotics/IoT"), ("SLAM", "Robotics/IoT"),
    # Product
    ("Product Roadmapping", "Product"), ("User Research", "Product"), ("Agile/Scrum", "Product"),
    ("Product Analytics", "Product"), ("Wireframing", "Product")
]

def seed_database():
    print("Creating all database tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Seed Skills Taxonomy
        print("Seeding canonical skills taxonomy...")
        skill_map = {}
        skills_to_add = []
        for name, cat in TAXONOMY_SKILLS:
            existing = db.query(Skill).filter(Skill.name == name).first()
            if not existing:
                skill_obj = Skill(name=name, category=cat)
                skills_to_add.append(skill_obj)
            else:
                skill_map[name] = existing.id

        if skills_to_add:
            db.add_all(skills_to_add)
            db.commit()
            for s in db.query(Skill).all():
                skill_map[s.name] = s.id

        # 2. Seed 1,000+ Internships (Batch Insert)
        data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "internships", "internships_1000.json")
        if not os.path.exists(data_file):
            print("Generating 1,000 realistic internships dataset...")
            dataset = generate_internships(1000)
            os.makedirs(os.path.dirname(data_file), exist_ok=True)
            with open(data_file, "w", encoding="utf-8") as f:
                json.dump(dataset, f, indent=2)
        else:
            with open(data_file, "r", encoding="utf-8") as f:
                dataset = json.load(f)

        existing_count = db.query(Internship).count()
        if existing_count < len(dataset):
            print(f"Seeding {len(dataset)} internships in batch...")
            internship_objs = []
            for item in dataset:
                existing = db.query(Internship.id).filter(
                    Internship.company == item["company"],
                    Internship.title == item["title"],
                    Internship.location == item["location"]
                ).first()
                if not existing:
                    internship_objs.append(Internship(
                        company=item["company"],
                        title=item["title"],
                        domain=item["domain"],
                        description=item["description"],
                        requirements=item["requirements"],
                        preferred_skills=item["preferred_skills"],
                        location=item["location"],
                        work_mode=item["work_mode"],
                        stipend=item["stipend"],
                        duration=item["duration"],
                        eligibility=item["eligibility"],
                        deadline=item["deadline"],
                        application_url=item["application_url"],
                        source=item.get("source", "Curated Dataset"),
                        source_type=item.get("source_type", "CURATED"),
                        source_job_id=item.get("source_job_id"),
                        company_logo_url=item.get("company_logo_url"),
                        is_active=item.get("is_active", True),
                        is_demo=item.get("is_demo", False),
                        posted_at=datetime.now(timezone.utc),
                        last_verified_at=datetime.now(timezone.utc)
                    ))
            
            if internship_objs:
                db.add_all(internship_objs)
                db.commit()
                print(f"Inserted {len(internship_objs)} new internships.")

        # Index in Hybrid RAG Vector Store
        all_internships = db.query(Internship).all()
        rag_records = [{
            "id": it.id, "company": it.company, "title": it.title, "domain": it.domain,
            "description": it.description, "requirements": it.requirements or [],
            "preferred_skills": it.preferred_skills or [], "location": it.location,
            "work_mode": it.work_mode, "stipend": it.stipend, "duration": it.duration,
            "eligibility": it.eligibility, "deadline": it.deadline,
            "application_url": it.application_url, "source": it.source,
            "source_type": it.source_type, "company_logo_url": it.company_logo_url,
            "is_active": it.is_active, "is_demo": it.is_demo
        } for it in all_internships]

        print(f"Indexing {len(rag_records)} opportunities into Hybrid RAG engine...")
        rag_store.index_internships(rag_records)

        # 3. Seed System Admin User (admin@careerbridge.ai / Admin@123)
        admin_email = "admin@careerbridge.ai"
        admin_user = db.query(User).filter(User.email == admin_email).first()
        if not admin_user:
            print("Creating System Admin account (admin@careerbridge.ai / Admin@123)...")
            admin_user = User(
                email=admin_email,
                password_hash=get_password_hash("Admin@123"),
                role="admin",
                is_active=True
            )
            db.add(admin_user)
            db.commit()

            admin_profile = Profile(
                user_id=admin_user.id,
                full_name="CareerBridge Administrator",
                phone="+91 99999 00000",
                location="Admin HQ",
                career_objective="System Platform Administrator for CareerBridge AI.",
                preferred_domains=["AI/ML", "Software Development"],
                preferred_locations=["Remote"],
                preferred_work_mode="Remote"
            )
            db.add(admin_profile)
            db.commit()

        # 4. Seed Demo Student User (demo@careerbridge.ai / Demo@123)
        demo_email = "demo@careerbridge.ai"
        demo_user = db.query(User).filter(User.email == demo_email).first()
        if not demo_user:
            print("Creating Demo Student account (demo@careerbridge.ai / Demo@123)...")
            demo_user = User(
                email=demo_email,
                password_hash=get_password_hash("Demo@123"),
                role="student",
                is_active=True
            )
            db.add(demo_user)
            db.commit()

            profile = Profile(
                user_id=demo_user.id,
                full_name="Aarav Sharma",
                phone="+91 98765 43210",
                location="Bangalore, India",
                career_objective="Aspiring AI Engineer and Full-Stack Developer passionate about building robust LLM agents, scalable microservices, and high-impact machine learning systems.",
                preferred_domains=["AI/ML", "Software Development", "Fullstack Development"],
                preferred_locations=["Bangalore, India", "Remote", "Hyderabad, India"],
                preferred_work_mode="Any",
                preferred_stipend="₹40,000+/month",
                preferred_duration="3-6 months"
            )
            db.add(profile)

            # Education
            db.add(Education(
                user_id=demo_user.id,
                degree="B.Tech in Computer Science and Engineering",
                institution="National Institute of Technology (NIT)",
                field="Computer Science & AI",
                start_year=2022,
                end_year=2026,
                cgpa_or_percentage="8.85 / 10.0"
            ))

            # Experience
            db.add(Experience(
                user_id=demo_user.id,
                company="TechCorp Innovations",
                role="Software Engineering Intern",
                description="Engineered RESTful microservices with FastAPI and PostgreSQL. Reduced API latency by 35% using Redis caching and optimized database query indexing.",
                start_date="May 2025",
                end_date="July 2025"
            ))

            # Projects
            db.add(Project(
                user_id=demo_user.id,
                title="Autonomous Multi-Agent Research Assistant",
                description="Built a distributed multi-agent RAG system utilizing LangChain, ChromaDB, and FastAPI to parse and summarize arXiv research papers in real time.",
                technologies=["Python", "FastAPI", "RAG", "LangChain", "PyTorch", "Docker"],
                project_url="https://github.com/aarav-sharma/multi-agent-rag"
            ))
            db.add(Project(
                user_id=demo_user.id,
                title="Distributed Task Orchestration Engine",
                description="Architected a resilient task queue with Go, Docker, and Redis, processing 10,000+ jobs/min with automated retry mechanisms and real-time dashboard.",
                technologies=["Go", "Docker", "Redis", "React", "PostgreSQL"],
                project_url="https://github.com/aarav-sharma/task-orchestrator"
            ))

            # User Skills
            user_demo_skills = [
                ("Python", "Advanced"), ("FastAPI", "Advanced"), ("Machine Learning", "Advanced"),
                ("PyTorch", "Intermediate"), ("React", "Intermediate"), ("PostgreSQL", "Advanced"),
                ("Docker", "Intermediate"), ("Data Structures", "Advanced"), ("Algorithms", "Advanced"),
                ("Git", "Advanced"), ("RAG", "Intermediate")
            ]
            for s_name, prof in user_demo_skills:
                s_id = skill_map.get(s_name)
                if s_id:
                    db.add(UserSkill(user_id=demo_user.id, skill_id=s_id, proficiency=prof, source="profile"))

            db.commit()

            # Seed Sample Application & Saved Job
            first_internship = db.query(Internship).filter(Internship.domain == "AI/ML").first()
            if first_internship:
                db.add(Application(
                    user_id=demo_user.id,
                    internship_id=first_internship.id,
                    status="APPLIED",
                    deadline=first_internship.deadline,
                    notes="Submitted custom tailored resume and cover letter. Technical screening scheduled.",
                    match_score=92.0
                ))
                db.add(SavedJob(user_id=demo_user.id, internship_id=first_internship.id))
                db.commit()

            # Seed Welcome Notification
            db.add(Notification(
                user_id=demo_user.id,
                type="SYSTEM",
                title="Welcome to CareerBridge AI!",
                message="Your profile is initialized. Upload your resume or explore 1,000+ verified internship opportunities.",
                read=False
            ))
            db.commit()

        print("Seeding completed successfully!")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
