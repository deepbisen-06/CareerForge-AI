# CareerBridge AI — High-Level System Architecture

```text
                                CAREERBRIDGE AI
                                       |
                 +---------------------+---------------------+
                 |                                           |
              FRONTEND                                    BACKEND
                 |                                           |
          React + Vite                                  FastAPI (Python 3.12+)
          TypeScript + Tailwind CSS                     PostgreSQL + SQLite fallback
          shadcn/ui Design System                       Redis / In-memory queue
          Recharts Visualizations                       pgvector & ChromaDB Engine
                 |                                           |
                 +---------------------+---------------------+
                                       |
                                AI ORCHESTRATOR
                                       |
          +----------+---------+-------+---------+----------+
          |          |         |                 |          |
          v          v         v                 v          v
      Resume        RAG     Matching         Skill Gap   Interview
       Agent       Agent      Agent            Agent       Agent
          |          |         |                 |          |
          +----------+---------+-----------------+----------+
                               |
                         Customization
                             Agent
                               |
                    +----------+----------+
                    |                     |
              Career Assistant      Application Tracker
```

---

## 1. Modular Agent Design

### A. Resume Agent (`app/agents/resume_agent.py`)
- **Multi-Format Extraction**: Parses text and layout from PDF (via `pypdf`/`pdfplumber`), DOCX, and plain text.
- **Section Extraction**: Identifies Contact Details, Education, Experience, Technical Projects, Certifications, and Achievements.
- **ATS Scoring Engine**: Evaluates keyword density, quantified impact metrics, action verb strength, and completeness (0-100 score).

### B. RAG Agent (`app/rag/vector_store.py`)
- **Knowledge Base**: 220+ curated, realistic internship opportunities across 10 distinct career domains.
- **Enriched Document Chunking**: Combines role titles, company profile, required skills, preferred tools, and eligibility.
- **Multi-Stage Retrieval**: Sublinear TF-IDF + Cosine Vector Matrix + Metadata Filters (`domain`, `location`, `work_mode`) + Skill-weighted Re-ranking.

### C. Matching Agent (`app/agents/matching_agent.py`)
- **Deterministic 6-Factor Scoring**:
  - **Skills Match (30%)**: Jaccard and taxonomy overlap between candidate and job requirements.
  - **Experience Match (20%)**: Role, domain, and past internship relevance.
  - **Projects Match (15%)**: Alignment of tech stacks and domain problems in candidate projects.
  - **Education Match (15%)**: Degree level, field of study, and CGPA thresholds.
  - **Eligibility Match (10%)**: Graduation batch and work mode criteria.
  - **Preferences Match (10%)**: Domain, stipend, and location preferences.
- **Explainability**: Generates an auditable breakdown, "Why you match" items, and actionable recommendations.

### D. Skill Gap Agent (`app/agents/skill_gap_agent.py`)
- Categorizes skills into **Matched**, **Partial**, and **Missing**.
- Assigns priority tags: `HIGH` (critical core requirements), `MEDIUM` (proficiency upgrades), `LOW` (bonus tools).
- Produces estimated learning timelines (hours) and links to curated tutorials/docs.

### E. Document Customization Agent (`app/agents/customization_agent.py`)
- **Factual Tailored Resume**: Reorders projects, aligns technical keywords, and strengthens action phrasing without hallucinating experiences.
- **Role-Specific Cover Letter**: Generates tailored hook, matching accomplishments, and professional sign-off.

### F. Interview Preparation Agent (`app/agents/interview_agent.py`)
- **Question Bank**: Technical, behavioral, HR, and resume-specific questions.
- **5-Day Study Calendar**: Daily milestones and study time estimates.
- **Live AI Mock Interview**: Turn-by-turn answer scoring across Technical Accuracy (1-10), Clarity (1-10), Relevance (1-10), and Confidence (1-10), with cumulative Interview Readiness Score (0-100%).

### G. Conversational Career Assistant (`app/agents/career_assistant.py`)
- Multi-tool dispatch: `get_user_profile`, `get_resume_summary`, `search_internships`, `get_match_score`, `get_skill_gaps`, `get_applications`, `get_upcoming_deadlines`.

### H. Application Tracker (`app/api/applications.py`)
- Kanban stages: `SAVED`, `PLANNED`, `APPLIED`, `ASSESSMENT`, `INTERVIEW`, `OFFER`, `SELECTED`, `REJECTED`, `WITHDRAWN`.
- Deadline alerts: `Overdue`, `Urgent` (≤ 48h), `Approaching` (≤ 7d), `Normal`.
