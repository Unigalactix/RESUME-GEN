import streamlit as st
from data_loader import load_all_data
from matcher import match_skills, format_bullet_points, evaluate_relevance, generate_suggestions
from markdown_generator import create_markdown_resume
from pdf_generator import generate_pdf_from_markdown

st.set_page_config(page_title="AI Resume Generator", page_icon="📄")

st.title("📄 AI Resume Generator")
st.markdown("Upload your LinkedIn export data into the `Data/` folder, paste a job description, and get a tailored PDF resume!")

# Load Data
@st.cache_data
def get_data():
    return load_all_data("Data")

with st.spinner("Loading profile data..."):
    data = get_data()

st.sidebar.header("Profile Loaded")
st.sidebar.write(f"**Name:** {data['profile'].get('first_name', '')} {data['profile'].get('last_name', '')}")
st.sidebar.write(f"**Total Skills:** {len(data['skills'])}")
st.sidebar.write(f"**Experience Entries:** {len(data['positions'])}")
st.sidebar.write(f"**Education Entries:** {len(data['education'])}")
st.sidebar.write(f"**Project Entries:** {len(data['projects'])}")

st.subheader("1. Enter Job Description")
jd = st.text_area("Paste the Job Description here:", height=200)

if st.button("Generate Tailored Resume"):
    if not jd.strip():
        st.warning("Please enter a job description.")
    else:
        with st.spinner("Analyzing job description and tailoring your resume..."):
            # 1. Match Skills
            top_skills = match_skills(data['skills'], jd, top_n=15)
            
            # 2. Filter, Format and sort experience bullets
            tailored_experience = []
            for i, job in enumerate(data['positions']):
                # Always keep the first (most recent) job, filter the rest
                if i == 0 or evaluate_relevance(job['description'], jd):
                    bullets = format_bullet_points(job['description'], jd)
                    # Keep top 4 most relevant bullets
                    job_copy = job.copy()
                    job_copy['bullets'] = bullets[:4]
                    if job_copy['bullets']: 
                        tailored_experience.append(job_copy)

            # 3. Filter and Format project bullets
            tailored_projects = []
            for proj in data['projects']:
                 if evaluate_relevance(proj['description'], jd):
                    bullets = format_bullet_points(proj['description'], jd) # Use JD to format projects too
                    proj_copy = proj.copy()
                    proj_copy['bullets'] = bullets[:3] # Max 3 bullets for projects
                    if proj_copy['bullets']:
                        tailored_projects.append(proj_copy)

            # 4. Generate AI Suggestions based on Job Description
            st.session_state.ai_suggestions = generate_suggestions(jd)

            # 5. Generate Initial Markdown
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
    
    # Editable text area for the markdown
    edited_md = st.text_area("Resume Content", value=st.session_state.resume_md, height=600)
    
    # Update session state if edited
    if edited_md != st.session_state.resume_md:
        st.session_state.resume_md = edited_md

    st.subheader("3. Download PDF")
    if st.button("Generate & Download PDF"):
        try:
            with st.spinner("Generating minimal PDF..."):
                pdf_bytes = generate_pdf_from_markdown(st.session_state.resume_md)
                
            st.download_button(
                label="Download Tailored Resume",
                data=pdf_bytes,
                file_name="Tailored_Resume.pdf",
                mime="application/pdf",
                # Use a different key so it doesn't clash with the generate button
                key="download_btn" 
            )
            st.success("PDF ready for download!")
        except Exception as e:
            st.error(f"Error generating PDF: {e}")
