import os
from openai import OpenAI

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

def _chat(prompt):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def analyze_resume(resume_text):
    prompt = f"""
You are an expert HR manager and career coach with 20 years of experience.

Analyze this resume and respond in EXACTLY this format:

SCORE: [number between 0-100]

STRENGTHS:
- [strength 1]
- [strength 2]
- [strength 3]

WEAKNESSES:
- [weakness 1]
- [weakness 2]
- [weakness 3]

SUGGESTIONS:
- [suggestion 1]
- [suggestion 2]
- [suggestion 3]

SUMMARY:
[Write 2-3 sentences overall summary of this candidate]

Resume:
{resume_text}
"""
    return _chat(prompt)


def generate_interview_questions(skills, job_title):
    skills_str = ", ".join(skills)
    prompt = f"""
You are an expert technical interviewer.

Generate exactly 10 interview questions for a {job_title} candidate.
Their skills are: {skills_str}

Format EXACTLY like this:

TECHNICAL QUESTIONS:
1. [question]
2. [question]
3. [question]
4. [question]
5. [question]

BEHAVIORAL QUESTIONS:
6. [question]
7. [question]
8. [question]

SITUATIONAL QUESTIONS:
9. [question]
10. [question]
"""
    return _chat(prompt)


def generate_skill_roadmap(missing_skills, target_job):
    skills_str = ", ".join(missing_skills)
    prompt = f"""
You are a career mentor and learning coach.

Create a learning roadmap for someone who wants to become a {target_job}.
They are missing these skills: {skills_str}

Format EXACTLY like this:

ROADMAP FOR {target_job.upper()}:

WEEK 1-2: [skill to learn]
- What to learn: [details]
- Resource: [free resource name]
- Project: [small project idea]

WEEK 3-4: [skill to learn]
- What to learn: [details]
- Resource: [free resource name]
- Project: [small project idea]

WEEK 5-6: [skill to learn]
- What to learn: [details]
- Resource: [free resource name]
- Project: [small project idea]

ESTIMATED TIME: [X weeks/months]
DIFFICULTY: [Easy/Medium/Hard]
"""
    return _chat(prompt)


def improve_resume_line(original_line):
    prompt = f"""
You are a professional resume writer.

Improve this resume bullet point to make it more impactful, 
quantified, and ATS-friendly.

Original: {original_line}

Give me 3 improved versions. Format like:

VERSION 1: [improved line]
VERSION 2: [improved line]  
VERSION 3: [improved line]

EXPLANATION: [why these are better]
"""
    return _chat(prompt)