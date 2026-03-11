import streamlit as st
import tempfile
import os
import random
import pandas as pd
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
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');

* { font-family: 'DM Sans', sans-serif; box-sizing: border-box; }
h1, h2, h3, h4, h5, h6,
.login-title, .profile-title, .hero-title, .section-title,
[class*="section-title"], strong { font-family: 'Sora', sans-serif; }
p, li, span, div { font-family: 'DM Sans', sans-serif; line-height: 1.65; }
code, pre { font-family: 'Fira Code', 'Courier New', monospace; }

.stApp { background: #080c14; }

.login-logo {
    font-family: 'Sora', sans-serif;
    font-size: 1.1rem; font-weight: 700; color: #00d4ff;
    letter-spacing: 2px; text-transform: uppercase;
    text-align: center; margin-bottom: 0.5rem;
}
.login-title {
    font-family: 'Sora', sans-serif;
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
    font-family: 'Sora', sans-serif;
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
.welcome-name { font-family:'Sora',sans-serif; font-size:1rem; font-weight:700; color:white; margin-bottom:0.2rem; }
.welcome-detail { color: #5a6478; font-size: 0.78rem; }
.welcome-email { color: #00d4ff; font-size: 0.75rem; margin-top: 0.3rem; }
.hero-title {
    font-family: 'Sora', sans-serif;
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
    font-family: 'Sora', sans-serif;
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

/* ── AI Output Rendering ──────────────────────────── */
.ai-block { font-family:'DM Sans',sans-serif; color:#d0dae8; line-height:1.75; }

.ai-section-heading {
    font-family:'Sora',sans-serif;
    font-size:1.05rem; font-weight:700;
    color:#00d4ff; letter-spacing:0.3px;
    margin: 1.4rem 0 0.5rem; padding: 0.35rem 0.75rem;
    border-left:3px solid #7b2ff7;
    background:rgba(0,212,255,0.04); border-radius:0 8px 8px 0;
}
.ai-sub-heading {
    font-family:'Sora',sans-serif;
    font-size:0.9rem; font-weight:600; color:#b0c4de;
    margin: 1rem 0 0.3rem;
}
.ai-bullet {
    display:flex; align-items:flex-start; gap:0.5rem;
    margin:0.35rem 0; padding:0.4rem 0.6rem;
    border-radius:8px; background:rgba(255,255,255,0.02);
}
.ai-bullet-icon { color:#00d4ff; font-size:0.8rem; margin-top:3px; flex-shrink:0; }
.ai-bullet-text { color:#c8d8e8; font-size:0.88rem; }

.ai-numbered {
    display:flex; align-items:flex-start; gap:0.6rem;
    margin:0.5rem 0; padding:0.5rem 0.75rem;
    background:rgba(123,47,247,0.05); border-radius:10px;
    border-left:2px solid rgba(123,47,247,0.3);
}
.ai-num-badge {
    background:linear-gradient(135deg,#00d4ff,#7b2ff7);
    color:white; font-family:'Sora',sans-serif;
    font-size:0.72rem; font-weight:700; width:22px; height:22px;
    border-radius:50%; display:flex; align-items:center;
    justify-content:center; flex-shrink:0; margin-top:1px;
}
.ai-num-content { flex:1; }
.ai-num-title { font-family:'Sora',sans-serif; font-weight:600; font-size:0.9rem; color:#e0eaf4; }
.ai-num-hint { font-size:0.8rem; color:#6a7f96; margin-top:2px; }
.ai-num-diff {
    font-size:0.72rem; font-weight:600; padding:2px 8px; border-radius:10px;
    margin-top:3px; display:inline-block;
}
.diff-easy { background:rgba(0,255,136,0.12); color:#00ff88; }
.diff-medium { background:rgba(255,187,0,0.12); color:#ffbb00; }
.diff-hard { background:rgba(255,68,68,0.12); color:#ff6b6b; }

.ai-score-row {
    display:flex; align-items:center; justify-content:space-between;
    padding:0.5rem 0.75rem; margin:0.3rem 0;
    background:rgba(255,255,255,0.03); border-radius:8px;
}
.ai-score-label { font-family:'Sora',sans-serif; font-size:0.82rem; color:#8892a4; }
.ai-score-val { font-family:'Sora',sans-serif; font-weight:700; font-size:0.88rem; color:#00d4ff; }

.ai-tag {
    display:inline-block; padding:3px 10px; border-radius:12px; margin:3px;
    font-size:0.78rem; font-weight:500;
}
.tag-green { background:rgba(0,255,136,0.1); color:#00ff88; border:1px solid rgba(0,255,136,0.2); }
.tag-red   { background:rgba(255,68,68,0.1);  color:#ff6b6b; border:1px solid rgba(255,68,68,0.2); }
.tag-blue  { background:rgba(0,212,255,0.1);  color:#00d4ff; border:1px solid rgba(0,212,255,0.2); }

.ai-summary-box {
    background:rgba(0,212,255,0.04); border:1px solid rgba(0,212,255,0.12);
    border-radius:12px; padding:1rem 1.2rem; margin:1rem 0;
    font-size:0.9rem; color:#b8cce0; line-height:1.7;
}
.chart-desc {
    font-size:0.82rem; color:#5a6478; font-style:italic;
    margin:0.2rem 0 0.8rem; padding:0.4rem 0.75rem;
    border-left:2px solid rgba(0,212,255,0.2);
}

/* ── Form & Enter-key UX ─────────────────────── */
.stForm { border: none !important; padding: 0 !important; }
[data-testid="stForm"] {
    border: none !important;
    background: transparent !important;
    padding: 0 !important;
}
/* Make form submit button match regular button style */
[data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(90deg, #00d4ff, #7b2ff7) !important;
    color: white !important; border: none !important;
    border-radius: 10px !important; font-weight: 600 !important;
    font-family: 'Sora', sans-serif !important;
    transition: opacity 0.2s ease !important;
    width: 100% !important;
}
[data-testid="stFormSubmitButton"] > button:hover {
    opacity: 0.88 !important;
}
/* Enter hint label */
.enter-hint {
    font-size: 0.72rem; color: #2a3a4a;
    text-align: right; margin-top: -0.4rem; margin-bottom: 0.5rem;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SENDER_EMAIL    = "nandu19jul@gmail.com"
SENDER_PASSWORD = "geyc nypl ctnc xexm"

def send_otp_email(to_email, otp):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Your OTP for AI Resume Analyzer: {otp}"
        msg["From"]    = SENDER_EMAIL
        msg["To"]      = to_email
        html = f"""
        <div style="font-family:Arial,sans-serif;max-width:480px;margin:auto;padding:32px;
                    background:#0d1117;border-radius:12px;border:1px solid #30363d;">
          <h2 style="color:#00d4ff;margin:0 0 8px;">🔐 Your OTP Code</h2>
          <p style="color:#8b949e;margin:0 0 24px;">Use this code to sign in to AI Resume Analyzer Pro</p>
          <div style="background:#161b22;border-radius:8px;padding:24px;text-align:center;
                      font-size:36px;font-weight:bold;letter-spacing:12px;color:#e6edf3;
                      border:1px solid #30363d;">{otp}</div>
          <p style="color:#8b949e;margin:24px 0 0;font-size:13px;">
            Valid for 10 minutes. Do not share this code with anyone.
          </p>
        </div>"""
        msg.attach(MIMEText(html, "html"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
            s.login(SENDER_EMAIL, SENDER_PASSWORD)
            s.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        return True
    except Exception as e:
        st.error(f"❌ Email error: {e}")
        return False


def send_phone_otp(phone, otp):
    """Send OTP via Fast2SMS using GET request (correct format)"""
    try:
        import urllib.request, urllib.parse, json as _json
        api_key = st.secrets.get("FAST2SMS_KEY", "")
        if not api_key:
            return False, "no_key"
        # Strip to last 10 digits
        number = phone.strip().replace("+91","").replace(" ","").replace("-","")
        if number.startswith("91") and len(number) == 12:
            number = number[2:]
        number = number[-10:]
        # Fast2SMS Quick SMS route (works without DLT registration)
        params = urllib.parse.urlencode({
            "authorization": api_key,
            "route":         "q",
            "message":       f"Your OTP for AI Resume Analyzer is {otp}. Valid for 10 minutes. Do not share.",
            "language":      "english",
            "flash":         0,
            "numbers":       number,
        })
        url = f"https://www.fast2sms.com/dev/bulkV2?{params}"
        req = urllib.request.Request(url, headers={"cache-control": "no-cache"})
        res = urllib.request.urlopen(req, timeout=10)
        result = _json.loads(res.read())
        if result.get("return") == True:
            return True, "sms"
        return False, result.get("message", "failed")
    except Exception as e:
        return False, str(e)


def get_user(identifier):
    """Get user by email or phone"""
    if not identifier:
        return None
    doc = db.collection("users").document(identifier).get()
    return doc.to_dict() if doc.exists else None


def save_session_token(identifier, token):
    """Save a persistent session token so app reopens without login"""
    db.collection("sessions").document(token).set({
        "identifier": identifier,
        "created": datetime.datetime.now().isoformat()
    })


def get_session_user(token):
    """Return user data if session token is valid"""
    if not token:
        return None
    doc = db.collection("sessions").document(token).get()
    if not doc.exists:
        return None
    data = doc.to_dict()
    return get_user(data.get("identifier",""))


def delete_session_token(token):
    """Remove session token on logout"""
    if token:
        try:
            db.collection("sessions").document(token).delete()
        except:
            pass


def create_user(email, name, job_target, education, purpose, bot_nickname="Aria"):
    db.collection("users").document(email).set({
        "email": email, "name": name,
        "job_target": job_target, "education": education,
        "purpose": purpose, "bot_nickname": bot_nickname
    })


# ══════════════════════════════════════════════════════════
# AI OUTPUT RENDERER
# ══════════════════════════════════════════════════════════

def render_ai_analysis(raw_text):
    import re
    html = '<div class="ai-block">'
    lines = raw_text.split("\n")
    section_icons = {
        "SCORE": "&#127919;", "STRENGTH": "&#9989;", "WEAKNESS": "&#9888;",
        "SUGGESTION": "&#128161;", "SUMMARY": "&#128203;",
        "BREAKDOWN": "&#128202;", "ATS": "&#129302;",
        "KEYWORD": "&#128273;", "RECOMMENDATION": "&#128204;",
        "TAILORING": "&#128295;", "ROADMAP": "&#128506;",
        "INTERVIEW": "&#127914;", "EXPERIENCE": "&#128084;", "OVERALL": "&#127942;",
    }
    for line in lines:
        s = line.strip()
        if not s:
            continue
        # Section headings (CAPS:)
        hm = re.match(r"^([A-Z][A-Z _&/\-]{2,}):(.*)$", s)
        if hm:
            key  = hm.group(1).strip()
            val  = hm.group(2).strip()
            icon = next((v for k, v in section_icons.items() if k in key), "&#128204;")
            clean = key.replace("_", " ").title()
            html += f'<div class="ai-section-heading">{icon} {clean}</div>'
            if val:
                html += f'<div class="ai-summary-box" style="padding:0.5rem 1rem;margin:0.25rem 0 0.5rem;">{val}</div>'
            continue
        # Bullet points
        if s.startswith("- ") or s.startswith("* "):
            text = s[2:].strip()
            html += f'<div class="ai-bullet"><span class="ai-bullet-icon">&#9656;</span><span class="ai-bullet-text">{text}</span></div>'
            continue
        # Numbered items
        nm = re.match(r"^(\d+)\. (.+)$", s)
        if nm:
            n, text = nm.group(1), nm.group(2)
            html += f'<div class="ai-numbered"><div class="ai-num-badge">{n}</div><div class="ai-num-content"><div class="ai-num-title">{text}</div></div></div>'
            continue
        # Score breakdown X/Y
        sm = re.match(r"^-?\s*(.+):\s*(\d+)/(\d+)\s*$", s)
        if sm:
            label, got, mx = sm.group(1).strip(), sm.group(2), sm.group(3)
            html += f'<div class="ai-score-row"><span class="ai-score-label">{label}</span><span class="ai-score-val">{got}/{mx}</span></div>'
            continue
        # Separators
        if len(set(s)) <= 3 and set(s) <= set("=-_"):
            html += "<hr style='border:none;border-top:1px solid rgba(255,255,255,0.05);margin:0.5rem 0'>"
            continue
        # Emoji/hint lines
        if s[:2] in ("&#", "**"):
            html += f'<div style="color:#8892a4;font-size:0.83rem;padding:0.2rem 0.8rem;">{s}</div>'
            continue
        # Normal text
        html += f'<div style="color:#9aaec8;font-size:0.88rem;padding:0.2rem 0.4rem;line-height:1.65;">{s}</div>'
    html += "</div>"
    return html


# ══════════════════════════════════════════════════════════
# SESSION STATE INIT
# ══════════════════════════════════════════════════════════

import hashlib, time

def _make_token(identifier):
    return hashlib.sha256(f"{identifier}{time.time()}".encode()).hexdigest()[:32]

# ── Set defaults FIRST (only if key not already present) ──
_defaults = {
    "page":          "login",
    "otp_sent":      False,
    "otp_code":      "",
    "otp_email":     "",
    "otp_phone":     "",
    "login_method":  "",
    "user":          None,
    "bot_nickname":  "",
    "chat_history":  [],
    "language":      "English",
    "session_token": "",
}
for _k, _v in _defaults.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ── Persistent session: check token ONLY once (when user is None) ──
if st.session_state.user is None and st.session_state.page == "login":
    _qt = st.query_params.get("s", "")
    if _qt:
        try:
            _sess_user = get_session_user(_qt)
            if _sess_user and _sess_user.get("name") and _sess_user.get("education"):
                st.session_state.user          = _sess_user
                st.session_state.bot_nickname  = _sess_user.get("bot_nickname", "Aria")
                st.session_state.language      = _sess_user.get("language", "English")
                st.session_state.session_token = _qt
                st.session_state.page          = "app"
                st.rerun()
        except Exception:
            pass  # bad token — stay on login page


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

        # ── STEP 1: Choose method ─────────────────────────
        if not st.session_state.login_method and not st.session_state.otp_sent:
            st.markdown("##### 👋 Sign in to continue")
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            col_e, col_p = st.columns(2)
            with col_e:
                if st.button("📧 Continue with Email", key="choose_email", use_container_width=True):
                    st.session_state.login_method = "email"
                    st.rerun()
            with col_p:
                if st.button("📱 Continue with Phone", key="choose_phone", use_container_width=True):
                    st.session_state.login_method = "phone"
                    st.rerun()
            st.markdown("""
            <div style="text-align:center;margin-top:2rem;color:#2a3040;font-size:0.8rem;">
                🔒 Secure OTP login · No password needed · Free forever
            </div>""", unsafe_allow_html=True)

        # ── STEP 2a: Email — enter address ────────────────
        elif st.session_state.login_method == "email" and not st.session_state.otp_sent:
            st.markdown("##### 📧 Sign in with Email OTP")
            if st.button("← Back", key="back_email"):
                st.session_state.login_method = ""
                st.rerun()
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
            with st.form("email_form", clear_on_submit=False):
                email_input = st.text_input("Email Address", placeholder="you@example.com",
                                             label_visibility="collapsed")
                submitted = st.form_submit_button("📨 Send OTP →", use_container_width=True)
            st.markdown('<div class="enter-hint">⌨️ Press Enter or click the button</div>', unsafe_allow_html=True)
            if submitted:
                _e = email_input.strip()
                if _e and "@" in _e and "." in _e:
                    with st.spinner("Sending OTP to your inbox..."):
                        otp = str(random.randint(100000, 999999))
                        if send_otp_email(_e, otp):
                            st.session_state.otp_sent  = True
                            st.session_state.otp_code  = otp
                            st.session_state.otp_email = _e
                            st.rerun()
                        else:
                            st.error("❌ Failed to send OTP. Check your email and try again.")
                else:
                    st.error("❌ Enter a valid email address.")

        # ── STEP 2b: Phone — enter number ─────────────────
        elif st.session_state.login_method == "phone" and not st.session_state.otp_sent:
            st.markdown("##### 📱 Sign in with Phone OTP")
            if st.button("← Back", key="back_phone"):
                st.session_state.login_method = ""
                st.rerun()
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
            with st.form("phone_form", clear_on_submit=False):
                phone_input = st.text_input("Phone Number", placeholder="+91 9876543210",
                                             label_visibility="collapsed")
                submitted_ph = st.form_submit_button("📨 Send OTP →", use_container_width=True)
            st.markdown('<div class="enter-hint">⌨️ Press Enter or click the button</div>', unsafe_allow_html=True)
            if submitted_ph:
                _ph = phone_input.strip().replace(" ","").replace("-","")
                if len(_ph) >= 10:
                    with st.spinner("Sending OTP to your phone..."):
                        otp = str(random.randint(100000, 999999))
                        ok, mode = send_phone_otp(_ph, otp)
                    if ok:
                        st.session_state.otp_sent  = True
                        st.session_state.otp_code  = otp
                        st.session_state.otp_phone = _ph
                        st.rerun()
                    elif mode == "no_key":
                        st.error("❌ Fast2SMS API key not configured in Streamlit secrets. Add FAST2SMS_KEY.")
                    else:
                        st.error(f"❌ SMS failed: {mode}")
                        st.info("💡 Use 📧 Email OTP instead — it works perfectly!")
                else:
                    st.error("❌ Enter a valid phone number (min 10 digits).")

        # ── STEP 3: Enter OTP (same for email and phone) ──
        elif st.session_state.otp_sent:
            _identifier  = st.session_state.otp_email or st.session_state.otp_phone
            _is_email    = bool(st.session_state.otp_email)
            st.markdown(f"""
            <div class="otp-box">
                <p>OTP sent to <strong>{_identifier}</strong></p>
                <p style="margin-top:0.3rem;font-size:0.78rem;">
                    {'📧 Check your inbox &amp; spam folder' if _is_email else '📱 Check your SMS messages'}
                </p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown('<div class="enter-hint">⌨️ Enter OTP and press Enter</div>', unsafe_allow_html=True)
            with st.form("otp_form", clear_on_submit=False):
                otp_input = st.text_input("Enter 6-digit OTP", placeholder="e.g. 482910",
                                           max_chars=6, label_visibility="collapsed")
                col_v, col_rs = st.columns(2)
                with col_v:
                    verify = st.form_submit_button("✅ Verify & Login", use_container_width=True)
                with col_rs:
                    resend = st.form_submit_button("🔄 Resend OTP", use_container_width=True)

            if verify:
                if otp_input.strip() == st.session_state.otp_code:
                    st.session_state.otp_sent = False
                    st.session_state.otp_code = ""
                    _id    = st.session_state.otp_email or st.session_state.otp_phone
                    _saved = get_user(_id) or {}
                    _has   = bool(_saved.get("name") and _saved.get("education") and _saved.get("job_target"))
                    if _has:
                        # ✅ Returning user — straight to app, no questions asked
                        st.session_state.user = {
                            "email":      _id,
                            "name":       _saved["name"],
                            "education":  _saved["education"],
                            "job_target": _saved["job_target"],
                            "purpose":    _saved.get("purpose",""),
                        }
                        st.session_state.bot_nickname = _saved.get("bot_nickname","Aria")
                        st.session_state.language     = _saved.get("language","English")
                        _tok = _make_token(_id)
                        save_session_token(_id, _tok)
                        st.session_state.session_token = _tok
                        st.query_params["s"] = _tok
                        st.session_state.page = "app"
                    else:
                        # 🆕 New user — profile page once only
                        st.session_state.page = "profile"
                    st.rerun()
                else:
                    st.error("❌ Wrong OTP. Try again.")

            if resend:
                otp = str(random.randint(100000, 999999))
                _id = st.session_state.otp_email or st.session_state.otp_phone
                if st.session_state.otp_email:
                    ok = send_otp_email(_id, otp)
                    if ok:
                        st.session_state.otp_code = otp
                        st.success("✅ New OTP sent to your inbox!")
                else:
                    ok, mode = send_phone_otp(_id, otp)
                    if ok:
                        st.session_state.otp_code = otp
                        st.success("✅ New OTP sent to your phone!")
                    else:
                        st.error(f"❌ Could not resend: {mode}")

        st.markdown("""
        <div style="text-align:center;margin-top:2rem;color:#2a3040;font-size:0.8rem;">
            🔒 Secure login · No password needed · Free to use
        </div>
        """, unsafe_allow_html=True)
    st.stop()


# ══════════════════════════════════════════════════════════
# PAGE: PROFILE
# ══════════════════════════════════════════════════════════

if st.session_state.page == "profile":
    # This page is shown ONLY ONCE — first time user logs in
    _id    = st.session_state.get("otp_email") or st.session_state.get("otp_phone","")
    _saved = {}  # Always blank — first time only

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("""
        <div style="height:30px"></div>
        <div style="text-align:center;font-size:3rem;margin-bottom:0.5rem;">👤</div>
        <div class="profile-title">One last step!</div>
        <div class="profile-sub">Tell us about yourself — we only ask this once.</div>
        <div style="height:10px"></div>
        <div style="text-align:center"><span class="step-badge">Step 2 of 2 — Profile Setup</span></div>
        <div style="height:16px"></div>
        """, unsafe_allow_html=True)

        st.markdown(f"**✅ Verified:** `{_id}`")
        st.markdown("---")

        with st.form("profile_form", clear_on_submit=False):
            name       = st.text_input("👤 Full Name",          placeholder="e.g. Priya Sharma")
            education  = st.text_input("🎓 Education / Degree", placeholder="e.g. B.Tech Computer Science")
            job_target = st.text_input("🎯 Target Job Role",    placeholder="e.g. Data Scientist, SDE, Product Manager")

            purpose_options = ["Campus Placement","Internship","Full-time Job","Career Switch","Higher Studies","Freelance / Gig Work"]
            purpose = st.selectbox("📌 Why are you using this app?", purpose_options)

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            submitted_profile = st.form_submit_button("🚀 Save & Continue →", use_container_width=True)

        if submitted_profile:
            if name.strip() and education.strip() and job_target.strip():
                create_user(_id, name.strip(), job_target.strip(), education.strip(), purpose)
                st.session_state.user = {
                    "email":      _id,
                    "name":       name.strip(),
                    "education":  education.strip(),
                    "job_target": job_target.strip(),
                    "purpose":    purpose
                }
                if not st.session_state.bot_nickname:
                    st.session_state.page = "nickname"
                else:
                    # Save session token for persistence
                    _tok = _make_token(_id)
                    save_session_token(_id, _tok)
                    st.session_state.session_token = _tok
                    st.query_params["s"] = _tok
                    st.session_state.page = "app"
                st.rerun()
            else:
                st.error("❌ Please fill in all fields to continue.")
    st.stop()


# ══════════════════════════════════════════════════════════
# PAGE: NICKNAME — What should we call our AI?
# ══════════════════════════════════════════════════════════

if st.session_state.page == "nickname":

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("""
        <div style="height:30px"></div>
        <div style="text-align:center;font-size:3.5rem;margin-bottom:0.5rem;">🤖</div>
        <div class="profile-title">One Last Thing!</div>
        <div class="profile-sub">Give your AI Career Mentor a name — make it yours!</div>
        <div style="height:10px"></div>
        <div style="text-align:center"><span class="step-badge">Step 3 of 3 — Personalize</span></div>
        <div style="height:20px"></div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background:rgba(0,212,255,0.05);border:1px solid rgba(0,212,255,0.15);
                    border-radius:14px;padding:1.2rem;margin-bottom:1rem;text-align:center;">
            <p style="color:#8892a4;font-size:0.88rem;margin:0 0 0.5rem;">
                💡 Your AI mentor will use this name in every conversation.<br/>
                You can change it anytime from Settings.
            </p>
            <p style="color:#5a6478;font-size:0.8rem;margin:0;">
                Popular names: <b style="color:#00d4ff">Chitti</b> · <b style="color:#00d4ff">Jarvis</b> · 
                <b style="color:#00d4ff">Nova</b> · <b style="color:#00d4ff">Aria</b> · <b style="color:#00d4ff">Max</b>
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        with st.form("nickname_form", clear_on_submit=False):
            nickname = st.text_input(
                "🤖 Name your AI mentor",
                placeholder="e.g. Chitti, Jarvis, Nova, Aria...",
                max_chars=20,
                label_visibility="collapsed"
            )
            col_a, col_b = st.columns(2)
            with col_a:
                set_name = st.form_submit_button("✨ Set Name & Enter App", use_container_width=True)
            with col_b:
                skip_name = st.form_submit_button("⏭️ Skip (Use 'Aria')", use_container_width=True)

        if set_name or skip_name:
            final_nick = (nickname.strip() if nickname.strip() else "Aria") if set_name else "Aria"
            st.session_state.bot_nickname = final_nick
            _uid = st.session_state.user.get("email","") if st.session_state.user else ""
            if _uid:
                db.collection("users").document(_uid).update({"bot_nickname": final_nick})
            # Save session token for app-reopen persistence
            _tok = _make_token(_uid or "user")
            save_session_token(_uid, _tok)
            st.session_state.session_token = _tok
            st.query_params["s"] = _tok
            st.session_state.page = "app"
            st.rerun()

    st.stop()

user = st.session_state.get("user") or {}

if not user:
    # Not logged in — force back to login page cleanly
    delete_session_token(st.session_state.get("session_token",""))
    st.query_params.clear()
    st.session_state.clear()
    st.session_state.page = "login"
    st.rerun()

name       = user.get("name", "")
education  = user.get("education", "")
job_target = user.get("job_target", "")
email      = user.get("email", "")
initials   = name[0].upper() if name else "?"

# ─── Sidebar ───────────────────────────────────────────────
with st.sidebar:

    bot_nick = st.session_state.get("bot_nickname", "Aria")

    # Welcome card
    st.markdown(f"""
    <div class="welcome-card">
        <div style="width:52px;height:52px;background:linear-gradient(135deg,#00d4ff,#7b2ff7);
                    border-radius:50%;display:flex;align-items:center;justify-content:center;
                    font-size:1.5rem;margin:0 auto 0.75rem;">{initials}</div>
        <div class="welcome-name">👋 {name}</div>
        <div class="welcome-detail">🎓 {education}</div>
        <div class="welcome-detail">🎯 {job_target}</div>
        <div class="welcome-email">✉️ {email}</div>
        <div style="margin-top:0.5rem;color:#7b2ff7;font-size:0.78rem;font-weight:600;">
            🤖 AI Mentor: <span style="color:#00d4ff">{bot_nick}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Resume Stats
    if 'skills' in st.session_state:
        st.markdown("### 📊 Resume Stats")
        st.metric("Skills Found", len(st.session_state['skills']))
        if 'resume_score' in st.session_state:
            score_val = st.session_state['resume_score']
            score_color = "🟢" if score_val >= 70 else "🟡" if score_val >= 50 else "🔴"
            st.metric("Resume Score", f"{score_color} {score_val}/100")
        if 'jobs' in st.session_state:
            st.metric("Best Job Match", st.session_state['jobs'][0]['title'])
        st.markdown("---")

    # Bottom actions
    st.markdown("<div style='flex:1'></div>", unsafe_allow_html=True)

    if st.button("⚙️ Settings", key="goto_settings_btn"):
        st.session_state.page = "settings"
        st.rerun()

    if st.button("🚪 Logout", key="logout_btn"):
        delete_session_token(st.session_state.get("session_token",""))
        st.query_params.clear()
        st.session_state.clear()
        st.session_state.page = "login"
        st.rerun()


# ══════════════════════════════════════════════════════════
# PAGE: SETTINGS
# ══════════════════════════════════════════════════════════

if st.session_state.page == "settings":

    bot_nick = st.session_state.get("bot_nickname", "Aria")

    with st.sidebar:
        st.markdown(f"""
        <div class="welcome-card">
            <div style="width:44px;height:44px;background:linear-gradient(135deg,#00d4ff,#7b2ff7);
                        border-radius:50%;display:flex;align-items:center;justify-content:center;
                        font-size:1.2rem;margin:0 auto 0.6rem;">{initials}</div>
            <div class="welcome-name">{name}</div>
            <div class="welcome-email">✉️ {email}</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")
        if st.button("← Back to App", key="settings_back"):
            st.session_state.page = "app"
            st.rerun()
        if st.button("🚪 Logout", key="settings_logout"):
            delete_session_token(st.session_state.get("session_token",""))
            st.query_params.clear()
            st.session_state.clear()
            st.session_state.page = "login"
            st.rerun()

    st.markdown('<div class="hero-title">⚙️ Settings</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Manage your account, preferences and personalization</div>', unsafe_allow_html=True)
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    s1, s2 = st.columns(2)

    with s1:
        # ── AI Mentor Personalization ──────────────────────
        st.markdown("""<div class="section-title">🤖 AI Mentor Name</div>""", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:rgba(0,212,255,0.05);border:1px solid rgba(0,212,255,0.15);
                    border-radius:12px;padding:1rem;margin-bottom:0.8rem;">
            <p style="color:#8892a4;font-size:0.85rem;margin:0 0 0.3rem;">Current AI Mentor Name</p>
            <p style="color:#00d4ff;font-size:1.4rem;font-weight:800;margin:0;">🤖 {bot_nick}</p>
        </div>
        """, unsafe_allow_html=True)
        with st.form("nick_form", clear_on_submit=False):
            new_nick = st.text_input("Change AI Mentor Name", placeholder="e.g. Chitti, Jarvis, Nova...",
                                      max_chars=20)
            save_nick = st.form_submit_button("💾 Save Mentor Name", use_container_width=True)
        st.caption("Popular: Chitti · Jarvis · Nova · Aria · Max · Zara · Atlas")
        if save_nick:
            if new_nick.strip():
                st.session_state.bot_nickname = new_nick.strip()
                db.collection("users").document(email).update({"bot_nickname": new_nick.strip()})
                st.success(f"✅ AI Mentor renamed to **{new_nick.strip()}**!")
                st.rerun()
            else:
                st.error("Please enter a name.")

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        # ── Language ──────────────────────────────────────
        st.markdown("""<div class="section-title">🌐 Language</div>""", unsafe_allow_html=True)
        languages = ["English", "Hindi", "Tamil", "Telugu", "Kannada", "Malayalam",
                     "Bengali", "Marathi", "Gujarati", "Spanish", "French", "German"]
        curr_lang = st.session_state.get("language", "English")
        lang_idx = languages.index(curr_lang) if curr_lang in languages else 0
        with st.form("lang_form", clear_on_submit=False):
            new_lang = st.selectbox("App Language", languages, index=lang_idx)
            save_lang = st.form_submit_button("💾 Save Language", use_container_width=True)
        if save_lang:
            st.session_state.language = new_lang
            st.success(f"✅ Language set to **{new_lang}**!")

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        # ── Appearance ────────────────────────────────────
        st.markdown("""<div class="section-title">🎨 Appearance</div>""", unsafe_allow_html=True)
        st.radio("Theme", ["Dark", "Light"], index=0, key="setting_theme")
        st.select_slider("Font Size", options=["Small", "Medium", "Large"], value="Medium", key="setting_font")
        st.caption("💡 Theme & font changes apply on next reload.")

    with s2:
        # ── Account & Profile ─────────────────────────────
        st.markdown("""<div class="section-title">👤 Account & Profile</div>""", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="card">
            <p style="color:#8892a4;font-size:0.82rem;margin:0 0 0.8rem;">Your saved profile details</p>
            <p style="color:white;margin:0.3rem 0;"><b style="color:#00d4ff">📧 Email:</b> {email}</p>
            <p style="color:white;margin:0.3rem 0;"><b style="color:#00d4ff">👤 Name:</b> {name}</p>
            <p style="color:white;margin:0.3rem 0;"><b style="color:#00d4ff">🎓 Education:</b> {education}</p>
            <p style="color:white;margin:0.3rem 0;"><b style="color:#00d4ff">🎯 Target Role:</b> {job_target}</p>
            <p style="color:white;margin:0.3rem 0;"><b style="color:#00d4ff">🤖 AI Mentor:</b> {bot_nick}</p>
            <p style="color:white;margin:0.3rem 0;"><b style="color:#00d4ff">🌐 Language:</b> {st.session_state.get('language','English')}</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("✏️ Edit Profile Details", key="settings_edit_profile"):
            st.session_state.page = "profile"
            st.rerun()

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        # ── Notifications ─────────────────────────────────
        st.markdown("""<div class="section-title">🔔 Notifications</div>""", unsafe_allow_html=True)
        st.toggle("Email tips & career updates", value=False, key="setting_notif")
        st.toggle("Show score improvement alerts", value=True, key="setting_alerts")
        st.toggle("Job match notifications", value=True, key="setting_job_notif")

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        # ── Help & Support ────────────────────────────────
        st.markdown("""<div class="section-title">❓ Help & Support</div>""", unsafe_allow_html=True)
        st.markdown("""
        <div class="card">
            <p style="color:#c0cce0;font-size:0.88rem;margin:0 0 0.5rem;"><b>📖 How to use:</b></p>
            <p style="color:#8892a4;font-size:0.82rem;margin:0.2rem 0;">1. Upload resume (PDF / DOCX / TXT)</p>
            <p style="color:#8892a4;font-size:0.82rem;margin:0.2rem 0;">2. Click Analyze My Resume</p>
            <p style="color:#8892a4;font-size:0.82rem;margin:0.2rem 0;">3. Explore all 7 tabs for insights</p>
            <p style="color:#8892a4;font-size:0.82rem;margin:0.2rem 0;">4. Chat with your AI mentor anytime!</p>
            <p style="color:#c0cce0;font-size:0.88rem;margin:0.8rem 0 0.3rem;"><b>🔧 Contact:</b></p>
            <p style="color:#00d4ff;font-size:0.82rem;margin:0;">support@airesume.pro</p>
            <p style="color:#5a6478;font-size:0.75rem;margin:0.5rem 0 0;">Version 1.0.0 · Built with Streamlit + Groq AI</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        # ── Danger Zone ───────────────────────────────────
        st.markdown("""<div class="section-title" style="border-left-color:#ff4444;color:#ff4444">⚠️ Session</div>""", unsafe_allow_html=True)
        if st.button("🚪 Logout & Clear Session", key="settings_logout_main"):
            delete_session_token(st.session_state.get("session_token",""))
            st.query_params.clear()
            st.session_state.clear()
            st.session_state.page = "login"
            st.rerun()

    st.stop()


# ══════════════════════════════════════════════════════════
# PAGE: MAIN APP — guard
# ══════════════════════════════════════════════════════════
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
    f"💬 Chat with {st.session_state.get('bot_nickname','Aria')}", "✍️ Resume Improver"
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
        st.markdown(render_ai_analysis(analysis), unsafe_allow_html=True)

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
        st.markdown("""
        <div class="ai-summary-box">
            📌 <b>How to use this tab:</b> First go to <b>Upload & Analyze</b>, upload your resume,
            and click <b>Analyze My Resume</b>. Then come back here to see your visual analytics.
        </div>""", unsafe_allow_html=True)
    else:
        score      = st.session_state['resume_score']
        skills     = st.session_state['skills']
        categories = st.session_state['categories']
        jobs       = st.session_state.get('jobs', [])
        analysis   = st.session_state.get('analysis', '')

        # ── Parse score breakdown from analysis ──────────────
        breakdown = {}
        breakdown_labels = {
            "Contact": "Contact & Info",
            "Summary": "Summary",
            "Experience": "Experience",
            "Skills": "Skills",
            "Education": "Education",
            "Projects": "Projects",
            "Certifications": "Certifications",
            "Formatting": "Formatting"
        }
        import re
        for key, label in breakdown_labels.items():
            match = re.search(rf"{key}.*?(\d+)/(\d+)", analysis)
            if match:
                breakdown[label] = {"got": int(match.group(1)), "max": int(match.group(2))}

        # ── Row 1: Score Gauge + Skills Donut ────────────────
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 🎯 Resume Score")
            st.markdown('<div class="chart-desc">Your overall resume quality score out of 100. Green = job-ready (70+), Yellow = needs work (50–70), Red = urgent improvements needed.</div>', unsafe_allow_html=True)
            color = "#00ff88" if score >= 70 else "#ffbb00" if score >= 50 else "#ff4444"
            label_text = "Job Ready! 🚀" if score >= 70 else "Needs Work 📈" if score >= 50 else "Urgent Fix ⚠️"
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': label_text, 'font': {'color': color, 'family': 'Sora', 'size': 14}},
                number={'font': {'color': color, 'size': 48, 'family': 'Sora'}},
                gauge={
                    'axis': {'range': [0, 100], 'tickcolor': "#5a6478", 'tickfont': {'color': '#5a6478'}},
                    'bar': {'color': color, 'thickness': 0.28},
                    'bgcolor': "rgba(0,0,0,0)",
                    'borderwidth': 0,
                    'steps': [
                        {'range': [0, 50],  'color': 'rgba(255,68,68,0.12)'},
                        {'range': [50, 70], 'color': 'rgba(255,187,0,0.12)'},
                        {'range': [70, 100],'color': 'rgba(0,255,136,0.12)'}
                    ],
                    'threshold': {'line': {'color': color, 'width': 3}, 'thickness': 0.85, 'value': score}
                }
            ))
            fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': 'white'}, height=280, margin=dict(t=40, b=10, l=20, r=20))
            st.plotly_chart(fig_gauge, use_container_width=True)

        with col2:
            st.markdown("#### 🧠 Skills by Category")
            st.markdown('<div class="chart-desc">Breakdown of your skills by domain. Hover over each slice to see how many skills you have per category. A balanced chart means you are well-rounded.</div>', unsafe_allow_html=True)
            if categories:
                cat_names = list(categories.keys())
                cat_counts = [len(v) for v in categories.values()]
                fig_pie = go.Figure(go.Pie(
                    labels=cat_names,
                    values=cat_counts,
                    hole=0.5,
                    textinfo='label+value',
                    hovertemplate='<b>%{label}</b><br>%{value} skills<br>%{percent}<extra></extra>',
                    marker=dict(colors=['#00d4ff','#7b2ff7','#00ff88','#ffbb00','#ff6b6b','#ff8c00','#a78bfa','#34d399'],
                                line=dict(color='#080c14', width=2))
                ))
                fig_pie.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', font={'color': 'white', 'family': 'DM Sans'},
                    height=280, margin=dict(t=10, b=10, l=10, r=10),
                    legend=dict(font=dict(size=11), bgcolor='rgba(0,0,0,0)')
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("No skill categories detected yet.")

        # ── Row 2: Score Breakdown Bar ────────────────────────
        if breakdown:
            st.markdown("#### 📋 Score Breakdown by Section")
            st.markdown('<div class="chart-desc">How you scored in each section of your resume. Each bar shows your actual score vs the maximum possible. Focus on the shortest bars first.</div>', unsafe_allow_html=True)
            bd_labels = list(breakdown.keys())
            bd_got    = [breakdown[k]["got"] for k in bd_labels]
            bd_max    = [breakdown[k]["max"] for k in bd_labels]
            bd_pct    = [round(g/m*100) if m > 0 else 0 for g, m in zip(bd_got, bd_max)]
            bd_colors = ['#00ff88' if p >= 70 else '#ffbb00' if p >= 40 else '#ff4444' for p in bd_pct]
            fig_bd = go.Figure()
            fig_bd.add_trace(go.Bar(
                name='Your Score', x=bd_labels, y=bd_got,
                marker_color=bd_colors,
                text=[f"{g}/{m}" for g, m in zip(bd_got, bd_max)],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Got: %{y}<br>Max: %{customdata}<extra></extra>',
                customdata=bd_max
            ))
            fig_bd.add_trace(go.Bar(
                name='Remaining', x=bd_labels, y=[m - g for g, m in zip(bd_got, bd_max)],
                marker_color='rgba(255,255,255,0.05)',
                hoverinfo='skip'
            ))
            fig_bd.update_layout(
                barmode='stack', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font={'color': 'white', 'family': 'DM Sans'},
                xaxis={'tickfont': {'size': 11}}, yaxis={'visible': False},
                height=320, margin=dict(t=30, b=10, l=10, r=10),
                legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(size=10)),
                showlegend=True
            )
            st.plotly_chart(fig_bd, use_container_width=True)

        # ── Row 3: Job Match Bar ──────────────────────────────
        if jobs:
            st.markdown("#### 💼 Job Match Scores")
            st.markdown('<div class="chart-desc">How well your resume matches different job roles based on your skills and experience. Green bars (70%+) are your best-fit jobs to apply for right now.</div>', unsafe_allow_html=True)
            jt = [j['title'] for j in jobs[:8]]
            js = [j.get('match_score') or j.get('similarity_score', 0) for j in jobs[:8]]
            cb = ['#00ff88' if s >= 70 else '#ffbb00' if s >= 40 else '#ff4444' for s in js]
            fig_bar = go.Figure(go.Bar(
                x=js, y=jt, orientation='h',
                marker_color=cb,
                text=[f"{s}%" for s in js], textposition='outside',
                hovertemplate='<b>%{y}</b><br>Match: %{x}%<extra></extra>'
            ))
            fig_bar.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font={'color': 'white', 'family': 'DM Sans'},
                xaxis={'range': [0, 115], 'showgrid': False, 'ticksuffix': '%'},
                yaxis={'tickfont': {'size': 11}},
                height=380, margin=dict(t=10, b=10, l=10, r=60)
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        # ── Row 4: Skill Radar ────────────────────────────────
        if categories and len(categories) >= 3:
            st.markdown("#### 🕸️ Skill Coverage Radar")
            st.markdown('<div class="chart-desc">A radar (spider) chart showing how many skills you have in each category. A larger, rounder shape means broader skill coverage. Narrow spikes mean you are specialized in few areas.</div>', unsafe_allow_html=True)
            rc = list(categories.keys())
            rv = [len(v) for v in categories.values()]
            rc_closed = rc + [rc[0]]
            rv_closed = rv + [rv[0]]
            fig_r = go.Figure(go.Scatterpolar(
                r=rv_closed, theta=rc_closed, fill='toself',
                fillcolor='rgba(0,212,255,0.10)',
                line=dict(color='#00d4ff', width=2),
                marker=dict(color='#7b2ff7', size=6),
                hovertemplate='<b>%{theta}</b><br>%{r} skills<extra></extra>'
            ))
            fig_r.update_layout(
                polar=dict(
                    bgcolor='rgba(0,0,0,0)',
                    radialaxis=dict(visible=True, gridcolor='rgba(255,255,255,0.08)', color='#5a6478', tickfont=dict(size=9)),
                    angularaxis=dict(gridcolor='rgba(255,255,255,0.08)', color='#8892a4', tickfont=dict(size=11))
                ),
                paper_bgcolor='rgba(0,0,0,0)', font={'color': 'white', 'family': 'DM Sans'},
                height=380, margin=dict(t=20, b=20, l=20, r=20)
            )
            st.plotly_chart(fig_r, use_container_width=True)

        # ── Score Comparison (if previous exists) ─────────────
        if 'previous_score' in st.session_state:
            prev = st.session_state['previous_score']
            st.markdown("#### 📈 Score Improvement")
            st.markdown('<div class="chart-desc">Comparison between your previous upload and current resume score. Green bar = improvement!</div>', unsafe_allow_html=True)
            diff = score - prev
            c_prev = '#ff6b6b' if prev < score else '#00ff88'
            c_curr = '#00ff88' if score >= prev else '#ff4444'
            fig_c = go.Figure(go.Bar(
                x=['Previous Resume', 'Current Resume'],
                y=[prev, score],
                marker_color=[c_prev, c_curr],
                text=[f"{prev}/100", f"{score}/100"],
                textposition='outside',
                hovertemplate='%{x}: %{y}/100<extra></extra>'
            ))
            fig_c.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font={'color': 'white', 'family': 'DM Sans'},
                yaxis={'range': [0, 115], 'showgrid': False},
                height=280, margin=dict(t=30, b=10, l=10, r=10)
            )
            st.plotly_chart(fig_c, use_container_width=True)
            diff_color = "#00ff88" if diff > 0 else "#ff4444" if diff < 0 else "#ffbb00"
            diff_msg   = f"📈 +{diff} points improvement!" if diff > 0 else f"📉 {diff} points — try the Resume Improver tab!" if diff < 0 else "➡️ Same score as before."
            st.markdown(f'<div class="ai-summary-box" style="border-color:{diff_color}40;color:{diff_color};font-weight:600;">{diff_msg}</div>', unsafe_allow_html=True)

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
        with st.form("jd_form", clear_on_submit=False):
            jd_text = st.text_area("Paste Job Description here:", height=250, placeholder="Paste job description...")
            jd_submitted = st.form_submit_button("🔍 Match Resume with JD", use_container_width=True)
        if jd_submitted:
            if jd_text.strip():
                with st.spinner("🤖 AI comparing..."):
                    prompt = f"""You are a senior ATS (Applicant Tracking System) expert and technical recruiter with 15+ years at top tech companies.

Perform a DEEP, ACCURATE analysis comparing the resume against the job description.

=== SCORING METHODOLOGY ===
MATCH SCORE (0-100): Based on % of JD requirements covered by resume
- Count total required skills/qualifications in JD
- Count how many the resume has
- Score = (matched / total) * 100, adjusted for experience level fit

ATS SCORE (0-100): Based on keyword density and formatting
- Exact keyword matches from JD found in resume
- Proper section headings (Experience, Skills, Education)
- Quantified achievements present
- No tables/columns that break ATS parsing

=== RESPOND IN EXACTLY THIS FORMAT ===

MATCH SCORE: [calculated number 0-100]

ATS SCORE: [calculated number 0-100]

MATCHED KEYWORDS:
- [exact keyword from JD found in resume]
- [exact keyword from JD found in resume]
- [list ALL matches, minimum 5]

MISSING KEYWORDS:
- [important keyword from JD NOT in resume]
- [important keyword from JD NOT in resume]
- [list top 5-8 missing keywords by importance]

EXPERIENCE_FIT: [Junior/Mid/Senior] level resume vs [Junior/Mid/Senior] level JD
OVERALL_FIT: [Poor/Fair/Good/Excellent]

RECOMMENDATION:
[3-4 specific sentences about this candidate's fit for this exact role. Mention specific skills they have vs what the JD needs. Be precise, not generic.]

TAILORING_TIPS:
- [Specific tip 1: exact keyword to add and where]
- [Specific tip 2: exact achievement to quantify]
- [Specific tip 3: specific section to improve]
- [Specific tip 4: specific skill gap to address]
- [Specific tip 5: formatting or structure fix]

INTERVIEW_PROBABILITY: [Low/Medium/High] — [1 sentence reason]

Resume:
{st.session_state['resume_text']}

Job Description:
{jd_text}"""
                    resp = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.1
                    )
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
            st.markdown(render_ai_analysis(result), unsafe_allow_html=True)

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
            raw_q = st.session_state["questions"]
            st.markdown(f'''
            <div style="margin-bottom:0.5rem;">
                <span style="font-family:Sora,sans-serif;font-size:1.1rem;font-weight:700;color:white;">
                    📝 Interview Questions
                </span>
                <span style="font-size:0.82rem;color:#5a6478;margin-left:0.5rem;">— {st.session_state["selected_job"]}</span>
            </div>''', unsafe_allow_html=True)

            def render_interview_questions(raw):
                import re
                html = '<div class="ai-block">'
                lines = raw.split("\n")
                q_num = 0
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    # Section headings
                    if any(h in line.upper() for h in ["TECHNICAL QUESTIONS", "BEHAVIORAL QUESTIONS", "SITUATIONAL", "CASE QUESTIONS"]):
                        icon = "⚙️" if "TECHNICAL" in line.upper() else "🧠" if "BEHAVIORAL" in line.upper() else "💡"
                        clean = re.sub(r"[:#\*]+", "", line).strip()
                        html += f'<div class="ai-section-heading">{icon} {clean}</div>'
                    # Numbered question line
                    elif re.match(r"^\d+\.", line):
                        q_num += 1
                        # Parse: "1. Question text | Difficulty: Hard"
                        parts = line.split("|")
                        q_text = re.sub(r"^\d+\.\s*", "", parts[0]).strip()
                        diff_label = ""
                        diff_class = "diff-medium"
                        if len(parts) > 1:
                            diff_match = re.search(r"(Easy|Medium|Hard)", parts[1], re.I)
                            if diff_match:
                                d = diff_match.group(1).capitalize()
                                diff_class = f"diff-{d.lower()}"
                                diff_label = f'<span class="ai-num-diff {diff_class}">{d}</span>'
                        html += f'''
                        <div class="ai-numbered">
                            <div class="ai-num-badge">{q_num}</div>
                            <div class="ai-num-content">
                                <div class="ai-num-title">{q_text}</div>
                                {diff_label}
                            </div>
                        </div>'''
                    # Hint / good answer line
                    elif line.startswith("→"):
                        hint_text = line.replace("→", "").replace("Good answer covers:", "").strip()
                        html += f'<div class="ai-num-hint" style="margin-left:2.2rem;margin-top:-0.3rem;margin-bottom:0.4rem;color:#5a7a96;font-size:0.78rem;">💡 {hint_text}</div>'
                    # Skip separator lines
                    elif set(line) <= set("=-─━"):
                        html += "<hr style='border:none;border-top:1px solid rgba(255,255,255,0.05);margin:0.5rem 0'>"
                    # Regular text
                    else:
                        html += f'<div style="color:#8892a4;font-size:0.82rem;padding:0.2rem 0.6rem;">{line}</div>'
                html += "</div>"
                return html

            st.markdown(render_interview_questions(raw_q), unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# TAB 6 — Roadmap
# ══════════════════════════════════════════════════════════
with tab6:
    st.markdown('<div class="section-title">📚 AI Learning Roadmap</div>', unsafe_allow_html=True)
    if 'roadmap' in st.session_state:
        st.markdown(render_ai_analysis(st.session_state["roadmap"]), unsafe_allow_html=True)
    else:
        st.info("Generate a custom roadmap below!")

    with st.form("roadmap_form", clear_on_submit=False):
        c1,c2 = st.columns(2)
        with c1: tj = st.text_input("Target Job Title", value=user.get('job_target',''))
        with c2: miss = st.text_input("Skills to Learn", placeholder="e.g. Deep Learning, SQL")
        gen_roadmap = st.form_submit_button("📚 Generate Roadmap", use_container_width=True)
    if gen_roadmap:
        if tj and miss:
            with st.spinner("🤖 Building your roadmap..."):
                rm = generate_skill_roadmap([s.strip() for s in miss.split(",")], tj)
                st.session_state['roadmap']     = rm
                st.session_state['roadmap_job'] = tj
            st.rerun()
        else:
            st.error("Please fill both fields!")

# ══════════════════════════════════════════════════════════
# TAB 7 — Career Chat (WhatsApp-style)
# ══════════════════════════════════════════════════════════
with tab7:
    bot_nick = st.session_state.get("bot_nickname", "Aria")

    # Header bar like WhatsApp
    st.markdown(f"""
    <div style="background:linear-gradient(90deg,rgba(0,212,255,0.08),rgba(123,47,247,0.08));
                border:1px solid rgba(0,212,255,0.15);border-radius:14px;
                padding:0.75rem 1.2rem;display:flex;align-items:center;margin-bottom:0.5rem;">
        <div style="width:40px;height:40px;background:linear-gradient(135deg,#00d4ff,#7b2ff7);
                    border-radius:50%;display:flex;align-items:center;justify-content:center;
                    font-size:1.2rem;margin-right:0.75rem;flex-shrink:0;">🤖</div>
        <div>
            <div style="color:white;font-weight:700;font-size:0.95rem;font-family:'Sora',sans-serif;">
                {bot_nick}
            </div>
            <div style="color:#00d4ff;font-size:0.72rem;">● Online · AI Career Mentor</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Chat window CSS
    st.markdown("""
    <style>
    .chat-window {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 14px;
        padding: 1rem;
        min-height: 320px;
        max-height: 420px;
        overflow-y: auto;
        margin-bottom: 0.75rem;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    .msg-user {
        align-self: flex-end;
        background: linear-gradient(135deg,#00d4ff,#0099bb);
        color: #080c14;
        border-radius: 16px 16px 4px 16px;
        padding: 0.55rem 1rem;
        max-width: 75%;
        font-size: 0.88rem;
        font-weight: 500;
        word-wrap: break-word;
    }
    .msg-bot {
        align-self: flex-start;
        background: rgba(123,47,247,0.12);
        border: 1px solid rgba(123,47,247,0.2);
        color: #e0e8f0;
        border-radius: 16px 16px 16px 4px;
        padding: 0.55rem 1rem;
        max-width: 80%;
        font-size: 0.88rem;
        word-wrap: break-word;
    }
    .msg-label-user { text-align:right; color:#5a6478; font-size:0.7rem; margin-bottom:2px; }
    .msg-label-bot  { text-align:left;  color:#5a6478; font-size:0.7rem; margin-bottom:2px; }
    .chat-empty {
        text-align:center; color:#2a3040; padding: 3rem 1rem;
        font-size: 0.9rem;
    }
    </style>
    """, unsafe_allow_html=True)

    # Build chat HTML
    if not st.session_state.chat_history:
        chat_html = f"""
        <div class="chat-window">
            <div class="chat-empty">
                🤖 <b style="color:#00d4ff">{bot_nick}</b> is ready!<br/>
                Ask me anything about your career, resume, or job search.<br/><br/>
                <span style="font-size:0.8rem;color:#2a3040">Type a message below to start chatting →</span>
            </div>
        </div>"""
    else:
        msgs_html = ""
        for msg in st.session_state.chat_history:
            if msg['role'] == 'user':
                msgs_html += f'<div class="msg-label-user">You</div><div class="msg-user">{msg["content"]}</div>'
            else:
                msgs_html += f'<div class="msg-label-bot">{bot_nick}</div><div class="msg-bot">{msg["content"]}</div>'
        chat_html = f'<div class="chat-window" id="chat-bottom">{msgs_html}</div>'

    st.markdown(chat_html, unsafe_allow_html=True)

    # Quick suggestion chips
    st.markdown("<div style='margin-bottom:0.4rem;color:#5a6478;font-size:0.78rem;'>💡 Quick questions:</div>", unsafe_allow_html=True)
    qc1, qc2, qc3, qc4 = st.columns(4)
    with qc1:
        if st.button("📝 Improve resume", key="q1"):
            st.session_state['quick_q'] = "How can I improve my resume?"
    with qc2:
        if st.button("💼 Best jobs for me", key="q2"):
            st.session_state['quick_q'] = f"What are the best jobs for my skills: {', '.join(st.session_state.get('skills',[])[:5])}"
    with qc3:
        if st.button("🎯 Interview tips", key="q3"):
            st.session_state['quick_q'] = "Give me tips to crack technical interviews."
    with qc4:
        if st.button("📈 Salary advice", key="q4"):
            st.session_state['quick_q'] = "How do I negotiate a better salary?"

    # Input row at bottom — Enter key sends
    with st.form("chat_form", clear_on_submit=True):
        inp_col, btn_col = st.columns([5, 1])
        with inp_col:
            user_msg = st.text_input(
                "Message",
                value=st.session_state.pop('quick_q', ''),
                placeholder=f"Message {bot_nick}...",
                label_visibility="collapsed"
            )
        with btn_col:
            send = st.form_submit_button("➤ Send", use_container_width=True)

    if send and user_msg.strip():
        ctx = f"You are {bot_nick}, a friendly and expert AI career mentor. User: {name}, Education: {education}, Target: {job_target}."
        if 'skills' in st.session_state:
            ctx += f" Skills: {', '.join(st.session_state['skills'][:10])}. Resume Score: {st.session_state.get('resume_score','?')}/100."
        ctx += f" Language: {st.session_state.get('language','English')}. Reply in that language. Be concise (max 150 words), warm and practical."

        with st.spinner(f"💬 {bot_nick} is typing..."):
            resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": f"{ctx}\n\nUser message: {user_msg.strip()}"}],
                temperature=0.5
            )
            reply = resp.choices[0].message.content

        st.session_state.chat_history.append({"role": "user", "content": user_msg.strip()})
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.rerun()

    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat", key="clear_chat_btn"):
            st.session_state.chat_history = []
            st.rerun()

# ══════════════════════════════════════════════════════════
# TAB 8 — Resume Improver
# ══════════════════════════════════════════════════════════
with tab8:
    st.markdown('<div class="section-title">✍️ Resume Line Improver</div>', unsafe_allow_html=True)
    st.markdown("Paste a weak bullet point → AI makes it powerful! 💪")

    with st.form("improver_form", clear_on_submit=False):
        ol = st.text_area("Your resume line:", placeholder='"Worked on Python project"', height=100)
        improve_sub = st.form_submit_button("✨ Improve This Line", use_container_width=True)
    if improve_sub:
        if ol.strip():
            with st.spinner("🤖 Rewriting..."):
                imp = improve_resume_line(ol)
                st.session_state['improved'] = imp
        else:
            st.error("Please enter a resume line!")

    if 'improved' in st.session_state:
        st.markdown("### ✅ Improved Versions:")
        st.markdown(render_ai_analysis(st.session_state["improved"]), unsafe_allow_html=True)
