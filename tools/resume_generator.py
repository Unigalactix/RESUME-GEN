import streamlit as st
from data_loader import build_profile_completeness_report, load_all_data
from matcher import build_target_role_brief, match_skills, format_bullet_points, evaluate_relevance, generate_suggestions, extract_text_from_url
from markdown_generator import create_markdown_resume
from pdf_generator import generate_pdf_from_markdown
from resume_formatter import get_resume_variant_config, get_resume_variant_guidance, get_resume_variant_names, get_section_order
from pdf2image import convert_from_bytes


COMPANY_REFERENCE_OPTIONS = [
    "Select a company reference",
    "Amazon",
    "Google",
    "Microsoft",
    "Meta",
    "Apple",
    "NVIDIA",
    "Databricks",
    "Snowflake",
    "Salesforce",
    "ServiceNow",
    "Uber",
    "DoorDash",
    "Visa",
    "JPMorgan Chase",
    "Adobe",
    "Deloitte",
    "Accenture",
]

ROLE_REFERENCE_OPTIONS = [
    "Select a role reference",
    "Software Engineer",
    "Backend Engineer",
    "Frontend Engineer",
    "Full Stack Engineer",
    "Data Engineer",
    "Data Analyst",
    "Data Scientist",
    "Machine Learning Engineer",
    "AI Engineer",
    "DevOps Engineer",
    "Cloud Engineer",
    "Product Manager",
    "Business Analyst",
    "QA Engineer",
    "Solutions Architect",
]

def display_pdf_preview(pdf_bytes):
    """Converts PDF bytes to an image preview so browsers cannot block embedded PDF rendering."""
    try:
        images = convert_from_bytes(pdf_bytes, dpi=180, first_page=1, last_page=1, fmt="png")
        if not images:
            st.warning("Unable to render PDF preview image.")
            return

        st.image(images[0], caption="PDF Preview (Page 1)", use_container_width=True)
    except Exception as err:
        st.warning(
            "Preview image could not be generated in this environment. "
            "You can still download the PDF normally. "
            f"Details: {err}"
        )

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


def get_default_sections_for_variant(data, variant_name):
    return [
        section for section in get_resume_variant_config(variant_name)["section_order"]
        if section_has_content(section, data)
    ]


def resolve_reference_value(custom_value, selected_value, placeholder):
    custom_clean = (custom_value or "").strip()
    if custom_clean:
        return custom_clean
    return "" if selected_value == placeholder else selected_value


def build_tailored_resume_from_jd(jd_text, data, variant_name, selected_sections):
    if not selected_sections:
        raise ValueError("Select at least one resume section.")

    top_skills = match_skills(data["skills"], jd_text, top_n=15)

    variant_config = get_resume_variant_config(variant_name)
    max_exp_bullets = variant_config.get("max_experience_bullets", 3)
    max_project_bullets = variant_config.get("max_project_bullets", 2)

    tailored_experience = []
    for i, job in enumerate(data["positions"]):
        if i == 0 or evaluate_relevance(job["description"], jd_text):
            bullets = format_bullet_points(job["description"], jd_text)
            job_copy = job.copy()
            job_copy["bullets"] = bullets[:max_exp_bullets]
            if job_copy["bullets"]:
                tailored_experience.append(job_copy)

    tailored_projects = []
    for proj in data["projects"]:
        if evaluate_relevance(proj["description"], jd_text) or variant_config.get("prioritize_projects"):
            bullets = format_bullet_points(proj["description"], jd_text)
            proj_copy = proj.copy()
            proj_copy["bullets"] = bullets[:max_project_bullets]
            if proj_copy["bullets"]:
                tailored_projects.append(proj_copy)

    ai_suggestions = generate_suggestions(jd_text)
    resume_md = create_markdown_resume(
        data["profile"],
        top_skills,
        tailored_experience,
        data["education"],
        tailored_projects,
        certifications=data["certifications"],
        publications=data["publications"],
        languages=data["languages"],
        volunteering=data["volunteering"],
        options={
            "variant": variant_name,
            "section_order": selected_sections,
        },
    )
    return {
        "resume_md": resume_md,
        "ai_suggestions": ai_suggestions,
    }

def render_resume_generator():
    st.title("📄 AI Resume Generator")
    st.markdown(
        "Upload your LinkedIn export data into the `Data/` folder, then generate a tailored PDF resume from either a job description or a company-and-role target."
    )

    with st.spinner("Loading profile data..."):
        data = get_data()
        completeness = build_profile_completeness_report(data)

    section_choices = [section for section in get_section_order() if section != "Header"]
    variant_name = st.selectbox("Resume variant", get_resume_variant_names())
    variant_guidance = get_resume_variant_guidance(variant_name)
    st.caption(variant_guidance["description"])
    st.caption(
        "Section flow: "
        + " -> ".join(variant_guidance["section_order"])
        + f" | Bullets: experience <= {variant_guidance['max_experience_bullets']}, projects <= {variant_guidance['max_project_bullets']}"
    )
    default_sections = get_default_sections_for_variant(data, variant_name)
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
    st.caption("If the application does not show a full job description, use the company and role inputs below instead.")

    st.subheader("2. Or build from company + role")
    st.caption("Choose a reference from the dropdowns or type your own values. The app will infer a compact target brief when no JD is available.")
    company_col, role_col = st.columns(2)
    with company_col:
        selected_company_reference = st.selectbox("Company reference", COMPANY_REFERENCE_OPTIONS)
        custom_company_name = st.text_input("Or type company name", placeholder="e.g. Stripe")
    with role_col:
        selected_role_reference = st.selectbox("Role reference", ROLE_REFERENCE_OPTIONS)
        custom_role_name = st.text_input("Or type role name", placeholder="e.g. Staff Backend Engineer")

    if st.button("Generate Tailored Resume"):
        company_name = resolve_reference_value(
            custom_company_name,
            selected_company_reference,
            "Select a company reference",
        )
        role_name = resolve_reference_value(
            custom_role_name,
            selected_role_reference,
            "Select a role reference",
        )

        if not jd_input.strip() and (not company_name or not role_name):
            st.warning("Provide either a job description or both company and role inputs.")
        else:
            with st.spinner("Processing input and tailoring your resume..."):
                jd = jd_input.strip()
                target_brief = ""

                if jd.startswith("http://") or jd.startswith("https://"):
                    jd = extract_text_from_url(jd)
                    if jd.startswith("ERROR:"):
                        st.error(f"Failed to extract text from URL: {jd}")
                        st.stop()
                    st.info("Successfully extracted text from the provided URL.")

                if not jd:
                    try:
                        target_brief = build_target_role_brief(company_name, role_name)
                    except ValueError as err:
                        st.error(str(err))
                        st.stop()
                    jd = target_brief
                    st.info(f"No job description provided. Using an inferred target brief for {role_name} at {company_name}.")

                if not selected_sections:
                    st.warning("Select at least one resume section to generate a resume.")
                    return

                package = build_tailored_resume_from_jd(
                    jd_text=jd,
                    data=data,
                    variant_name=variant_name,
                    selected_sections=selected_sections,
                )

                st.session_state.ai_suggestions = package["ai_suggestions"]
                st.session_state.resume_variant = variant_name
                st.session_state.resume_md = package["resume_md"]
                st.session_state.resume_target_brief = target_brief
                st.session_state.resume_target_company = company_name
                st.session_state.resume_target_role = role_name

                st.success("Analysis complete! Review and edit your resume below.")

    if 'resume_md' in st.session_state:
        st.subheader("2. Review & Edit Resume (Markdown)")

        if st.session_state.get("resume_target_brief"):
            company_name = st.session_state.get("resume_target_company", "Target company")
            role_name = st.session_state.get("resume_target_role", "Target role")
            with st.expander(f"Inferred target brief for {role_name} at {company_name}", expanded=False):
                st.write(st.session_state["resume_target_brief"])
        
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
                display_pdf_preview(pdf_bytes)
                
            except Exception as e:
                st.error(f"Error generating PDF: {e}")
