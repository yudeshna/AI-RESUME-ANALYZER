from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

JOBS_DATA = [
    {
        "title": "Data Scientist",
        "description": "Python Machine Learning Deep Learning Statistics SQL TensorFlow PyTorch Pandas NumPy Scikit-learn data analysis predictive modeling feature engineering A/B testing experimental design hypothesis testing regression classification clustering",
        "required_skills": ["Python", "Machine Learning", "Statistics", "SQL", "Pandas", "Scikit-learn"],
        "bonus_skills": ["Deep Learning", "TensorFlow", "PyTorch", "Spark", "Tableau"],
        "salary": "6-18 LPA",
        "companies": "Google, Amazon, Flipkart, Swiggy, CRED, Meesho"
    },
    {
        "title": "Data Analyst",
        "description": "SQL Excel Power BI Python Tableau Statistics Pandas data visualization reporting business intelligence dashboards KPIs metrics analysis storytelling stakeholder communication",
        "required_skills": ["SQL", "Excel", "Python", "Statistics", "Data Visualization"],
        "bonus_skills": ["Power BI", "Tableau", "Pandas", "Looker", "BigQuery"],
        "salary": "4-10 LPA",
        "companies": "Deloitte, Accenture, Infosys, TCS, Wipro, Razorpay"
    },
    {
        "title": "ML Engineer",
        "description": "Python Deep Learning TensorFlow PyTorch Docker Machine Learning MLOps model deployment production Kubernetes CI/CD API model serving feature store data pipelines monitoring",
        "required_skills": ["Python", "Machine Learning", "Deep Learning", "Docker", "CI/CD"],
        "bonus_skills": ["TensorFlow", "PyTorch", "Kubernetes", "MLflow", "Airflow"],
        "salary": "10-25 LPA",
        "companies": "Microsoft, Apple, Netflix, Uber, Razorpay, Sarvam AI"
    },
    {
        "title": "Frontend Developer",
        "description": "React JavaScript HTML CSS TypeScript Next.js Vue Angular Redux Tailwind CSS responsive design UI UX web performance accessibility webpack vite component libraries design systems",
        "required_skills": ["React", "JavaScript", "HTML", "CSS", "TypeScript"],
        "bonus_skills": ["Next.js", "Vue", "Redux", "Tailwind CSS", "GraphQL"],
        "salary": "5-16 LPA",
        "companies": "Zomato, Zepto, PhonePe, Paytm, Meesho, Groww"
    },
    {
        "title": "Backend Developer",
        "description": "Python Java Node.js SQL REST API Docker MongoDB PostgreSQL microservices server database API development authentication authorization system design caching Redis message queues",
        "required_skills": ["Python", "SQL", "REST API", "MongoDB", "PostgreSQL"],
        "bonus_skills": ["Docker", "Redis", "Kafka", "Microservices", "Java"],
        "salary": "6-18 LPA",
        "companies": "Atlassian, Freshworks, Zoho, Postman, BrowserStack"
    },
    {
        "title": "Full Stack Developer",
        "description": "React Node.js JavaScript TypeScript SQL MongoDB PostgreSQL Python Docker full stack web application frontend backend REST API GraphQL CI/CD Next.js responsive design",
        "required_skills": ["React", "Node.js", "JavaScript", "SQL", "MongoDB"],
        "bonus_skills": ["TypeScript", "Python", "Docker", "GraphQL", "Next.js"],
        "salary": "8-20 LPA",
        "companies": "Spotify, LinkedIn, Notion, Figma, Vercel, Supabase"
    },
    {
        "title": "DevOps Engineer",
        "description": "Docker Kubernetes CI/CD AWS Linux Python Jenkins Terraform Ansible infrastructure automation cloud deployment pipeline monitoring Prometheus Grafana GitOps Helm Nginx",
        "required_skills": ["Docker", "Kubernetes", "CI/CD", "AWS", "Linux"],
        "bonus_skills": ["Terraform", "Ansible", "Prometheus", "Python", "Helm"],
        "salary": "10-22 LPA",
        "companies": "Red Hat, HashiCorp, Cloudflare, Datadog, PagerDuty"
    },
    {
        "title": "Cloud Architect",
        "description": "AWS Azure GCP Docker Kubernetes Python Terraform cloud infrastructure architecture scalability high availability disaster recovery networking security IAM cost optimization multi-cloud hybrid cloud",
        "required_skills": ["AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform"],
        "bonus_skills": ["Python", "Networking", "Security", "IAM"],
        "salary": "18-40 LPA",
        "companies": "Amazon, Microsoft, Google, IBM, Oracle, Deloitte"
    },
    {
        "title": "Data Engineer",
        "description": "Python SQL Spark PySpark Hadoop AWS Pandas data pipeline ETL big data warehouse Airflow Kafka dbt Snowflake BigQuery Redshift Databricks streaming batch processing",
        "required_skills": ["Python", "SQL", "Spark", "AWS", "ETL", "Airflow"],
        "bonus_skills": ["Kafka", "dbt", "Snowflake", "BigQuery", "Databricks"],
        "salary": "8-20 LPA",
        "companies": "Databricks, Snowflake, Confluent, dbt Labs, Fivetran"
    },
    {
        "title": "AI Research Scientist",
        "description": "Python Deep Learning NLP TensorFlow PyTorch Statistics research papers computer vision transformers LLM BERT GPT reinforcement learning optimization mathematics linear algebra probability",
        "required_skills": ["Python", "Deep Learning", "NLP", "PyTorch", "Statistics", "Mathematics"],
        "bonus_skills": ["TensorFlow", "Transformers", "BERT", "Reinforcement Learning"],
        "salary": "15-50 LPA",
        "companies": "OpenAI, DeepMind, Anthropic, Meta AI, Google Brain, IIT Labs"
    },
    {
        "title": "NLP Engineer",
        "description": "Python NLP transformers BERT GPT Hugging Face spaCy NLTK text classification sentiment analysis language models LLM RAG fine-tuning embeddings vector database Pinecone",
        "required_skills": ["Python", "NLP", "Hugging Face", "Transformers", "Machine Learning"],
        "bonus_skills": ["LLM", "RAG", "spaCy", "Vector Database", "PyTorch"],
        "salary": "10-25 LPA",
        "companies": "Sarvam AI, Krutrim, CoRover, Vernacular.ai, Observe.AI"
    },
    {
        "title": "Business Analyst",
        "description": "SQL Excel Power BI Tableau Statistics communication project management Agile Scrum requirements analysis stakeholder management user stories process mapping BPMN Jira documentation",
        "required_skills": ["SQL", "Excel", "Communication", "Agile", "Jira"],
        "bonus_skills": ["Power BI", "Tableau", "Statistics", "Python", "Confluence"],
        "salary": "5-14 LPA",
        "companies": "McKinsey, BCG, Bain, KPMG, PwC, EY"
    },
    {
        "title": "Product Manager",
        "description": "Product management roadmap OKRs KPIs Agile Scrum user research A/B testing analytics SQL communication leadership stakeholder management prioritization go-to-market strategy Jira Figma",
        "required_skills": ["Product Management", "Agile", "Communication", "SQL", "Leadership"],
        "bonus_skills": ["A/B Testing", "Figma", "Data Analysis", "Jira", "User Research"],
        "salary": "12-30 LPA",
        "companies": "Google, Amazon, Flipkart, Razorpay, CRED, Zepto"
    },
    {
        "title": "Mobile Developer (Android/iOS)",
        "description": "Android iOS React Native Flutter Kotlin Swift Java mobile application development UI UX REST API Firebase push notifications app store deployment Jetpack Compose SwiftUI",
        "required_skills": ["Android", "Kotlin", "Swift", "iOS", "REST API"],
        "bonus_skills": ["React Native", "Flutter", "Firebase", "Java"],
        "salary": "6-18 LPA",
        "companies": "PhonePe, Paytm, Dream11, CRED, Swiggy, Zomato"
    },
    {
        "title": "Cybersecurity Analyst",
        "description": "Cybersecurity network security penetration testing ethical hacking OWASP SSL TLS cryptography firewalls vulnerability assessment incident response SIEM SOC compliance Python Linux",
        "required_skills": ["Cybersecurity", "Network Security", "Linux", "Python"],
        "bonus_skills": ["Penetration Testing", "Ethical Hacking", "SIEM", "OWASP"],
        "salary": "6-18 LPA",
        "companies": "Wipro, TCS, HCL, Palo Alto Networks, Crowdstrike"
    },
    {
        "title": "Software Development Engineer (SDE)",
        "description": "Java Python C++ JavaScript data structures algorithms system design OOP design patterns REST API SQL Git Linux problem solving LeetCode competitive programming scalability",
        "required_skills": ["Java", "Python", "Data Structures", "Algorithms", "SQL", "Git"],
        "bonus_skills": ["System Design", "C++", "JavaScript", "Microservices"],
        "salary": "8-25 LPA",
        "companies": "Google, Amazon, Microsoft, Flipkart, Atlassian, Oracle"
    },
    {
        "title": "Generative AI Engineer",
        "description": "Python LLM GPT Claude Gemini RAG Hugging Face LangChain prompt engineering vector database Pinecone ChromaDB fine-tuning embeddings AI agents OpenAI API function calling",
        "required_skills": ["Python", "LLM", "RAG", "Hugging Face", "Prompt Engineering"],
        "bonus_skills": ["LangChain", "Vector Database", "Fine-tuning", "OpenAI API"],
        "salary": "15-40 LPA",
        "companies": "OpenAI, Anthropic, Google, Sarvam AI, Krutrim, startups"
    },
    {
        "title": "Site Reliability Engineer (SRE)",
        "description": "Linux Python Go Kubernetes Docker CI/CD monitoring Prometheus Grafana Datadog SLO SLA incident management reliability performance optimization distributed systems scalability",
        "required_skills": ["Linux", "Python", "Kubernetes", "Docker", "Monitoring"],
        "bonus_skills": ["Go", "Prometheus", "Grafana", "CI/CD", "Datadog"],
        "salary": "12-28 LPA",
        "companies": "Google, Uber, Airbnb, Stripe, Cloudflare"
    },
    {
        "title": "UI/UX Designer",
        "description": "Figma Adobe XD UI design UX research wireframing prototyping user testing design systems HTML CSS responsive design accessibility usability Sketch interaction design",
        "required_skills": ["Figma", "UI Design", "UX Research", "Prototyping"],
        "bonus_skills": ["Adobe XD", "HTML", "CSS", "User Testing", "Design Systems"],
        "salary": "5-16 LPA",
        "companies": "Zomato, Swiggy, PhonePe, Razorpay, Groww, startups"
    },
    {
        "title": "Blockchain Developer",
        "description": "Solidity Ethereum Web3 JavaScript TypeScript smart contracts DeFi NFT blockchain Hardhat Truffle React Node.js cryptography consensus mechanisms distributed ledger",
        "required_skills": ["Solidity", "Web3", "JavaScript", "Smart Contracts", "Ethereum"],
        "bonus_skills": ["React", "Node.js", "TypeScript", "DeFi", "Cryptography"],
        "salary": "10-30 LPA",
        "companies": "CoinDCX, WazirX, Polygon, startups, Web3 companies"
    },
]


def smart_job_match(resume_text, n_results=5):
    """
    Skill-based job matching:
    - Primary: exact required skill match percentage
    - Secondary: bonus skill match
    - Tertiary: TF-IDF for context
    Score = directly reflects how many required skills the user has
    """
    resume_lower = resume_text.lower()

    # ── Step 1: Pure skill overlap (main score driver) ────────────────────────
    def calc_skill_score(job):
        required = job["required_skills"]
        bonus    = job.get("bonus_skills", [])

        req_found   = [s for s in required if s.lower() in resume_lower]
        bonus_found = [s for s in bonus    if s.lower() in resume_lower]

        req_pct   = len(req_found)   / max(len(required), 1)   # 0.0 - 1.0
        bonus_pct = len(bonus_found) / max(len(bonus), 1)       # 0.0 - 1.0

        # Weight: 80% required skills, 20% bonus skills
        return (req_pct * 0.80) + (bonus_pct * 0.20), req_found, bonus_found

    # ── Step 2: TF-IDF for context boost ──────────────────────────────────────
    job_descriptions = [job["description"] for job in JOBS_DATA]
    all_docs = [resume_text] + job_descriptions
    vectorizer = TfidfVectorizer(
        stop_words="english", ngram_range=(1, 2),
        min_df=1, max_features=5000, sublinear_tf=True
    )
    tfidf_matrix  = vectorizer.fit_transform(all_docs)
    tfidf_scores  = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1:])[0]
    # Normalize TF-IDF to 0-1
    max_tfidf = max(tfidf_scores) if max(tfidf_scores) > 0 else 1
    tfidf_norm = tfidf_scores / max_tfidf

    # ── Step 3: Final score = 75% skill + 25% tfidf ───────────────────────────
    matched_jobs = []
    for i, job in enumerate(JOBS_DATA):
        skill_score, req_found, bonus_found = calc_skill_score(job)
        final_raw = (skill_score * 0.75) + (tfidf_norm[i] * 0.25)

        # Convert to percentage directly — no artificial scaling
        pct = int(final_raw * 100)
        pct = max(3, min(99, pct))

        matched_jobs.append({
            "title":            job["title"],
            "similarity_score": pct,
            "match_score":      pct,
            "salary":           job["salary"],
            "companies":        job["companies"],
            "required_skills":  job["required_skills"],
            "skills_matched":   req_found,
            "skills_missing":   [s for s in job["required_skills"] if s.lower() not in resume_lower],
        })

    results = sorted(matched_jobs, key=lambda x: x["similarity_score"], reverse=True)
    return results[:n_results]