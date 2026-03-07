from firebase_config import db

# Create sample data
doc_ref = db.collection("users").document("test_user")

doc_ref.set({
    "name": "Test User",
    "email": "test@email.com",
    "job_target": "Data Scientist"
})

print("Firebase connection successful!")