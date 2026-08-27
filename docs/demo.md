# CareerBridge AI — Complete End-to-End Demo Script

Follow this script to demonstrate all 9 core agentic modules:

---

## Step 1: Instant 1-Click Login
1. Open the frontend (`http://localhost:5173`).
2. Click **"1-Click Instant Demo Login"**.
3. You are authenticated as **Aarav Sharma** (`demo@careerbridge.ai`).

---

## Step 2: Review Student Profile Wizard
1. Navigate to **Profile Wizard** (`/profile-wizard`).
2. Walk through the 6 steps:
   - Personal details, Education (NIT CS & AI, 8.8 CGPA)
   - Skills Inventory (Python, FastAPI, Machine Learning, PyTorch, React, PostgreSQL)
   - Projects (Multi-Agent RAG Assistant, Task Orchestration Engine)
   - Experience (TechCorp Innovations)
   - Career Preferences (AI/ML, Software Development, Remote/Any).
3. Click **"Save Changes"**.

---

## Step 3: Resume Intelligence & ATS Studio
1. Navigate to **Resume Intelligence** (`/resume-studio`).
2. Drag and drop any sample PDF/DOCX resume (or review the latest parsed resume).
3. Inspect:
   - ATS Compatibility Score (e.g. **86/100**)
   - Identified Strengths (Clear contact info, strong technical keywords, quantified metrics)
   - Actionable Recommendations.
   - Extracted Skills synced into candidate profile.

---

## Step 4: RAG Internship Explorer
1. Navigate to **Internship Explorer** (`/internships`).
2. Type a semantic query like `"Machine Learning with PyTorch and FastAPI"`.
3. Filter by **Domain** (`AI/ML`) and **Work Mode** (`Remote`).
4. Notice ranked cards with live deterministic match badges (e.g. **92% Match**).

---

## Step 5: 360° Explainable Compatibility Breakdown
1. Click on the top internship card (e.g. *Machine Learning Engineer Intern*).
2. Inspect the **360° Explainable Compatibility Breakdown**:
   - Skills (30%), Experience (20%), Projects (15%), Education (15%), Eligibility (10%), Preferences (10%).
3. Review **"Why You Match"** vs **"Identified Skill Gaps"**.
4. Read the **Auditable AI Verdict**.

---

## Step 6: Skill Gap Roadmap
1. Click **"View Skill Gaps"** or navigate to **Skill Gap Matrix** (`/skill-gaps`).
2. Inspect HIGH / MEDIUM / LOW priority skill tags.
3. Review estimated study hours and curated tutorial links.
4. Read the **3-Phase Action Plan**.

---

## Step 7: Factual Resume & Cover Letter Customization
1. Click **"Tailor Resume"** or navigate to **Tailored Documents** (`/documents`).
2. Switch between **"Tailored ATS Resume"** and **"Role-Specific Cover Letter"**.
3. Notice the zero-hallucination guardrail: original projects and skills are strategically reordered and highlighted to match the job requirements.
4. Click **"Copy Text"** or **"Export Markdown"**.

---

## Step 8: Interview Preparation & AI Mock Interview
1. Navigate to **Interview Prep** (`/interview-prep`).
2. Explore the **Question Bank** and toggle **"Reveal Ideal Answer"**.
3. Check the **5-Day Study Calendar**.
4. Click **"Launch Mock Interview"** (`/mock-interview`).
5. Answer questions via typing or clicking **"Speak Answer"** (speech recognition).
6. Click **"Evaluate Answer"** to observe real-time AI scoring across:
   - Technical Accuracy
   - Clarity & Communication
   - Relevance
   - Confidence
7. Watch the **Interview Readiness Score (%)** update live.

---

## Step 9: Kanban Application Tracker
1. Navigate to **Application Tracker** (`/applications`).
2. Observe columns: *Saved*, *Applied*, *Assessment*, *Interview*, *Offer*, *Archived*.
3. Move applications across stages using the status dropdown.
4. Check deadline warning badges (*Due Soon*, *Overdue*, *Normal*).

---

## Step 10: Conversational AI Career Assistant
1. Click the floating **"Ask Assistant"** button on the top-right navbar or navigate to `/chat`.
2. Try the prompt chips:
   - *"Which internship should I apply to?"* (triggers tool: `search_internships()`)
   - *"What skills am I missing for the top match?"* (triggers tool: `get_skill_gaps()`)
   - *"What applications and deadlines are pending?"* (triggers tool: `get_upcoming_deadlines()`)
3. Notice the tool execution badges and grounded context answers.
