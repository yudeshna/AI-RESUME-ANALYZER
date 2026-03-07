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
    api_key = os.getenv("GROQ_API_KEY")
)

# Firebase Setup
if not firebase_admin._apps:
    firebase_key = dict(st.secrets["firebase"])
    firebase_key["private_key"] = firebase_key["private_key"].replace("\\n", "\n")

    cred = credentials.Certificate(firebase_key)
    firebase_admin.initialize_app(cred)
# ─── Load Jobs Dataset ─────────────────────
try:
    jobs_df = pd.read_csv("jobs_dataset.csv")
except:
    jobs_df = None

# ─── Email Config ──────────────────────────────────────────
SENDER_EMAIL    = "nandu19jul@gmail.com"
SENDER_PASSWORD = "vsoo tsqc xbgy brln"

# ─── Page Config ───────────────────────────────────────────
st.set_page_config(
    page_title="AI Resume Analyzer Pro",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0e1117 0%, #1a1f2e 100%); }
    .hero-title {
        font-size: 2.8rem;
        font-weight: 900;
        background: linear-gradient(90deg, #00d4ff, #7b2ff7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    .hero-sub { text-align: center; color: #8892a4; font-size: 1.1rem; margin-bottom: 2rem; }
    .card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px; padding: 1.5rem; margin: 1rem 0;
    }
    .skill-tag {
        display: inline-block;
        background: linear-gradient(90deg, #00d4ff22, #7b2ff722);
        border: 1px solid #00d4ff44; color: #00d4ff;
        padding: 4px 12px; border-radius: 20px; margin: 4px; font-size: 0.85rem;
    }
    .section-title {
        font-size: 1.4rem; font-weight: 700; color: #00d4ff;
        margin: 1rem 0 0.5rem 0; border-left: 4px solid #7b2ff7; padding-left: 0.75rem;
    }
    .stButton > button {
        background: linear-gradient(90deg, #00d4ff, #7b2ff7);
        color: white; border: none; border-radius: 8px;
        padding: 0.5rem 2rem; font-weight: 600; font-size: 1rem; width: 100%;
    }
    .chat-user {
        background: rgba(0,212,255,0.1); border: 1px solid rgba(0,212,255,0.3);
        border-radius: 12px; padding: 0.75rem 1rem; margin: 0.5rem 0; text-align: right;
    }
    .chat-ai {
        background: rgba(123,47,247,0.1); border: 1px solid rgba(123,47,247,0.3);
        border-radius: 12px; padding: 0.75rem 1rem; margin: 0.5rem 0;
    }
    .metric-card {
        background: rgba(255,255,255,0.05); border-radius: 12px; padding: 1rem;
        text-align: center; border: 1px solid rgba(255,255,255,0.1);
    }
    @keyframes shake {
        0%   { transform: translateX(0); }
        20%  { transform: translateX(-10px) rotate(-3deg); }
        40%  { transform: translateX(10px) rotate(3deg); }
        60%  { transform: translateX(-10px) rotate(-3deg); }
        80%  { transform: translateX(10px) rotate(3deg); }
        100% { transform: translateX(0); }
    }
    @keyframes pulse {
        0%   { transform: scale(1); opacity: 1; }
        50%  { transform: scale(1.15); opacity: 0.8; }
        100% { transform: scale(1); opacity: 1; }
    }
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        30%  { transform: translateY(-18px); }
        60%  { transform: translateY(-8px); }
    }
    @keyframes explode {
        0%   { transform: scale(0.3) rotate(0deg);   opacity: 0; }
        30%  { transform: scale(2.5) rotate(-20deg); opacity: 1; }
        60%  { transform: scale(1.8) rotate(15deg);  opacity: 1; }
        100% { transform: scale(2.2) rotate(-5deg);  opacity: 0.7; }
    }
    @keyframes flyaway {
        0%   { transform: translate(0,0) scale(1);           opacity: 1; }
        30%  { transform: translate(-50px,-80px) scale(1.4); opacity: 1; }
        70%  { transform: translate(60px,-200px) scale(0.5); opacity: 0.5; }
        100% { transform: translate(-30px,-320px) scale(0);  opacity: 0; }
    }
    @keyframes flyaway2 {
        0%   { transform: translate(0,0) scale(1);            opacity: 1; }
        30%  { transform: translate(60px,-70px) scale(1.3);   opacity: 1; }
        70%  { transform: translate(-40px,-210px) scale(0.4); opacity: 0.4; }
        100% { transform: translate(40px,-330px) scale(0);    opacity: 0; }
    }
    @keyframes flyaway3 {
        0%   { transform: translate(0,0) scale(1); opacity: 1; }
        100% { transform: translate(90px,-340px) scale(0); opacity: 0; }
    }
    .anim-shake   { display: inline-block; animation: shake    0.6s ease infinite; }
    .anim-pulse   { display: inline-block; animation: pulse    1.2s ease infinite; }
    .anim-bounce  { display: inline-block; animation: bounce   1.0s ease infinite; }
    .anim-explode { display: inline-block; animation: explode  0.7s ease-out forwards; }
    .anim-fly1    { display: inline-block; animation: flyaway  1.3s ease-out forwards; }
    .anim-fly2    { display: inline-block; animation: flyaway2 1.5s ease-out 0.1s forwards; }
    .anim-fly3    { display: inline-block; animation: flyaway3 1.1s ease-out 0.2s forwards; }
    .banner-excellent {
        background: linear-gradient(90deg, #00ff88, #00d4ff);
        border-radius: 14px; padding: 1.2rem 2rem; text-align: center;
        font-size: 1.5rem; font-weight: 800; color: #0e1117; margin: 1rem 0;
        box-shadow: 0 0 30px rgba(0,255,136,0.4);
    }
    .banner-medium {
        background: linear-gradient(90deg, #ffbb00, #ff8c00);
        border-radius: 14px; padding: 1.2rem 2rem; text-align: center;
        font-size: 1.5rem; font-weight: 800; color: #0e1117; margin: 1rem 0;
        box-shadow: 0 0 30px rgba(255,187,0,0.4);
    }
    .banner-poor {
        background: linear-gradient(90deg, #ff4444, #ff0000);
        border-radius: 14px; padding: 1.2rem 2rem; text-align: center;
        font-size: 1.5rem; font-weight: 800; color: white; margin: 1rem 0;
        box-shadow: 0 0 30px rgba(255,68,68,0.4);
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
        <div style="font-family:Arial,sans-serif;background:#0e1117;padding:2rem;border-radius:12px;max-width:500px;margin:auto;">
            <h2 style="color:#00d4ff;text-align:center;">🧠 AI Resume Analyzer Pro</h2>
            <p style="color:#ffffff;font-size:1rem;text-align:center;">Your One-Time Password is:</p>
            <div style="background:linear-gradient(90deg,#00d4ff,#7b2ff7);padding:1rem 2rem;
                        border-radius:10px;font-size:2.5rem;font-weight:900;color:white;
                        letter-spacing:10px;text-align:center;margin:1.5rem 0;">
                {otp}
            </div>
            <p style="color:#8892a4;font-size:0.85rem;text-align:center;">
                Valid for 5 minutes. Do not share this with anyone.
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
        "email":      email,
        "name":       name,
        "job_target": job_target,
        "education":  education,
        "purpose":    purpose
    })


# ══════════════════════════════════════════════════════════
# SESSION STATE INIT
# ══════════════════════════════════════════════════════════

if "page"      not in st.session_state: st.session_state.page      = "login"
if "otp_sent"  not in st.session_state: st.session_state.otp_sent  = False
if "otp_code"  not in st.session_state: st.session_state.otp_code  = ""
if "otp_email" not in st.session_state: st.session_state.otp_email = ""
if "user"      not in st.session_state: st.session_state.user      = None


# ══════════════════════════════════════════════════════════
# PAGE: LOGIN
# ══════════════════════════════════════════════════════════

if st.session_state.page == "login":

    st.markdown('<div class="hero-title">Analyze Your Resume with AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Get your resume score, skill gaps, job matches & interview prep — in seconds</div>', unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:

        st.markdown("### 🔐 Login / Sign Up")
        st.markdown("Enter your email address to receive a 6-digit OTP")
        st.markdown("---")

        email_input = st.text_input("📧 Email Address", placeholder="you@example.com", key="login_email")

        if st.button("📨 Send OTP to My Email"):
            if email_input.strip() and "@" in email_input and "." in email_input:
                with st.spinner("Sending OTP to your email..."):
                    otp = str(random.randint(100000, 999999))
                    if send_otp_email(email_input.strip(), otp):
                        st.session_state.otp_sent  = True
                        st.session_state.otp_code  = otp
                        st.session_state.otp_email = email_input.strip()
                        st.success(f"✅ OTP sent to **{email_input.strip()}** — check your inbox!")
                    else:
                        st.error("❌ Failed to send email. Check your internet connection.")
            else:
                st.error("❌ Please enter a valid email address!")

        if st.session_state.otp_sent:
            st.markdown("---")
            st.info(f"📬 OTP sent to: **{st.session_state.otp_email}**")
            otp_input = st.text_input("🔑 Enter the 6-digit OTP from your email", placeholder="e.g. 482910", max_chars=6, key="otp_input")

            if st.button("✅ Verify OTP & Login"):
                if otp_input.strip() == st.session_state.otp_code:
                    email     = st.session_state.otp_email
                    user_data = get_user(email)
                    st.session_state.otp_sent = False
                    st.session_state.otp_code = ""
                    if user_data:
                        # Existing user — go straight to app
                        st.session_state.user = user_data
                        st.session_state.page = "app"
                        st.rerun()
                    else:
                        # New user — fill profile first
                        st.session_state.page = "profile"
                        st.rerun()
                else:
                    st.error("❌ Wrong OTP! Please check your email and try again.")

            if st.button("🔄 Resend OTP"):
                otp = str(random.randint(100000, 999999))
                if send_otp_email(st.session_state.otp_email, otp):
                    st.session_state.otp_code = otp
                    st.success("✅ New OTP sent!")

    st.stop()


# ══════════════════════════════════════════════════════════
# PAGE: PROFILE CREATION (new users only)
# ══════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════
# PAGE: PROFILE
# ══════════════════════════════════════════════════════════

if st.session_state.page == "profile":

    st.markdown('<div class="hero-title">👤 Complete Your Profile</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Just a few details to personalize your experience</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])

    with col2:

        st.markdown(f"**📧 Logged in as:** `{st.session_state.otp_email}`")
        st.markdown("---")

        name = st.text_input(
            "👤 Full Name",
            placeholder="e.g. Priya Sharma"
        )

        education = st.text_input(
            "🎓 Education",
            placeholder="e.g. B.Tech CSE"
        )

        job_target = st.text_input(
            "🎯 Target Job Role",
            placeholder="e.g. Data Scientist"
        )

        purpose = st.selectbox(
            "📌 Purpose of Resume",
            [
                "Campus Placement",
                "Internship",
                "Full-time Job",
                "Higher Studies",
                "Freelance / Gig Work"
            ]
        )

        if st.button("🚀 Save Profile & Continue"):

            if name and education and job_target:

                create_user(
                    st.session_state.otp_email,
                    name,
                    job_target,
                    education,
                    purpose
                )

                st.session_state.user = {
                    "email": st.session_state.otp_email,
                    "name": name,
                    "education": education,
                    "job_target": job_target,
                    "purpose": purpose
                }

                st.session_state.page = "app"
                st.success("Profile saved successfully!")

                st.rerun()

            else:
                st.error("❌ Please fill all fields")

    st.stop()

# ══════════════════════════════════════════════════════════
# PAGE: MAIN APP
# ══════════════════════════════════════════════════════════

user = st.session_state.get("user", {})

# ─── Sidebar ───────────────────────────────────────────────
# ───────────────── Sidebar ─────────────────
with st.sidebar:

    st.markdown("## 🧠 AI Resume Analyzer Pro")
    st.markdown("---")

    st.markdown("### 📋 All Features")

    st.markdown("""
    ✅ Resume Parsing (PDF/DOCX/TXT)  
    ✅ AI Skill Extraction (NLP)  
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
    ✅ Score Comparison  
    ✅ Download PDF Report
    """)

    st.markdown("---")

    st.markdown("### 🤖 Powered By")

    st.markdown("""
    • Groq + Llama 3.3  
    • ChromaDB Vector Search  
    • spaCy NLP  
    • Plotly Charts  
    • Firebase Database
    """)

    st.markdown("---")

    if 'skills' in st.session_state:

        st.markdown("### 📊 Resume Stats")

        st.metric("Skills Found", len(st.session_state['skills']))

        if 'resume_score' in st.session_state:
            st.metric("Resume Score", f"{st.session_state['resume_score']}/100")

        if 'jobs' in st.session_state:
            st.metric("Best Job Match", st.session_state['jobs'][0]['title'])


# ───────────────── Hero Section ─────────────────
st.markdown(
    '<div class="hero-title">🚀 AI Resume Analyzer Pro</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="hero-sub">Upload your resume and get instant AI-powered career insights</div>',
    unsafe_allow_html=True
)


# ───────────────── Tabs ─────────────────
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "📄 Upload & Analyze",
    "📊 Visual Charts",
    "💼 Smart Job Match",
    "🔍 JD Matcher",
    "🎯 Interview Prep",
    "📚 Roadmap",
    "💬 Career Chat",
    "✍️ Resume Improver"
])
# ══════════════════════════════════════════════════════════
# TAB 1 — Upload & Analyze
# ══════════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════════
# TAB 1 — Upload & Analyze (Enhanced)
# ══════════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════════
# TAB 1 — Upload & Analyze
# ═════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-title">📄 Upload Your Resume</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        uploaded_file = st.file_uploader(
            "Choose resume file",
            type=["pdf", "docx", "txt"],
        )
    with col2:
        pasted_text = st.text_area(
            "Or paste resume text here:",
            height=150,
            placeholder="Paste your resume text here..."
        )

    if 'resume_score' in st.session_state:
        st.info(f"📊 Previous Score: *{st.session_state['resume_score']}/100* — Upload new resume to compare!")

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

        with st.spinner("🔍 Extracting skills with NLP..."):
            skills = extract_skills(resume_text)
            st.session_state['skills'] = skills
            st.session_state['categories'] = get_skill_categories(skills)

        with st.spinner("🤖 AI analyzing resume (20-30 seconds)..."):
            analysis = analyze_resume(resume_text)
            st.session_state['analysis'] = analysis

        with st.spinner("💼 Matching jobs..."):
            jobs = match_jobs(skills)
            st.session_state['jobs'] = jobs

        # Extract score
        try:
            score_line = [l for l in analysis.split('\n') if 'SCORE:' in l][0]
            score = int(''.join(filter(str.isdigit, score_line)))
            score = min(score, 100)
        except:
            score = 70
        st.session_state['resume_score'] = score
        # Save result to Firebase
        db.collection("resume_analysis").add({
        "score": score,
        "skills": skills,
        "top_job_match": jobs[0]["title"] if jobs else "None",
        "match_score": jobs[0]["match_score"] if jobs else 0,
        "timestamp": datetime.datetime.now().isoformat()
})

        # ── Score-based animations ──────────────────────────
        if score >= 75:
            # EXCELLENT — green glowing banner + bouncing trophy
            st.markdown("""
            <div class="banner-excellent">
                <span class="anim-bounce" style="font-size:2rem">🏆</span>
                &nbsp; EXCELLENT RESUME! You are Job Ready! &nbsp;
                <span class="anim-bounce" style="font-size:2rem">🎉</span>
            </div>
            """, unsafe_allow_html=True)
            st.success(f"✅ Amazing! Your resume scored {score}/100 — Start applying NOW!")

        elif score >= 50:
            # MEDIUM — orange banner + pulsing emoji
            st.markdown("""
            <div class="banner-medium">
                <span class="anim-pulse" style="font-size:2rem">👍</span>
                &nbsp; GOOD RESUME! A Few Improvements Needed &nbsp;
                <span class="anim-pulse" style="font-size:2rem">📈</span>
            </div>
            """, unsafe_allow_html=True)
            st.warning(f"⚠️ Your resume scored {score}/100 — Check the suggestions below to improve it!")

        else:
            # POOR — balloons EXPLODING 💥 + flying away + red shaking banner
            st.markdown("""
            <div style="text-align:center; padding:1.5rem 0; height:130px; position:relative; overflow:hidden;">
                <span class="anim-explode" style="font-size:4.5rem; position:absolute; left:8%;  top:5%;">💥</span>
                <span class="anim-fly1"    style="font-size:3.5rem; position:absolute; left:18%; top:25%;">🎈</span>
                <span class="anim-fly2"    style="font-size:3.5rem; position:absolute; left:38%; top:15%;">🎈</span>
                <span class="anim-fly3"    style="font-size:3.5rem; position:absolute; left:58%; top:25%;">🎈</span>
                <span class="anim-explode" style="font-size:4rem;   position:absolute; left:72%; top:5%;  animation-delay:0.2s;">💥</span>
                <span class="anim-fly1"    style="font-size:3rem;   position:absolute; left:83%; top:30%; animation-delay:0.15s;">🎈</span>
                <span class="anim-explode" style="font-size:2.5rem; position:absolute; left:48%; top:45%; animation-delay:0.35s;">💥</span>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("""
            <div class="banner-poor">
                <span class="anim-shake" style="font-size:2rem">⚠️</span>
                &nbsp; RESUME NEEDS A LOT OF WORK! &nbsp;
                <span class="anim-shake" style="font-size:2rem">📄</span>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("""
            <div style="text-align:center; font-size:3.5rem; margin:0.5rem 0;">
                <span class="anim-shake">😬</span>
                &nbsp;
                <span class="anim-shake" style="animation-delay:0.15s">❌</span>
                &nbsp;
                <span class="anim-shake" style="animation-delay:0.3s">📉</span>
            </div>
            """, unsafe_allow_html=True)
            st.error(f"❌ Your resume scored only {score}/100 — Urgent improvements needed! Read the AI suggestions carefully.")

    # ── Show Results ──
    if 'analysis' in st.session_state:
        analysis   = st.session_state['analysis']
        skills     = st.session_state['skills']
        categories = st.session_state['categories']
        score      = st.session_state['resume_score']

        st.markdown("---")

        # Score comparison banner
        if 'previous_score' in st.session_state:
            prev  = st.session_state['previous_score']
            diff  = score - prev
            emoji = "📈" if diff > 0 else "📉" if diff < 0 else "➡️"
            color = "green" if diff > 0 else "red" if diff < 0 else "gray"
            st.markdown(f"""
            <div class="card" style="text-align:center">
                <h3>Score Comparison {emoji}</h3>
                <span style="font-size:2rem">Previous: <b>{prev}</b></span>
                &nbsp;&nbsp;→&nbsp;&nbsp;
                <span style="font-size:2rem">New: <b style="color:{color}">{score}</b></span>
                &nbsp;&nbsp;
                <span style="font-size:1.5rem;color:{color}">({'+' if diff>0 else ''}{diff} points)</span>
            </div>
            """, unsafe_allow_html=True)

        # Top metrics
        col1, col2, col3, col4 = st.columns(4)
        color = "#00ff88" if score >= 70 else "#ffbb00" if score >= 50 else "#ff4444"
        with col1:
            st.markdown(f"""<div class="metric-card">
                <div style="font-size:3rem;font-weight:900;color:{color}">{score}</div>
                <div style="color:#8892a4">Resume Score</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""<div class="metric-card">
                <div style="font-size:3rem;font-weight:900;color:#00d4ff">{len(skills)}</div>
                <div style="color:#8892a4">Skills Found</div>
            </div>""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""<div class="metric-card">
                <div style="font-size:3rem;font-weight:900;color:#7b2ff7">{len(categories)}</div>
                <div style="color:#8892a4">Skill Categories</div>
            </div>""", unsafe_allow_html=True)
        with col4:
            top_match = st.session_state['jobs'][0]['match_score'] if st.session_state.get('jobs') else 0
            st.markdown(f"""<div class="metric-card">
                <div style="font-size:3rem;font-weight:900;color:#ff6b6b">{top_match}%</div>
                <div style="color:#8892a4">Top Job Match</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("---")
        st.progress(score / 100)

        # Full AI Analysis
        st.markdown('<div class="section-title">🤖 Full AI Analysis</div>', unsafe_allow_html=True)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(analysis)
        st.markdown('</div>', unsafe_allow_html=True)

        # Skills by category
        st.markdown('<div class="section-title">🧠 Skills Detected</div>', unsafe_allow_html=True)
        if categories:
            cols = st.columns(3)
            for i, (cat, cat_skills) in enumerate(categories.items()):
                with cols[i % 3]:
                    st.markdown(f"*{cat}*")
                    for s in cat_skills:
                        st.markdown(f'<span class="skill-tag">{s}</span>', unsafe_allow_html=True)
        else:
            st.warning("No skills detected.")

        # PDF Download
        st.markdown("---")
        st.markdown('<div class="section-title">📥 Download Report</div>', unsafe_allow_html=True)
        candidate_name = st.text_input("Your name for the report:", placeholder="e.g. Supriya Sharma")
        if st.button("📄 Generate & Download PDF Report"):
            if candidate_name:
                with st.spinner("Generating PDF report..."):
                    questions = st.session_state.get('questions', '')
                    pdf_path = generate_pdf_report(
                        candidate_name, score, skills,
                        analysis, st.session_state['jobs'], questions
                    )
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label="⬇️ Download PDF Report",
                        data=f,
                        file_name=f"resume_analysis_{candidate_name.replace(' ','_')}.pdf",
                        mime="application/pdf"
                    )
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
                mode="gauge+number+delta", value=score,
                domain={'x': [0,1], 'y': [0,1]},
                title={'text': "Resume Score", 'font': {'color': 'white'}},
                delta={'reference': 70, 'increasing': {'color': "#00ff88"}},
                gauge={
                    'axis': {'range': [0,100], 'tickcolor': "white"},
                    'bar': {'color': "#00d4ff"}, 'bgcolor': "rgba(0,0,0,0)",
                    'steps': [
                        {'range': [0,50],   'color': 'rgba(255,68,68,0.3)'},
                        {'range': [50,70],  'color': 'rgba(255,187,0,0.3)'},
                        {'range': [70,100], 'color': 'rgba(0,255,136,0.3)'},
                    ],
                    'threshold': {'line': {'color': "#7b2ff7", 'width': 4}, 'thickness': 0.75, 'value': 70}
                }
            ))
            fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': 'white'}, height=300)
            st.plotly_chart(fig_gauge, use_container_width=True)

        with col2:
            st.markdown("#### 🧠 Skills by Category")
            if categories:
                fig_pie = px.pie(
                    names=list(categories.keys()),
                    values=[len(v) for v in categories.values()],
                    color_discrete_sequence=px.colors.sequential.Plasma, hole=0.4
                )
                fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': 'white'}, height=300)
                st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("#### 💼 Job Match Scores")
        job_titles = [j['title'] for j in jobs[:8]]
        job_scores = [j['match_score'] for j in jobs[:8]]
        colors     = ['#00ff88' if s>=70 else '#ffbb00' if s>=40 else '#ff4444' for s in job_scores]
        fig_bar = go.Figure(go.Bar(
            x=job_scores, y=job_titles, orientation='h',
            marker_color=colors, text=[f"{s}%" for s in job_scores], textposition='outside'
        ))
        fig_bar.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font={'color': 'white'}, xaxis={'range': [0,110], 'gridcolor': 'rgba(255,255,255,0.1)'},
            yaxis={'gridcolor': 'rgba(255,255,255,0.1)'}, height=400, title="Job Match Percentage"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("#### 🕸️ Skill Radar Chart")
        if categories:
            radar_cats   = list(categories.keys())
            radar_values = [len(v) for v in categories.values()]
            radar_cats.append(radar_cats[0])
            radar_values.append(radar_values[0])
            fig_radar = go.Figure(go.Scatterpolar(
                r=radar_values, theta=radar_cats, fill='toself',
                fillcolor='rgba(0,212,255,0.2)', line_color='#00d4ff', name='Your Skills'
            ))
            fig_radar.update_layout(
                polar=dict(
                    bgcolor='rgba(0,0,0,0)',
                    radialaxis=dict(visible=True, gridcolor='rgba(255,255,255,0.2)', color='white'),
                    angularaxis=dict(gridcolor='rgba(255,255,255,0.2)', color='white')
                ),
                paper_bgcolor='rgba(0,0,0,0)', font={'color': 'white'}, height=400
            )
            st.plotly_chart(fig_radar, use_container_width=True)

        if 'previous_score' in st.session_state:
            st.markdown("#### 📈 Score Comparison")
            fig_comp = go.Figure(go.Bar(
                x=['Previous Resume', 'Current Resume'],
                y=[st.session_state['previous_score'], score],
                marker_color=['#ff6b6b', '#00ff88'],
                text=[f"{st.session_state['previous_score']}", f"{score}"],
                textposition='outside'
            ))
            fig_comp.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font={'color': 'white'}, yaxis={'range': [0,110]}, height=300
            )
            st.plotly_chart(fig_comp, use_container_width=True)

# ══════════════════════════════════════════════════════════
# TAB 3 — Smart Job Match (ChromaDB)
# ══════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-title">💼 ChromaDB Smart Job Matching</div>', unsafe_allow_html=True)
    st.markdown("Uses **AI Vector Search** to find semantically similar jobs — smarter than keyword matching!")

    if 'resume_text' not in st.session_state:
        st.info("👆 Please analyze your resume first!")
    else:
        if st.button("🔍 Run Smart Job Match", key="chroma_btn"):
            with st.spinner("🧠 ChromaDB vector search running..."):
                smart_jobs = smart_job_match(st.session_state['resume_text'])
                st.session_state['smart_jobs'] = smart_jobs

        if 'smart_jobs' in st.session_state:
            st.markdown("### 🎯 AI-Powered Job Recommendations")
            for i, job in enumerate(st.session_state['smart_jobs']):
                score_j = job['similarity_score']
                emoji   = "🥇" if i==0 else "🥈" if i==1 else "🥉" if i==2 else "⭐"
                with st.expander(f"{emoji} {job['title']} — {score_j}% AI Match"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**AI Similarity Score:** {score_j}%")
                        st.progress(score_j / 100)
                        st.markdown(f"**💰 Salary Range:** {job['salary']}")
                        st.markdown(f"**🏢 Top Companies:** {job['companies']}")
                    with col2:
                        st.markdown("**Required Skills:**")
                        for s in job['required_skills']:
                            has_skill = s.lower() in [sk.lower() for sk in st.session_state['skills']]
                            st.markdown(f"{'✅' if has_skill else '❌'} {s}")

# ══════════════════════════════════════════════════════════
# TAB 4 — JD Matcher
# ══════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-title">🔍 Resume vs Job Description Matcher</div>', unsafe_allow_html=True)
    st.markdown("Paste any job description from LinkedIn/Naukri → AI compares with your resume!")

    if 'resume_text' not in st.session_state:
        st.info("👆 Please analyze your resume first!")
    else:
        jd_text = st.text_area(
            "Paste Job Description here:", height=250,
            placeholder="Paste the full job description here..."
        )

        if st.button("🔍 Match Resume with JD", key="jd_btn"):
            if jd_text.strip():
                with st.spinner("🤖 AI comparing resume with job description..."):
                    prompt = f"""
You are an expert ATS and career coach.
Compare this resume with the job description and give EXACTLY this format:

MATCH SCORE: [0-100]

MATCHED KEYWORDS:
- [keyword 1]
- [keyword 2]

MISSING KEYWORDS:
- [missing 1]
- [missing 2]

ATS SCORE: [0-100]

RECOMMENDATION:
[3-4 sentences]

TAILORING TIPS:
- [tip 1]
- [tip 2]

Resume:
{st.session_state['resume_text']}

Job Description:
{jd_text}
"""
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": prompt}]
                    )
                    jd_result = response.choices[0].message.content
                    st.session_state['jd_result'] = jd_result
            else:
                st.error("Please paste a job description!")

        if 'jd_result' in st.session_state:
            result = st.session_state['jd_result']

            try:
                match_score = min(int(''.join(filter(str.isdigit, [l for l in result.split('\n') if 'MATCH SCORE:' in l][0]))), 100)
            except:
                match_score = 60

            col1, col2 = st.columns(2)
            with col1:
                color = "#00ff88" if match_score>=70 else "#ffbb00" if match_score>=50 else "#ff4444"
                st.markdown(f"""<div class="metric-card">
                    <div style="font-size:3rem;font-weight:900;color:{color}">{match_score}%</div>
                    <div style="color:#8892a4">JD Match Score</div>
                </div>""", unsafe_allow_html=True)
                st.progress(match_score/100)
            with col2:
                try:
                    ats_score = min(int(''.join(filter(str.isdigit, [l for l in result.split('\n') if 'ATS SCORE:' in l][0]))), 100)
                except:
                    ats_score = 65
                color2 = "#00ff88" if ats_score>=70 else "#ffbb00" if ats_score>=50 else "#ff4444"
                st.markdown(f"""<div class="metric-card">
                    <div style="font-size:3rem;font-weight:900;color:{color2}">{ats_score}%</div>
                    <div style="color:#8892a4">ATS Score</div>
                </div>""", unsafe_allow_html=True)
                st.progress(ats_score/100)

            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(result)
            st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# TAB 5 — Interview Prep
# ══════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-title">🎯 AI Interview Question Generator</div>', unsafe_allow_html=True)

    if 'skills' not in st.session_state:
        st.info("👆 Please analyze your resume first!")
    else:
        col1, col2 = st.columns(2)
        with col1:
            job_titles   = [j['title'] for j in st.session_state.get('jobs', [])] or ["Data Scientist"]
            selected_job = st.selectbox("Select Target Job", job_titles)
        with col2:
            difficulty = st.selectbox("Difficulty Level", ["Entry Level", "Mid Level", "Senior Level"])

        if st.button("🎯 Generate Interview Questions", key="interview_btn"):
            with st.spinner("🤖 Generating questions..."):
                questions = generate_interview_questions(
                    st.session_state['skills'], f"{difficulty} {selected_job}"
                )
                st.session_state['questions']    = questions
                st.session_state['selected_job'] = selected_job

        if 'questions' in st.session_state:
            st.markdown(f"### 📝 {st.session_state['selected_job']} Interview Questions")
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(st.session_state['questions'])
            st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# TAB 6 — Learning Roadmap
# ══════════════════════════════════════════════════════════
with tab6:
    st.markdown('<div class="section-title">📚 AI Learning Roadmap</div>', unsafe_allow_html=True)

    if 'roadmap' in st.session_state:
        st.markdown(f"### 🗺️ Roadmap for {st.session_state.get('roadmap_job','')}")
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(st.session_state['roadmap'])
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Go to Smart Job Match tab → click 'Get Roadmap' on any job!")

    st.markdown("### ✏️ Custom Roadmap Generator")
    col1, col2 = st.columns(2)
    with col1:
        target_job = st.text_input("Target Job Title", value=user.get('job_target', ''))
    with col2:
        missing = st.text_input("Skills to Learn (comma separated)", placeholder="e.g. Deep Learning, Statistics")

    if st.button("📚 Generate My Roadmap", key="roadmap_btn"):
        if target_job and missing:
            missing_list = [s.strip() for s in missing.split(",")]
            with st.spinner("🤖 Creating personalized roadmap..."):
                roadmap = generate_skill_roadmap(missing_list, target_job)
                st.session_state['roadmap']     = roadmap
                st.session_state['roadmap_job'] = target_job
            st.rerun()
        else:
            st.error("Please fill in both fields!")

# ══════════════════════════════════════════════════════════
# TAB 7 — AI Career Chat
# ══════════════════════════════════════════════════════════
with tab7:
    st.markdown('<div class="section-title">💬 AI Career Mentor Chat</div>', unsafe_allow_html=True)
    st.markdown("Ask me anything about your career, resume, jobs, or skills! 🤖")

    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    for msg in st.session_state['chat_history']:
        if msg['role'] == 'user':
            st.markdown(f'<div class="chat-user">👤 <b>You:</b> {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-ai">🤖 <b>AI Mentor:</b> {msg["content"]}</div>', unsafe_allow_html=True)

    st.markdown("**Quick Questions:**")
    qcol1, qcol2, qcol3 = st.columns(3)
    with qcol1:
        if st.button("How to improve my resume?"):
            st.session_state['quick_q'] = "How can I improve my resume to get more interviews?"
    with qcol2:
        if st.button("Best jobs for my skills?"):
            skills_str = ', '.join(st.session_state.get('skills', [])[:5])
            st.session_state['quick_q'] = f"What are the best jobs for someone with these skills: {skills_str}?"
    with qcol3:
        if st.button("How to crack tech interviews?"):
            st.session_state['quick_q'] = "Give me tips to crack technical interviews at top tech companies."

    user_input = st.text_input(
        "Ask your career question:",
        value=st.session_state.pop('quick_q', ''),
        placeholder="e.g. How do I become a Data Scientist? What salary should I expect?"
    )

    if st.button("💬 Send", key="chat_btn"):
        if user_input.strip():
            context = f"User: {user.get('name','')}, Education: {user.get('education','')}, Target: {user.get('job_target','')}."
            if 'skills' in st.session_state:
                context += f" Skills: {', '.join(st.session_state['skills'])}. Score: {st.session_state.get('resume_score','unknown')}/100."
            prompt = f"""You are an expert career mentor.
{context}
Answer helpfully and practically (max 200 words).
Question: {user_input}"""
            with st.spinner("🤖 AI is thinking..."):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}]
                )
                ai_reply = response.choices[0].message.content
            st.session_state['chat_history'].append({"role": "user",      "content": user_input})
            st.session_state['chat_history'].append({"role": "assistant", "content": ai_reply})
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
    st.markdown('<div class="section-title">✍️ AI Resume Line Improver</div>', unsafe_allow_html=True)
    st.markdown("Paste any weak resume bullet point → AI makes it powerful and ATS-friendly! 💪")

    original_line = st.text_area(
        "Your resume line:",
        placeholder='e.g. "Worked on Python project" or "Did data analysis tasks"',
        height=100
    )

    if st.button("✨ Improve This Line", key="improve_btn"):
        if original_line.strip():
            with st.spinner("🤖 AI rewriting your resume line..."):
                improved = improve_resume_line(original_line)
                st.session_state['improved'] = improved
        else:
            st.error("Please enter a resume line!")

    if 'improved' in st.session_state:
        st.markdown("### ✅ AI Improved Versions:")
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(st.session_state['improved'])
        st.markdown('</div>', unsafe_allow_html=True)