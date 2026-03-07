import chromadb
from chromadb.utils import embedding_functions

# Jobs database with detailed descriptions
JOBS_DATA = [
    {
        "id": "job_1",
        "title": "Data Scientist",
        "description": "Python Machine Learning Deep Learning Statistics SQL TensorFlow Pandas NumPy data analysis predictive modeling",
        "skills": ["Python","Machine Learning","Statistics","Deep Learning","SQL","TensorFlow","Pandas"],
        "salary": "6-15 LPA",
        "companies": ["Google","Amazon","Flipkart","Swiggy","CRED"]
    },
    {
        "id": "job_2",
        "title": "Data Analyst",
        "description": "SQL Excel Power BI Python Tableau Statistics Pandas data visualization reporting business intelligence",
        "skills": ["SQL","Excel","Power BI","Python","Tableau","Statistics","Pandas"],
        "salary": "4-10 LPA",
        "companies": ["Deloitte","Accenture","Infosys","TCS","Wipro"]
    },
    {
        "id": "job_3",
        "title": "ML Engineer",
        "description": "Python Deep Learning TensorFlow PyTorch Docker Machine Learning MLOps model deployment production",
        "skills": ["Python","Deep Learning","TensorFlow","PyTorch","Docker","Machine Learning"],
        "salary": "8-20 LPA",
        "companies": ["Microsoft","Apple","Netflix","Uber","Razorpay"]
    },
    {
        "id": "job_4",
        "title": "Frontend Developer",
        "description": "React JavaScript HTML CSS TypeScript Vue Angular UI UX web development responsive design",
        "skills": ["React","JavaScript","HTML","CSS","TypeScript","Vue"],
        "salary": "5-14 LPA",
        "companies": ["Zomato","Zepto","PhonePe","Paytm","Meesho"]
    },
    {
        "id": "job_5",
        "title": "Backend Developer",
        "description": "Python Java Node.js SQL REST API Docker MongoDB microservices server database API development",
        "skills": ["Python","Java","Node.js","SQL","REST API","Docker","MongoDB"],
        "salary": "6-16 LPA",
        "companies": ["Atlassian","Freshworks","Zoho","Postman","BrowserStack"]
    },
    {
        "id": "job_6",
        "title": "Full Stack Developer",
        "description": "React Node.js JavaScript SQL MongoDB Python Docker full stack web application frontend backend",
        "skills": ["React","Node.js","JavaScript","SQL","MongoDB","Python","Docker"],
        "salary": "7-18 LPA",
        "companies": ["Spotify","LinkedIn","Twitter","Airbnb","Notion"]
    },
    {
        "id": "job_7",
        "title": "DevOps Engineer",
        "description": "Docker Kubernetes CI/CD AWS Linux Python Jenkins infrastructure automation cloud deployment pipeline",
        "skills": ["Docker","Kubernetes","CI/CD","AWS","Linux","Python","Jenkins"],
        "salary": "8-20 LPA",
        "companies": ["Red Hat","HashiCorp","Cloudflare","Datadog","PagerDuty"]
    },
    {
        "id": "job_8",
        "title": "Cloud Architect",
        "description": "AWS Azure GCP Docker Kubernetes Python Terraform cloud infrastructure architecture scalability",
        "skills": ["AWS","Azure","GCP","Docker","Kubernetes","Python","Terraform"],
        "salary": "15-35 LPA",
        "companies": ["Amazon","Microsoft","Google","IBM","Oracle"]
    },
    {
        "id": "job_9",
        "title": "Data Engineer",
        "description": "Python SQL Spark Hadoop AWS Pandas data pipeline ETL big data warehouse Airflow Kafka",
        "skills": ["Python","SQL","Spark","Hadoop","AWS","Pandas"],
        "salary": "8-18 LPA",
        "companies": ["Databricks","Snowflake","Confluent","dbt Labs","Fivetran"]
    },
    {
        "id": "job_10",
        "title": "AI Research Scientist",
        "description": "Python Deep Learning NLP TensorFlow PyTorch Statistics research papers computer vision transformers LLM",
        "skills": ["Python","Deep Learning","NLP","TensorFlow","PyTorch","Statistics"],
        "salary": "12-40 LPA",
        "companies": ["OpenAI","DeepMind","Anthropic","Meta AI","Google Brain"]
    },
    {
        "id": "job_11",
        "title": "NLP Engineer",
        "description": "Python NLP transformers BERT GPT spaCy NLTK text classification sentiment analysis language models",
        "skills": ["Python","NLP","Machine Learning","Deep Learning","spaCy","TensorFlow"],
        "salary": "8-22 LPA",
        "companies": ["Sarvam AI","Krutrim","CoRover","Vernacular.ai","Observe.AI"]
    },
    {
        "id": "job_12",
        "title": "Business Analyst",
        "description": "SQL Excel Power BI Tableau Statistics communication project management Agile Scrum requirements analysis",
        "skills": ["SQL","Excel","Power BI","Tableau","Statistics","Communication","Agile"],
        "salary": "5-12 LPA",
        "companies": ["McKinsey","BCG","Bain","KPMG","PwC"]
    },
]


def setup_chroma():
    """Setup ChromaDB collection with job data"""
    # ✅ FIXED: embedding_fn initialized INSIDE function, not at module level
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    chroma_client = chromadb.Client()

    try:
        chroma_client.delete_collection("jobs")
    except:
        pass

    collection = chroma_client.create_collection(
        name="jobs",
        embedding_function=embedding_fn
    )

    documents = [job["description"] for job in JOBS_DATA]
    ids = [job["id"] for job in JOBS_DATA]
    metadatas = [
        {
            "title": job["title"],
            "salary": job["salary"],
            "companies": ", ".join(job["companies"]),
            "skills": ", ".join(job["skills"])
        }
        for job in JOBS_DATA
    ]

    collection.add(
        documents=documents,
        ids=ids,
        metadatas=metadatas
    )
    return collection


def smart_job_match(resume_text, n_results=5):
    """Use ChromaDB vector search to find best job matches"""
    collection = setup_chroma()

    results = collection.query(
        query_texts=[resume_text],
        n_results=n_results
    )

    matched_jobs = []
    for i in range(len(results['ids'][0])):
        job_id = results['ids'][0][i]
        metadata = results['metadatas'][0][i]
        distance = results['distances'][0][i]

        # Convert distance to similarity score (0-100)
        similarity = round((1 - distance) * 100)
        similarity = max(0, min(100, similarity))

        matched_jobs.append({
            "title": metadata["title"],
            "similarity_score": similarity,
            "salary": metadata["salary"],
            "companies": metadata["companies"],
            "required_skills": metadata["skills"].split(", ")
        })

    return sorted(matched_jobs, key=lambda x: x["similarity_score"], reverse=True)