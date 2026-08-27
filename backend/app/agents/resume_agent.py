import re
import io
import json
from typing import Dict, Any, List, Tuple
from app.core.llm_provider import get_llm_provider

class ResumeAgent:
    def __init__(self):
        self.llm = get_llm_provider()

    def extract_text(self, file_bytes: bytes, filename: str) -> str:
        ext = filename.lower().split('.')[-1]
        text = ""
        
        if ext == "pdf":
            try:
                import pypdf
                reader = pypdf.PdfReader(io.BytesIO(file_bytes))
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
            except Exception as e:
                try:
                    import pdfplumber
                    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                        for page in pdf.pages:
                            extracted = page.extract_text()
                            if extracted:
                                text += extracted + "\n"
                except Exception as inner_e:
                    text = f"Error reading PDF: {e} / {inner_e}"
                    
        elif ext in ["docx", "doc"]:
            try:
                import docx
                doc = docx.Document(io.BytesIO(file_bytes))
                for para in doc.paragraphs:
                    text += para.text + "\n"
            except Exception as e:
                text = f"Error reading DOCX: {e}"
        else: # plain text
            text = file_bytes.decode('utf-8', errors='ignore')
            
        return text.strip()

    def parse_resume(self, raw_text: str) -> Dict[str, Any]:
        """
        Extract structured fields from resume raw text:
        name, contact, education, skills, experience, projects, certifications, achievements, links
        """
        # Heuristic extraction + LLM structuring
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', raw_text)
        phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', raw_text)
        github_match = re.search(r'(https?://)?(www\.)?github\.com/[\w-]+', raw_text, re.IGNORECASE)
        linkedin_match = re.search(r'(https?://)?(www\.)?linkedin\.com/in/[\w-]+', raw_text, re.IGNORECASE)
        
        extracted_links = []
        if github_match:
            extracted_links.append(github_match.group(0))
        if linkedin_match:
            extracted_links.append(linkedin_match.group(0))

        # Known skills lexicon matching
        skills_lexicon = [
            "Python", "Java", "C++", "C", "Go", "Rust", "JavaScript", "TypeScript", "SQL",
            "FastAPI", "Flask", "Django", "React", "Next.js", "Node.js", "Express", "Vue.js", "Tailwind CSS",
            "Machine Learning", "Deep Learning", "PyTorch", "TensorFlow", "NLP", "Computer Vision",
            "LLMs", "RAG", "LangChain", "Scikit-Learn", "OpenCV", "Pandas", "NumPy",
            "Docker", "Kubernetes", "AWS", "GCP", "Azure", "CI/CD", "Linux", "Git", "PostgreSQL", "MongoDB", "Redis",
            "REST APIs", "GraphQL", "Microservices", "Data Structures", "Algorithms"
        ]
        
        found_skills = []
        text_lower = raw_text.lower()
        for skill in skills_lexicon:
            # Word boundary matching
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.append(skill)

        # Name extraction heuristic (first non-empty line or title)
        lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
        candidate_name = lines[0] if lines else "Candidate"
        if len(candidate_name) > 40 or "@" in candidate_name or "resume" in candidate_name.lower():
            candidate_name = "Candidate"

        parsed = {
            "name": candidate_name,
            "email": email_match.group(0) if email_match else "",
            "phone": phone_match.group(0) if phone_match else "",
            "links": extracted_links,
            "skills": found_skills,
            "education": [],
            "experience": [],
            "projects": [],
            "certifications": [],
            "achievements": [],
            "raw_preview": raw_text[:500]
        }

        # Identify sections by headings
        sec_headers = {
            "education": r'(education|academic background|qualifications)',
            "experience": r'(experience|work history|employment|internships)',
            "projects": r'(projects|technical projects|academic projects)',
            "certifications": r'(certifications|certificates|courses)',
            "achievements": r'(achievements|awards|honors|publications)'
        }
        
        for sec_name, pattern in sec_headers.items():
            if re.search(pattern, text_lower):
                parsed[sec_name].append(f"Section detected in resume text")

        return parsed

    def analyze_resume_intelligence(self, raw_text: str, parsed_data: Dict[str, Any]) -> Tuple[float, List[str], List[str], List[str], List[str]]:
        """
        Calculates ATS Score (0-100), Strengths, Weaknesses, Missing Sections, and Recommendations.
        """
        score = 50.0
        strengths = []
        weaknesses = []
        missing_sections = []
        recommendations = []

        # 1. Contact information check
        if parsed_data.get("email") and parsed_data.get("phone"):
            score += 10
            strengths.append("Clear contact information (Email and Phone present)")
        else:
            weaknesses.append("Missing complete contact information (Email/Phone)")
            recommendations.append("Ensure both professional email and phone number are clearly visible at the top.")

        # 2. Links check
        if parsed_data.get("links"):
            score += 5
            strengths.append("Included relevant profile links (GitHub / LinkedIn)")
        else:
            weaknesses.append("No GitHub or LinkedIn profile links detected")
            recommendations.append("Add links to your active GitHub profile and LinkedIn page.")

        # 3. Skills density
        skill_count = len(parsed_data.get("skills", []))
        if skill_count >= 8:
            score += 15
            strengths.append(f"Strong technical skill variety ({skill_count} relevant technical skills identified)")
        elif skill_count >= 4:
            score += 8
            strengths.append(f"Solid foundational technical skills ({skill_count} skills identified)")
        else:
            weaknesses.append("Limited technical keywords and specific skills listed")
            recommendations.append("Explicitly list relevant programming languages, frameworks, and developer tools.")

        # 4. Action verbs and quantified metrics check
        metrics_pattern = re.findall(r'\b\d+([%kKmM\+]|\s*(percent|users|x|ms|s|hours|latency|throughput))\b', raw_text, re.IGNORECASE)
        action_verbs = ["architected", "developed", "engineered", "implemented", "optimized", "built", "reduced", "scaled", "designed", "deployed"]
        verb_count = sum(1 for verb in action_verbs if verb in raw_text.lower())
        
        if len(metrics_pattern) >= 2:
            score += 10
            strengths.append("Includes measurable, quantified project outcomes and impact metrics")
        else:
            weaknesses.append("Few quantified achievements (e.g. % improvement, latency reduction, user count)")
            recommendations.append("Use the XYZ formula: 'Accomplished [X] as measured by [Y], by doing [Z]'.")

        if verb_count >= 3:
            score += 10
            strengths.append("Effective use of strong action verbs across project and experience descriptions")
        else:
            recommendations.append("Start each bullet point with strong action verbs like 'Engineered', 'Optimized', or 'Architected'.")

        # 5. Section completeness
        expected_sections = ["education", "experience", "projects", "certifications"]
        for sec in expected_sections:
            if not parsed_data.get(sec):
                missing_sections.append(sec.capitalize())

        if "Education" in missing_sections:
            score -= 10
            recommendations.append("Add a dedicated Education section with your degree, institution, field, and CGPA.")
        if "Projects" in missing_sections:
            score -= 10
            recommendations.append("Highlight 2-3 prominent technical projects demonstrating real-world problem solving.")

        score = max(20.0, min(100.0, score))
        return score, strengths, weaknesses, missing_sections, recommendations

resume_agent = ResumeAgent()
