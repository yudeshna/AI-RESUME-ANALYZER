import os
from openai import OpenAI

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

def _chat(prompt, temperature=0.2):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature
    )
    return response.choices[0].message.content


def analyze_resume(resume_text):
    prompt = f"""You are a senior HR director and ATS expert with 20+ years of experience evaluating resumes at top tech companies like Google, Amazon, and Microsoft.

Analyze this resume using the EXACT scoring rubric below. Be strict, precise and consistent.

=== SCORING RUBRIC (Total: 100 points) ===

1. CONTACT & PROFESSIONAL INFO (5 pts)
   - Has email, phone, LinkedIn/GitHub, location → Full 5 pts
   - Missing 1-2 items → 3 pts
   - Missing most → 1 pt

2. PROFESSIONAL SUMMARY / OBJECTIVE (10 pts)
   - Strong, tailored summary with keywords → 10 pts
   - Generic summary → 5 pts
   - Missing → 0 pts

3. WORK EXPERIENCE (30 pts)
   - 3+ relevant jobs with quantified achievements (numbers, %) → 30 pts
   - 2 jobs with some metrics → 20 pts
   - 1 job or vague descriptions → 10 pts
   - No experience → 0 pts

4. SKILLS SECTION (20 pts)
   - 10+ relevant technical skills listed clearly → 20 pts
   - 5-9 skills → 12 pts
   - 1-4 skills → 6 pts
   - No skills section → 0 pts

5. EDUCATION (10 pts)
   - Degree with GPA/achievements from known institution → 10 pts
   - Degree without details → 7 pts
   - Certifications only → 5 pts

6. PROJECTS / PORTFOLIO (15 pts)
   - 3+ projects with tech stack, impact, GitHub links → 15 pts
   - 1-2 projects with some detail → 8 pts
   - Projects listed but no detail → 3 pts
   - No projects → 0 pts

7. CERTIFICATIONS & ACHIEVEMENTS (5 pts)
   - 2+ relevant certifications or awards → 5 pts
   - 1 certification → 3 pts
   - None → 0 pts

8. RESUME FORMATTING & ATS COMPATIBILITY (5 pts)
   - Clean structure, consistent formatting, no tables/images → 5 pts
   - Minor issues → 3 pts
   - Poor formatting → 1 pt

=== RESPOND IN EXACTLY THIS FORMAT ===

SCORE: [total number 0-100, calculated from rubric above]

SCORE_BREAKDOWN:
- Contact & Info: [X]/5
- Summary: [X]/10
- Experience: [X]/30
- Skills: [X]/20
- Education: [X]/10
- Projects: [X]/15
- Certifications: [X]/5
- Formatting: [X]/5

STRENGTHS:
- [specific strength with evidence from resume]
- [specific strength with evidence from resume]
- [specific strength with evidence from resume]

WEAKNESSES:
- [specific weakness with evidence from resume]
- [specific weakness with evidence from resume]
- [specific weakness with evidence from resume]

SUGGESTIONS:
- [actionable suggestion to improve score]
- [actionable suggestion to improve score]
- [actionable suggestion to improve score]
- [actionable suggestion to improve score]

ATS_KEYWORDS_FOUND:
- [keyword 1], [keyword 2], [keyword 3], [keyword 4], [keyword 5]

ATS_KEYWORDS_MISSING:
- [keyword 1], [keyword 2], [keyword 3]

SUMMARY:
[Write 3 sentences: overall candidate quality, top strength, most critical improvement needed]

Resume Text:
{resume_text}
"""
    return _chat(prompt, temperature=0.1)


def generate_interview_questions(skills, job_title, difficulty="Entry Level"):
    skills_str = ", ".join(skills[:15]) if skills else "general"

    # Map difficulty to clear instructions
    diff_map = {
        "Entry Level": {
            "label": "Entry Level (0-1 years experience, fresher)",
            "instruction": "Questions must be BASIC and FUNDAMENTAL. Assume the candidate is a fresher with no work experience. Ask about core concepts, definitions, and simple scenarios. Avoid advanced system design or complex case studies."
        },
        "Mid Level": {
            "label": "Mid Level (2-4 years experience)",
            "instruction": "Questions must be INTERMEDIATE. Assume the candidate has 2-4 years of work experience. Ask about practical application, problem-solving, trade-offs, and some leadership scenarios. Mix of concepts and real-world application."
        },
        "Senior Level": {
            "label": "Senior Level (5+ years experience)",
            "instruction": "Questions must be ADVANCED and COMPLEX. Assume the candidate is a senior professional. Ask about architecture decisions, leadership challenges, complex problem-solving, strategic thinking, and mentoring others."
        }
    }
    diff_info = diff_map.get(difficulty, diff_map["Entry Level"])

    # Detect domain to tailor questions correctly
    job_lower = job_title.lower()
    is_govt = any(w in job_lower for w in ["upsc","ias","ips","irs","ssc","bank po","railway","psc","defence","government","civil service","nda","cds"])
    is_medical = any(w in job_lower for w in ["doctor","mbbs","pharmacist","nurse","medical","clinical","hospital","health","dentist"])
    is_law = any(w in job_lower for w in ["lawyer","legal","advocate","judge","compliance","law"])
    is_finance = any(w in job_lower for w in ["ca","chartered","accountant","finance","banking","investment","actuary","tax","audit"])
    is_design = any(w in job_lower for w in ["designer","ui","ux","graphic","creative","animator","illustrator"])
    is_management = any(w in job_lower for w in ["manager","mba","hr","operations","supply chain","project manager","product manager","scrum"])
    is_tech = not any([is_govt, is_medical, is_law, is_finance, is_design, is_management])

    if is_govt:
        domain_context = f"""This is a GOVERNMENT / CIVIL SERVICES interview for: {job_title}
Questions must cover: General Knowledge, Current Affairs, Indian Polity & Constitution, History, Geography, Economy, Ethics & Integrity, Public Administration, and role-specific knowledge.
Do NOT ask coding or software questions."""
    elif is_medical:
        domain_context = f"""This is a HEALTHCARE / MEDICAL interview for: {job_title}
Questions must cover: Clinical knowledge, patient care, medical ethics, pharmacology (if relevant), anatomy, diagnosis, and healthcare regulations.
Do NOT ask coding or software questions."""
    elif is_law:
        domain_context = f"""This is a LEGAL / LAW interview for: {job_title}
Questions must cover: Legal concepts, case law, Indian Penal Code, Constitution, contract law, compliance regulations, and legal reasoning."""
    elif is_finance:
        domain_context = f"""This is a FINANCE / ACCOUNTING interview for: {job_title}
Questions must cover: Financial statements, taxation, audit, investment principles, risk management, financial regulations, and accounting standards."""
    elif is_design:
        domain_context = f"""This is a DESIGN interview for: {job_title}
Questions must cover: Design principles, UX research, tools (Figma, Adobe), typography, color theory, portfolio review, and design thinking process."""
    elif is_management:
        domain_context = f"""This is a MANAGEMENT / BUSINESS interview for: {job_title}
Questions must cover: Leadership, team management, strategy, stakeholder communication, conflict resolution, and role-specific business knowledge."""
    else:
        domain_context = f"""This is a TECHNICAL interview for: {job_title}
Candidate's technical skills: {skills_str}
Questions must be directly relevant to these skills and this specific role."""

    prompt = f"""You are an expert interviewer with 15 years of experience hiring for {job_title} roles.

{domain_context}

DIFFICULTY LEVEL: {diff_info["label"]}
{diff_info["instruction"]}

Generate exactly 12 highly relevant interview questions for a {difficulty} {job_title} position.

STRICT RULES:
- Every question must match the {difficulty} difficulty level EXACTLY
- Every question must be 100% relevant to {job_title} — no off-topic questions
- Questions must match the actual domain (govt exam = GK/polity, medical = clinical, tech = coding/systems)
- Entry Level = basic concepts only, Mid Level = practical application, Senior Level = advanced/strategic
- Include what a GOOD answer should cover

Format EXACTLY like this (NO difficulty labels inside questions):

TECHNICAL QUESTIONS:
1. [{difficulty}-appropriate question for {job_title}]
   → Good answer covers: [2-3 key points]

2. [{difficulty}-appropriate question for {job_title}]
   → Good answer covers: [2-3 key points]

3. [{difficulty}-appropriate question for {job_title}]
   → Good answer covers: [2-3 key points]

4. [{difficulty}-appropriate question for {job_title}]
   → Good answer covers: [2-3 key points]

5. [{difficulty}-appropriate question for {job_title}]
   → Good answer covers: [2-3 key points]

6. [{difficulty}-appropriate question for {job_title}]
   → Good answer covers: [2-3 key points]

BEHAVIORAL QUESTIONS:
7. [{difficulty}-level behavioral question for {job_title}]
   → Good answer covers: [2-3 key points]

8. [{difficulty}-level behavioral question for {job_title}]
   → Good answer covers: [2-3 key points]

9. [{difficulty}-level behavioral question for {job_title}]
   → Good answer covers: [2-3 key points]

SITUATIONAL / CASE QUESTIONS:
10. [{difficulty}-level real scenario for {job_title}]
    → Good answer covers: [2-3 key points]

11. [{difficulty}-level real scenario for {job_title}]
    → Good answer covers: [2-3 key points]

12. [{difficulty}-level problem-solving question for {job_title}]
    → Good answer covers: [2-3 key points]
"""
    return _chat(prompt, temperature=0.3)


def generate_skill_roadmap(missing_skills, target_job):
    # Expand common shortcuts to full skill names
    SHORTCUTS = {
        "dl": "Deep Learning", "ml": "Machine Learning", "ai": "Artificial Intelligence",
        "nlp": "Natural Language Processing", "cv": "Computer Vision",
        "sql": "SQL", "nosql": "NoSQL", "js": "JavaScript", "ts": "TypeScript",
        "py": "Python", "tf": "TensorFlow", "pt": "PyTorch", "sk": "Scikit-learn",
        "ds": "Data Science", "da": "Data Analysis", "de": "Data Engineering",
        "aws": "Amazon Web Services", "gcp": "Google Cloud Platform",
        "k8s": "Kubernetes", "ci/cd": "CI/CD", "oop": "Object Oriented Programming",
        "api": "REST API", "db": "Database", "fe": "Frontend Development",
        "be": "Backend Development", "fs": "Full Stack Development",
        "dsa": "Data Structures and Algorithms", "os": "Operating Systems",
        "cn": "Computer Networks", "se": "Software Engineering",
        "pm": "Project Management", "agile": "Agile Methodology",
        "git": "Git Version Control", "docker": "Docker",
        "llm": "Large Language Models", "rag": "RAG (Retrieval Augmented Generation)",
        "gen ai": "Generative AI", "genai": "Generative AI",
    }
    expanded = []
    for s in missing_skills:
        key = s.strip().lower()
        expanded.append(SHORTCUTS.get(key, s.strip()))
    skills_str = ", ".join(expanded)
    prompt = f"""You are an expert career coach and curriculum designer who has helped 10,000+ people land jobs at top tech companies.

Create a detailed, realistic 12-week learning roadmap for someone targeting: {target_job}
Skills they need to learn: {skills_str}

Rules:
- Be specific with resource names (actual websites, courses, books)
- Include free AND paid options
- Each week must have a concrete mini-project
- Prioritize skills by job market demand

Format EXACTLY like this:

🎯 ROADMAP: {target_job.upper()}
📅 Duration: 12 Weeks | 💰 Budget: Free + Optional Paid

━━━ PHASE 1: FOUNDATION (Weeks 1-4) ━━━

WEEK 1-2: [Skill Name]
📚 What to Learn:
  - [Topic 1]
  - [Topic 2]
  - [Topic 3]
🔗 Free Resources:
  - [Resource name + URL or platform]
  - [Resource name + URL or platform]
💰 Paid Option: [Course name on Udemy/Coursera - approx price]
🛠️ Mini Project: [Specific small project idea]
✅ Success Metric: [How to know you've mastered it]

WEEK 3-4: [Skill Name]
📚 What to Learn:
  - [Topic 1]
  - [Topic 2]
🔗 Free Resources:
  - [Resource]
💰 Paid Option: [Course]
🛠️ Mini Project: [Project idea]
✅ Success Metric: [Metric]

━━━ PHASE 2: CORE SKILLS (Weeks 5-8) ━━━

WEEK 5-6: [Skill Name]
📚 What to Learn: [topics]
🔗 Free Resources: [resources]
🛠️ Mini Project: [project]

WEEK 7-8: [Skill Name]
📚 What to Learn: [topics]
🔗 Free Resources: [resources]
🛠️ Mini Project: [project]

━━━ PHASE 3: ADVANCED + JOB READY (Weeks 9-12) ━━━

WEEK 9-10: [Skill/Capstone Project]
🛠️ Capstone Project: [Full project idea that demonstrates all skills]

WEEK 11-12: [Interview Prep + Portfolio]
📋 Checklist:
  - Update GitHub with all projects
  - Add projects to resume
  - Practice 50 LeetCode problems
  - Apply to 10 jobs per week

📊 FINAL ASSESSMENT:
  ⏱️ Total Time: ~[X] hours
  💪 Difficulty: [Easy/Medium/Hard]
  🎯 Job Readiness: [X]% after completion
  💰 Expected Salary: [range]
"""
    return _chat(prompt, temperature=0.2)


def improve_resume_line(original_line):
    prompt = f"""You are a professional resume writer who has helped candidates get into Google, Amazon, Microsoft and top startups.

Transform this weak resume bullet point into 3 powerful, ATS-optimized versions.

Original line: "{original_line}"

Rules for improvement:
1. Start with a STRONG action verb (Engineered, Architected, Spearheaded, Optimized, etc.)
2. Add QUANTIFIED metrics (%, $, time saved, users impacted, performance gain)
3. Include relevant technical keywords for ATS
4. Show IMPACT not just activity
5. Keep under 2 lines

Format EXACTLY like this:

❌ ORIGINAL ISSUE:
[What makes the original weak - be specific]

✅ VERSION 1 (Impact-focused):
[Improved bullet point with metrics and strong verb]
💡 Why better: [1 sentence explanation]

✅ VERSION 2 (Technical-focused):
[Improved bullet point emphasizing tech stack and scale]
💡 Why better: [1 sentence explanation]

✅ VERSION 3 (Leadership/Outcome-focused):
[Improved bullet point emphasizing ownership and results]
💡 Why better: [1 sentence explanation]

🎯 TOP RECOMMENDATION: Version [1/2/3] — [reason why]

📌 POWER VERBS TO USE FOR YOUR FIELD:
[List 5 strong action verbs relevant to this type of work]
"""
    return _chat(prompt, temperature=0.3)
