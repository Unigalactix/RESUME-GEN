import streamlit as st
from ai_helper import get_ai_status
from data_loader import get_data_inventory
from tools.resume_generator import render_resume_generator
from tools.resume_scorer import render_resume_scorer
from tools.job_finder import render_job_finder

st.set_page_config(page_title="AI Career Suite", page_icon="🚀", layout="wide")

ai_status = get_ai_status()
data_inventory = get_data_inventory("Data")

st.sidebar.title("Navigation")
st.sidebar.markdown("Welcome to the AI Career Suite. Select a tool below:")
selection = st.sidebar.radio("Go to:", ["AI Resume Generator", "Resume Score", "Find Jobs"])

st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip:** Use the AI Resume Generator to build a tailored PDF, then verify its impact with the Resume Score tool!")

if ai_status["configured"]:
    st.sidebar.success(ai_status["message"])
else:
    st.sidebar.warning(ai_status["message"])

if data_inventory["exists"] and not data_inventory["missing_required"]:
    st.sidebar.success("LinkedIn export files detected.")
else:
    missing_files = ", ".join(data_inventory["missing_required"])
    st.sidebar.warning(f"Missing required data files: {missing_files}")

if not ai_status["configured"]:
    st.warning("AI features are running in fallback mode because GEMINI_API_KEY is not configured.")

if data_inventory["missing_required"]:
    st.warning("The app is missing required LinkedIn export files. Resume generation quality will be limited until the Data folder is complete.")

if selection == "AI Resume Generator":
    render_resume_generator()
elif selection == "Resume Score":
    render_resume_scorer()
elif selection == "Find Jobs":
    render_job_finder()
