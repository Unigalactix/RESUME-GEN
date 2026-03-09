import streamlit as st
import requests
from bs4 import BeautifulSoup
import base64
from data_loader import load_all_data
from matcher import match_skills, format_bullet_points, evaluate_relevance, generate_suggestions
from markdown_generator import create_markdown_resume
from pdf_generator import generate_pdf_from_markdown

def extract_text_from_url(url):
    """Fetches and cleans visible text from a URL."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        for script in soup(["script", "style"]):
            script.extract()
        return soup.get_text(separator=' ', strip=True)
    except Exception as e:
        return f"ERROR: {e}"

def display_pdf(pdf_bytes):
    """Embeds the PDF using an HTML iframe via base64 encoding."""
    base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

@st.cache_data
def get_data():
    return load_all_data("Data")

def render_resume_generator():
    st.title("📄 AI Resume Generator")
    st.markdown("Upload your LinkedIn export data into the `Data/` folder, paste a job description, and get a tailored PDF resume!")

    with st.spinner("Loading profile data..."):
        data = get_data()

    st.sidebar.header("Profile Loaded")
    st.sidebar.write(f"**Name:** {data['profile'].get('first_name', '')} {data['profile'].get('last_name', '')}")
    st.sidebar.write(f"**Total Skills:** {len(data['skills'])}")
    st.sidebar.write(f"**Experience Entries:** {len(data['positions'])}")
    st.sidebar.write(f"**Education Entries:** {len(data['education'])}")
    st.sidebar.write(f"**Project Entries:** {len(data['projects'])}")

    st.subheader("1. Enter Job Description or URL")
    jd_input = st.text_area("Paste the Job Description text OR a link to the job posting:", height=200)

    if st.button("Generate Tailored Resume"):
        if not jd_input.strip():
            st.warning("Please enter a job description or URL.")
        else:
            with st.spinner("Processing input and tailoring your resume..."):
                jd = jd_input.strip()
                
                if jd.startswith("http://") or jd.startswith("https://"):
                    jd = extract_text_from_url(jd)
                    if jd.startswith("ERROR:"):
                        st.error(f"Failed to extract text from URL: {jd}")
                        st.stop()
                    st.info("Successfully extracted text from the provided URL.")
                    
                top_skills = match_skills(data['skills'], jd, top_n=15)
                
                tailored_experience = []
                for i, job in enumerate(data['positions']):
                    if i == 0 or evaluate_relevance(job['description'], jd):
                        bullets = format_bullet_points(job['description'], jd)
                        job_copy = job.copy()
                        job_copy['bullets'] = bullets[:4]
                        if job_copy['bullets']: 
                            tailored_experience.append(job_copy)

                tailored_projects = []
                for proj in data['projects']:
                     if evaluate_relevance(proj['description'], jd):
                        bullets = format_bullet_points(proj['description'], jd)
                        proj_copy = proj.copy()
                        proj_copy['bullets'] = bullets[:3]
                        if proj_copy['bullets']:
                            tailored_projects.append(proj_copy)

                st.session_state.ai_suggestions = generate_suggestions(jd)

                st.session_state.resume_md = create_markdown_resume(
                    data['profile'], 
                    top_skills, 
                    tailored_experience, 
                    data['education'], 
                    tailored_projects
                )
                    
                st.success("Analysis complete! Review and edit your resume below.")

    if 'resume_md' in st.session_state:
        st.subheader("2. Review & Edit Resume (Markdown)")
        
        if st.session_state.get('ai_suggestions'):
            with st.expander("💡 AI Content Suggestions (Based on Role)", expanded=True):
                st.info("Consider adding these keyword-rich bullet points into your experience section if they apply to you:")
                for s in st.session_state.ai_suggestions:
                    st.write(f"- {s}")
                    
        st.info("You can edit the text below. The changes will be reflected in the final PDF.")
        
        edited_md = st.text_area("Resume Content", value=st.session_state.resume_md, height=600)
        
        if edited_md != st.session_state.resume_md:
            st.session_state.resume_md = edited_md

        st.subheader("3. View & Download PDF")
        if st.button("Generate Final PDF"):
            try:
                with st.spinner("Generating minimal PDF..."):
                    pdf_bytes = generate_pdf_from_markdown(st.session_state.resume_md)
                    
                st.success("PDF generated successfully!")
                
                st.download_button(
                    label="Download Tailored Resume",
                    data=pdf_bytes,
                    file_name="Tailored_Resume.pdf",
                    mime="application/pdf",
                    key="download_btn" 
                )
                
                st.markdown("### PDF Preview")
                display_pdf(pdf_bytes)
                
            except Exception as e:
                st.error(f"Error generating PDF: {e}")
