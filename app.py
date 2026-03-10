import streamlit as st
import tempfile, os, random, smtplib, hashlib, datetime
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import plotly.graph_objects as go
import plotly.express as px
import firebase_admin
from firebase_admin import credentials, firestore
from resume_parser import extract_text
from skill_extractor import extract_skills, get_skill_categories
from job_matcher import match_jobs
from ai_analyzer import analyze_resume, generate_interview_questions, generate_skill_roadmap, improve_resume_line
from chroma_matcher import smart_job_match
from pdf_report import generate_pdf_report
from openai import OpenAI

# ── Groq ──────────────────────────────────────────────────
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
)

# ── Firebase ──────────────────────────────────────────────
if not firebase_admin._apps:
    fk = dict(st.secrets["firebase"])
    fk["private_key"] = fk["private_key"].replace("\\n", "\n")
    firebase_admin.initialize_app(credentials.Certificate(fk))
db = firestore.client()

# ── Email ─────────────────────────────────────────────────
SENDER_EMAIL    = "nandu19jul@gmail.com"
SENDER_PASSWORD = "geyc nypl ctnc xexm"

# ── Page config ───────────────────────────────────────────
st.set_page_config(page_title="AI Resume Analyzer Pro", page_icon="🚀",
                   layout="wide", initial_sidebar_state="expanded")

# ══════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');
*{font-family:'DM Sans',sans-serif;box-sizing:border-box;}
h1,h2,h3,h4,h5,h6{font-family:'Sora',sans-serif;}
.stApp{background:#080c14;}
.login-title{font-family:'Sora',sans-serif;font-size:2.2rem;font-weight:800;
  background:linear-gradient(135deg,#fff 0%,#00d4ff 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  text-align:center;line-height:1.2;margin-bottom:.5rem;}
.login-sub{text-align:center;color:#5a6478;font-size:.95rem;margin-bottom:1.5rem;}
.otp-box{background:rgba(0,212,255,.05);border:1px solid rgba(0,212,255,.2);
  border-radius:16px;padding:1.2rem;margin:1rem 0;text-align:center;}
.otp-box p{color:#8892a4;font-size:.88rem;margin:0;}
.otp-box strong{color:#00d4ff;}
.profile-title{font-family:'Sora',sans-serif;font-size:1.8rem;font-weight:800;
  color:white;margin-bottom:.3rem;text-align:center;}
.profile-sub{color:#5a6478;font-size:.95rem;text-align:center;}
.step-badge{display:inline-block;background:rgba(0,212,255,.08);
  border:1px solid rgba(0,212,255,.2);color:#00d4ff;padding:4px 16px;
  border-radius:20px;font-size:.78rem;font-weight:600;letter-spacing:1px;text-transform:uppercase;}
.welcome-card{background:linear-gradient(135deg,rgba(0,212,255,.08),rgba(123,47,247,.08));
  border:1px solid rgba(0,212,255,.15);border-radius:16px;padding:1.2rem;
  margin-bottom:1rem;text-align:center;}
.welcome-name{font-family:'Sora',sans-serif;font-size:1rem;font-weight:700;color:white;margin-bottom:.2rem;}
.welcome-detail{color:#5a6478;font-size:.78rem;}
.welcome-email{color:#00d4ff;font-size:.75rem;margin-top:.3rem;}
.hero-title{font-family:'Sora',sans-serif;font-size:2.6rem;font-weight:900;
  background:linear-gradient(90deg,#00d4ff,#7b2ff7);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  text-align:center;padding:.5rem 0;}
.hero-sub{text-align:center;color:#5a6478;font-size:1rem;margin-bottom:1.5rem;}
.welcome-banner{background:linear-gradient(90deg,rgba(0,212,255,.06),rgba(123,47,247,.06));
  border:1px solid rgba(0,212,255,.12);border-radius:12px;padding:.9rem 1.5rem;
  text-align:center;margin-bottom:1.5rem;font-size:1rem;color:#c0cce0;}
.welcome-banner span{color:#00d4ff;font-weight:700;}
.card{background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);
  border-radius:16px;padding:1.5rem;margin:1rem 0;}
.skill-tag{display:inline-block;background:rgba(0,212,255,.07);
  border:1px solid rgba(0,212,255,.18);color:#00d4ff;padding:4px 12px;
  border-radius:20px;margin:4px;font-size:.82rem;}
.section-title{font-family:'Sora',sans-serif;font-size:1.3rem;font-weight:700;
  color:#00d4ff;margin:1rem 0 .5rem;border-left:3px solid #7b2ff7;padding-left:.75rem;}
.metric-card{background:rgba(255,255,255,.03);border-radius:12px;padding:1rem;
  text-align:center;border:1px solid rgba(255,255,255,.07);}
.stButton>button{background:linear-gradient(90deg,#00d4ff,#7b2ff7);color:white;
  border:none;border-radius:10px;padding:.6rem 2rem;font-weight:600;font-size:.95rem;width:100%;}
[data-testid="stFormSubmitButton"]>button{background:linear-gradient(90deg,#00d4ff,#7b2ff7)!important;
  color:white!important;border:none!important;border-radius:10px!important;
  font-weight:600!important;width:100%!important;}
.chat-window{background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.06);
  border-radius:14px;padding:1rem;min-height:320px;max-height:420px;overflow-y:auto;
  margin-bottom:.75rem;display:flex;flex-direction:column;gap:.5rem;}
.msg-user{align-self:flex-end;background:linear-gradient(135deg,#00d4ff,#0099bb);color:#080c14;
  border-radius:16px 16px 4px 16px;padding:.55rem 1rem;max-width:75%;font-size:.88rem;font-weight:500;}
.msg-bot{align-self:flex-start;background:rgba(123,47,247,.12);border:1px solid rgba(123,47,247,.2);
  color:#e0e8f0;border-radius:16px 16px 16px 4px;padding:.55rem 1rem;max-width:80%;font-size:.88rem;}
.msg-label-user{text-align:right;color:#5a6478;font-size:.7rem;margin-bottom:2px;}
.msg-label-bot{text-align:left;color:#5a6478;font-size:.7rem;margin-bottom:2px;}
.chat-empty{text-align:center;color:#2a3040;padding:3rem 1rem;font-size:.9rem;}
@keyframes bounce{0%,100%{transform:translateY(0)}30%{transform:translateY(-18px)}60%{transform:translateY(-8px)}}
@keyframes pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.15)}}
@keyframes shake{0%,100%{transform:translateX(0)}20%{transform:translateX(-10px)}40%{transform:translateX(10px)}60%{transform:translateX(-10px)}80%{transform:translateX(10px)}}
@keyframes flyaway{0%{transform:translate(0,0) scale(1);opacity:1}100%{transform:translate(-30px,-320px) scale(0);opacity:0}}
@keyframes flyaway2{0%{transform:translate(0,0) scale(1);opacity:1}100%{transform:translate(40px,-330px) scale(0);opacity:0}}
@keyframes flyaway3{0%{transform:translate(0,0) scale(1);opacity:1}100%{transform:translate(90px,-340px) scale(0);opacity:0}}
@keyframes explode{0%{transform:scale(.3);opacity:0}30%{transform:scale(2.5);opacity:1}100%{transform:scale(2.2);opacity:.7}}
.anim-bounce{display:inline-block;animation:bounce 1s ease infinite}
.anim-pulse{display:inline-block;animation:pulse 1.2s ease infinite}
.anim-shake{display:inline-block;animation:shake .6s ease infinite}
.anim-fly1{display:inline-block;animation:flyaway 1.3s ease-out forwards}
.anim-fly2{display:inline-block;animation:flyaway2 1.5s ease-out .1s forwards}
.anim-fly3{display:inline-block;animation:flyaway3 1.1s ease-out .2s forwards}
.anim-explode{display:inline-block;animation:explode .7s ease-out forwards}
.banner-excellent{background:linear-gradient(90deg,#00ff88,#00d4ff);border-radius:14px;
  padding:1.2rem 2rem;text-align:center;font-size:1.5rem;font-weight:800;color:#080c14;margin:1rem 0;}
.banner-medium{background:linear-gradient(90deg,#ffbb00,#ff8c00);border-radius:14px;
  padding:1.2rem 2rem;text-align:center;font-size:1.5rem;font-weight:800;color:#080c14;margin:1rem 0;}
.banner-poor{background:linear-gradient(90deg,#ff4444,#ff0000);border-radius:14px;
  padding:1.2rem 2rem;text-align:center;font-size:1.5rem;font-weight:800;color:white;margin:1rem 0;}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════

def make_token(uid: str) -> str:
    raw = f"{uid}-{datetime.datetime.now().isoformat()}-{random.randint(10000,99999)}"
    return hashlib.sha256(raw.encode()).hexdigest()[:40]

def save_token(uid: str, token: str):
    db.collection("sessions").document(token).set({
        "uid": uid, "created": datetime.datetime.now().isoformat()
    })

def get_uid_from_token(token: str):
    try:
        doc = db.collection("sessions").document(token).get()
        return doc.to_dict().get("uid") if doc.exists else None
    except: return None

def delete_token(token: str):
    try: db.collection("sessions").document(token).delete()
    except: pass

def get_user(uid: str):
    try:
        doc = db.collection("users").document(uid).get()
        return doc.to_dict() if doc.exists else None
    except: return None

def save_user(uid, name, education, job_target, purpose, bot_nick="Aria"):
    db.collection("users").document(uid).set({
        "uid": uid, "name": name, "education": education,
        "job_target": job_target, "purpose": purpose, "bot_nick": bot_nick
    })

def send_email_otp(to_email: str, otp: str) -> bool:
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "🔐 Your OTP — AI Resume Analyzer Pro"
        msg["From"]    = SENDER_EMAIL
        msg["To"]      = to_email
        msg.attach(MIMEText(f"""
        <div style="font-family:Arial,sans-serif;background:#080c14;padding:2rem;border-radius:16px;max-width:480px;margin:auto;">
          <h2 style="color:#00d4ff;text-align:center;">🚀 AI Resume Analyzer Pro</h2>
          <p style="color:#8892a4;text-align:center;">Your one-time login code</p>
          <div style="background:rgba(0,212,255,.08);border-radius:12px;padding:1.5rem;text-align:center;margin:1.5rem 0;">
            <div style="font-size:2.8rem;font-weight:900;color:white;letter-spacing:12px;font-family:monospace;">{otp}</div>
          </div>
          <p style="color:#5a6478;text-align:center;font-size:.8rem;">⏱️ Valid for 10 minutes · 🔒 Do not share</p>
        </div>""", "html"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
            s.login(SENDER_EMAIL, SENDER_PASSWORD)
            s.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        return True
    except Exception as e:
        st.error(f"Email error: {e}")
        return False

def send_sms_otp(phone: str, otp: str):
    try:
        key = st.secrets.get("FAST2SMS_KEY", "")
        if not key: return False, "no_key"
        import urllib.request, json as _j
        payload = _j.dumps({"route":"otp","variables_values":otp,
                             "numbers":phone.lstrip("+").lstrip("91")[-10:]}).encode()
        req = urllib.request.Request("https://www.fast2sms.com/dev/bulkV2", data=payload,
              headers={"authorization":key,"Content-Type":"application/json"})
        res = urllib.request.urlopen(req, timeout=10)
        data = _j.loads(res.read())
        return (True,"ok") if data.get("return") else (False, data.get("message","err"))
    except Exception as e: return False, str(e)


# ══════════════════════════════════════════════════════════
# SESSION DEFAULTS
# ══════════════════════════════════════════════════════════
_D = {"page":"boot","otp_sent":False,"otp_code":"","otp_uid":"","login_method":"",
      "user":None,"bot_nick":"Aria","chat_history":[],"language":"English","token":""}
for k,v in _D.items():
    if k not in st.session_state: st.session_state[k] = v


# ══════════════════════════════════════════════════════════
# BOOT — check for saved session token in URL
# ══════════════════════════════════════════════════════════
if st.session_state.page == "boot":
    token = st.query_params.get("token","")
    if token:
        uid = get_uid_from_token(token)
        if uid:
            u = get_user(uid)
            if u and u.get("name") and u.get("education"):
                # ✅ Already logged in → go straight to app
                st.session_state.user     = u
                st.session_state.bot_nick = u.get("bot_nick","Aria")
                st.session_state.language = u.get("language","English")
                st.session_state.token    = token
                st.session_state.page     = "app"
            else:
                # Has token but profile incomplete
                st.session_state.otp_uid  = uid
                st.session_state.token    = token
                st.session_state.page     = "profile"
        else:
            st.query_params.clear()
            st.session_state.page = "login"
    else:
        st.session_state.page = "login"
    st.rerun()


# ══════════════════════════════════════════════════════════
# PAGE: LOGIN
# ══════════════════════════════════════════════════════════
if st.session_state.page == "login":
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("""
        <div style="height:40px"></div>
        <div style="text-align:center;font-size:3rem;margin-bottom:.4rem;">🚀</div>
        <div style="text-align:center;font-size:.9rem;font-weight:700;color:#00d4ff;
                    letter-spacing:2px;text-transform:uppercase;margin-bottom:.4rem;">
            AI Resume Analyzer Pro
        </div>
        <div class="login-title">Your Career,<br/>Supercharged by AI</div>
        <div class="login-sub">Score your resume · Match jobs · Ace interviews<br/>in under 60 seconds.</div>
        """, unsafe_allow_html=True)
        st.markdown("---")

        # ── Step 1: Choose method ─────────────────────────
        if not st.session_state.login_method and not st.session_state.otp_sent:
            st.markdown("##### 👋 How would you like to sign in?")
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                if st.button("📧  Email OTP", key="btn_email", use_container_width=True):
                    st.session_state.login_method = "email"
                    st.rerun()
            with c2:
                if st.button("📱  Phone OTP", key="btn_phone", use_container_width=True):
                    st.session_state.login_method = "phone"
                    st.rerun()

            st.markdown("""<div style="text-align:center;margin-top:1.5rem;color:#2a3a4a;font-size:.8rem;">
                🔒 OTP login · No password needed · Free forever</div>""", unsafe_allow_html=True)

        # ── Step 2a: Email form ───────────────────────────
        elif st.session_state.login_method == "email" and not st.session_state.otp_sent:
            st.markdown("##### 📧 Enter your Email")
            if st.button("← Back", key="back_e"):
                st.session_state.login_method = ""
                st.rerun()

            with st.form("form_email"):
                email_in = st.text_input("Email", placeholder="you@example.com", label_visibility="collapsed")
                go       = st.form_submit_button("📨 Send OTP →", use_container_width=True)

            if go:
                e = email_in.strip()
                if "@" in e and "." in e:
                    otp = str(random.randint(100000,999999))
                    with st.spinner("Sending OTP to your inbox..."):
                        ok = send_email_otp(e, otp)
                    if ok:
                        st.session_state.otp_sent = True
                        st.session_state.otp_code = otp
                        st.session_state.otp_uid  = e
                        st.rerun()
                    else:
                        st.error("❌ Could not send email. Please try again.")
                else:
                    st.error("❌ Enter a valid email address.")

        # ── Step 2b: Phone form ───────────────────────────
        elif st.session_state.login_method == "phone" and not st.session_state.otp_sent:
            st.markdown("##### 📱 Enter your Phone Number")
            if st.button("← Back", key="back_p"):
                st.session_state.login_method = ""
                st.rerun()

            with st.form("form_phone"):
                phone_in = st.text_input("Phone", placeholder="+91 9876543210", label_visibility="collapsed")
                go_p     = st.form_submit_button("📨 Send OTP →", use_container_width=True)

            if go_p:
                ph = phone_in.strip().replace(" ","").replace("-","")
                if len(ph) >= 10:
                    otp = str(random.randint(100000,999999))
                    with st.spinner("Sending OTP to your phone..."):
                        ok, msg = send_sms_otp(ph, otp)
                    if ok:
                        st.session_state.otp_sent = True
                        st.session_state.otp_code = otp
                        st.session_state.otp_uid  = ph
                        st.rerun()
                    elif msg == "no_key":
                        st.error("❌ Phone OTP not configured. Please use Email instead.")
                    else:
                        st.error(f"❌ SMS failed: {msg}")
                else:
                    st.error("❌ Enter a valid 10-digit phone number.")

        # ── Step 3: OTP verify ────────────────────────────
        elif st.session_state.otp_sent:
            uid      = st.session_state.otp_uid
            is_email = "@" in uid

            st.markdown(f"""
            <div class="otp-box">
                <p>OTP sent to <strong>{uid}</strong></p>
                <p style="margin-top:.3rem;font-size:.78rem;">
                    {'📧 Check inbox &amp; spam folder' if is_email else '📱 Check your SMS messages'}
                </p>
            </div>""", unsafe_allow_html=True)

            with st.form("form_otp"):
                otp_in  = st.text_input("Enter 6-digit OTP", placeholder="e.g. 482910",
                                        max_chars=6, label_visibility="collapsed")
                cv, cr  = st.columns(2)
                with cv: verify = st.form_submit_button("✅ Verify & Login", use_container_width=True)
                with cr: resend = st.form_submit_button("🔄 Resend OTP",     use_container_width=True)

            if verify:
                if otp_in.strip() == st.session_state.otp_code:
                    # ✅ OTP correct — create persistent session token
                    token = make_token(uid)
                    save_token(uid, token)
                    st.session_state.token    = token
                    st.session_state.otp_sent = False
                    st.session_state.otp_code = ""
                    st.query_params["token"]  = token   # 👈 saves in URL = stays after refresh

                    # Check if this user already has a complete profile
                    saved = get_user(uid)
                    if saved and saved.get("name") and saved.get("education") and saved.get("job_target"):
                        st.session_state.user     = saved
                        st.session_state.bot_nick = saved.get("bot_nick","Aria")
                        st.session_state.language = saved.get("language","English")
                        st.session_state.page     = "app"     # 👈 returning user → straight to app
                    else:
                        st.session_state.page     = "profile" # 👈 new user → fill profile first
                    st.rerun()
                else:
                    st.error("❌ Wrong OTP. Please try again.")

            if resend:
                new_otp = str(random.randint(100000,999999))
                if is_email:
                    if send_email_otp(uid, new_otp):
                        st.session_state.otp_code = new_otp
                        st.success("✅ New OTP sent to your inbox!")
                else:
                    ok, msg = send_sms_otp(uid, new_otp)
                    if ok:
                        st.session_state.otp_code = new_otp
                        st.success("✅ New OTP sent to your phone!")
                    else:
                        st.error(f"❌ {msg}")

    st.stop()


# ══════════════════════════════════════════════════════════
# PAGE: PROFILE  ← shown ONLY first time
# ══════════════════════════════════════════════════════════
if st.session_state.page == "profile":
    uid      = st.session_state.otp_uid or (st.session_state.user or {}).get("uid","")
    existing = get_user(uid) or {}

    _, col, _ = st.columns([1,1.5,1])
    with col:
        st.markdown("""
        <div style="height:30px"></div>
        <div style="text-align:center;font-size:3rem;">👤</div>
        <div class="profile-title">Almost there!</div>
        <div class="profile-sub">Tell us about yourself — asked only once!</div>
        <div style="height:10px"></div>
        <div style="text-align:center"><span class="step-badge">Step 2 of 2 — Profile Setup</span></div>
        <div style="height:16px"></div>
        """, unsafe_allow_html=True)
        st.markdown(f"**Signed in as:** `{uid}`")
        st.markdown("---")

        with st.form("form_profile"):
            name       = st.text_input("👤 Full Name",          value=existing.get("name",""),       placeholder="e.g. Priya Sharma")
            education  = st.text_input("🎓 Education / Degree", value=existing.get("education",""),  placeholder="e.g. B.Tech Computer Science")
            job_target = st.text_input("🎯 Target Job Role",    value=existing.get("job_target",""), placeholder="e.g. Data Scientist, SDE")
            purposes   = ["Campus Placement","Internship","Full-time Job","Career Switch","Higher Studies","Freelance"]
            sp         = existing.get("purpose","Campus Placement")
            purpose    = st.selectbox("📌 Why are you here?", purposes,
                                      index=purposes.index(sp) if sp in purposes else 0)
            done       = st.form_submit_button("🚀 Save & Continue", use_container_width=True)

        if done:
            if name and education and job_target:
                prev_nick = existing.get("bot_nick","")
                save_user(uid, name, education, job_target, purpose, prev_nick or "Aria")
                st.session_state.user = {"uid":uid,"name":name,"education":education,
                                         "job_target":job_target,"purpose":purpose,
                                         "bot_nick": prev_nick or "Aria"}
                st.session_state.bot_nick = prev_nick or "Aria"
                st.session_state.page = "nickname" if not prev_nick else "app"
                st.rerun()
            else:
                st.error("❌ Please fill in all three fields.")
    st.stop()


# ══════════════════════════════════════════════════════════
# PAGE: NICKNAME  ← shown ONLY once after first profile
# ══════════════════════════════════════════════════════════
if st.session_state.page == "nickname":
    _, col, _ = st.columns([1,1.5,1])
    with col:
        st.markdown("""
        <div style="height:30px"></div>
        <div style="text-align:center;font-size:3.5rem;">🤖</div>
        <div class="profile-title">One Last Thing!</div>
        <div class="profile-sub">Give your AI Career Mentor a name — make it yours!</div>
        <div style="height:10px"></div>
        <div style="text-align:center"><span class="step-badge">Step 3 of 3 — Personalize</span></div>
        <div style="height:20px"></div>
        """, unsafe_allow_html=True)
        st.markdown("""<div style="background:rgba(0,212,255,.05);border:1px solid rgba(0,212,255,.15);
            border-radius:14px;padding:1.2rem;margin-bottom:1rem;text-align:center;">
            <p style="color:#8892a4;font-size:.88rem;margin:0 0 .5rem;">
                💡 You can change this anytime from Settings.</p>
            <p style="color:#5a6478;font-size:.8rem;margin:0;">
                Popular: <b style="color:#00d4ff">Chitti</b> · <b style="color:#00d4ff">Jarvis</b> ·
                <b style="color:#00d4ff">Nova</b> · <b style="color:#00d4ff">Aria</b> · <b style="color:#00d4ff">Max</b>
            </p></div>""", unsafe_allow_html=True)
        st.markdown("---")
        with st.form("form_nick"):
            nick    = st.text_input("Name your AI mentor", placeholder="e.g. Chitti, Jarvis…",
                                    max_chars=20, label_visibility="collapsed")
            ca, cb  = st.columns(2)
            with ca: do_set  = st.form_submit_button("✨ Set Name & Enter App", use_container_width=True)
            with cb: do_skip = st.form_submit_button("⏭️ Skip (Use 'Aria')",    use_container_width=True)
        if do_set or do_skip:
            final = nick.strip() if (do_set and nick.strip()) else "Aria"
            st.session_state.bot_nick = final
            uid = (st.session_state.user or {}).get("uid","")
            if uid: db.collection("users").document(uid).update({"bot_nick": final})
            st.session_state.page = "app"
            st.rerun()
    st.stop()


# ══════════════════════════════════════════════════════════
# AUTH GUARD — if somehow user is None, back to login
# ══════════════════════════════════════════════════════════
user = st.session_state.get("user") or {}
if not user:
    st.session_state.clear()
    st.session_state.page = "login"
    st.query_params.clear()
    st.rerun()

name       = user.get("name","")
education  = user.get("education","")
job_target = user.get("job_target","")
uid_key    = user.get("uid", user.get("identifier",""))
initials   = name[0].upper() if name else "?"
bot_nick   = st.session_state.get("bot_nick","Aria")


# ══════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
    <div class="welcome-card">
        <div style="width:52px;height:52px;background:linear-gradient(135deg,#00d4ff,#7b2ff7);
            border-radius:50%;display:flex;align-items:center;justify-content:center;
            font-size:1.5rem;margin:0 auto .75rem;">{initials}</div>
        <div class="welcome-name">👋 {name}</div>
        <div class="welcome-detail">🎓 {education}</div>
        <div class="welcome-detail">🎯 {job_target}</div>
        <div class="welcome-email">✉️ {uid_key}</div>
        <div style="margin-top:.5rem;color:#7b2ff7;font-size:.78rem;font-weight:600;">
            🤖 AI Mentor: <span style="color:#00d4ff">{bot_nick}</span></div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    if 'skills' in st.session_state:
        st.markdown("### 📊 Resume Stats")
        st.metric("Skills Found", len(st.session_state['skills']))
        if 'resume_score' in st.session_state:
            sv = st.session_state['resume_score']
            st.metric("Resume Score", f"{'🟢' if sv>=70 else '🟡' if sv>=50 else '🔴'} {sv}/100")
        if 'jobs' in st.session_state:
            st.metric("Best Match", st.session_state['jobs'][0]['title'])
        st.markdown("---")

    if st.button("⚙️ Settings", key="goto_settings"):
        st.session_state.page = "settings"
        st.rerun()

    if st.button("🚪 Logout", key="logout_btn"):
        tok = st.session_state.get("token","")
        if tok: delete_token(tok)      # delete from Firebase
        st.session_state.clear()       # wipe everything
        st.query_params.clear()        # remove ?token= from URL
        st.session_state.page = "login"
        st.rerun()


# ══════════════════════════════════════════════════════════
# PAGE: SETTINGS
# ══════════════════════════════════════════════════════════
if st.session_state.page == "settings":
    with st.sidebar:
        st.markdown(f"""<div class="welcome-card">
            <div style="width:44px;height:44px;background:linear-gradient(135deg,#00d4ff,#7b2ff7);
                border-radius:50%;display:flex;align-items:center;justify-content:center;
                font-size:1.2rem;margin:0 auto .6rem;">{initials}</div>
            <div class="welcome-name">{name}</div>
            <div class="welcome-email">✉️ {uid_key}</div>
        </div>""", unsafe_allow_html=True)
        st.markdown("---")
        if st.button("← Back to App", key="back_to_app"):
            st.session_state.page = "app"; st.rerun()
        if st.button("🚪 Logout", key="sett_logout"):
            tok = st.session_state.get("token","")
            if tok: delete_token(tok)
            st.session_state.clear(); st.query_params.clear()
            st.session_state.page = "login"; st.rerun()

    st.markdown('<div class="hero-title">⚙️ Settings</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Manage your account, preferences and personalization</div>', unsafe_allow_html=True)

    s1, s2 = st.columns(2)
    with s1:
        st.markdown('<div class="section-title">🤖 AI Mentor Name</div>', unsafe_allow_html=True)
        st.markdown(f"""<div style="background:rgba(0,212,255,.05);border:1px solid rgba(0,212,255,.15);
            border-radius:12px;padding:1rem;margin-bottom:.8rem;">
            <p style="color:#8892a4;font-size:.85rem;margin:0 0 .3rem;">Current Name</p>
            <p style="color:#00d4ff;font-size:1.4rem;font-weight:800;margin:0;">🤖 {bot_nick}</p>
        </div>""", unsafe_allow_html=True)
        with st.form("form_nick_s"):
            nn     = st.text_input("New name", placeholder="e.g. Chitti, Jarvis…", max_chars=20)
            sv_n   = st.form_submit_button("💾 Save Name", use_container_width=True)
        st.caption("Popular: Chitti · Jarvis · Nova · Aria · Max")
        if sv_n and nn.strip():
            st.session_state.bot_nick = nn.strip()
            db.collection("users").document(uid_key).update({"bot_nick": nn.strip()})
            st.success(f"✅ Renamed to **{nn.strip()}**!")
            st.rerun()

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">🌐 Language</div>', unsafe_allow_html=True)
        langs = ["English","Hindi","Tamil","Telugu","Kannada","Malayalam","Bengali","Marathi","Gujarati","Spanish","French","German"]
        cur   = st.session_state.get("language","English")
        with st.form("form_lang_s"):
            nl   = st.selectbox("Language", langs, index=langs.index(cur) if cur in langs else 0)
            sv_l = st.form_submit_button("💾 Save Language", use_container_width=True)
        if sv_l:
            st.session_state.language = nl
            db.collection("users").document(uid_key).update({"language": nl})
            st.success(f"✅ Language set to **{nl}**!")

    with s2:
        st.markdown('<div class="section-title">👤 Account & Profile</div>', unsafe_allow_html=True)
        st.markdown(f"""<div class="card">
            <p style="color:#8892a4;font-size:.82rem;margin:0 0 .8rem;">Your saved profile</p>
            <p style="color:white;margin:.3rem 0;"><b style="color:#00d4ff">📧 Login:</b> {uid_key}</p>
            <p style="color:white;margin:.3rem 0;"><b style="color:#00d4ff">👤 Name:</b> {name}</p>
            <p style="color:white;margin:.3rem 0;"><b style="color:#00d4ff">🎓 Education:</b> {education}</p>
            <p style="color:white;margin:.3rem 0;"><b style="color:#00d4ff">🎯 Target:</b> {job_target}</p>
            <p style="color:white;margin:.3rem 0;"><b style="color:#00d4ff">🤖 Mentor:</b> {bot_nick}</p>
            <p style="color:white;margin:.3rem 0;"><b style="color:#00d4ff">🌐 Language:</b> {st.session_state.get('language','English')}</p>
        </div>""", unsafe_allow_html=True)
        if st.button("✏️ Edit Profile", key="edit_prof"):
            st.session_state.page = "profile"; st.rerun()

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">🔔 Notifications</div>', unsafe_allow_html=True)
        st.toggle("Email tips & updates",     value=False, key="notif1")
        st.toggle("Score improvement alerts", value=True,  key="notif2")
        st.toggle("Job match notifications",  value=True,  key="notif3")

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">❓ Help & Support</div>', unsafe_allow_html=True)
        st.markdown("""<div class="card">
            <p style="color:#c0cce0;font-size:.88rem;"><b>📖 How to use:</b></p>
            <p style="color:#8892a4;font-size:.82rem;margin:.2rem 0;">1. Upload resume (PDF / DOCX / TXT)</p>
            <p style="color:#8892a4;font-size:.82rem;margin:.2rem 0;">2. Click Analyze My Resume</p>
            <p style="color:#8892a4;font-size:.82rem;margin:.2rem 0;">3. Explore all 8 tabs for insights</p>
            <p style="color:#8892a4;font-size:.82rem;margin:.2rem 0;">4. Chat with your AI mentor anytime!</p>
            <p style="color:#00d4ff;font-size:.82rem;margin:.8rem 0 0;">support@airesume.pro</p>
            <p style="color:#5a6478;font-size:.75rem;margin:.4rem 0 0;">Version 2.0 · Streamlit + Groq AI</p>
        </div>""", unsafe_allow_html=True)

    st.stop()


# ══════════════════════════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════════════════════════
st.markdown('<div class="hero-title">🚀 AI Resume Analyzer Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Upload your resume and get instant AI-powered career insights</div>', unsafe_allow_html=True)
st.markdown(f"""<div class="welcome-banner">
    Hello, <span>{name}</span>! 👋 &nbsp;·&nbsp;
    🎯 Target: <span>{job_target}</span> &nbsp;·&nbsp;
    🎓 <span>{education}</span>
</div>""", unsafe_allow_html=True)

tab1,tab2,tab3,tab4,tab5,tab6,tab7,tab8 = st.tabs([
    "📄 Upload & Analyze","📊 Visual Charts","💼 Smart Job Match",
    "🔍 JD Matcher","🎯 Interview Prep","📚 Roadmap",
    f"💬 Chat with {bot_nick}","✍️ Resume Improver"
])

# ── Tab 1: Upload & Analyze ───────────────────────────────
with tab1:
    st.markdown('<div class="section-title">📄 Upload Your Resume</div>', unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1: uploaded_file = st.file_uploader("Resume file", type=["pdf","docx","txt"])
    with c2: pasted_text   = st.text_area("Or paste text:", height=150, placeholder="Paste resume text here...")

    if 'resume_score' in st.session_state:
        st.info(f"📊 Previous Score: **{st.session_state['resume_score']}/100** — Upload new resume to compare!")

    if st.button("🔍 Analyze My Resume", key="analyze_btn"):
        resume_text = ""
        if uploaded_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
                tmp.write(uploaded_file.read()); tmp_path = tmp.name
            resume_text = extract_text(tmp_path)
            os.unlink(tmp_path)
        elif pasted_text.strip():
            resume_text = pasted_text
        else:
            st.error("❌ Please upload a file or paste resume text!"); st.stop()

        if len(resume_text.strip()) < 50:
            st.error("❌ Resume text too short. Check your file."); st.stop()

        if 'resume_score' in st.session_state:
            st.session_state['previous_score'] = st.session_state['resume_score']
        st.session_state['resume_text'] = resume_text

        with st.spinner("🔍 Extracting skills..."):
            skills = extract_skills(resume_text)
            st.session_state['skills']     = skills
            st.session_state['categories'] = get_skill_categories(skills)

        with st.spinner("🤖 AI analyzing resume (20–30 sec)..."):
            analysis = analyze_resume(resume_text)
            st.session_state['analysis'] = analysis

        with st.spinner("💼 Matching jobs..."):
            jobs = match_jobs(skills)
            st.session_state['jobs'] = jobs

        try:
            score = min(int(''.join(filter(str.isdigit,
                [l for l in analysis.split('\n') if 'SCORE:' in l][0]))), 100)
        except: score = 70
        st.session_state['resume_score'] = score

        try:
            db.collection("resume_analysis").add({
                "user": uid_key, "name": name, "score": score, "skills": skills,
                "top_job": jobs[0]["title"] if jobs else "None",
                "timestamp": datetime.datetime.now().isoformat()
            })
        except: pass

        if score >= 75:
            st.markdown("""<div class="banner-excellent">
                <span class="anim-bounce" style="font-size:2rem">🏆</span>
                &nbsp; EXCELLENT RESUME! You are Job Ready! &nbsp;
                <span class="anim-bounce" style="font-size:2rem">🎉</span>
            </div>""", unsafe_allow_html=True)
            st.success(f"✅ Your resume scored {score}/100 — Start applying NOW!")
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
                <span class="anim-explode" style="font-size:4.5rem;position:absolute;left:8%;top:5%">💥</span>
                <span class="anim-fly1"    style="font-size:3.5rem;position:absolute;left:18%;top:25%">🎈</span>
                <span class="anim-fly2"    style="font-size:3.5rem;position:absolute;left:38%;top:15%">🎈</span>
                <span class="anim-fly3"    style="font-size:3.5rem;position:absolute;left:58%;top:25%">🎈</span>
                <span class="anim-explode" style="font-size:4rem;position:absolute;left:72%;top:5%;animation-delay:.2s">💥</span>
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
            prev = st.session_state['previous_score']; diff = score-prev
            color = "green" if diff>0 else "red" if diff<0 else "gray"
            st.markdown(f"""<div class="card" style="text-align:center">
                <h3>Score Comparison {'📈' if diff>0 else '📉' if diff<0 else '➡️'}</h3>
                Previous: <b>{prev}</b> → New: <b style="color:{color}">{score}</b>
                <span style="color:{color}">({'+' if diff>0 else ''}{diff} pts)</span>
            </div>""", unsafe_allow_html=True)

        cc = "#00ff88" if score>=70 else "#ffbb00" if score>=50 else "#ff4444"
        c1,c2,c3,c4 = st.columns(4)
        with c1: st.markdown(f'<div class="metric-card"><div style="font-size:3rem;font-weight:900;color:{cc}">{score}</div><div style="color:#5a6478">Resume Score</div></div>',unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="metric-card"><div style="font-size:3rem;font-weight:900;color:#00d4ff">{len(skills)}</div><div style="color:#5a6478">Skills Found</div></div>',unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="metric-card"><div style="font-size:3rem;font-weight:900;color:#7b2ff7">{len(categories)}</div><div style="color:#5a6478">Categories</div></div>',unsafe_allow_html=True)
        with c4:
            tm = st.session_state['jobs'][0]['match_score'] if st.session_state.get('jobs') else 0
            st.markdown(f'<div class="metric-card"><div style="font-size:3rem;font-weight:900;color:#ff6b6b">{tm}%</div><div style="color:#5a6478">Top Job Match</div></div>',unsafe_allow_html=True)

        st.progress(score/100)
        st.markdown('<div class="section-title">🤖 Full AI Analysis</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card">{analysis}</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">🧠 Skills Detected</div>', unsafe_allow_html=True)
        if categories:
            cols = st.columns(3)
            for i,(cat,cs) in enumerate(categories.items()):
                with cols[i%3]:
                    st.markdown(f"**{cat}**")
                    for s in cs: st.markdown(f'<span class="skill-tag">{s}</span>', unsafe_allow_html=True)
        else:
            st.warning("No skills detected.")

        st.markdown("---")
        st.markdown('<div class="section-title">📥 Download Report</div>', unsafe_allow_html=True)
        cname = st.text_input("Your name for the report:", value=name)
        if st.button("📄 Generate & Download PDF Report"):
            if cname:
                with st.spinner("Generating PDF..."):
                    pdf_path = generate_pdf_report(cname, score, skills, analysis,
                                                   st.session_state['jobs'],
                                                   st.session_state.get('questions',''))
                with open(pdf_path,"rb") as f:
                    st.download_button("⬇️ Download PDF Report", data=f,
                        file_name=f"resume_{cname.replace(' ','_')}.pdf", mime="application/pdf")
            else:
                st.error("Please enter your name!")

# ── Tab 2: Visual Charts ──────────────────────────────────
with tab2:
    st.markdown('<div class="section-title">📊 Visual Analytics</div>', unsafe_allow_html=True)
    if 'skills' not in st.session_state:
        st.info("👆 Please analyze your resume first!")
    else:
        score      = st.session_state['resume_score']
        skills     = st.session_state['skills']
        categories = st.session_state['categories']
        jobs       = st.session_state.get('jobs',[])

        c1,c2 = st.columns(2)
        with c1:
            st.markdown("#### 🎯 Resume Score Gauge")
            color = "#00ff88" if score>=70 else "#ffbb00" if score>=50 else "#ff4444"
            fig = go.Figure(go.Indicator(
                mode="gauge+number",value=score,domain={'x':[0,1],'y':[0,1]},
                title={'text':"Resume Score",'font':{'color':'white'}},
                number={'font':{'color':color}},
                gauge={'axis':{'range':[0,100],'tickcolor':'white'},'bar':{'color':color},
                       'bgcolor':'rgba(0,0,0,0)',
                       'steps':[{'range':[0,50],'color':'rgba(255,68,68,.2)'},
                                 {'range':[50,70],'color':'rgba(255,187,0,.2)'},
                                 {'range':[70,100],'color':'rgba(0,255,136,.2)'}],
                       'threshold':{'line':{'color':'#7b2ff7','width':4},'thickness':.75,'value':70}}
            ))
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',font={'color':'white'},height=300)
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            st.markdown("#### 🧠 Skills by Category")
            if categories:
                fig2 = px.pie(names=list(categories.keys()),
                              values=[len(v) for v in categories.values()],
                              color_discrete_sequence=px.colors.sequential.Plasma, hole=0.4)
                fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)',font={'color':'white'},height=300)
                st.plotly_chart(fig2, use_container_width=True)

        if jobs:
            st.markdown("#### 💼 Job Match Scores")
            jt=[j['title'] for j in jobs[:8]]; js=[j['match_score'] for j in jobs[:8]]
            fig3=go.Figure(go.Bar(x=js,y=jt,orientation='h',
                marker_color=['#00ff88' if s>=70 else '#ffbb00' if s>=40 else '#ff4444' for s in js],
                text=[f"{s}%" for s in js],textposition='outside'))
            fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
                font={'color':'white'},xaxis={'range':[0,115]},height=400)
            st.plotly_chart(fig3, use_container_width=True)

        if categories and len(categories)>=3:
            st.markdown("#### 🕸️ Skill Radar")
            rc=list(categories.keys()); rv=[len(v) for v in categories.values()]
            fig4=go.Figure(go.Scatterpolar(r=rv+[rv[0]],theta=rc+[rc[0]],fill='toself',
                fillcolor='rgba(0,212,255,.1)',line_color='#00d4ff'))
            fig4.update_layout(polar=dict(bgcolor='rgba(0,0,0,0)',
                radialaxis=dict(visible=True,gridcolor='rgba(255,255,255,.08)',color='white'),
                angularaxis=dict(gridcolor='rgba(255,255,255,.08)',color='white')),
                paper_bgcolor='rgba(0,0,0,0)',font={'color':'white'},height=400)
            st.plotly_chart(fig4, use_container_width=True)

        if 'previous_score' in st.session_state:
            prev=st.session_state['previous_score']
            fig5=go.Figure(go.Bar(x=['Previous','Current'],y=[prev,score],
                marker_color=['#ff6b6b','#00ff88'],
                text=[str(prev),str(score)],textposition='outside'))
            fig5.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
                font={'color':'white'},yaxis={'range':[0,115]},height=300)
            st.plotly_chart(fig5, use_container_width=True)

# ── Tab 3: Smart Job Match ────────────────────────────────
with tab3:
    st.markdown('<div class="section-title">💼 Smart Job Matching</div>', unsafe_allow_html=True)
    st.markdown("Uses **AI Vector Search** to find semantically similar jobs!")
    if 'resume_text' not in st.session_state:
        st.info("👆 Please analyze your resume first!")
    else:
        if st.button("🔍 Run Smart Job Match", key="chroma_btn"):
            with st.spinner("🧠 AI searching best jobs..."):
                st.session_state['smart_jobs'] = smart_job_match(st.session_state['resume_text'])
        if 'smart_jobs' in st.session_state:
            for i,job in enumerate(st.session_state['smart_jobs']):
                sj=job['similarity_score']; em="🥇" if i==0 else "🥈" if i==1 else "🥉" if i==2 else "⭐"
                with st.expander(f"{em} {job['title']} — {sj}% Match"):
                    c1,c2=st.columns(2)
                    with c1:
                        st.markdown(f"**Score:** {sj}%"); st.progress(sj/100)
                        st.markdown(f"**💰 Salary:** {job['salary']}")
                        st.markdown(f"**🏢 Companies:** {job['companies']}")
                    with c2:
                        st.markdown("**Required Skills:**")
                        for s in job['required_skills']:
                            has = s.lower() in [sk.lower() for sk in st.session_state['skills']]
                            st.markdown(f"{'✅' if has else '❌'} {s}")

# ── Tab 4: JD Matcher ─────────────────────────────────────
with tab4:
    st.markdown('<div class="section-title">🔍 Resume vs JD Matcher</div>', unsafe_allow_html=True)
    if 'resume_text' not in st.session_state:
        st.info("👆 Please analyze your resume first!")
    else:
        with st.form("form_jd"):
            jd_text = st.text_area("Paste Job Description:", height=250, placeholder="Paste job description...")
            jd_go   = st.form_submit_button("🔍 Match Resume with JD", use_container_width=True)
        if jd_go:
            if jd_text.strip():
                with st.spinner("🤖 AI comparing..."):
                    resp = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role":"user","content":f"""You are a senior ATS expert.
MATCH SCORE: [0-100]
ATS SCORE: [0-100]
MATCHED KEYWORDS:\n- [keyword]\nMISSING KEYWORDS:\n- [keyword]
EXPERIENCE_FIT: [level]
OVERALL_FIT: [Poor/Fair/Good/Excellent]
RECOMMENDATION:\n[3-4 sentences]
TAILORING_TIPS:\n- [tip 1]\n- [tip 2]\n- [tip 3]\n- [tip 4]\n- [tip 5]
INTERVIEW_PROBABILITY: [Low/Medium/High] — [reason]

Resume:\n{st.session_state['resume_text']}\n\nJob Description:\n{jd_text}"""}],
                        temperature=0.1)
                    st.session_state['jd_result'] = resp.choices[0].message.content
            else: st.error("Please paste a job description!")

        if 'jd_result' in st.session_state:
            result=st.session_state['jd_result']
            try: ms  = min(int(''.join(filter(str.isdigit,[l for l in result.split('\n') if 'MATCH SCORE:' in l][0]))),100)
            except: ms=60
            try: ats = min(int(''.join(filter(str.isdigit,[l for l in result.split('\n') if 'ATS SCORE:'   in l][0]))),100)
            except: ats=65
            c1,c2=st.columns(2)
            with c1:
                cc="#00ff88" if ms>=70 else "#ffbb00" if ms>=50 else "#ff4444"
                st.markdown(f'<div class="metric-card"><div style="font-size:3rem;font-weight:900;color:{cc}">{ms}%</div><div style="color:#5a6478">JD Match</div></div>',unsafe_allow_html=True)
                st.progress(ms/100)
            with c2:
                cc2="#00ff88" if ats>=70 else "#ffbb00" if ats>=50 else "#ff4444"
                st.markdown(f'<div class="metric-card"><div style="font-size:3rem;font-weight:900;color:{cc2}">{ats}%</div><div style="color:#5a6478">ATS Score</div></div>',unsafe_allow_html=True)
                st.progress(ats/100)
            st.markdown(f'<div class="card">{result}</div>',unsafe_allow_html=True)

# ── Tab 5: Interview Prep ─────────────────────────────────
with tab5:
    st.markdown('<div class="section-title">🎯 Interview Question Generator</div>', unsafe_allow_html=True)
    if 'skills' not in st.session_state:
        st.info("👆 Please analyze your resume first!")
    else:
        c1,c2=st.columns(2)
        with c1:
            jtl=[j['title'] for j in st.session_state.get('jobs',[])] or ["Data Scientist"]
            sel_job=st.selectbox("Target Job",jtl)
        with c2:
            diff=st.selectbox("Difficulty",["Entry Level","Mid Level","Senior Level"])
        if st.button("🎯 Generate Questions",key="interview_btn"):
            with st.spinner("🤖 Generating..."):
                qs=generate_interview_questions(st.session_state['skills'],f"{diff} {sel_job}")
                st.session_state['questions']=qs; st.session_state['selected_job']=sel_job
        if 'questions' in st.session_state:
            st.markdown(f"### 📝 {st.session_state['selected_job']} Questions")
            st.markdown(f'<div class="card">{st.session_state["questions"]}</div>',unsafe_allow_html=True)

# ── Tab 6: Roadmap ────────────────────────────────────────
with tab6:
    st.markdown('<div class="section-title">📚 AI Learning Roadmap</div>', unsafe_allow_html=True)
    if 'roadmap' in st.session_state:
        st.markdown(f'<div class="card">{st.session_state["roadmap"]}</div>',unsafe_allow_html=True)
    else: st.info("Generate a custom roadmap below!")
    with st.form("form_roadmap"):
        c1,c2=st.columns(2)
        with c1: tj   = st.text_input("Target Job Title", value=user.get('job_target',''))
        with c2: miss = st.text_input("Skills to Learn",  placeholder="e.g. Deep Learning, SQL")
        gen=st.form_submit_button("📚 Generate Roadmap", use_container_width=True)
    if gen:
        if tj and miss:
            with st.spinner("🤖 Building your roadmap..."):
                rm=generate_skill_roadmap([s.strip() for s in miss.split(",")],tj)
                st.session_state['roadmap']=rm
            st.rerun()
        else: st.error("Please fill both fields!")

# ── Tab 7: Career Chat ────────────────────────────────────
with tab7:
    st.markdown(f"""
    <div style="background:linear-gradient(90deg,rgba(0,212,255,.08),rgba(123,47,247,.08));
        border:1px solid rgba(0,212,255,.15);border-radius:14px;
        padding:.75rem 1.2rem;display:flex;align-items:center;margin-bottom:.5rem;">
        <div style="width:40px;height:40px;background:linear-gradient(135deg,#00d4ff,#7b2ff7);
            border-radius:50%;display:flex;align-items:center;justify-content:center;
            font-size:1.2rem;margin-right:.75rem;">🤖</div>
        <div>
            <div style="color:white;font-weight:700;font-size:.95rem;">{bot_nick}</div>
            <div style="color:#00d4ff;font-size:.72rem;">● Online · AI Career Mentor</div>
        </div>
    </div>""", unsafe_allow_html=True)

    if not st.session_state.chat_history:
        chat_html = f'<div class="chat-window"><div class="chat-empty">🤖 <b style="color:#00d4ff">{bot_nick}</b> is ready!<br/>Ask me anything about your career or resume.<br/><br/><span style="font-size:.8rem;color:#2a3040">Type a message below →</span></div></div>'
    else:
        msgs=""
        for m in st.session_state.chat_history:
            if m['role']=='user': msgs+=f'<div class="msg-label-user">You</div><div class="msg-user">{m["content"]}</div>'
            else:                 msgs+=f'<div class="msg-label-bot">{bot_nick}</div><div class="msg-bot">{m["content"]}</div>'
        chat_html=f'<div class="chat-window">{msgs}</div>'
    st.markdown(chat_html, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:.4rem;color:#5a6478;font-size:.78rem;'>💡 Quick questions:</div>", unsafe_allow_html=True)
    qc1,qc2,qc3,qc4=st.columns(4)
    with qc1:
        if st.button("📝 Improve resume", key="q1"): st.session_state['quick_q']="How can I improve my resume?"
    with qc2:
        if st.button("💼 Best jobs",      key="q2"): st.session_state['quick_q']=f"Best jobs for my skills: {', '.join(st.session_state.get('skills',[])[:5])}"
    with qc3:
        if st.button("🎯 Interview tips", key="q3"): st.session_state['quick_q']="Tips to crack technical interviews."
    with qc4:
        if st.button("📈 Salary advice",  key="q4"): st.session_state['quick_q']="How do I negotiate a better salary?"

    with st.form("form_chat", clear_on_submit=True):
        ic,bc=st.columns([5,1])
        with ic: user_msg=st.text_input("Message",value=st.session_state.pop('quick_q',''),
                                         placeholder=f"Message {bot_nick}...",label_visibility="collapsed")
        with bc: send=st.form_submit_button("➤ Send",use_container_width=True)

    if send and user_msg.strip():
        ctx=f"You are {bot_nick}, a friendly expert AI career mentor. User: {name}, Education: {education}, Target: {job_target}."
        if 'skills' in st.session_state:
            ctx+=f" Skills: {', '.join(st.session_state['skills'][:10])}. Score: {st.session_state.get('resume_score','?')}/100."
        ctx+=f" Language: {st.session_state.get('language','English')}. Be concise (max 150 words), warm, practical."
        with st.spinner(f"💬 {bot_nick} is typing..."):
            resp=client.chat.completions.create(model="llama-3.3-70b-versatile",
                messages=[{"role":"user","content":f"{ctx}\n\nUser: {user_msg.strip()}"}],temperature=0.5)
            reply=resp.choices[0].message.content
        st.session_state.chat_history.append({"role":"user","content":user_msg.strip()})
        st.session_state.chat_history.append({"role":"assistant","content":reply})
        st.rerun()

    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat", key="clear_chat"): st.session_state.chat_history=[]; st.rerun()

# ── Tab 8: Resume Improver ────────────────────────────────
with tab8:
    st.markdown('<div class="section-title">✍️ Resume Line Improver</div>', unsafe_allow_html=True)
    st.markdown("Paste a weak bullet point → AI makes it powerful! 💪")
    with st.form("form_improver"):
        ol    =st.text_area("Your resume line:",placeholder='"Worked on Python project"',height=100)
        go_imp=st.form_submit_button("✨ Improve This Line",use_container_width=True)
    if go_imp:
        if ol.strip():
            with st.spinner("🤖 Rewriting..."):
                st.session_state['improved']=improve_resume_line(ol)
        else: st.error("Please enter a resume line!")
    if 'improved' in st.session_state:
        st.markdown("### ✅ Improved Versions:")
        st.markdown(f'<div class="card">{st.session_state["improved"]}</div>',unsafe_allow_html=True)