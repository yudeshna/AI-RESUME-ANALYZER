from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

JOBS_DATA = [
    {"title": "Data Scientist", "description": "Python Machine Learning Deep Learning Statistics SQL TensorFlow Pandas NumPy", "skills": ["Python","Machine Learning","Statistics","Deep Learning","SQL","TensorFlow","Pandas"], "salary": "6-15 LPA", "companies": ["Google","Amazon","Flipkart"]},
    {"title": "Data Analyst", "description": "SQL Excel Power BI Python Tableau Statistics Pandas data visualization", "skills": ["SQL","Excel","Power BI","Python","Tableau","Statistics"], "salary": "4-10 LPA", "companies": ["Deloitte","Accenture","Infosys"]},
    {"title": "ML Engineer", "description": "Python Deep Learning TensorFlow PyTorch Docker Machine Learning MLOps", "skills": ["Python","Deep Learning","TensorFlow","PyTorch","Docker","Machine Learning"], "salary": "8-20 LPA", "companies": ["Microsoft","Apple","Netflix"]},
    {"title": "Frontend Developer", "description": "React JavaScript HTML CSS TypeScript Vue Angular UI UX web development", "skills": ["React","JavaScript","HTML","CSS","TypeScript","Vue"], "salary": "5-14 LPA", "companies": ["Zomato","PhonePe","Paytm"]},
    {"title": "Backend Developer", "description": "Python Java Node.js SQL REST API Docker MongoDB microservices", "skills": ["Python","Java","Node.js","SQL","REST API","Docker","MongoDB"], "salary": "6-16 LPA", "companies": ["Atlassian","Freshworks","Zoho"]},
    {"title": "Full Stack Developer", "description": "React Node.js JavaScript SQL MongoDB Python Docker full stack", "skills": ["React","Node.js","JavaScript","SQL","MongoDB","Python","Docker"], "salary": "7-18 LPA", "companies": ["Spotify","LinkedIn","Airbnb"]},
    {"title": "DevOps Engineer", "description": "Docker Kubernetes CI/CD AWS Linux Python Jenkins infrastructure automation", "skills": ["Docker","Kubernetes","CI/CD","AWS","Linux","Python","Jenkins"], "salary": "8-20 LPA", "companies": ["Red Hat","Cloudflare","Datadog"]},
    {"title": "Cloud Architect", "description": "AWS Azure GCP Docker Kubernetes Python Terraform cloud infrastructure", "skills": ["AWS","Azure","GCP","Docker","Kubernetes","Python","Terraform"], "salary": "15-35 LPA", "companies": ["Amazon","Microsoft","Google"]},
    {"title": "Data Engineer", "description": "Python SQL Spark Hadoop AWS Pandas data pipeline ETL Airflow Kafka", "skills": ["Python","SQL","Spark","Hadoop","AWS","Pandas"], "salary": "8-18 LPA", "companies": ["Databricks","Snowflake","Confluent"]},
    {"title": "AI Research Scientist", "description": "Python Deep Learning NLP TensorFlow PyTorch Statistics transformers LLM", "skills": ["Python","Deep Learning","NLP","TensorFlow","PyTorch","Statistics"], "salary": "12-40 LPA", "companies": ["OpenAI","DeepMind","Anthropic"]},
    {"title": "NLP Engineer", "description": "Python NLP transformers BERT GPT NLTK text classification sentiment analysis", "skills": ["Python","NLP","Machine Learning","Deep Learning","TensorFlow"], "salary": "8-22 LPA", "companies": ["Sarvam AI","Krutrim","Observe.AI"]},
    {"title": "Business Analyst", "description": "SQL Excel Power BI Tableau Statistics Agile Scrum project management", "skills": ["SQL","Excel","Power BI","Tableau","Statistics","Agile"], "salary": "5-12 LPA", "companies": ["McKinsey","BCG","KPMG"]},
]

def smart_job_match(resume_text, n_results=5):
    job_descriptions = [job["description"] for job in JOBS_DATA]
    all_docs = [resume_text] + job_descriptions
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(all_docs)
    similarities = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1:])[0]
    matched_jobs = []
    for i, job in enumerate(JOBS_DATA):
        similarity = max(0, min(100, round(float(similarities[i]) * 100)))
        matched_jobs.append({
            "title": job["title"],
            "similarity_score": similarity,
            "salary": job["salary"],
            "companies": ", ".join(job["companies"]),
            "required_skills": job["skills"]
        })
    return sorted(matched_jobs, key=lambda x: x["similarity_score"], reverse=True)[:n_results]