import streamlit as st
from file_utils import save_candidate, load_candidates, update_candidate
from vapi_call import call_candidate_with_vapi
import os

st.title("ATS + Vapi AI Calling Platform")

# --- Credentials (edit these) ---
VAPI_API_KEY = os.getenv("VAPI_API_KEY", "YOUR_VAPI_API_KEY")
VAPI_ASSISTANT_ID = os.getenv("VAPI_ASSISTANT_ID", "YOUR_VAPI_ASSISTANT_ID")
CALLBACK_URL = os.getenv("CALLBACK_URL", "YOUR_WEBHOOK_URL")
VAPI_PHONE_NUMBER_ID = os.getenv("VAPI_PHONE_NUMBER_ID", "YOUR_VAPI_PHONE_NUMBER_ID")

# Dummy Gemini analysis part (replace with your own)
summary = st.text_area("Resume Summary (Paste or Generate from Gemini)", "")
score = st.number_input("AI Score (Paste or Generate from Gemini)", min_value=0, max_value=100, value=80)

candidate_name = st.text_input("Candidate Name")
candidate_phone = st.text_input("Candidate Phone Number")

if st.button("Shortlist"):
    candidate = {
        "name": candidate_name,
        "phone": candidate_phone,
        "resume_summary": summary,
        "AI_score": str(score),
        "shortlist_status": "shortlisted",
        "call_status": "",
        "vapi_result": ""
    }
    save_candidate(candidate)
    st.success("Candidate shortlisted and saved!")

st.subheader("Shortlisted Candidates")
candidates = load_candidates()

for cand in load_candidates():
    if 'name' in cand and 'phone' in cand:  # Only print if keys exist
        st.write(f"{cand['name']} | {cand['phone']} | Shortlisted: {cand.get('shortlist_status', '')}")
    else:
        st.write("Row skipped: missing data", cand)

for idx, cand in enumerate(candidates):
    st.write(
        f"{cand['name']} | {cand['phone']} | Shortlisted: {cand['shortlist_status']} | "
        f"Call: {cand.get('call_status','')} | Vapi Result: {cand.get('vapi_result','')}"
    )
    btn_key = f"call-{cand['name']}-{cand['phone']}-{idx}"
    if st.button(f"AI Call Candidate {cand['name']} ({cand['phone']})", key=btn_key):
        result = call_candidate_with_vapi(
            cand["name"], cand["phone"],
            VAPI_ASSISTANT_ID, VAPI_API_KEY, VAPI_PHONE_NUMBER_ID
        )
        st.write(f"Call initiated: {result}")
