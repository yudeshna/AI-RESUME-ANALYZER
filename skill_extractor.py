import re

# ── Comprehensive skills list (300+ skills) ──────────────────────────────────
SKILLS_LIST = [
    # Programming Languages
    "Python", "Java", "JavaScript", "C++", "C#", "C", "R", "SQL", "TypeScript",
    "Go", "Golang", "Scala", "MATLAB", "PHP", "Swift", "Kotlin", "Rust", "Ruby",
    "Perl", "Shell", "Bash", "PowerShell", "COBOL", "Fortran", "Haskell",
    "Lua", "Dart", "Elixir", "Julia", "Assembly",

    # AI / ML / DL
    "Machine Learning", "Deep Learning", "NLP", "Natural Language Processing",
    "Computer Vision", "TensorFlow", "PyTorch", "Keras", "Scikit-learn",
    "Scikit learn", "OpenCV", "Reinforcement Learning", "Statistics",
    "Data Science", "Hugging Face", "Transformers", "BERT", "GPT",
    "LLM", "Large Language Models", "RAG", "Retrieval Augmented Generation",
    "XGBoost", "LightGBM", "CatBoost", "Random Forest", "SVM",
    "Neural Networks", "CNN", "RNN", "LSTM", "GAN", "Diffusion Models",
    "Feature Engineering", "Hyperparameter Tuning", "Model Deployment",
    "MLOps", "Weights & Biases", "MLflow", "Kubeflow", "AutoML",
    "spaCy", "NLTK", "Gensim", "FastText", "Word2Vec",

    # Web Development - Frontend
    "React", "React.js", "ReactJS", "Vue", "Vue.js", "VueJS",
    "Angular", "AngularJS", "Next.js", "NextJS", "Nuxt.js",
    "HTML", "HTML5", "CSS", "CSS3", "JavaScript", "TypeScript",
    "Tailwind CSS", "Bootstrap", "Material UI", "Sass", "SCSS",
    "Webpack", "Vite", "Redux", "Zustand", "jQuery", "Svelte",
    "Web3", "Three.js", "D3.js", "Chart.js", "Figma", "Adobe XD",

    # Web Development - Backend
    "Node.js", "NodeJS", "Express.js", "ExpressJS", "Django", "Flask",
    "FastAPI", "Spring Boot", "Spring", "Laravel", "Ruby on Rails",
    "ASP.NET", ".NET", "REST API", "RESTful API", "GraphQL",
    "gRPC", "WebSocket", "Microservices", "API Development",
    "OAuth", "JWT", "Authentication", "Authorization",

    # Data & Analytics
    "Pandas", "NumPy", "Matplotlib", "Seaborn", "Plotly",
    "Power BI", "Tableau", "Excel", "Google Sheets", "Looker",
    "Metabase", "Spark", "PySpark", "Hadoop", "Hive",
    "Elasticsearch", "Kibana", "Grafana", "Airflow", "Kafka",
    "dbt", "Snowflake", "BigQuery", "Redshift", "Databricks",
    "Data Visualization", "Business Intelligence", "ETL", "Data Pipeline",
    "Data Warehousing", "Data Modeling", "A/B Testing", "Statistical Analysis",
    "R Studio", "Jupyter", "Jupyter Notebook",

    # Cloud & Infrastructure
    "AWS", "Amazon Web Services", "Azure", "Microsoft Azure",
    "GCP", "Google Cloud", "Google Cloud Platform",
    "Docker", "Kubernetes", "K8s", "Terraform", "Ansible",
    "CI/CD", "Jenkins", "GitHub Actions", "GitLab CI",
    "Linux", "Unix", "Nginx", "Apache", "Serverless",
    "Lambda", "EC2", "S3", "CloudFormation", "IAM",
    "Load Balancing", "Auto Scaling", "VPC", "Networking",
    "Infrastructure as Code", "IaC", "Helm", "Istio",

    # Databases
    "MongoDB", "PostgreSQL", "MySQL", "SQLite", "Redis",
    "Cassandra", "DynamoDB", "Firebase", "Firestore",
    "Neo4j", "Oracle", "SQL Server", "MariaDB",
    "ChromaDB", "Pinecone", "Weaviate", "Vector Database",
    "Database Design", "Database Administration", "Query Optimization",
    "ORM", "SQLAlchemy", "Prisma", "Sequelize",

    # DevOps & Tools
    "Git", "GitHub", "GitLab", "Bitbucket", "Jira",
    "Confluence", "Postman", "Swagger", "OpenAPI",
    "Prometheus", "Datadog", "New Relic", "Splunk",
    "SonarQube", "Selenium", "Cypress", "Jest", "PyTest",
    "Unit Testing", "Integration Testing", "TDD", "BDD",
    "Agile", "Scrum", "Kanban", "Sprint Planning",

    # Mobile Development
    "Android", "iOS", "React Native", "Flutter", "Xamarin",
    "Swift", "Kotlin", "Objective-C", "Ionic", "Cordova",

    # Cybersecurity
    "Cybersecurity", "Network Security", "Penetration Testing",
    "Ethical Hacking", "OWASP", "SSL/TLS", "Cryptography",
    "Firewalls", "IDS/IPS", "SIEM", "SOC", "Vulnerability Assessment",

    # Product & Management
    "Product Management", "Project Management", "Agile", "Scrum",
    "PMP", "PRINCE2", "Risk Management", "Stakeholder Management",
    "Roadmap Planning", "OKRs", "KPIs", "Business Analysis",
    "Requirements Gathering", "User Stories",

    # Soft Skills
    "Communication", "Leadership", "Teamwork", "Problem Solving",
    "Critical Thinking", "Time Management", "Presentation Skills",
    "Technical Writing", "Mentoring", "Cross-functional Collaboration",
]

# ── Alias/variant mapping for fuzzy matching ──────────────────────────────────
SKILL_ALIASES = {
    "ml": "Machine Learning",
    "dl": "Deep Learning",
    "ai": "Machine Learning",
    "nlp": "NLP",
    "cv": "Computer Vision",
    "react.js": "React",
    "reactjs": "React",
    "vue.js": "Vue",
    "vuejs": "Vue",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "next.js": "Next.js",
    "nextjs": "Next.js",
    "angular.js": "Angular",
    "angularjs": "Angular",
    "sklearn": "Scikit-learn",
    "scikit learn": "Scikit-learn",
    "scikit-learn": "Scikit-learn",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "mongo": "MongoDB",
    "mongodb": "MongoDB",
    "aws": "AWS",
    "amazon web services": "AWS",
    "gcp": "GCP",
    "google cloud": "GCP",
    "azure": "Azure",
    "microsoft azure": "Azure",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "pyspark": "Spark",
    "apache spark": "Spark",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "continuous integration": "CI/CD",
    "rest api": "REST API",
    "restful": "REST API",
    "restful api": "REST API",
    "large language model": "LLM",
    "llm": "LLM",
    "llms": "LLM",
    "huggingface": "Hugging Face",
    "hugging face": "Hugging Face",
    "jupyter notebook": "Jupyter",
    "power bi": "Power BI",
    "powerbi": "Power BI",
    "ms excel": "Excel",
    "microsoft excel": "Excel",
    "git hub": "GitHub",
    "flask api": "Flask",
    "fast api": "FastAPI",
    "spring boot": "Spring Boot",
    "dot net": ".NET",
    "asp.net": "ASP.NET",
    "html5": "HTML",
    "css3": "CSS",
    "tailwind": "Tailwind CSS",
    "material ui": "Material UI",
    "mui": "Material UI",
    "word2vec": "Word2Vec",
    "xgboost": "XGBoost",
    "lightgbm": "LightGBM",
    "random forest": "Random Forest",
    "neural network": "Neural Networks",
    "convolutional neural": "CNN",
    "recurrent neural": "RNN",
    "long short": "LSTM",
    "generative adversarial": "GAN",
    "data viz": "Data Visualization",
    "bi": "Business Intelligence",
    "github actions": "GitHub Actions",
    "iac": "Infrastructure as Code",
    "tdd": "TDD",
    "bdd": "BDD",
    "mlops": "MLOps",
    "rag": "RAG",
}


def extract_skills(text):
    """Extract skills using exact match + alias mapping + word boundary matching"""
    found = set()
    text_lower = text.lower()

    # 1. Exact match from SKILLS_LIST (word-boundary aware)
    for skill in SKILLS_LIST:
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found.add(skill)

    # 2. Alias matching
    for alias, canonical in SKILL_ALIASES.items():
        pattern = r'\b' + re.escape(alias.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found.add(canonical)

    # 3. Remove duplicates where canonical already found
    # (e.g. if both "React" and "React.js" found, keep canonical "React")
    deduped = set()
    canonical_values = set(SKILL_ALIASES.values())
    for skill in found:
        if skill in canonical_values or skill not in [
            s for s in found if s != skill and skill.lower() in s.lower()
        ]:
            deduped.add(skill)

    return sorted(list(deduped))


def get_skill_categories(skills):
    """Categorize skills into groups"""
    categories = {
        "Programming": [
            "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "C",
            "R", "SQL", "Go", "Golang", "Scala", "PHP", "Swift", "Kotlin",
            "Rust", "Ruby", "Bash", "Shell", "Dart", "Julia", "MATLAB"
        ],
        "AI / ML": [
            "Machine Learning", "Deep Learning", "NLP", "Natural Language Processing",
            "Computer Vision", "TensorFlow", "PyTorch", "Keras", "Scikit-learn",
            "OpenCV", "Reinforcement Learning", "Statistics", "Data Science",
            "Hugging Face", "Transformers", "BERT", "GPT", "LLM", "RAG",
            "XGBoost", "LightGBM", "Random Forest", "SVM", "Neural Networks",
            "CNN", "RNN", "LSTM", "GAN", "MLOps", "spaCy", "NLTK", "AutoML"
        ],
        "Web Dev": [
            "React", "Vue", "Angular", "Next.js", "Node.js", "Django", "Flask",
            "FastAPI", "Spring Boot", "HTML", "CSS", "Tailwind CSS", "Bootstrap",
            "REST API", "GraphQL", "Express.js", "Laravel", "ASP.NET",
            "Redux", "Material UI", "Svelte", "WebSocket", "Microservices"
        ],
        "Data & BI": [
            "Pandas", "NumPy", "Matplotlib", "Seaborn", "Plotly",
            "Power BI", "Tableau", "Excel", "Looker", "Spark", "PySpark",
            "Hadoop", "Hive", "Airflow", "Kafka", "dbt", "Snowflake",
            "BigQuery", "Redshift", "Databricks", "ETL", "Data Visualization",
            "Business Intelligence", "A/B Testing", "Statistical Analysis"
        ],
        "Cloud & DevOps": [
            "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform",
            "Ansible", "CI/CD", "Jenkins", "GitHub Actions", "Linux",
            "Nginx", "Serverless", "Infrastructure as Code", "Helm",
            "Lambda", "EC2", "S3", "Load Balancing", "Networking"
        ],
        "Databases": [
            "MongoDB", "PostgreSQL", "MySQL", "Redis", "Cassandra",
            "DynamoDB", "Firebase", "Firestore", "Neo4j", "Oracle",
            "SQL Server", "ChromaDB", "Pinecone", "Vector Database",
            "Database Design", "SQLAlchemy"
        ],
        "Mobile": [
            "Android", "iOS", "React Native", "Flutter", "Swift",
            "Kotlin", "Xamarin", "Ionic"
        ],
        "Tools & PM": [
            "Git", "GitHub", "GitLab", "Jira", "Confluence", "Postman",
            "Swagger", "Selenium", "Jest", "PyTest", "Agile", "Scrum",
            "Kanban", "Product Management", "Project Management", "TDD"
        ],
    }

    result = {}
    skills_set = set(skills)
    for category, cat_skills in categories.items():
        matched = [s for s in cat_skills if s in skills_set]
        if matched:
            result[category] = matched
    return result
