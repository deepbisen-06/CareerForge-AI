<div align="center">

# ⚡ CareerForge AI
### *Autonomous Taskmaster Agent for End-to-End Career Intelligence & Application Execution*

[![Hackathon Track: Taskmaster Agent](https://img.shields.io/badge/Track-Taskmaster%20Agent-8A2BE2?style=for-the-badge&logo=probot&logoColor=white)](#-autonomous-taskmaster-agent-loop)
[![Google Gemini ADK](https://img.shields.io/badge/Google%20Gemini-ADK%20Orchestrator-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React 19](https://img.shields.io/badge/React-19.0-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Deterministic Fit](https://img.shields.io/badge/Deterministic%20Fit-6--Factor%20Auditable-00C853?style=for-the-badge)](#-6-factor-deterministic-compatibility-engine)
[![Factuality Guardrail](https://img.shields.io/badge/Zero--Hallucination-100%25%20Verified-brightgreen?style=for-the-badge)](#-zero-hallucination-guardrails--responsible-ai)

<br/>

[🌟 Key Capabilities](#-key-capabilities--modules) • [📊 System Architecture](#-system-architecture--diagrams) • [🤖 Agentic Loop](#-autonomous-taskmaster-agent-loop) • [📈 Benchmarks](#-quantitative-evaluation-benchmarks) • [⚡ Live Demo](#-instant-1-click-demo-access)

<br/>

---

### 🖥️ Visual Platform Showcase

| 📊 Executive Candidate Dashboard | 🤖 Autonomous Agent Workspace |
| :---: | :---: |
| ![CareerForge AI Executive Dashboard](docs/images/dashboard_preview.jpg) | ![CareerForge AI Agent Workspace](docs/images/agent_workspace_preview.jpg) |
| *Real-time 6-factor compatibility radar, ATS resume scoring & active agent telemetry.* | *Streaming chain-of-thought, dynamic tool invocation tree & Human-in-the-Loop gate.* |

---

</div>

## 💡 The Paradigm Shift: Why CareerForge AI?

Traditional internship hunting is broken: candidates spend dozens of hours scrolling disjointed boards, guessing match eligibility, and manually adapting resumes. Generic chatbots only output ungrounded advice.

**CareerForge AI** introduces an **Autonomous Goal-Driven Taskmaster Agent** backed by deterministic mathematical verification and strict zero-hallucination guardrails.

```
                  ┌─────────────────────────────────────────────────────────┐
  USER GOAL ───►  │ "Find top AI/ML internships matching my profile,        │
                  │  verify my eligibility, and prepare tailored materials" │
                  └────────────────────────────┬────────────────────────────┘
                                               │
                        ┌──────────────────────▼──────────────────────┐
                        │      CAREERFORGE TASKMASTER AGENT           │
                        │                                             │
                        │  1. Hybrid Semantic RAG Discovery (1k+ DB)  │
                        │  2. 6-Factor Deterministic Mathematical Fit │
                        │  3. Hard/Soft Eligibility Verification      │
                        │  4. Priority-Weighted Skill Gap Matrix      │
                        │  5. Zero-Hallucination Document Synthesis   │
                        │  6. Human-in-the-Loop Approval Gate         │
                        └──────────────────────┬──────────────────────┘
                                               │
                  ┌────────────────────────────▼────────────────────────────┐
  OUTCOME   ───►  │  Audited Compatibility + ATS Tailored Application Pack  │
                  │  + 5-Day Interview Strategy & Live Mock Simulator       │
                  └─────────────────────────────────────────────────────────┘
```

### 🥊 Comparative Landscape

| Capability | Traditional Job Portals | Generic AI Chatbots | ⚡ CareerForge AI (Taskmaster) |
| :--- | :---: | :---: | :---: |
| **Search Mechanism** | Keyword regex | Hallucinated links | **Sublinear Hybrid RAG Vector Retrieval** |
| **Compatibility Score** | Black-box / None | Subjective text | **6-Factor Deterministic Auditable Formula** |
| **Eligibility Verification** | Manual reading | Unreliable | **Automated Hard/Soft Rule Engine** |
| **Document Synthesis** | Generic templates | Fabricates skills | **Zero-Hallucination ATS Grounded Tailoring** |
| **Action Execution** | 100% Manual | None | **Autonomous Tool-Calling Multi-Step Loop** |
| **Safety Governance** | N/A | Ungoverned | **Human-in-the-Loop Approval Gate** |

---

## 📊 System Architecture & Diagrams

### 1. High-Level Multi-Tier Architecture

```mermaid
graph TB
    subgraph ClientLayer["🖥️ Frontend Application Layer (React 19 + TypeScript + Tailwind)"]
        UI_Dash["Executive Dashboard"]
        UI_Agent["Autonomous Agent Workspace"]
        UI_Wiz["Profile & Skill Wizard"]
        UI_Res["ATS Resume Intelligence Studio"]
        UI_RAG["Internship Explorer & RAG Search"]
        UI_Match["360° Explainability Radar"]
        UI_Gap["Skill Gap Matrix & Roadmap"]
        UI_Doc["Document Customizer"]
        UI_Prep["Interactive AI Mock Studio"]
        UI_Kan["Kanban Application Pipeline"]
        UI_Chat["Contextual Career Assistant"]
    end

    subgraph APILayer["⚡ High-Performance REST Gateway (FastAPI + Pydantic v2)"]
        AuthRouter["/api/v1/auth"]
        AgentRouter["/api/v1/agent"]
        ProfRouter["/api/v1/profile"]
        ResRouter["/api/v1/resume"]
        IntRouter["/api/v1/internships"]
        MatchRouter["/api/v1/matching"]
        GapRouter["/api/v1/skill-gaps"]
        DocRouter["/api/v1/documents"]
        PrepRouter["/api/v1/interview"]
        AppRouter["/api/v1/applications"]
        ChatRouter["/api/v1/chat"]
    end

    subgraph AgentCore["🤖 Taskmaster Agent & Modular Agent Engine"]
        Orchestrator["Taskmaster Agent Orchestrator"]
        Tools["Dynamic Tool Registry (8 Core Tools)"]
        ResumeAgent["Resume Intelligence Agent"]
        RAGAgent["RAG Vector Retrieval Agent"]
        MatchAgent["Deterministic Matching Agent"]
        GapAgent["Skill Gap & Roadmap Agent"]
        DocAgent["Factual Customization Agent"]
        InterviewAgent["Interview & Mock Simulator Agent"]
        ChatAgent["Contextual Tool-Calling Assistant"]
    end

    subgraph Persistence["🗄️ Persistence & Vector Storage"]
        SQL[(PostgreSQL / SQLite - 1,000 Curated Opportunities)]
        VectorDB[(RAG Vector Store - TF-IDF / Cosine Similarity)]
        AuditLog[(Immutable Agent Runs & Telemetry Log)]
        LLMProvider["LLM Engine (Google Gemini / ADK / Fallback)"]
    end

    ClientLayer --> APILayer
    APILayer --> AgentCore
    AgentCore --> Tools
    Tools --> Persistence
    AgentCore --> Persistence
```

---

### 2. Autonomous Taskmaster Agent Loop

```mermaid
flowchart TD
    UserGoal([User Goal Ingestion]) --> PromptPlanner[Gemini LLM: Formulate Multi-Step Execution Plan]
    PromptPlanner --> RunInit[Initialize Agent Run & Telemetry Session]
    
    RunInit --> StepLoop{Steps Remaining?}
    StepLoop -- Yes --> SelectTool[Select Specialized Tool & Bind Parameters]
    SelectTool --> ExecTool[Execute Tool: RAG / Match / Gap / Doc / Track]
    ExecTool --> Telemetry[Stream Event Telemetry to UI]
    Telemetry --> GateCheck{Requires Human Authorization?}
    
    GateCheck -- Yes --> PauseState[Set Status: AWAITING_HUMAN_APPROVAL]
    PauseState --> UserDecision[Candidate Reviews Package in Modal]
    UserDecision -- Approved --> ResumeRun[Resume Plan Execution]
    UserDecision -- Rejected --> AbortRun[Cancel Plan & Log Rejection Reason]
    ResumeRun --> StepLoop
    
    GateCheck -- No --> StepLoop
    StepLoop -- No --> ReportSynthesis[Gemini LLM: Synthesize Actionable Executive Summary]
    ReportSynthesis --> Done([Goal Achieved & Applications Ready])
```

---

### 3. End-to-End Candidate Journey

```mermaid
sequenceDiagram
    autonumber
    actor Candidate as Student / Candidate
    participant UI as CareerForge Web UI
    participant Gateway as FastAPI Gateway
    participant Agent as Autonomous Taskmaster
    participant Engine as Deterministic Tool Engine
    participant DB as Knowledge Base & DB

    Candidate->>UI: Upload Resume (PDF/DOCX) or Complete Wizard
    UI->>Gateway: POST /resume/upload
    Gateway->>Engine: Parse Resume & Compute ATS Health (0-100)
    Engine-->>UI: Verified Skills Taxonomy & ATS Breakdown (88/100)

    Candidate->>UI: Submit Autonomous Objective ("Find AI/ML Roles & Prepare")
    UI->>Gateway: POST /agent/run
    Gateway->>Agent: Launch Goal Pipeline
    
    Agent->>Engine: RAG Vector Retrieval (1,000 Opportunities)
    Engine-->>Agent: Top-Ranked Candidate Internships
    
    Agent->>Engine: Calculate 6-Factor Compatibility Matrix
    Engine-->>Agent: Auditable Scores (94% Compatibility)
    
    Agent->>Engine: Audit Hard/Soft Eligibility Rules
    Engine-->>Agent: Eligibility Verified (GPA, Visa, Grad Year)
    
    Agent->>Engine: Synthesize Factual Tailored Resume & Cover Letter
    Engine-->>Agent: Zero-Hallucination Application Package
    
    Agent->>UI: Trigger Human-in-the-Loop Approval Modal
    Candidate->>UI: Click "Approve & Submit"
    UI->>Gateway: POST /agent/runs/{id}/approve
    Gateway->>DB: Advance Pipeline Stage to APPLIED
    
    Candidate->>UI: Launch AI Mock Interview Session
    UI->>Gateway: POST /interview/generate-questions & POST /submit-answer
    Gateway->>Engine: Evaluate Candidate STAR Response (4 Dimensions)
    Engine-->>UI: Real-Time Accuracy, Clarity, Relevance, Confidence Scores
```

---

### 4. 6-Factor Deterministic Compatibility Engine

Unlike stochastic LLMs that hallucinate match ratings, CareerForge AI utilizes an auditable, multi-variable mathematical formulation:

$$\text{Match Score} = 0.30 \cdot S_{\text{skills}} + 0.20 \cdot S_{\text{exp}} + 0.15 \cdot S_{\text{proj}} + 0.15 \cdot S_{\text{edu}} + 0.10 \cdot S_{\text{elig}} + 0.10 \cdot S_{\text{pref}}$$

```mermaid
flowchart LR
    subgraph Factors["6-Factor Dimensions"]
        F1["Technical Skills Match (30%)"]
        F2["Domain Experience (20%)"]
        F3["Relevant Projects (15%)"]
        F4["Education & CGPA (15%)"]
        F5["Eligibility & Batch (10%)"]
        F6["Role Preferences (10%)"]
    end

    subgraph Engine["Deterministic Engine"]
        WeightedSum["Weighted Arithmetic Normalizer"]
    end

    subgraph Output["Explainability Layer"]
        FinalScore["Final Compatibility Score (0 - 100%)"]
        Radar["360° Radar Visualization"]
        AuditLog["Auditable Strengths & Weaknesses"]
    end

    F1 --> WeightedSum
    F2 --> WeightedSum
    F3 --> WeightedSum
    F4 --> WeightedSum
    F5 --> WeightedSum
    F6 --> WeightedSum

    WeightedSum --> FinalScore
    WeightedSum --> Radar
    WeightedSum --> AuditLog
```

---

## 🌟 Key Capabilities & Modules

```
 ┌────────────────────────────────────────────────────────────────────────┐
 │                        CAREERFORGE AI MODULES                          │
 ├─────────────────────────┬─────────────────────────┬────────────────────┤
 │ 01. Autonomous Agent    │ 02. ATS Resume Studio   │ 03. RAG Explorer   │
 │ Multi-step tool runner  │ Multi-format parser     │ 1,000+ curated DB  │
 │ Live telemetry stream   │ 0-100 scoring engine    │ Cosine similarity  │
 ├─────────────────────────┼─────────────────────────┼────────────────────┤
 │ 04. 6-Factor Matching   │ 05. Skill Gap Matrix    │ 06. Tailored Docs  │
 │ Deterministic formula   │ Prioritized gaps (H/M/L)│ Zero-hallucination │
 │ Natural language audit  │ 3-phase study roadmap   │ ATS resume & cover │
 ├─────────────────────────┼─────────────────────────┼────────────────────┤
 │ 07. Mock Interview AI   │ 08. Kanban Tracker      │ 09. Assistant Chat │
 │ STAR response scoring   │ Stage visual pipeline   │ Grounded db tools  │
 │ 4-dimension evaluation  │ Deadline warnings       │ Deep context memory│
 └─────────────────────────┴─────────────────────────┴────────────────────┘
```

---

## 🧰 Autonomous Agent Dynamic Tool Suite

The Taskmaster Agent orchestrates **8 purpose-built deterministic tools**:

| Tool Identifier | Subsystem | Function & Contract |
| :--- | :--- | :--- |
| `profile_tools.get_candidate_profile` | Profile Engine | Extracts candidate profile, verified skills taxonomy, coursework, and projects. |
| `opportunity_tools.discover_opportunities` | Hybrid RAG | Executes semantic vector retrieval across 1,000 curated opportunities. |
| `matching_tools.evaluate_compatibility` | Math Engine | Evaluates 6-factor deterministic weighted compatibility breakdown (0–100%). |
| `eligibility_tools.verify_eligibility` | Rule Engine | Validates graduation batch, work authorization, minimum CGPA, and prerequisites. |
| `skill_gap_tools.generate_gap_matrix` | Gap Analyzer | Computes missing/partial skills, estimated study hours, and resource paths. |
| `application_tools.tailor_application_package` | Doc Customizer | Formulates grounded ATS resume and tailored cover letter without hallucinated facts. |
| `tracker_tools.manage_application_pipeline` | Kanban Engine | Advances candidate application stage and synchronizes deadline countdowns. |
| `interview_tools.build_interview_prep_pack` | Prep Studio | Assembles tailored technical/behavioral question banks, rubrics, and 5-day study plans. |

---

## 📈 Quantitative Evaluation Benchmarks

CareerForge AI includes an automated benchmark evaluation suite (`backend/run_evaluation.py`) assessing **10 student profile personas** against the **1,000-internship knowledge base**:

```
================================================================================
          CAREERFORGE AI BENCHMARK EVALUATION RESULTS (1,000 DATASET)
================================================================================
 Metric                                  Target        Achieved     Status
--------------------------------------------------------------------------------
 RAG Precision@5                         >= 80.0%       100.0%      ✅ EXCEEDED
 RAG Recall@5                            >= 80.0%       100.0%      ✅ EXCEEDED
 RAG Recall@10                           >= 90.0%       100.0%      ✅ EXCEEDED
 Mean Reciprocal Rank (MRR)              >= 0.85         1.000      ✅ EXCEEDED
 Matching Compatibility Accuracy         >= 90.0%        98.0%      ✅ EXCEEDED
 Skill Gap Priority Precision            >= 85.0%        96.4%      ✅ EXCEEDED
 Zero-Hallucination Factuality Rate      100.0%         100.0%      ✅ PERFECT
================================================================================
```

---

## 🛡 Zero-Hallucination Guardrails & Responsible AI

1. **Anti-Hallucination Document Synthesis**: Generated resumes and cover letters strictly restructure, reorder, and emphasize verified candidate experiences — never inventing employers, dates, or skills.
2. **Deterministic Mathematical Compatibility**: Compatibility scores are computed via reproducible arithmetic rather than unpredictable LLM prompts.
3. **Turn-by-Turn Structured Interview Rubrics**: Live mock interview scoring evaluates answers against orthogonal dimensions (*Technical Accuracy, Communication Clarity, Relevance, and Confidence*).
4. **Human-in-the-Loop Safety Gate**: The Taskmaster Agent pauses execution before advancing application statuses, providing candidates with full oversight.
5. **Multi-Tenant JWT Security**: Cryptographic token isolation across all protected REST endpoints.

---

## ⚡ Instant 1-Click Demo Access

To explore CareerForge AI without manual registration:
- **Email**: `demo@careerbridge.ai`
- **Password**: `Demo@123`
- *(Or click **"1-Click Instant Demo Login"** on the web login screen)*

---

## 🐳 Cloud Deployment (Google Cloud Run & Docker)

### 1-Click Google Cloud Run Deployment
Deploy the backend service directly to Google Cloud Run:
```bash
export GCP_PROJECT_ID="your-gcp-project-id"
export GCP_REGION="us-central1"
export GEMINI_API_KEY="your-gemini-key"

bash deploy_cloud_run.sh
```

### Docker Compose Multi-Container Stack
```bash
docker compose up --build
```

---

## 📂 Project Directory Layout

```text
CareerForge-AI/
├── backend/
│   ├── app/
│   │   ├── agents/          # Autonomous Orchestrator & Multi-Agent tools
│   │   ├── api/             # 13 FastAPI REST endpoints (auth, agent, profile, resume, etc.)
│   │   ├── auth/            # JWT authentication & Bcrypt security
│   │   ├── core/            # Config & Multi-LLM provider abstraction (Gemini / OpenAI)
│   │   ├── database/        # Session engine & migrations
│   │   ├── models/          # SQLAlchemy ORM entities (agent_runs, agent_events, internships)
│   │   ├── rag/             # Hybrid RAG Vector Store & TF-IDF matrix
│   │   └── schemas/         # Pydantic v2 data contracts
│   ├── tests/               # Pytest suite (100% pass)
│   ├── seed_data.py         # Database seeder (1,000 internships + Demo persona)
│   ├── seed_generator.py    # Internship dataset synthesizer
│   ├── run_evaluation.py    # Benchmark evaluation suite
│   ├── Dockerfile           # Backend container definition
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/      # Reusable UI components (AI Assistant Drawer, etc.)
│   │   ├── layouts/         # Dashboard layout with sidebar navigation
│   │   ├── lib/             # AuthProvider & Theme context
│   │   ├── pages/           # 13 React pages (Agent Workspace, Runs, Dashboard, Resume, etc.)
│   │   ├── services/        # Type-safe API client
│   │   ├── types/           # TypeScript domain definitions
│   │   ├── App.tsx          # Application routing & ProtectedRoute guards
│   │   └── main.tsx         # Client entry point
│   ├── Dockerfile           # Production container
│   ├── nginx.conf           # Reverse proxy configuration
│   └── package.json         # Node dependencies
├── data/
│   └── internships/         # 1,000 curated internship records (JSON)
├── docs/
│   ├── images/              # Visual platform showcase screenshots
│   ├── architecture.md      # Detailed system architecture guide
│   ├── api.md               # Complete REST API reference
│   ├── rag.md               # RAG vector retrieval & re-ranking specifications
│   ├── demo.md              # Step-by-step interactive demo script
│   └── evaluation.md        # Benchmark metrics report
├── deploy_cloud_run.sh      # Cloud Run deployment script
├── docker-compose.yml       # Production Docker orchestration
├── .env.example             # Environment variable template
├── run_live_demo.py         # Automated end-to-end verification script
└── README.md                # Comprehensive documentation
```

---

## 📜 License

Distributed under the **MIT License**. See `LICENSE` for details.

<div align="center">
  <sub>Built with ⚡ by <b>Deep Bisen</b> for the Autonomous Agent Hackathon.</sub>
</div>
