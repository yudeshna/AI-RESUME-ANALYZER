import spacy

nlp = spacy.load("en_core_web_sm")

SKILLS_LIST = [
    # Programming Languages
    "Python", "Java", "JavaScript", "C++", "C#", "R", "SQL",
    "TypeScript", "Go", "Scala", "MATLAB", "PHP", "Swift", "Kotlin",
    # AI / ML
    "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
    "TensorFlow", "PyTorch", "Keras", "Scikit-learn", "OpenCV",
    "Reinforcement Learning", "Statistics", "Data Science",
    # Web
    "React", "Vue", "Angular", "Node.js", "HTML", "CSS",
    "Django", "Flask", "FastAPI", "REST API", "GraphQL",
    # Data
    "Pandas", "NumPy", "Matplotlib", "Seaborn", "Power BI",
    "Tableau", "Excel", "Spark", "Hadoop", "Elasticsearch",
    # Cloud / DevOps
    "AWS", "Azure", "GCP", "Docker", "Kubernetes",
    "CI/CD", "Jenkins", "Terraform", "Linux", "Git",
    # Databases
    "MongoDB", "PostgreSQL", "MySQL", "Redis", "ChromaDB",
    # Soft Skills
    "Communication", "Leadership", "Teamwork",
    "Project Management", "Agile", "Scrum",
]

def extract_skills(text):
    found_skills = []
    text_lower = text.lower()
    for skill in SKILLS_LIST:
        if skill.lower() in text_lower:
            found_skills.append(skill)
    return list(set(found_skills))

def get_skill_categories(skills):
    categories = {
        "Programming": ["Python","Java","JavaScript","C++","C#","R","SQL",
                        "TypeScript","Go","Scala","MATLAB","PHP"],
        "AI / ML": ["Machine Learning","Deep Learning","NLP","Computer Vision",
                    "TensorFlow","PyTorch","Keras","Scikit-learn","Statistics"],
        "Web Dev": ["React","Vue","Angular","Node.js","HTML","CSS",
                    "Django","Flask","FastAPI"],
        "Data & BI": ["Pandas","NumPy","Power BI","Tableau","Excel","Spark"],
        "Cloud & DevOps": ["AWS","Azure","GCP","Docker","Kubernetes","Linux","Git"],
        "Databases": ["MongoDB","PostgreSQL","MySQL","Redis","ChromaDB"],
    }
    result = {}
    for category, cat_skills in categories.items():
        matched = [s for s in skills if s in cat_skills]
        if matched:
            result[category] = matched
    return result