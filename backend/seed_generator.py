import json
import os
import random

COMPANY_METADATA = [
    {"name": "Infosys", "logo": "https://upload.wikimedia.org/wikipedia/commons/9/95/Infosys_logo.svg", "domain_pref": "Software Development"},
    {"name": "TCS", "logo": "https://upload.wikimedia.org/wikipedia/commons/b/b1/Tata_Consultancy_Services_Logo.svg", "domain_pref": "Software Development"},
    {"name": "Wipro", "logo": "https://upload.wikimedia.org/wikipedia/commons/a/a0/Wipro_Primary_Logo_Color_RGB.svg", "domain_pref": "Fullstack Development"},
    {"name": "Google", "logo": "https://upload.wikimedia.org/wikipedia/commons/2/2f/Google_2015_logo.svg", "domain_pref": "AI/ML"},
    {"name": "Microsoft", "logo": "https://upload.wikimedia.org/wikipedia/commons/9/96/Microsoft_logo_%282012%29.svg", "domain_pref": "Cloud & DevOps"},
    {"name": "Amazon", "logo": "https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg", "domain_pref": "Cloud & DevOps"},
    {"name": "IBM", "logo": "https://upload.wikimedia.org/wikipedia/commons/5/51/IBM_logo.svg", "domain_pref": "AI/ML"},
    {"name": "NVIDIA", "logo": "https://upload.wikimedia.org/wikipedia/commons/2/21/Nvidia_logo.svg", "domain_pref": "AI/ML"},
    {"name": "Adobe", "logo": "https://upload.wikimedia.org/wikipedia/commons/8/8d/Adobe_Corporate_Logo.svg", "domain_pref": "Frontend Development"},
    {"name": "Intel", "logo": "https://upload.wikimedia.org/wikipedia/commons/7/7d/Intel_logo_%282020%29.svg", "domain_pref": "Robotics & IoT"},
    {"name": "Oracle", "logo": "https://upload.wikimedia.org/wikipedia/commons/5/50/Oracle_logo.svg", "domain_pref": "Data Science"},
    {"name": "Zoho", "logo": "https://upload.wikimedia.org/wikipedia/commons/6/69/Zoho_Corporation_logo.png", "domain_pref": "Fullstack Development"},
    {"name": "Swiggy", "logo": "https://upload.wikimedia.org/wikipedia/commons/1/13/Swiggy_logo.svg", "domain_pref": "Fullstack Development"},
    {"name": "Zomato", "logo": "https://upload.wikimedia.org/wikipedia/commons/b/bd/Zomato_Logo.svg", "domain_pref": "Software Development"},
    {"name": "Razorpay", "logo": "https://upload.wikimedia.org/wikipedia/commons/8/89/Razorpay_logo.svg", "domain_pref": "Fullstack Development"},
    {"name": "Flipkart", "logo": "https://upload.wikimedia.org/wikipedia/commons/7/7a/Flipkart_logo.svg", "domain_pref": "Data Science"},
    {"name": "Freshworks", "logo": "https://upload.wikimedia.org/wikipedia/commons/b/b3/Freshworks_Logo.png", "domain_pref": "Frontend Development"},
    {"name": "Paytm", "logo": "https://upload.wikimedia.org/wikipedia/commons/2/24/Paytm_Logo.jpg", "domain_pref": "Cybersecurity"},
    {"name": "Cisco", "logo": "https://upload.wikimedia.org/wikipedia/commons/0/08/Cisco_logo_blue_2016.svg", "domain_pref": "Cybersecurity"},
    {"name": "Accenture", "logo": "https://upload.wikimedia.org/wikipedia/commons/c/cd/Accenture.svg", "domain_pref": "Cloud & DevOps"},
    {"name": "Capgemini", "logo": "https://upload.wikimedia.org/wikipedia/commons/9/9d/Capgemini_2017_logo.svg", "domain_pref": "Software Development"},
    {"name": "Cognizant", "logo": "https://upload.wikimedia.org/wikipedia/commons/a/a7/Cognizant_logo_2022.svg", "domain_pref": "Software Development"},
    {"name": "Deloitte", "logo": "https://upload.wikimedia.org/wikipedia/commons/c/c0/Deloitte.svg", "domain_pref": "Data Science"},
    {"name": "Postman", "logo": "https://upload.wikimedia.org/wikipedia/commons/c/c2/Postman_%28software%29.png", "domain_pref": "Software Development"},
    {"name": "Groww", "logo": "https://upload.wikimedia.org/wikipedia/commons/a/ad/Groww_app_logo.png", "domain_pref": "Mobile Development"}
]

DOMAINS = [
    "AI/ML", "Data Science", "Software Development", "Fullstack Development", "Frontend Development",
    "Cloud & DevOps", "Cybersecurity", "Mobile Development", "Robotics & IoT", "Product Management"
]

LOCATIONS = [
    "Bangalore, India", "Hyderabad, India", "Pune, India", "Gurgaon, India", "Mumbai, India",
    "Chennai, India", "Noida, India", "Remote"
]

WORK_MODES = ["Remote", "Hybrid", "Onsite"]
PLATFORMS = ["LinkedIn", "Naukri", "Internshala", "Unstop"]

SKILL_SETS = {
    "AI/ML": {
        "titles": ["AI Engineer Intern", "Machine Learning Research Intern", "Applied GenAI Intern", "Deep Learning Engineering Intern", "NLP Systems Intern", "Computer Vision Intern"],
        "req": [["Python", "PyTorch", "Machine Learning"], ["Python", "TensorFlow", "Deep Learning"], ["Python", "Transformers", "NLP"], ["Python", "OpenCV", "Computer Vision"], ["Python", "Scikit-Learn", "Data Analysis"], ["Python", "LLMs", "RAG", "LangChain"]],
        "pref": ["Docker", "MLflow", "CUDA", "FastAPI", "Vector Databases", "Git", "HuggingFace", "AWS SageMaker", "ONNX"]
    },
    "Data Science": {
        "titles": ["Data Science Intern", "Data Analyst Intern", "Big Data Engineering Intern", "Quantitative Analytics Intern", "Business Intelligence Intern"],
        "req": [["Python", "SQL", "Pandas", "NumPy"], ["Python", "R", "Statistical Modeling"], ["SQL", "Tableau", "Python", "PowerBI"], ["Python", "BigQuery", "ETL Pipelines"]],
        "pref": ["Spark", "Airflow", "Snowflake", "dbt", "Machine Learning", "A/B Testing", "Looker", "Matplotlib"]
    },
    "Software Development": {
        "titles": ["Software Engineering Intern", "Backend Developer Intern", "Systems Engineering Intern", "Core Python Engineer Intern", "Java Microservices Intern"],
        "req": [["Python", "FastAPI", "PostgreSQL", "Data Structures"], ["Java", "Spring Boot", "REST APIs", "MySQL"], ["Go", "Microservices", "gRPC", "Docker"], ["C++", "Algorithms", "System Design", "Multithreading"], ["Node.js", "TypeScript", "Express", "MongoDB"]],
        "pref": ["Redis", "Kubernetes", "Kafka", "Git", "Unit Testing", "CI/CD", "AWS", "Linux"]
    },
    "Fullstack Development": {
        "titles": ["Full Stack Developer Intern", "Web Application Engineering Intern", "React & Node.js Developer Intern", "Next.js Fullstack Intern"],
        "req": [["React", "Node.js", "TypeScript", "PostgreSQL"], ["Next.js", "Tailwind CSS", "FastAPI", "PostgreSQL"], ["React", "Python", "Flask", "MongoDB"], ["Vue.js", "Node.js", "Express", "MySQL"]],
        "pref": ["GraphQL", "Docker", "Redux", "Prisma", "AWS", "REST APIs", "Jest", "Vite"]
    },
    "Frontend Development": {
        "titles": ["Frontend Developer Intern", "UI/UX & Web Developer Intern", "React Frontend Engineer Intern", "Web Performance Engineering Intern"],
        "req": [["React", "TypeScript", "Tailwind CSS", "JavaScript"], ["Next.js", "React", "CSS3", "HTML5"], ["Vue.js", "TypeScript", "JavaScript", "Pinia"]],
        "pref": ["Figma", "Web Performance", "State Management", "Jest", "Vite", "Accessibility (a11y)", "Storybook"]
    },
    "Cloud & DevOps": {
        "titles": ["Cloud Infrastructure Intern", "DevOps Engineer Intern", "Site Reliability Engineering (SRE) Intern", "Kubernetes Platform Intern"],
        "req": [["Linux", "Docker", "Kubernetes", "AWS"], ["CI/CD", "Terraform", "GitHub Actions", "Docker"], ["GCP", "Kubernetes", "Python", "Bash Scripting"], ["AWS", "Terraform", "Monitoring (Prometheus/Grafana)"]],
        "pref": ["Ansible", "Helm", "ArgoCD", "Networking", "Security Best Practices", "Golang", "CloudWatch"]
    },
    "Cybersecurity": {
        "titles": ["Cybersecurity Analyst Intern", "Penetration Testing Intern", "Security Operations Center (SOC) Intern", "Application Security Intern"],
        "req": [["Network Security", "Linux", "Python", "Cryptography"], ["Penetration Testing", "OWASP Top 10", "Burp Suite"], ["SIEM", "SOC Operations", "Threat Intelligence", "Wireshark"]],
        "pref": ["Security+", "CEH", "Bash Scripting", "Reverse Engineering", "Cloud Security", "Docker Security"]
    },
    "Mobile Development": {
        "titles": ["Mobile Application Developer Intern", "Flutter Developer Intern", "Android Engineering Intern", "iOS App Development Intern"],
        "req": [["Flutter", "Dart", "REST APIs", "Mobile Architecture"], ["Android", "Kotlin", "Java", "Jetpack Compose"], ["iOS", "Swift", "SwiftUI", "Xcode"]],
        "pref": ["Firebase", "State Management (Bloc/Provider)", "App Store / Play Store Deployment", "CI/CD for Mobile", "SQLite"]
    },
    "Robotics & IoT": {
        "titles": ["Robotics & Perception Intern", "Embedded Systems Intern", "IoT Firmware Engineer Intern", "Autonomous Systems Intern"],
        "req": [["C++", "ROS2", "Linux", "Robotics Kinematics"], ["Embedded C", "Microcontrollers", "RTOS", "UART/SPI/I2C"], ["Python", "OpenCV", "SLAM", "Point Cloud Processing"]],
        "pref": ["Gazebo", "Hardware Debugging", "PCB Design", "Sensor Fusion", "Matlab/Simulink"]
    },
    "Product Management": {
        "titles": ["Associate Product Manager (APM) Intern", "Technical Product Management Intern", "Product Strategy & Growth Intern", "Product Analytics Intern"],
        "req": [["Product Roadmapping", "User Research", "Agile/Scrum", "Data Analysis"], ["Wireframing", "SQL", "Product Analytics", "PRD Writing"], ["User Journey Mapping", "Market Research", "Feature Prioritization"]],
        "pref": ["Figma", "Mixpanel", "Jira", "A/B Testing Methodologies", "Python for Analytics"]
    }
}

STIPENDS = [
    "₹30,000 / month", "₹40,000 / month", "₹50,000 / month", "₹65,000 / month",
    "₹80,000 / month", "₹1,00,000 / month", "₹1,25,000 / month", "Performance Stipend (₹45k - ₹75k)"
]

DURATIONS = ["3 Months", "6 Months", "6 Months (Convertible to PPO)", "Summer Internship (8-10 Weeks)"]

ELIGIBILITY = [
    "B.Tech / B.E / Dual Degree in Computer Science, AI, EE, or related branch graduating in 2025/2026/2027.",
    "Pursuing Bachelor's or Master's degree in Computer Science, Data Science, or Software Engineering.",
    "Pre-final or Final year undergraduate student with strong data structures and engineering fundamentals.",
    "Graduating 2026 or 2027 with demonstrated technical project portfolio."
]

def generate_internships(count: int = 1000):
    dataset = []
    random.seed(42)

    for i in range(1, count + 1):
        comp_obj = random.choice(COMPANY_METADATA)
        company_name = comp_obj["name"]
        company_logo = comp_obj["logo"]

        domain = random.choice(DOMAINS)
        domain_info = SKILL_SETS[domain]

        title = random.choice(domain_info["titles"])
        req_skills = random.choice(domain_info["req"])
        pref_skills = random.sample(domain_info["pref"], k=random.randint(2, 4))
        location = random.choice(LOCATIONS)
        work_mode = random.choice(WORK_MODES)
        stipend = random.choice(STIPENDS)
        duration = random.choice(DURATIONS)
        eligibility = random.choice(ELIGIBILITY)
        platform = random.choice(PLATFORMS)
        source_type = "CURATED" if i <= 200 else "LIVE"

        month = random.choice(["September", "October", "November", "December"])
        day = random.randint(15, 30)
        deadline = f"{month} {day}, 2026"

        desc = (
            f"Join {company_name} as a {title} within our high-impact {domain} organization. "
            f"You will collaborate directly with senior staff engineers and researchers to architect production-grade features, "
            f"optimize scalable distributed systems, and implement robust automated test suites. "
            f"Ideal candidates have hands-on proficiency in {', '.join(req_skills)} and a passion for engineering excellence."
        )

        app_url = f"https://careers.{company_name.lower().replace(' ', '')}.com/jobs/intern-{i:04d}"

        dataset.append({
            "id": i,
            "company": company_name,
            "title": title,
            "domain": domain,
            "description": desc,
            "requirements": req_skills,
            "preferred_skills": pref_skills,
            "location": location,
            "work_mode": work_mode,
            "stipend": stipend,
            "duration": duration,
            "eligibility": eligibility,
            "deadline": deadline,
            "application_url": app_url,
            "source": f"{platform} Verified Feed",
            "source_type": source_type,
            "source_job_id": f"{platform.lower()}_{company_name.lower()}_{i}",
            "company_logo_url": company_logo,
            "is_active": True,
            "is_demo": (source_type == "DEMO")
        })

    return dataset

if __name__ == "__main__":
    data = generate_internships(1000)
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "internships")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "internships_1000.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Generated {len(data)} realistic internships in {out_path}")
