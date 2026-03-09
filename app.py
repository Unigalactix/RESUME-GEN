import streamlit as st
from tools.resume_generator import render_resume_generator
from tools.resume_scorer import render_resume_scorer
from tools.job_finder import render_job_finder

st.set_page_config(page_title="AI Career Suite", page_icon="🚀", layout="wide")

st.sidebar.title("Navigation")
st.sidebar.markdown("Welcome to the AI Career Suite. Select a tool below:")
selection = st.sidebar.radio("Go to:", ["AI Resume Generator", "Resume Score", "Find Jobs"])

st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip:** Use the AI Resume Generator to build a tailored PDF, then verify its impact with the Resume Score tool!")

if selection == "AI Resume Generator":
    render_resume_generator()
elif selection == "Resume Score":
    render_resume_scorer()
elif selection == "Find Jobs":
    render_job_finder()
