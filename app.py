import streamlit as st
from data_loader import load_all_data
from matcher import match_skills, format_bullet_points
from pdf_generator import generate_pdf

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
            
            # 2. Format and sort experience bullets
            tailored_experience = []
            for job in data['positions']:
                bullets = format_bullet_points(job['description'], jd)
                # Keep top 4 most relevant bullets
                job_copy = job.copy()
                job_copy['bullets'] = bullets[:4]
                if job_copy['bullets']: # Only append if there's actual content
                    tailored_experience.append(job_copy)

            # 3. Format project bullets (no sorting for now, just formatting)
            tailored_projects = []
            for proj in data['projects']:
                bullets = format_bullet_points(proj['description'], None) # No sorting
                proj_copy = proj.copy()
                proj_copy['bullets'] = bullets
                if proj_copy['bullets']:
                    tailored_projects.append(proj_copy)

            # 4. Generate PDF
            try:
                pdf_bytes = generate_pdf(
                    data['profile'], 
                    top_skills, 
                    tailored_experience, 
                    data['education'], 
                    tailored_projects
                )
                
                st.success("Resume generated successfully!")
                
                # Download Button
                st.download_button(
                    label="Download Tailored Resume",
                    data=pdf_bytes,
                    file_name="Tailored_Resume.pdf",
                    mime="application/pdf"
                )
                
                with st.expander("Preview Tailored Elements"):
                    st.write("**Top Skills Selected:**")
                    st.write(", ".join(top_skills))
                    st.write("**Top Bullet Point (Most Recent Job):**")
                    if tailored_experience and tailored_experience[0]['bullets']:
                        st.write(f"- {tailored_experience[0]['bullets'][0]}")

            except Exception as e:
                st.error(f"Error generating PDF: {e}")
