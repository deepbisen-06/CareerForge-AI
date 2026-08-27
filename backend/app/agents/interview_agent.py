from typing import Dict, Any, List, Optional
import re
from app.core.llm_provider import get_llm_provider

QUESTION_CONCEPT_TEMPLATES = {
    "Technical": [
        {
            "question_pattern": "In {role}, how do you ensure high reliability and optimal latency when working with {skill}?",
            "expected_concepts": ["caching with redis", "database indexing", "asynchronous i/o", "profiling bottlenecks", "circuit breakers", "health checks"]
        },
        {
            "question_pattern": "Explain how you would design and test a scalable API endpoint handling large concurrent request spikes.",
            "expected_concepts": ["rate limiting", "load balancing", "stateless service architecture", "asynchronous worker queues", "automated load testing"]
        },
        {
            "question_pattern": "How does PostgreSQL manage concurrency and transaction isolation via MVCC and WAL logs?",
            "expected_concepts": ["multiversion concurrency control", "write-ahead logging", "isolation levels", "acid properties", "vacuuming"]
        }
    ],
    "Resume-based": [
        {
            "question_pattern": "In your project '{project}', what was the most challenging technical tradeoff you encountered and how did you resolve it?",
            "expected_concepts": ["star method", "architectural tradeoff", "latency vs throughput", "technical solution", "quantified impact"]
        }
    ],
    "Behavioral": [
        {
            "question_pattern": "Tell me about a time you had to learn an unfamiliar technology or framework under a tight deadline. How did you approach it?",
            "expected_concepts": ["proactive research", "official documentation", "minimal proof-of-concept", "mentorship/collaboration", "on-time delivery"]
        }
    ],
    "Role-specific": [
        {
            "question_pattern": "Why are you specifically interested in joining {company} for the {role} internship, and how does your skillset align with our technical focus?",
            "expected_concepts": ["company engineering culture", "alignment with required skills", "learning goals", "enthusiasm for team mission"]
        }
    ],
    "HR": [
        {
            "question_pattern": "How do you prioritize competing deadlines when managing academic commitments alongside engineering project deliverables?",
            "expected_concepts": ["eisenhower matrix", "time blocking", "transparent communication", "realistic milestones"]
        }
    ]
}

class InterviewAgent:
    def __init__(self):
        self.llm = get_llm_provider()

    def generate_question_bank(
        self,
        internship: Dict[str, Any],
        student_profile: Dict[str, Any],
        count: int = 8
    ) -> List[Dict[str, Any]]:
        """
        Generates role-specific questions with expected concept benchmarks.
        """
        role = internship.get("title", "Software Engineer")
        company = internship.get("company", "Company")
        req_skills = internship.get("requirements", ["Python", "FastAPI"])
        primary_skill = req_skills[0] if req_skills else "Backend Architecture"
        projects = student_profile.get("projects", [])
        project_name = projects[0].get("title") if projects else "Distributed Systems"

        questions = [
            # Technical 1
            {
                "question": f"In {role}, how do you ensure high reliability and optimal latency when working with {primary_skill}?",
                "category": "Technical",
                "difficulty": "Medium",
                "ideal_answer": f"Explain key optimization strategies: proper indexing, asynchronous I/O, caching strategies with Redis, profiling bottlenecks, and implementing health-check / circuit-breaker patterns.",
                "expected_concepts": ["caching with redis", "database indexing", "asynchronous i/o", "profiling bottlenecks", "circuit breakers", "health checks"]
            },
            # Technical 2
            {
                "question": f"Explain how you would design and test a scalable API endpoint handling large concurrent request spikes.",
                "category": "Technical",
                "difficulty": "Hard",
                "ideal_answer": f"Discuss rate limiting, load balancing, stateless service architecture, asynchronous worker queues (Celery/Redis), and automated load testing with Locust or k6.",
                "expected_concepts": ["rate limiting", "load balancing", "stateless architecture", "asynchronous worker queues", "load testing"]
            },
            # Resume-based
            {
                "question": f"In your project '{project_name}', what was the most challenging technical tradeoff you encountered and how did you resolve it?",
                "category": "Resume-based",
                "difficulty": "Medium",
                "ideal_answer": f"Structure using the STAR framework (Situation, Task, Action, Result). Quantify the impact (e.g. latency reduced, throughput achieved) and articulate why the chosen technical architecture was superior to alternatives.",
                "expected_concepts": ["star method", "architectural tradeoff", "latency vs throughput", "technical solution", "quantified impact"]
            },
            # Behavioral
            {
                "question": f"Tell me about a time you had to learn an unfamiliar technology or framework under a tight deadline. How did you approach it?",
                "category": "Behavioral",
                "difficulty": "Medium",
                "ideal_answer": f"Highlight proactive research, reading official documentation, building a minimal proof-of-concept, seeking targeted guidance from peers/mentors, and successfully delivering on time.",
                "expected_concepts": ["proactive research", "official documentation", "minimal proof-of-concept", "mentorship/collaboration", "on-time delivery"]
            },
            # Role-specific / Company
            {
                "question": f"Why are you specifically interested in joining {company} for the {role} internship, and how does your skillset align with our technical focus?",
                "category": "Role-specific",
                "difficulty": "Easy",
                "ideal_answer": f"Reference {company}'s products or engineering ethos, connect specific skills ({', '.join(req_skills[:2])}), and state clear learning and contribution goals.",
                "expected_concepts": ["company engineering culture", "alignment with required skills", "learning goals", "enthusiasm for team mission"]
            },
            # HR
            {
                "question": "How do you prioritize competing deadlines when managing academic commitments alongside engineering project deliverables?",
                "category": "HR",
                "difficulty": "Easy",
                "ideal_answer": "Discuss Eisenhower matrix prioritization, time blocking, transparent communication with team leads, and setting realistic milestones.",
                "expected_concepts": ["eisenhower matrix", "time blocking", "transparent communication", "realistic milestones"]
            }
        ]

        return questions[:count]

    def generate_5_day_plan(
        self,
        internship: Dict[str, Any],
        student_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generates a 5-day structured preparation roadmap.
        """
        req_skills = internship.get("requirements", ["Python", "Data Structures"])
        primary_skill = req_skills[0] if req_skills else "Core Programming"
        second_skill = req_skills[1] if len(req_skills) > 1 else "System Architecture"

        return [
            {
                "day": 1,
                "title": f"Day 1: Foundations & {primary_skill} Deep Dive",
                "tasks": [
                    f"Review core syntax, standard library, and runtime internals of {primary_skill}.",
                    "Solve 3 medium algorithmic problems (Arrays, Hash Maps, Two Pointers).",
                    "Review memory management and concurrency concepts."
                ],
                "time_estimate": "3.5 Hours"
            },
            {
                "day": 2,
                "title": f"Day 2: Advanced Topics & {second_skill}",
                "tasks": [
                    f"Study architectural best practices and common pitfalls in {second_skill}.",
                    "Deep dive into database query optimization and API contract design.",
                    "Practice 2 dynamic programming or tree/graph traversal problems."
                ],
                "time_estimate": "4.0 Hours"
            },
            {
                "day": 3,
                "title": "Day 3: Resume Projects & System Design",
                "tasks": [
                    "Prepare 2-minute elevator pitches for your top 2 resume projects.",
                    "Anticipate deep-dive questions on project architecture, bottlenecks, and tech choices.",
                    "Review basic distributed system patterns (Caching, Queues, Microservices)."
                ],
                "time_estimate": "3.5 Hours"
            },
            {
                "day": 4,
                "title": f"Day 4: Behavioral Mastery & {internship.get('company', 'Company')} Research",
                "tasks": [
                    "Draft 4 STAR-format stories: Conflict Resolution, Tight Deadline, Technical Failure, Leadership.",
                    f"Research {internship.get('company')}'s engineering blog and recent public updates.",
                    "Prepare 3 thoughtful questions to ask the interviewer."
                ],
                "time_estimate": "3.0 Hours"
            },
            {
                "day": 5,
                "title": "Day 5: Full Mock Interview & Final Polish",
                "tasks": [
                    "Complete a timed turn-by-turn AI Mock Interview session on CareerBridge.",
                    "Review live evaluation scores on Accuracy, Clarity, Relevance, and Confidence.",
                    "Rest and prepare a distraction-free interview environment."
                ],
                "time_estimate": "2.5 Hours"
            }
        ]

    def evaluate_answer(
        self,
        question: str,
        ideal_answer: str,
        user_answer: str,
        expected_concepts: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Objective Concept-Coverage Evaluation Engine.
        Compares user answer against expected concepts and computes 4D criteria scores.
        """
        words = user_answer.strip().split()
        length = len(words)
        user_lower = user_answer.lower()

        if length < 6:
            return {
                "score": 3.0,
                "feedback": "Answer is too brief. Provide a structured response detailing architectural choices, examples, or specific methodology.",
                "expected_concepts": expected_concepts or [],
                "detected_concepts": [],
                "missing_concepts": expected_concepts or [],
                "criteria": {
                    "accuracy": 3.0,
                    "clarity": 4.0,
                    "relevance": 4.0,
                    "confidence": 3.0
                }
            }

        # Concept Detection
        expected = expected_concepts or [w for w in ideal_answer.lower().split() if len(w) > 4]
        detected = []
        missing = []

        for concept in expected:
            concept_words = concept.lower().split()
            if all(cw in user_lower for cw in concept_words):
                detected.append(concept)
            else:
                missing.append(concept)

        concept_ratio = len(detected) / (len(expected) or 1)

        # 4D Dimension Calculations
        accuracy = min(10.0, max(4.0, 5.0 + concept_ratio * 4.5 + (0.5 if length > 30 else 0.0)))
        clarity = min(10.0, max(5.0, 7.0 + (1.5 if "." in user_answer and length > 20 else 0.5)))
        relevance = min(10.0, max(4.5, 6.5 + (2.5 * concept_ratio)))
        confidence = min(10.0, max(4.0, 8.0 + (1.0 if not any(w in user_lower for w in ["maybe", "i guess", "not sure", "probably"]) else -2.0)))

        overall_score = round((accuracy * 0.35 + clarity * 0.25 + relevance * 0.25 + confidence * 0.15), 1)

        feedback_notes = []
        if detected:
            feedback_notes.append(f"✓ Strong coverage of key concepts: {', '.join(detected[:3])}.")
        if missing:
            feedback_notes.append(f"Consider elaborating on: {', '.join(missing[:3])}.")
        if accuracy >= 8.5:
            feedback_notes.append("Excellent technical precision and correct domain terminology.")

        return {
            "score": overall_score,
            "feedback": " ".join(feedback_notes),
            "expected_concepts": expected,
            "detected_concepts": detected,
            "missing_concepts": missing,
            "criteria": {
                "accuracy": round(accuracy, 1),
                "clarity": round(clarity, 1),
                "relevance": round(relevance, 1),
                "confidence": round(confidence, 1)
            }
        }

interview_agent = InterviewAgent()
