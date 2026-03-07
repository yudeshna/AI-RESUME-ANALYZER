import pandas as pd
import os

JOBS = [
    {"title": "Data Scientist", "skills": ["Python","Machine Learning","Statistics","Deep Learning","SQL","TensorFlow","Pandas"]},
    {"title": "Data Analyst", "skills": ["SQL","Excel","Power BI","Python","Tableau","Statistics","Pandas"]},
    {"title": "ML Engineer", "skills": ["Python","Deep Learning","TensorFlow","PyTorch","Docker","Machine Learning"]},
    {"title": "Frontend Developer", "skills": ["React","JavaScript","HTML","CSS","TypeScript","Vue"]},
    {"title": "Backend Developer", "skills": ["Python","Java","Node.js","SQL","REST API","Docker","MongoDB"]},
    {"title": "Full Stack Developer", "skills": ["React","Node.js","JavaScript","SQL","MongoDB","Python","Docker"]},
    {"title": "DevOps Engineer", "skills": ["Docker","Kubernetes","CI/CD","AWS","Linux","Python","Jenkins"]},
    {"title": "Cloud Architect", "skills": ["AWS","Azure","GCP","Docker","Kubernetes","Python","Terraform"]},
    {"title": "Data Engineer", "skills": ["Python","SQL","Spark","Hadoop","AWS","Pandas","Airflow"]},
    {"title": "AI Research Scientist", "skills": ["Python","Deep Learning","NLP","TensorFlow","PyTorch","Statistics","Research"]},
    {"title": "Cybersecurity Analyst", "skills": ["Linux","Python","Network Security","Firewalls","Git"]},
    {"title": "Business Analyst", "skills": ["SQL","Excel","Power BI","Tableau","Statistics","Communication","Agile"]},
]

def match_jobs(user_skills):
    results = []
    user_skills_lower = [s.lower() for s in user_skills]

    for job in JOBS:
        job_skills_lower = [s.lower() for s in job["skills"]]
        matched = [s for s in job["skills"] if s.lower() in user_skills_lower]
        missing = [s for s in job["skills"] if s.lower() not in user_skills_lower]
        score = round((len(matched) / len(job["skills"])) * 100)
        results.append({
            "title": job["title"],
            "match_score": score,
            "matched_skills": matched,
            "missing_skills": missing,
            "total_required": len(job["skills"])
        })

    return sorted(results, key=lambda x: x["match_score"], reverse=True)