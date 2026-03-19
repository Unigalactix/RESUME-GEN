import streamlit as st
from data_loader import build_profile_completeness_report, load_all_data
from matcher import build_target_role_brief, build_targeting_context, get_matched_keywords, is_locally_relevant, match_skills, format_bullet_points, generate_suggestions, extract_text_from_url, select_top_relevant_items
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


def build_tailored_resume_from_jd(jd_text, data, variant_name, selected_sections, company_name="", role_name="", max_exp_items=3, max_project_items=3, max_cert_items=3):
    if not selected_sections:
        raise ValueError("Select at least one resume section.")

    top_skills = match_skills(data["skills"], jd_text, top_n=15)

    variant_config = get_resume_variant_config(variant_name)
    max_exp_bullets = variant_config.get("max_experience_bullets", 3)
    max_project_bullets = variant_config.get("max_project_bullets", 2)
    targeting_context = build_targeting_context(jd_text, company_name=company_name, role_name=role_name)

    selected_jobs = select_top_relevant_items(
        data["positions"],
        targeting_context,
        text_builder=lambda job: " ".join(
            [
                str(job.get("title", "")),
                str(job.get("company", "")),
                str(job.get("description", "")),
            ]
        ),
        max_items=max_exp_items,
        min_score=1,
    )

    tailored_experience = []
    for job in selected_jobs:
        bullets = format_bullet_points(job["description"], jd_text)
        job_copy = job.copy()
        job_copy["bullets"] = bullets[:max_exp_bullets]
        if job_copy["bullets"]:
            tailored_experience.append(job_copy)

    selected_projects = select_top_relevant_items(
        data["projects"],
        targeting_context,
        text_builder=lambda project: " ".join(
            [
                str(project.get("title", "")),
                str(project.get("description", "")),
            ]
        ),
        max_items=max_project_items,
        min_score=1,
    )

    tailored_projects = []
    for proj in selected_projects:
        bullets = format_bullet_points(proj["description"], jd_text)
        proj_copy = proj.copy()
        proj_copy["bullets"] = bullets[:max_project_bullets]
        if proj_copy["bullets"]:
            tailored_projects.append(proj_copy)

    tailored_certifications = select_top_relevant_items(
        data["certifications"],
        targeting_context,
        text_builder=lambda cert: " ".join(
            [
                str(cert.get("name", "")),
                str(cert.get("authority", "")),
            ]
        ),
        max_items=max_cert_items,
        min_score=1,
    )

    experience_selection_details = [
        {
            "title": job.get("title", ""),
            "company": job.get("company", ""),
            "matched_keywords": get_matched_keywords(
                " ".join([job.get("title", ""), job.get("company", ""), job.get("description", "")]),
                targeting_context,
            ),
        }
        for job in tailored_experience
    ]
    project_selection_details = [
        {
            "title": proj.get("title", ""),
            "matched_keywords": get_matched_keywords(
                " ".join([proj.get("title", ""), proj.get("description", "")]),
                targeting_context,
            ),
        }
        for proj in tailored_projects
    ]

    ai_suggestions = generate_suggestions(jd_text)
    resume_md = create_markdown_resume(
        data["profile"],
        top_skills,
        tailored_experience,
        data["education"],
        tailored_projects,
        certifications=tailored_certifications,
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
        "selected_experience_count": len(tailored_experience),
        "selected_projects_count": len(tailored_projects),
        "selected_certifications_count": len(tailored_certifications),
        "selection_details": {
            "experience": experience_selection_details,
            "projects": project_selection_details,
        },
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

    st.subheader("3. Targeting controls")
    with st.expander("⚙️ Adjust how many entries to include per section", expanded=False):
        st.caption("Entries are ranked by keyword relevance. Use these controls to include the top 2 or top 3 per section.")
        ctrl_col1, ctrl_col2, ctrl_col3 = st.columns(3)
        with ctrl_col1:
            max_exp_items = st.selectbox("Max experience entries", [2, 3], index=1, key="max_exp_items")
        with ctrl_col2:
            max_project_items = st.selectbox("Max project entries", [2, 3], index=1, key="max_proj_items")
        with ctrl_col3:
            max_cert_items = st.selectbox("Max certifications", [2, 3], index=1, key="max_cert_items")

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
                    company_name=company_name,
                    role_name=role_name,
                    max_exp_items=max_exp_items,
                    max_project_items=max_project_items,
                    max_cert_items=max_cert_items,
                )

                st.session_state.ai_suggestions = package["ai_suggestions"]
                st.session_state.resume_variant = variant_name
                st.session_state.resume_md = package["resume_md"]
                st.session_state.resume_target_brief = target_brief
                st.session_state.resume_target_company = company_name
                st.session_state.resume_target_role = role_name
                st.session_state.resume_selection_summary = (
                    package["selected_experience_count"],
                    package["selected_projects_count"],
                    package["selected_certifications_count"],
                )
                st.session_state.selection_details = package["selection_details"]

                st.success("Analysis complete! Review and edit your resume below.")

    if 'resume_md' in st.session_state:
        st.subheader("2. Review & Edit Resume (Markdown)")

        if st.session_state.get("resume_target_brief"):
            company_name = st.session_state.get("resume_target_company", "Target company")
            role_name = st.session_state.get("resume_target_role", "Target role")
            with st.expander(f"Inferred target brief for {role_name} at {company_name}", expanded=False):
                st.write(st.session_state["resume_target_brief"])

        if st.session_state.get("resume_selection_summary"):
            exp_count, project_count, cert_count = st.session_state["resume_selection_summary"]
            st.caption(
                f"Selected {exp_count} experience entries, {project_count} projects, and {cert_count} certifications based on target keyword relevance."
            )

        if st.session_state.get("selection_details"):
            details = st.session_state["selection_details"]
            with st.expander("🔍 Why these items were selected", expanded=False):
                exp_items = details.get("experience", [])
                proj_items = details.get("projects", [])
                if exp_items:
                    st.markdown("**Experience entries selected**")
                    for item in exp_items:
                        kws = ", ".join(item["matched_keywords"]) or "general relevance"
                        st.write(f"- **{item['title']}** at {item['company']}: `{kws}`")
                if proj_items:
                    st.markdown("**Projects selected**")
                    for item in proj_items:
                        kws = ", ".join(item["matched_keywords"]) or "general relevance"
                        st.write(f"- **{item['title']}**: `{kws}`")

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
