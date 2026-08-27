# CareerBridge AI — API Reference

Base URL: `/api/v1`

---

## 1. Authentication (`/auth`)

### `POST /auth/register`
- **Body**: `{ "email": "string", "password": "string", "full_name": "string" }`
- **Response**: `{ "access_token": "string", "token_type": "bearer", "user_id": 1, "email": "string", "full_name": "string" }`

### `POST /auth/login`
- **Body**: `{ "email": "string", "password": "string" }`
- **Response**: `{ "access_token": "string", "token_type": "bearer", "user_id": 1, "email": "string", "full_name": "string" }`

### `GET /auth/me`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: User object.

---

## 2. Student Profile (`/profile`)

### `GET /profile/me`
- Returns full student profile, skills, education, projects, experiences, and `completion_percentage`.

### `PUT /profile/update`
- Updates profile details, skills inventory, projects, and career preferences.

---

## 3. Resume Intelligence (`/resume`)

### `POST /resume/upload`
- **Form Data**: `file: <binary PDF/DOCX/TXT>`
- **Response**: ATS Score (0-100), parsed sections, strengths, weaknesses, missing sections, and recommendations.

### `GET /resume/latest`
- Fetches latest resume ATS score and intelligence audit.

---

## 4. Internships & RAG Search (`/internships`)

### `GET /internships/`
- **Query Params**:
  - `q`: Semantic search query (e.g. `machine learning engineer`)
  - `domain`: Domain filter (e.g. `AI/ML`)
  - `location`: Location filter
  - `work_mode`: `Remote` | `Hybrid` | `Onsite`
  - `limit`: Default 50
- **Response**: Ranked list of internship objects with real-time candidate `match_score`.

### `GET /internships/{id}`
- Returns detailed internship metadata and candidate compatibility.

---

## 5. Job Matching & Explainability (`/matching`)

### `GET /matching/{internship_id}`
- Returns 360-degree explainable breakdown:
  - `overall_score`: 0-100%
  - `score_breakdown`: Skills (30%), Experience (20%), Projects (15%), Education (15%), Eligibility (10%), Preferences (10%)
  - `matched_skills`, `missing_skills`, `strengths`, `recommendation`, `reasoning`.

---

## 6. Skill Gap Analysis (`/skill-gaps`)

### `GET /skill-gaps/{internship_id}`
- Returns categorized skill gaps with `priority` (`HIGH`, `MEDIUM`, `LOW`), estimated hours, and curated tutorial links.

---

## 7. Document Customization (`/documents`)

### `POST /documents/generate`
- **Body**: `{ "internship_id": 1, "document_type": "TAILORED_RESUME" | "COVER_LETTER", "additional_notes": "string" }`
- **Response**: Generated document object with formatted Markdown content.

---

## 8. Interview Preparation (`/interview`)

### `POST /interview/generate-questions`
- **Body**: `{ "internship_id": 1, "count": 8 }`
- **Response**: Generated `InterviewSession` with technical, behavioral, HR, and resume-based questions.

### `GET /interview/prep-plan/{internship_id}`
- Returns 5-day structured study calendar.

### `POST /interview/submit-answer`
- **Body**: `{ "question_id": 1, "user_answer": "string" }`
- **Response**: Graded question with score (0-10) and criteria (Accuracy, Clarity, Relevance, Confidence).

---

## 9. Application Tracker (`/applications`)

### `GET /applications/`
- Returns all tracked applications with deadline status (`Overdue`, `Urgent`, `Approaching`, `Normal`).

### `POST /applications/`
- **Body**: `{ "internship_id": 1, "status": "SAVED" | "APPLIED" | ... }`

### `PUT /applications/{id}`
- Updates status, notes, or deadlines.

---

## 10. Conversational Career Assistant (`/chat`)

### `POST /chat/message`
- **Body**: `{ "message": "string", "session_id": 1 }`
- **Response**: Assistant reply with array of executed internal tool calls.

---

## 11. Dashboard Overview (`/dashboard`)

### `GET /dashboard/overview`
- Consolidates profile completion, ATS score, top matches, skill gaps, deadlines, and interview readiness.
