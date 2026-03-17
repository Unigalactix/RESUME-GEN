import streamlit as st
import base64
from data_loader import build_profile_completeness_report, load_all_data
from matcher import match_skills, format_bullet_points, evaluate_relevance, generate_suggestions, extract_text_from_url
from markdown_generator import create_markdown_resume
from pdf_generator import generate_pdf_from_markdown
from resume_formatter import get_resume_variant_config, get_resume_variant_names, get_section_order

def display_pdf(pdf_bytes):
    """Embeds the PDF using an HTML iframe via base64 encoding."""
    base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

@st.cache_data
def get_data():
    return load_all_data("Data")


def section_has_content(section_name, data, tailored_experience=None, tailored_projects=None):
    if section_name == "Summary":
        return bool(data["profile"].get("summary"))
    if section_name == "Skills":
        return bool(data["skills"])
    if section_name == "Experience":
        return bool(tailored_experience if tailored_experience is not None else data["positions"])
    if section_name == "Projects":
        return bool(tailored_projects if tailored_projects is not None else data["projects"])
    if section_name == "Certifications":
        return bool(data["certifications"])
    if section_name == "Publications":
        return bool(data["publications"])
    if section_name == "Volunteering":
        return bool(data["volunteering"])
    if section_name == "Languages":
        return bool(data["languages"])
    if section_name == "Education":
        return bool(data["education"])
    return False

def render_resume_generator():
    st.title("📄 AI Resume Generator")
    st.markdown("Upload your LinkedIn export data into the `Data/` folder, paste a job description, and get a tailored PDF resume!")

    with st.spinner("Loading profile data..."):
        data = get_data()
        completeness = build_profile_completeness_report(data)

    section_choices = [section for section in get_section_order() if section != "Header"]
    variant_name = st.selectbox("Resume variant", get_resume_variant_names())
    default_sections = [
        section for section in get_resume_variant_config(variant_name)["section_order"]
        if section_has_content(section, data)
    ]
    selected_sections = st.multiselect(
        "Sections to include and order",
        section_choices,
        default=default_sections,
        help="The order of your selection is used as the resume section order.",
    )

    st.sidebar.header("Profile Loaded")
    st.sidebar.write(f"**Name:** {data['profile'].get('first_name', '')} {data['profile'].get('last_name', '')}")
    st.sidebar.write(f"**Total Skills:** {len(data['skills'])}")
    st.sidebar.write(f"**Experience Entries:** {len(data['positions'])}")
    st.sidebar.write(f"**Education Entries:** {len(data['education'])}")
    st.sidebar.write(f"**Project Entries:** {len(data['projects'])}")
    st.sidebar.write(f"**Certifications:** {len(data['certifications'])}")
    st.sidebar.write(f"**Languages:** {len(data['languages'])}")

    if completeness["missing_sections"]:
        st.sidebar.warning("Missing profile sections: " + ", ".join(completeness["missing_sections"]))

    with st.expander("Profile completeness insights"):
        for item in completeness["highlights"]:
            st.write(f"- {item}")
        for item in completeness["warnings"]:
            st.write(f"- {item}")

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

                if not selected_sections:
                    st.warning("Select at least one resume section to generate a resume.")
                    return

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
                    if evaluate_relevance(proj['description'], jd) or variant_name == "New Grad Focus":
                        bullets = format_bullet_points(proj['description'], jd)
                        proj_copy = proj.copy()
                        proj_copy['bullets'] = bullets[: get_resume_variant_config(variant_name)["max_project_bullets"]]
                        if proj_copy['bullets']:
                            tailored_projects.append(proj_copy)

                st.session_state.ai_suggestions = generate_suggestions(jd)
                st.session_state.resume_variant = variant_name

                st.session_state.resume_md = create_markdown_resume(
                    data['profile'], 
                    top_skills, 
                    tailored_experience, 
                    data['education'], 
                    tailored_projects,
                    certifications=data['certifications'],
                    publications=data['publications'],
                    languages=data['languages'],
                    volunteering=data['volunteering'],
                    options={
                        "variant": variant_name,
                        "section_order": selected_sections,
                    },
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
