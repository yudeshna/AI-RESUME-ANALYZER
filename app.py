import streamlit as st
import tempfile
import os
import random
import smtplib
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import plotly.graph_objects as go
import plotly.express as px
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
from resume_parser import extract_text
from skill_extractor import extract_skills, get_skill_categories
from job_matcher import match_jobs
from ai_analyzer import (
    analyze_resume,
    generate_interview_questions,
    generate_skill_roadmap,
    improve_resume_line
)
from chroma_matcher import smart_job_match
from pdf_report import generate_pdf_report
from openai import OpenAI

# ─── Groq Client ───────────────────────────────────────────
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
)

# ─── Firebase Setup ────────────────────────────────────────
if not firebase_admin._apps:
    firebase_key = dict(st.secrets["firebase"])
    firebase_key["private_key"] = firebase_key["private_key"].replace("\\n", "\n")
    cred = credentials.Certificate(firebase_key)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ─── Email Config ──────────────────────────────────────────
SENDER_EMAIL    = "nandu19jul@gmail.com"
SENDER_PASSWORD = "geyc nypl ctnc xexm"

# ─── Page Config ───────────────────────────────────────────
st.set_page_config(
    page_title="AI Resume Analyzer Pro",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Global CSS ────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700;800&family=Inter:wght@300;400;500&display=swap');

* { font-family: 'Inter', sans-serif; }
h1,h2,h3,h4 { font-family: 'Space Grotesk', sans-serif; }

.stApp { background: #080c14; }

.login-logo {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.1rem; font-weight: 700; color: #00d4ff;
    letter-spacing: 2px; text-transform: uppercase;
    text-align: center; margin-bottom: 0.5rem;
}
.login-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.2rem; font-weight: 800;
    background: linear-gradient(135deg, #ffffff 0%, #00d4ff 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    text-align: center; line-height: 1.2; margin-bottom: 0.5rem;
}
.login-sub { text-align: center; color: #5a6478; font-size: 0.95rem; margin-bottom: 2rem; }
.otp-box {
    background: rgba(0,212,255,0.05); border: 1px solid rgba(0,212,255,0.2);
    border-radius: 16px; padding: 1.2rem; margin: 1rem 0; text-align: center;
}
.otp-box p { color: #8892a4; font-size: 0.88rem; margin: 0; }
.otp-box strong { color: #00d4ff; }
.profile-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.8rem; font-weight: 800; color: white; margin-bottom: 0.3rem;
    text-align: center;
}
.profile-sub { color: #5a6478; font-size: 0.95rem; text-align: center; }
.step-badge {
    display: inline-block;
    background: rgba(0,212,255,0.08); border: 1px solid rgba(0,212,255,0.2);
    color: #00d4ff; padding: 4px 16px; border-radius: 20px;
    font-size: 0.78rem; font-weight: 600; letter-spacing: 1px; text-transform: uppercase;
}
.welcome-card {
    background: linear-gradient(135deg, rgba(0,212,255,0.08), rgba(123,47,247,0.08));
    border: 1px solid rgba(0,212,255,0.15);
    border-radius: 16px; padding: 1.2rem; margin-bottom: 1rem; text-align: center;
}
.welcome-name { font-family:'Space Grotesk',sans-serif; font-size:1rem; font-weight:700; color:white; margin-bottom:0.2rem; }
.welcome-detail { color: #5a6478; font-size: 0.78rem; }
.welcome-email { color: #00d4ff; font-size: 0.75rem; margin-top: 0.3rem; }
.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.6rem; font-weight: 900;
    background: linear-gradient(90deg, #00d4ff, #7b2ff7);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    text-align: center; padding: 0.5rem 0;
}
.hero-sub { text-align: center; color: #5a6478; font-size: 1rem; margin-bottom: 1.5rem; }
.welcome-banner {
    background: linear-gradient(90deg, rgba(0,212,255,0.06), rgba(123,47,247,0.06));
    border: 1px solid rgba(0,212,255,0.12);
    border-radius: 12px; padding: 0.9rem 1.5rem;
    text-align: center; margin-bottom: 1.5rem;
    font-size: 1rem; color: #c0cce0;
}
.welcome-banner span { color: #00d4ff; font-weight: 700; }
.card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px; padding: 1.5rem; margin: 1rem 0;
}
.skill-tag {
    display: inline-block;
    background: rgba(0,212,255,0.07); border: 1px solid rgba(0,212,255,0.18);
    color: #00d4ff; padding: 4px 12px; border-radius: 20px; margin: 4px; font-size: 0.82rem;
}
.section-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.3rem; font-weight: 700; color: #00d4ff;
    margin: 1rem 0 0.5rem 0; border-left: 3px solid #7b2ff7; padding-left: 0.75rem;
}
.stButton > button {
    background: linear-gradient(90deg, #00d4ff, #7b2ff7);
    color: white; border: none; border-radius: 10px;
    padding: 0.6rem 2rem; font-weight: 600; font-size: 0.95rem; width: 100%;
}
.metric-card {
    background: rgba(255,255,255,0.03); border-radius: 12px; padding: 1rem;
    text-align: center; border: 1px solid rgba(255,255,255,0.07);
}
.chat-user {
    background: rgba(0,212,255,0.06); border: 1px solid rgba(0,212,255,0.18);
    border-radius: 12px; padding: 0.75rem 1rem; margin: 0.5rem 0; text-align: right;
}
.chat-ai {
    background: rgba(123,47,247,0.06); border: 1px solid rgba(123,47,247,0.18);
    border-radius: 12px; padding: 0.75rem 1rem; margin: 0.5rem 0;
}
@keyframes shake {
    0%,100%{transform:translateX(0)} 20%{transform:translateX(-10px) rotate(-3deg)}
    40%{transform:translateX(10px) rotate(3deg)} 60%{transform:translateX(-10px) rotate(-3deg)}
    80%{transform:translateX(10px) rotate(3deg)}
}
@keyframes pulse { 0%,100%{transform:scale(1);opacity:1} 50%{transform:scale(1.15);opacity:0.8} }
@keyframes bounce { 0%,100%{transform:translateY(0)} 30%{transform:translateY(-18px)} 60%{transform:translateY(-8px)} }
@keyframes explode {
    0%{transform:scale(0.3) rotate(0deg);opacity:0} 30%{transform:scale(2.5) rotate(-20deg);opacity:1}
    60%{transform:scale(1.8) rotate(15deg);opacity:1} 100%{transform:scale(2.2) rotate(-5deg);opacity:0.7}
}
@keyframes flyaway {
    0%{transform:translate(0,0) scale(1);opacity:1} 30%{transform:translate(-50px,-80px) scale(1.4);opacity:1}
    70%{transform:translate(60px,-200px) scale(0.5);opacity:0.5} 100%{transform:translate(-30px,-320px) scale(0);opacity:0}
}
@keyframes flyaway2 {
    0%{transform:translate(0,0) scale(1);opacity:1} 30%{transform:translate(60px,-70px) scale(1.3);opacity:1}
    70%{transform:translate(-40px,-210px) scale(0.4);opacity:0.4} 100%{transform:translate(40px,-330px) scale(0);opacity:0}
}
@keyframes flyaway3 {
    0%{transform:translate(0,0) scale(1);opacity:1} 100%{transform:translate(90px,-340px) scale(0);opacity:0}
}
.anim-shake  {display:inline-block;animation:shake   0.6s ease infinite}
.anim-pulse  {display:inline-block;animation:pulse   1.2s ease infinite}
.anim-bounce {display:inline-block;animation:bounce  1.0s ease infinite}
.anim-explode{display:inline-block;animation:explode 0.7s ease-out forwards}
.anim-fly1   {display:inline-block;animation:flyaway  1.3s ease-out forwards}
.anim-fly2   {display:inline-block;animation:flyaway2 1.5s ease-out 0.1s forwards}
.anim-fly3   {display:inline-block;animation:flyaway3 1.1s ease-out 0.2s forwards}
.banner-excellent {
    background:linear-gradient(90deg,#00ff88,#00d4ff); border-radius:14px;
    padding:1.2rem 2rem; text-align:center; font-size:1.5rem; font-weight:800;
    color:#080c14; margin:1rem 0; box-shadow:0 0 30px rgba(0,255,136,0.25);
}
.banner-medium {
    background:linear-gradient(90deg,#ffbb00,#ff8c00); border-radius:14px;
    padding:1.2rem 2rem; text-align:center; font-size:1.5rem; font-weight:800;
    color:#080c14; margin:1rem 0; box-shadow:0 0 30px rgba(255,187,0,0.25);
}
.banner-poor {
    background:linear-gradient(90deg,#ff4444,#ff0000); border-radius:14px;
    padding:1.2rem 2rem; text-align:center; font-size:1.5rem; font-weight:800;
    color:white; margin:1rem 0; box-shadow:0 0 30px rgba(255,68,68,0.25);
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════

def send_otp_email(receiver_email, otp):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "🔐 Your OTP — AI Resume Analyzer Pro"
        msg["From"]    = SENDER_EMAIL
        msg["To"]      = receiver_email
        html = f"""
        <div style="font-family:'Segoe UI',Arial,sans-serif;background:#080c14;padding:2.5rem;
                    border-radius:16px;max-width:500px;margin:auto;border:1px solid rgba(255,255,255,0.08);">
            <div style="text-align:center;margin-bottom:1.5rem;">
                <div style="font-size:2.5rem;margin-bottom:0.5rem;">🚀</div>
                <h2 style="color:#00d4ff;margin:0;font-size:1.4rem;font-weight:800;">AI Resume Analyzer Pro</h2>
                <p style="color:#5a6478;font-size:0.9rem;margin:0.3rem 0 0;">Your login verification code</p>
            </div>
            <div style="background:rgba(0,212,255,0.08);border:1px solid rgba(0,212,255,0.2);
                        border-radius:12px;padding:1.5rem 2rem;text-align:center;margin:1.5rem 0;">
                <p style="color:#8892a4;font-size:0.85rem;margin:0 0 0.5rem;">Your One-Time Password</p>
                <div style="font-size:2.8rem;font-weight:900;color:white;letter-spacing:12px;font-family:monospace;">{otp}</div>
            </div>
            <p style="color:#5a6478;font-size:0.8rem;text-align:center;margin:0;">
                ⏱️ Valid for 5 minutes &nbsp;·&nbsp; 🔒 Do not share this code
            </p>
        </div>
        """
        msg.attach(MIMEText(html, "html"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        return True
    except Exception as e:
        st.error(f"❌ Email error: {e}")
        return False


def get_user(email):
    doc = db.collection("users").document(email).get()
    return doc.to_dict() if doc.exists else None


def create_user(email, name, job_target, education, purpose):
    db.collection("users").document(email).set({
        "email": email, "name": name,
        "job_target": job_target, "education": education, "purpose": purpose
    })


# ══════════════════════════════════════════════════════════
# SESSION STATE INIT
# ══════════════════════════════════════════════════════════

for key, val in [("page","login"),("otp_sent",False),("otp_code",""),("otp_email",""),("user",None)]:
    if key not in st.session_state:
        st.session_state[key] = val


# ══════════════════════════════════════════════════════════
# PAGE: LOGIN
# ══════════════════════════════════════════════════════════

if st.session_state.page == "login":

    col_l, col_c, col_r = st.columns([1, 1.2, 1])
    with col_c:
        st.markdown("""
        <div style="height:40px"></div>
        <div style="text-align:center;margin-bottom:0.5rem;font-size:3rem;">🚀</div>
        <div class="login-logo">AI Resume Analyzer Pro</div>
        <div class="login-title">Your Career,<br/>Supercharged by AI</div>
        <div class="login-sub">Get your resume scored, matched to jobs,<br/>and interview-ready in under 60 seconds.</div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("##### 📧 Sign in with Email OTP")

        email_input = st.text_input("Email Address", placeholder="you@example.com",
                                     key="login_email", label_visibility="collapsed")

        if st.button("📨 Send OTP →", key="send_otp_btn"):
            if email_input.strip() and "@" in email_input and "." in email_input:
                with st.spinner("Sending secure OTP to your inbox..."):
                    otp = str(random.randint(100000, 999999))
                    if send_otp_email(email_input.strip(), otp):
                        st.session_state.otp_sent  = True
                        st.session_state.otp_code  = otp
                        st.session_state.otp_email = email_input.strip()
                        st.success(f"✅ OTP sent to **{email_input.strip()}**")
                    else:
                        st.error("❌ Failed to send OTP. Try again.")
            else:
                st.error("❌ Enter a valid email address.")

        if st.session_state.otp_sent:
            st.markdown(f"""
            <div class="otp-box">
                <p>OTP sent to <strong>{st.session_state.otp_email}</strong></p>
                <p style="margin-top:0.3rem;font-size:0.78rem;">Check inbox and spam folder</p>
            </div>
            """, unsafe_allow_html=True)

            otp_input = st.text_input("Enter 6-digit OTP", placeholder="e.g. 482910",
                                       max_chars=6, key="otp_input", label_visibility="collapsed")

            col_v, col_rs = st.columns(2)
            with col_v:
                if st.button("✅ Verify & Login", key="verify_btn"):
                    if otp_input.strip() == st.session_state.otp_code:
                        email = st.session_state.otp_email
                        user_data = get_user(email)
                        st.session_state.otp_sent = False
                        st.session_state.otp_code = ""
                        if user_data:
                            st.session_state.user = user_data
                            st.session_state.page = "app"
                        else:
                            st.session_state.page = "profile"
                        st.rerun()
                    else:
                        st.error("❌ Wrong OTP. Try again.")
            with col_rs:
                if st.button("🔄 Resend OTP", key="resend_btn"):
                    otp = str(random.randint(100000, 999999))
                    if send_otp_email(st.session_state.otp_email, otp):
                        st.session_state.otp_code = otp
                        st.success("✅ New OTP sent!")

        st.markdown("""
        <div style="text-align:center;margin-top:2rem;color:#2a3040;font-size:0.8rem;">
            🔒 Secure login · No password needed · Free to use
        </div>
        """, unsafe_allow_html=True)

    st.stop()


# ══════════════════════════════════════════════════════════
# PAGE: PROFILE (new users only)
# ══════════════════════════════════════════════════════════

if st.session_state.page == "profile":

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("""
        <div style="height:30px"></div>
        <div style="text-align:center;font-size:3rem;margin-bottom:0.5rem;">👤</div>
        <div class="profile-title">Almost there!</div>
        <div class="profile-sub">Tell us about yourself to personalize your experience</div>
        <div style="height:10px"></div>
        <div style="text-align:center"><span class="step-badge">Step 2 of 2 — Profile Setup</span></div>
        <div style="height:16px"></div>
        """, unsafe_allow_html=True)

        st.markdown(f"**📧 Logged in as:** `{st.session_state.otp_email}`")
        st.markdown("---")

        name       = st.text_input("👤 Full Name", placeholder="e.g. Priya Sharma")
        education  = st.text_input("🎓 Education / Degree", placeholder="e.g. B.Tech Computer Science")
        job_target = st.text_input("🎯 Target Job Role", placeholder="e.g. Data Scientist, SDE, Product Manager")
        purpose    = st.selectbox("📌 Why are you using this app?", [
            "Campus Placement", "Internship", "Full-time Job",
            "Career Switch", "Higher Studies", "Freelance / Gig Work"
        ])

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        if st.button("🚀 Complete Setup & Enter App"):
            if name and education and job_target:
                create_user(st.session_state.otp_email, name, job_target, education, purpose)
                st.session_state.user = {
                    "email": st.session_state.otp_email, "name": name,
                    "education": education, "job_target": job_target, "purpose": purpose
                }
                st.session_state.page = "app"
                st.rerun()
            else:
                st.error("❌ Please fill in all fields to continue.")

    st.stop()


# ══════════════════════════════════════════════════════════
# PAGE: MAIN APP
# ══════════════════════════════════════════════════════════

user       = st.session_state.get("user") or {}
name       = user.get("name", "User")
education  = user.get("education", "")
job_target = user.get("job_target", "")
email      = user.get("email", "")
initials   = name[0].upper() if name else "U"

# ─── Sidebar ───────────────────────────────────────────────
with st.sidebar:

    st.markdown(f"""
    <div class="welcome-card">
        <div style="width:52px;height:52px;background:linear-gradient(135deg,#00d4ff,#7b2ff7);
                    border-radius:50%;display:flex;align-items:center;justify-content:center;
                    font-size:1.5rem;margin:0 auto 0.75rem;">{initials}</div>
        <div class="welcome-name">👋 Welcome, {name}!</div>
        <div class="welcome-detail">🎓 {education}</div>
        <div class="welcome-detail">🎯 {job_target}</div>
        <div class="welcome-email">✉️ {email}</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚪 Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.markdown("---")
    st.markdown("### 📋 Features")
    st.markdown("""
    ✅ Resume Parsing (PDF/DOCX/TXT)
    ✅ AI Skill Extraction
    ✅ Resume Score (0-100)
    ✅ Strengths & Weaknesses
    ✅ Visual Charts & Graphs
    ✅ Smart Job Matching
    ✅ Resume vs JD Matcher
    ✅ Skill Gap Analysis
    ✅ AI Learning Roadmap
    ✅ Interview Questions
    ✅ Resume Line Improver
    ✅ AI Career Mentor Chat
    ✅ Download PDF Report
    """)

    st.markdown("---")
    st.markdown("### 🤖 Powered By")
    st.markdown("• Groq + Llama 3.3\n• TF-IDF Vector Search\n• Plotly Charts\n• Firebase")

    st.markdown("---")
    if 'skills' in st.session_state:
        st.markdown("### 📊 Resume Stats")
        st.metric("Skills Found", len(st.session_state['skills']))
        if 'resume_score' in st.session_state:
            st.metric("Resume Score", f"{st.session_state['resume_score']}/100")
        if 'jobs' in st.session_state:
            st.metric("Best Job Match", st.session_state['jobs'][0]['title'])


# ─── Hero + Welcome Banner ─────────────────────────────────
st.markdown('<div class="hero-title">🚀 AI Resume Analyzer Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Upload your resume and get instant AI-powered career insights</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="welcome-banner">
    Hello, <span>{name}</span>! 👋 &nbsp;·&nbsp;
    🎯 Target: <span>{job_target}</span> &nbsp;·&nbsp;
    🎓 <span>{education}</span>
</div>
""", unsafe_allow_html=True)

# ─── Tabs ──────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "📄 Upload & Analyze", "📊 Visual Charts", "💼 Smart Job Match",
    "🔍 JD Matcher", "🎯 Interview Prep", "📚 Roadmap",
    "💬 Career Chat", "✍️ Resume Improver"
])

# ══════════════════════════════════════════════════════════
# TAB 1 — Upload & Analyze
# ══════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-title">📄 Upload Your Resume</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        uploaded_file = st.file_uploader("Choose resume file", type=["pdf","docx","txt"])
    with col2:
        pasted_text = st.text_area("Or paste resume text here:", height=150, placeholder="Paste your resume text here...")

    if 'resume_score' in st.session_state:
        st.info(f"📊 Previous Score: **{st.session_state['resume_score']}/100** — Upload new resume to compare!")

    if st.button("🔍 Analyze My Resume", key="analyze_btn"):
        resume_text = ""
        if uploaded_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name
            resume_text = extract_text(tmp_path)
            os.unlink(tmp_path)
        elif pasted_text.strip():
            resume_text = pasted_text
        else:
            st.error("❌ Please upload a file or paste resume text!")
            st.stop()

        if len(resume_text.strip()) < 50:
            st.error("❌ Resume text too short. Please check your file.")
            st.stop()

        if 'resume_score' in st.session_state:
            st.session_state['previous_score'] = st.session_state['resume_score']

        st.session_state['resume_text'] = resume_text

        with st.spinner("🔍 Extracting skills..."):
            skills = extract_skills(resume_text)
            st.session_state['skills']     = skills
            st.session_state['categories'] = get_skill_categories(skills)

        with st.spinner("🤖 AI analyzing resume (20-30 seconds)..."):
            analysis = analyze_resume(resume_text)
            st.session_state['analysis'] = analysis

        with st.spinner("💼 Matching jobs..."):
            jobs = match_jobs(skills)
            st.session_state['jobs'] = jobs

        try:
            score_line = [l for l in analysis.split('\n') if 'SCORE:' in l][0]
            score = int(''.join(filter(str.isdigit, score_line)))
            score = min(score, 100)
        except:
            score = 70
        st.session_state['resume_score'] = score

        db.collection("resume_analysis").add({
            "user_email": email, "user_name": name, "score": score,
            "skills": skills,
            "top_job_match": jobs[0]["title"] if jobs else "None",
            "match_score": jobs[0]["match_score"] if jobs else 0,
            "timestamp": datetime.datetime.now().isoformat()
        })

        if score >= 75:
            st.markdown("""<div class="banner-excellent">
                <span class="anim-bounce" style="font-size:2rem">🏆</span>
                &nbsp; EXCELLENT RESUME! You are Job Ready! &nbsp;
                <span class="anim-bounce" style="font-size:2rem">🎉</span>
            </div>""", unsafe_allow_html=True)
            st.success(f"✅ Amazing! Your resume scored {score}/100 — Start applying NOW!")
        elif score >= 50:
            st.markdown("""<div class="banner-medium">
                <span class="anim-pulse" style="font-size:2rem">👍</span>
                &nbsp; GOOD RESUME! A Few Improvements Needed &nbsp;
                <span class="anim-pulse" style="font-size:2rem">📈</span>
            </div>""", unsafe_allow_html=True)
            st.warning(f"⚠️ Your resume scored {score}/100 — Check suggestions below!")
        else:
            st.markdown("""
            <div style="text-align:center;padding:1.5rem 0;height:130px;position:relative;overflow:hidden;">
                <span class="anim-explode" style="font-size:4.5rem;position:absolute;left:8%;top:5%;">💥</span>
                <span class="anim-fly1"    style="font-size:3.5rem;position:absolute;left:18%;top:25%;">🎈</span>
                <span class="anim-fly2"    style="font-size:3.5rem;position:absolute;left:38%;top:15%;">🎈</span>
                <span class="anim-fly3"    style="font-size:3.5rem;position:absolute;left:58%;top:25%;">🎈</span>
                <span class="anim-explode" style="font-size:4rem;position:absolute;left:72%;top:5%;animation-delay:0.2s;">💥</span>
            </div>
            <div class="banner-poor">
                <span class="anim-shake" style="font-size:2rem">⚠️</span>
                &nbsp; RESUME NEEDS A LOT OF WORK! &nbsp;
                <span class="anim-shake" style="font-size:2rem">📄</span>
            </div>""", unsafe_allow_html=True)
            st.error(f"❌ Your resume scored only {score}/100 — Urgent improvements needed!")

    if 'analysis' in st.session_state:
        analysis   = st.session_state['analysis']
        skills     = st.session_state['skills']
        categories = st.session_state['categories']
        score      = st.session_state['resume_score']

        st.markdown("---")

        if 'previous_score' in st.session_state:
            prev = st.session_state['previous_score']
            diff = score - prev
            emoji = "📈" if diff > 0 else "📉" if diff < 0 else "➡️"
            color = "green" if diff > 0 else "red" if diff < 0 else "gray"
            st.markdown(f"""<div class="card" style="text-align:center">
                <h3>Score Comparison {emoji}</h3>
                <span style="font-size:2rem">Previous: <b>{prev}</b></span> &nbsp;→&nbsp;
                <span style="font-size:2rem">New: <b style="color:{color}">{score}</b></span>
                &nbsp;<span style="color:{color}">({'+' if diff>0 else ''}{diff} pts)</span>
            </div>""", unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        c = "#00ff88" if score>=70 else "#ffbb00" if score>=50 else "#ff4444"
        with col1:
            st.markdown(f'<div class="metric-card"><div style="font-size:3rem;font-weight:900;color:{c}">{score}</div><div style="color:#5a6478">Resume Score</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card"><div style="font-size:3rem;font-weight:900;color:#00d4ff">{len(skills)}</div><div style="color:#5a6478">Skills Found</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-card"><div style="font-size:3rem;font-weight:900;color:#7b2ff7">{len(categories)}</div><div style="color:#5a6478">Skill Categories</div></div>', unsafe_allow_html=True)
        with col4:
            top_match = st.session_state['jobs'][0]['match_score'] if st.session_state.get('jobs') else 0
            st.markdown(f'<div class="metric-card"><div style="font-size:3rem;font-weight:900;color:#ff6b6b">{top_match}%</div><div style="color:#5a6478">Top Job Match</div></div>', unsafe_allow_html=True)

        st.markdown("---")
        st.progress(score / 100)

        st.markdown('<div class="section-title">🤖 Full AI Analysis</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card">{analysis}</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">🧠 Skills Detected</div>', unsafe_allow_html=True)
        if categories:
            cols = st.columns(3)
            for i, (cat, cat_skills) in enumerate(categories.items()):
                with cols[i % 3]:
                    st.markdown(f"**{cat}**")
                    for s in cat_skills:
                        st.markdown(f'<span class="skill-tag">{s}</span>', unsafe_allow_html=True)
        else:
            st.warning("No skills detected.")

        st.markdown("---")
        st.markdown('<div class="section-title">📥 Download Report</div>', unsafe_allow_html=True)
        candidate_name = st.text_input("Your name for the report:", value=name)
        if st.button("📄 Generate & Download PDF Report"):
            if candidate_name:
                with st.spinner("Generating PDF..."):
                    questions = st.session_state.get('questions', '')
                    pdf_path = generate_pdf_report(candidate_name, score, skills, analysis, st.session_state['jobs'], questions)
                with open(pdf_path, "rb") as f:
                    st.download_button("⬇️ Download PDF Report", data=f,
                        file_name=f"resume_{candidate_name.replace(' ','_')}.pdf", mime="application/pdf")
            else:
                st.error("Please enter your name!")

# ══════════════════════════════════════════════════════════
# TAB 2 — Visual Charts
# ══════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">📊 Visual Analytics</div>', unsafe_allow_html=True)
    if 'skills' not in st.session_state:
        st.info("👆 Please analyze your resume first!")
    else:
        score      = st.session_state['resume_score']
        skills     = st.session_state['skills']
        categories = st.session_state['categories']
        jobs       = st.session_state['jobs']

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 🎯 Resume Score Gauge")
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta", value=score, domain={'x':[0,1],'y':[0,1]},
                title={'text':"Resume Score",'font':{'color':'white'}},
                delta={'reference':70,'increasing':{'color':"#00ff88"}},
                gauge={'axis':{'range':[0,100],'tickcolor':"white"},'bar':{'color':"#00d4ff"},
                       'bgcolor':"rgba(0,0,0,0)",
                       'steps':[{'range':[0,50],'color':'rgba(255,68,68,0.3)'},
                                 {'range':[50,70],'color':'rgba(255,187,0,0.3)'},
                                 {'range':[70,100],'color':'rgba(0,255,136,0.3)'}],
                       'threshold':{'line':{'color':"#7b2ff7",'width':4},'thickness':0.75,'value':70}}
            ))
            fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)',font={'color':'white'},height=300)
            st.plotly_chart(fig_gauge, use_container_width=True)

        with col2:
            st.markdown("#### 🧠 Skills by Category")
            if categories:
                fig_pie = px.pie(names=list(categories.keys()), values=[len(v) for v in categories.values()],
                                  color_discrete_sequence=px.colors.sequential.Plasma, hole=0.4)
                fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)',font={'color':'white'},height=300)
                st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("#### 💼 Job Match Scores")
        jt = [j['title'] for j in jobs[:8]]; js = [j['match_score'] for j in jobs[:8]]
        cb = ['#00ff88' if s>=70 else '#ffbb00' if s>=40 else '#ff4444' for s in js]
        fig_bar = go.Figure(go.Bar(x=js,y=jt,orientation='h',marker_color=cb,
                                    text=[f"{s}%" for s in js],textposition='outside'))
        fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
                               font={'color':'white'},xaxis={'range':[0,110]},height=400)
        st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("#### 🕸️ Skill Radar")
        if categories:
            rc = list(categories.keys()); rv = [len(v) for v in categories.values()]
            rc.append(rc[0]); rv.append(rv[0])
            fig_r = go.Figure(go.Scatterpolar(r=rv,theta=rc,fill='toself',
                                               fillcolor='rgba(0,212,255,0.12)',line_color='#00d4ff'))
            fig_r.update_layout(polar=dict(bgcolor='rgba(0,0,0,0)',
                radialaxis=dict(visible=True,gridcolor='rgba(255,255,255,0.1)',color='white'),
                angularaxis=dict(gridcolor='rgba(255,255,255,0.1)',color='white')),
                paper_bgcolor='rgba(0,0,0,0)',font={'color':'white'},height=400)
            st.plotly_chart(fig_r, use_container_width=True)

        if 'previous_score' in st.session_state:
            fig_c = go.Figure(go.Bar(x=['Previous','Current'],
                y=[st.session_state['previous_score'],score],marker_color=['#ff6b6b','#00ff88'],
                text=[str(st.session_state['previous_score']),str(score)],textposition='outside'))
            fig_c.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
                                  font={'color':'white'},yaxis={'range':[0,110]},height=300)
            st.plotly_chart(fig_c, use_container_width=True)

# ══════════════════════════════════════════════════════════
# TAB 3 — Smart Job Match
# ══════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-title">💼 Smart Job Matching</div>', unsafe_allow_html=True)
    st.markdown("Uses **AI Vector Search** to find semantically similar jobs!")

    if 'resume_text' not in st.session_state:
        st.info("👆 Please analyze your resume first!")
    else:
        if st.button("🔍 Run Smart Job Match", key="chroma_btn"):
            with st.spinner("🧠 AI searching best jobs for you..."):
                smart_jobs = smart_job_match(st.session_state['resume_text'])
                st.session_state['smart_jobs'] = smart_jobs

        if 'smart_jobs' in st.session_state:
            for i, job in enumerate(st.session_state['smart_jobs']):
                sj = job['similarity_score']
                em = "🥇" if i==0 else "🥈" if i==1 else "🥉" if i==2 else "⭐"
                with st.expander(f"{em} {job['title']} — {sj}% Match"):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"**Score:** {sj}%"); st.progress(sj/100)
                        st.markdown(f"**💰 Salary:** {job['salary']}")
                        st.markdown(f"**🏢 Companies:** {job['companies']}")
                    with c2:
                        st.markdown("**Required Skills:**")
                        for s in job['required_skills']:
                            has = s.lower() in [sk.lower() for sk in st.session_state['skills']]
                            st.markdown(f"{'✅' if has else '❌'} {s}")

# ══════════════════════════════════════════════════════════
# TAB 4 — JD Matcher
# ══════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-title">🔍 Resume vs JD Matcher</div>', unsafe_allow_html=True)
    if 'resume_text' not in st.session_state:
        st.info("👆 Please analyze your resume first!")
    else:
        jd_text = st.text_area("Paste Job Description here:", height=250, placeholder="Paste job description...")
        if st.button("🔍 Match Resume with JD", key="jd_btn"):
            if jd_text.strip():
                with st.spinner("🤖 AI comparing..."):
                    prompt = f"""You are an ATS expert. Compare resume with JD. Use EXACTLY this format:

MATCH SCORE: [0-100]
MATCHED KEYWORDS:\n- keyword\nMISSING KEYWORDS:\n- keyword
ATS SCORE: [0-100]
RECOMMENDATION:\n[3-4 sentences]
TAILORING TIPS:\n- tip

Resume:\n{st.session_state['resume_text']}\n\nJob Description:\n{jd_text}"""
                    resp = client.chat.completions.create(model="llama-3.3-70b-versatile",
                                                          messages=[{"role":"user","content":prompt}])
                    st.session_state['jd_result'] = resp.choices[0].message.content
            else:
                st.error("Please paste a job description!")

        if 'jd_result' in st.session_state:
            result = st.session_state['jd_result']
            try:
                ms = min(int(''.join(filter(str.isdigit,[l for l in result.split('\n') if 'MATCH SCORE:' in l][0]))),100)
            except: ms = 60
            try:
                ats = min(int(''.join(filter(str.isdigit,[l for l in result.split('\n') if 'ATS SCORE:' in l][0]))),100)
            except: ats = 65
            c1,c2 = st.columns(2)
            with c1:
                cc="#00ff88" if ms>=70 else "#ffbb00" if ms>=50 else "#ff4444"
                st.markdown(f'<div class="metric-card"><div style="font-size:3rem;font-weight:900;color:{cc}">{ms}%</div><div style="color:#5a6478">JD Match</div></div>',unsafe_allow_html=True)
                st.progress(ms/100)
            with c2:
                cc2="#00ff88" if ats>=70 else "#ffbb00" if ats>=50 else "#ff4444"
                st.markdown(f'<div class="metric-card"><div style="font-size:3rem;font-weight:900;color:{cc2}">{ats}%</div><div style="color:#5a6478">ATS Score</div></div>',unsafe_allow_html=True)
                st.progress(ats/100)
            st.markdown(f'<div class="card">{result}</div>',unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# TAB 5 — Interview Prep
# ══════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-title">🎯 Interview Question Generator</div>', unsafe_allow_html=True)
    if 'skills' not in st.session_state:
        st.info("👆 Please analyze your resume first!")
    else:
        c1,c2 = st.columns(2)
        with c1:
            jtl = [j['title'] for j in st.session_state.get('jobs',[])] or ["Data Scientist"]
            sel_job = st.selectbox("Select Target Job", jtl)
        with c2:
            diff = st.selectbox("Difficulty", ["Entry Level","Mid Level","Senior Level"])
        if st.button("🎯 Generate Questions", key="interview_btn"):
            with st.spinner("🤖 Generating..."):
                qs = generate_interview_questions(st.session_state['skills'], f"{diff} {sel_job}")
                st.session_state['questions']    = qs
                st.session_state['selected_job'] = sel_job
        if 'questions' in st.session_state:
            st.markdown(f"### 📝 {st.session_state['selected_job']} Questions")
            st.markdown(f'<div class="card">{st.session_state["questions"]}</div>',unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# TAB 6 — Roadmap
# ══════════════════════════════════════════════════════════
with tab6:
    st.markdown('<div class="section-title">📚 AI Learning Roadmap</div>', unsafe_allow_html=True)
    if 'roadmap' in st.session_state:
        st.markdown(f'<div class="card">{st.session_state["roadmap"]}</div>',unsafe_allow_html=True)
    else:
        st.info("Generate a custom roadmap below!")

    c1,c2 = st.columns(2)
    with c1: tj = st.text_input("Target Job Title", value=user.get('job_target',''))
    with c2: miss = st.text_input("Skills to Learn", placeholder="e.g. Deep Learning, SQL")
    if st.button("📚 Generate Roadmap", key="roadmap_btn"):
        if tj and miss:
            with st.spinner("🤖 Building your roadmap..."):
                rm = generate_skill_roadmap([s.strip() for s in miss.split(",")], tj)
                st.session_state['roadmap']     = rm
                st.session_state['roadmap_job'] = tj
            st.rerun()
        else:
            st.error("Please fill both fields!")

# ══════════════════════════════════════════════════════════
# TAB 7 — Career Chat
# ══════════════════════════════════════════════════════════
with tab7:
    st.markdown('<div class="section-title">💬 AI Career Mentor</div>', unsafe_allow_html=True)
    st.markdown(f"Hi **{name}**! Ask me anything about your career 🤖")

    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    for msg in st.session_state['chat_history']:
        if msg['role'] == 'user':
            st.markdown(f'<div class="chat-user">👤 <b>You:</b> {msg["content"]}</div>',unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-ai">🤖 <b>Mentor:</b> {msg["content"]}</div>',unsafe_allow_html=True)

    qc1,qc2,qc3 = st.columns(3)
    with qc1:
        if st.button("Improve my resume?"): st.session_state['quick_q'] = "How can I improve my resume?"
    with qc2:
        if st.button("Best jobs for me?"):
            st.session_state['quick_q'] = f"Best jobs for skills: {', '.join(st.session_state.get('skills',[])[:5])}"
    with qc3:
        if st.button("Crack tech interviews?"): st.session_state['quick_q'] = "Tips to crack technical interviews?"

    ui = st.text_input("Ask anything:", value=st.session_state.pop('quick_q',''),
                        placeholder="e.g. How do I become a Data Scientist?")

    if st.button("💬 Send", key="chat_btn"):
        if ui.strip():
            ctx = f"User: {name}, Education: {education}, Target: {job_target}."
            if 'skills' in st.session_state:
                ctx += f" Skills: {', '.join(st.session_state['skills'])}. Score: {st.session_state.get('resume_score','?')}/100."
            with st.spinner("🤖 Thinking..."):
                resp = client.chat.completions.create(model="llama-3.3-70b-versatile",
                    messages=[{"role":"user","content":f"You are an expert career mentor.\n{ctx}\nAnswer in max 200 words.\nQuestion: {ui}"}])
                ai_r = resp.choices[0].message.content
            st.session_state['chat_history'].append({"role":"user","content":ui})
            st.session_state['chat_history'].append({"role":"assistant","content":ai_r})
            st.rerun()
        else:
            st.error("Please type a question!")

    if st.session_state['chat_history']:
        if st.button("🗑️ Clear Chat"):
            st.session_state['chat_history'] = []
            st.rerun()

# ══════════════════════════════════════════════════════════
# TAB 8 — Resume Improver
# ══════════════════════════════════════════════════════════
with tab8:
    st.markdown('<div class="section-title">✍️ Resume Line Improver</div>', unsafe_allow_html=True)
    st.markdown("Paste a weak bullet point → AI makes it powerful! 💪")

    ol = st.text_area("Your resume line:", placeholder='"Worked on Python project"', height=100)
    if st.button("✨ Improve This Line", key="improve_btn"):
        if ol.strip():
            with st.spinner("🤖 Rewriting..."):
                imp = improve_resume_line(ol)
                st.session_state['improved'] = imp
        else:
            st.error("Please enter a resume line!")

    if 'improved' in st.session_state:
        st.markdown("### ✅ Improved Versions:")
        st.markdown(f'<div class="card">{st.session_state["improved"]}</div>',unsafe_allow_html=True)