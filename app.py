import streamlit as st
from file_utils import load_candidates, save_candidate, bulk_save_candidates, clear_candidates, update_candidate
from vapi_call import call_candidate_with_vapi
import pdfplumber
import docx
import os

def extract_text_from_resume(file):
    text = ""
    if file.name.endswith(".pdf"):
        pdf = pdfplumber.open(file)
        for page in pdf.pages:
            text += page.extract_text() or ""
    elif file.name.endswith(".docx"):
        docx_file = docx.Document(file)
        for para in docx_file.paragraphs:
            text += para.text + "\n"
    else:
        text = file.read().decode(errors="ignore")
    return text


#---------CSS-----------------
st.markdown("""
<style>
html, body, .stApp {
    background: #131416 !important;
    color: #f2f3f5 !important;
    font-family: 'Segoe UI', 'Roboto', sans-serif !important;
}
[data-testid="stSidebar"] {
    background: linear-gradient(135deg, #24263C 60%, #14151A 100%)!important;
    color: #eee !important;
}
.st-bb, .st-c9, .st-cq, .st-cn, .st-co, .block-container {
    background: none !important;
}
h1, h2, h3, h4 {color: #ffa14f;}
.upload-block, .job-block, .cand-block, .stFileUploader, .stTextArea, .stDataFrame {
    background: #22232a !important;
    border-radius: 22px !important;
    box-shadow: 0 10px 32px #020d1991, 0 1.5px 0px #222;
    color: #f2f3f5 !important;
    border: 1.5px solid #1e1f21 !important;
}
.stTextInput>div>div>input, .stNumberInput>div>input, .stTextArea>div>textarea {
    background-color: #1c1d23 !important;
    color: #f7f7f7 !important;
    border-radius: 10px !important;
    border:1.5px solid #232433 !important;
}
.stFileUploader .widget-label {color: #ffa14f !important;}
.stButton>button, .vapi-btn {
    background: linear-gradient(90deg,#43e97b,#38f9d7);
    color: #18191A !important; font-weight:700; font-size:1.15em;
    border:none; padding:13px 34px; border-radius:15px;
    box-shadow:0 5px 22px #43e97b41; margin: 8px 0; transition:0.18s;
}
.stButton>button:hover, .vapi-btn:hover {background:linear-gradient(90deg,#ffa14f,#ff512f); color:#fff;}
.sidebar .sidebar-content {background: none !important;}
.stDataFrame {background: #191a1f !important; border-radius:16px;}
hr {border-top: 1.5px solid #292929;}
code {background: #191a1d !important;}
.success-msg {color:#90ffe5; font-weight:700; animation:bounce 0.9s;}
.error-msg {color:#ff4d4d; font-weight:700; animation:shake 1s;}
@keyframes bounce {0%{transform:scale(1);} 40%{transform:scale(1.09);} 60%{transform:scale(.93);} 80%{transform:scale(1.05);} 100%{transform:scale(1);}}
@keyframes shake {0%,100%{transform:translateX(0);}20%,60%{transform:translateX(-6px);}40%,80%{transform:translateX(6px);}}
label[data-testid="stWidgetLabel"] {color: #ffa14f !important;}
.st-bw, .st-ar {background: #18191A !important;}
.stAlert {background: #252633 !important;}
</style>
""",unsafe_allow_html=True)


# ---- SIDEBAR ----
with st.sidebar:
    st.image("https://emojicdn.elk.sh/🤖", width=60)
    st.title("ATS Admin Panel")
    st.markdown("**Quick Links:**")
    st.markdown('''
- [MongoDB Atlas](https://cloud.mongodb.com/)
- [Vapi Docs](https://docs.vapi.ai/)
- [Contact](mailto:admin@yourdomain.com)
''')
    st.markdown("---")
    st.info("1. Upload the job description.\n2. Upload resumes.\n3. Click 'Bulk Process & Shortlist'.\n \nView and call shortlists in the next tab!")

tabs = st.tabs(["🔍 Data Upload & Shortlist", "📋 Shortlists/Admin"])

with tabs[0]:
    st.markdown("""<div class="headerblock"><h1>ATS AI Bulk Shortlisting System</h1><div style='font-size:1.4rem;color:#E4572E;font-weight:600;margin-top:7px'>MongoDB + Vapi Integration</div></div>""", unsafe_allow_html=True)

    st.markdown('<div class="mxcard">',unsafe_allow_html=True)
    st.markdown('<span class="uploadicon">📄</span> <b>Step 1: Upload Job Description</b>', unsafe_allow_html=True)
    jd_file = st.file_uploader("Job Description (TXT/PDF/DOCX)", type=["txt", "pdf", "docx"], key="jd")
    job_desc = ""
    if jd_file:
        job_desc = extract_text_from_resume(jd_file)
        st.text_area("Job Description Content", value=job_desc, height=80, key="jobdesc")
    st.markdown('</div>',unsafe_allow_html=True)

    st.markdown('<div class="mxcard">',unsafe_allow_html=True)
    st.markdown('<span class="uploadicon">📂</span> <b>Step 2: Upload Résumés</b>', unsafe_allow_html=True)
    resume_files = st.file_uploader("Upload Resumes (PDF, DOCX, TXT)", type=["pdf","docx","txt"], accept_multiple_files=True, key="resumeup")
    st.markdown('</div>',unsafe_allow_html=True)

    st.markdown('<div class="mxcard">',unsafe_allow_html=True)
    st.markdown('<span class="uploadicon">🔢</span> <b>Step 3: Number of Candidates to Shortlist</b>', unsafe_allow_html=True)
    num_to_shortlist = st.number_input("Shortlist N candidates:", min_value=1, max_value=100, value=5, key="nshort")
    st.markdown('</div>',unsafe_allow_html=True)

    msg = ""
    checkpoint = 0
    if st.button("🚦 Bulk Process & Shortlist", key="bulkbtn", help="Process uploaded resumes and shortlist automatically",):
        if not job_desc or not resume_files:
            msg = '<div class="mxwarn">❗ Please upload BOTH a job description AND at least 1 resume.</div>'
        else:
            checkpoint += 1
            st.progress(0.33, text="🔍 Checking files…")
            jd_words = set(job_desc.lower().split())
            candidate_entries = []
            for file in resume_files:
                text = extract_text_from_resume(file)
                if not text.strip():
                    st.warning(f"Resume {file.name} is empty or corrupt, skipped!")
                    continue
                resume_words = set(text.lower().split())
                score = len(jd_words.intersection(resume_words))
                candidate_entries.append({
                    "name": file.name.replace('.pdf', '').replace('.docx',''),
                    "phone": "", "resume": text[:3000], "AI_score": score,
                    "shortlist_status": "", "call_status": "", "vapi_result": ""
                })
            if not candidate_entries:
                msg = '<div class="mxwarn">❗ All resumes are invalid or empty.</div>'
            else:
                st.progress(0.66, text="🤖 Scoring & Sorting resumes…")
                candidate_entries.sort(key=lambda x: x["AI_score"], reverse=True)
                for idx, cand in enumerate(candidate_entries):
                    cand['shortlist_status'] = "shortlisted" if idx < num_to_shortlist else ""
                clear_candidates()
                bulk_save_candidates(candidate_entries)
                st.progress(1.0, text="🎉 All done! Shortlists saved.")
                checkpoint += 2
                msg = f'<div class="mxsucc"><span class="checkpoint">✔</span> {len(candidate_entries)} resumes processed.<br><span class="checkpoint">✔</span> Top {num_to_shortlist} auto-shortlisted!</div>'
                import pandas as pd
                st.dataframe(pd.DataFrame(candidate_entries).drop(columns=["resume"]))
    if msg:
        st.markdown(msg, unsafe_allow_html=True)

with tabs[1]:
    st.markdown('<div class="headerblock"><h2 style="margin-bottom:7px;">Shortlists & All Candidates</h2></div>', unsafe_allow_html=True)
    candidates = load_candidates()
    if not candidates:
        st.markdown('<div class="mxwarn">No candidates in system! Please upload and process resumes first.</div>', unsafe_allow_html=True)
    for cand in candidates:
        shortlist = cand.get('shortlist_status') == "shortlisted"
        extra_class = "sbadge" if shortlist else ""
        st.markdown(f"<div class='candcard'>", unsafe_allow_html=True)
        st.markdown(f"""
<h4>{cand.get('name','?')} <span class="score">{"⭐" if shortlist else ""}{cand.get('AI_score','')}</span>
<span class="{extra_class}">{'Shortlisted' if shortlist else 'Candidate'}</span></h4>
<b>Call Status:</b> {cand.get('call_status','')}<br>
<b>Result:</b> <code>{cand.get('vapi_result','')}</code>
""", unsafe_allow_html=True)
        # VAPI call button for shortlists
        if shortlist:
            btn_key = f"call_{cand['name']}_{cand.get('AI_score')}"
            call_clicked = st.button(f"📞 Vapi Call {cand['name']}", key=btn_key, help="Trigger an AI call to this candidate")
            if call_clicked:
                phone = cand.get('phone','')
                name = cand.get('name','')
                callback_url = os.getenv("VAPI_CALLBACK_URL", "https://yourcallbackurl.com")
                vapi_response = call_candidate_with_vapi(
                    name, phone,
                    os.getenv("VAPI_ASSISTANT_ID", ""),
                    os.getenv("VAPI_API_KEY", ""),
                    os.getenv("VAPI_PHONE_NUMBER_ID", ""),
                    callback_url
                )
                st.markdown(f'<div class="mxsucc">📞 AI Call initiated for <b>{name}</b>!<br>Returned: {vapi_response}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
