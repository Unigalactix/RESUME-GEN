import streamlit as st
import urllib.parse
import json
from ai_helper import generate_json

COMMON_ROLES = [
    "Software Engineer",
    "Data Engineer",
    "Data Analyst",
    "Data Scientist",
    "Machine Learning Engineer",
    "AI Engineer",
    "Backend Engineer",
    "Frontend Engineer",
    "Full Stack Engineer",
    "DevOps Engineer",
    "Cloud Engineer",
    "Cybersecurity Analyst",
    "Product Manager",
    "Business Analyst",
    "QA Engineer",
    "Solutions Architect",
]

INDUSTRY_OPTIONS = [
    "Software",
    "AI / ML",
    "Fintech",
    "Consulting",
    "Healthcare Tech",
    "E-commerce",
    "Cloud / Infrastructure",
    "Cybersecurity",
    "Semiconductors",
]

COMPANY_STAGE_OPTIONS = ["Startup", "Mid-size", "Large enterprise", "Consulting"]
JOB_MODE_OPTIONS = ["Remote", "Hybrid", "On-site"]

WORK_AUTH_OPTIONS = [
    "General search",
    "F-1 OPT friendly",
    "STEM OPT friendly",
    "H-1B sponsorship required",
    "Cap-exempt H-1B only",
]

SEARCH_PRESETS = {
    "Custom": {
        "description": "Start with your own filters.",
        "experience_level": "Any",
        "work_auth_focus": "General search",
        "job_modes": ["Remote", "Hybrid"],
        "industries": [],
        "sponsor_only": False,
    },
    "F-1 OPT New Grad": {
        "description": "Biases the search toward entry-level roles and companies that commonly hire international new grads.",
        "experience_level": "New Grad",
        "work_auth_focus": "F-1 OPT friendly",
        "job_modes": ["Remote", "Hybrid"],
        "industries": ["Software", "AI / ML", "Fintech"],
        "sponsor_only": False,
    },
    "STEM OPT Early Career": {
        "description": "Targets practical early-career roles where STEM OPT is common and longer-term sponsorship is realistic.",
        "experience_level": "Entry Level",
        "work_auth_focus": "STEM OPT friendly",
        "job_modes": ["Remote", "Hybrid"],
        "industries": ["Software", "Cloud / Infrastructure", "AI / ML"],
        "sponsor_only": False,
    },
    "H-1B Transfer": {
        "description": "Focuses on known sponsors and roles that are more realistic for current H-1B holders switching employers.",
        "experience_level": "Mid Level",
        "work_auth_focus": "H-1B sponsorship required",
        "job_modes": ["Hybrid", "On-site"],
        "industries": ["Software", "Consulting", "Fintech"],
        "sponsor_only": True,
    },
    "Cap-Exempt Research": {
        "description": "Narrower search mode for university, nonprofit, or research-oriented employers.",
        "experience_level": "Any",
        "work_auth_focus": "Cap-exempt H-1B only",
        "job_modes": ["On-site", "Hybrid"],
        "industries": ["Healthcare Tech", "AI / ML"],
        "sponsor_only": True,
    },
}

KNOWN_H1B_SPONSORS = {
    "Accenture",
    "Adobe",
    "Amazon",
    "Apple",
    "Capgemini",
    "Cisco",
    "Cognizant",
    "Databricks",
    "Deloitte",
    "DoorDash",
    "Google",
    "IBM",
    "Infosys",
    "Intel",
    "JPMorgan Chase",
    "KPMG",
    "Meta",
    "Microsoft",
    "NVIDIA",
    "Oracle",
    "PwC",
    "Qualcomm",
    "Salesforce",
    "ServiceNow",
    "Snowflake",
    "Tesla",
    "Uber",
    "Visa",
    "Walmart Global Tech",
    "Wayfair",
}

ROLE_FAMILY_SPONSORS = {
    "software": ["Google", "Microsoft", "Amazon", "Meta", "Apple", "Databricks", "Snowflake", "ServiceNow"],
    "data": ["Databricks", "Snowflake", "Amazon", "Microsoft", "Google", "Walmart Global Tech", "Visa", "JPMorgan Chase"],
    "ml": ["NVIDIA", "Google", "Microsoft", "Meta", "Apple", "Amazon", "Databricks", "Tesla"],
    "cloud": ["Amazon", "Microsoft", "Google", "Oracle", "Cisco", "IBM", "Salesforce", "ServiceNow"],
    "security": ["Cisco", "Google", "Microsoft", "IBM", "Amazon", "Oracle", "Qualcomm", "Tesla"],
    "product": ["Google", "Microsoft", "Amazon", "Meta", "Adobe", "Salesforce", "Uber", "DoorDash"],
    "business": ["Accenture", "Deloitte", "PwC", "KPMG", "Visa", "JPMorgan Chase", "Capgemini", "Cognizant"],
    "general": ["Amazon", "Google", "Microsoft", "Accenture", "Deloitte", "Salesforce", "Adobe", "Oracle"],
}


def normalize_company_name(name):
    return "".join(ch for ch in name.lower() if ch.isalnum())


def is_known_h1b_sponsor(company):
    normalized_company = normalize_company_name(company)
    for sponsor in KNOWN_H1B_SPONSORS:
        normalized_sponsor = normalize_company_name(sponsor)
        if normalized_company == normalized_sponsor:
            return True
        if normalized_company in normalized_sponsor or normalized_sponsor in normalized_company:
            return True
    return False


def infer_role_family(role):
    normalized_role = role.lower()

    if any(keyword in normalized_role for keyword in ["machine learning", "ml", "ai", "artificial intelligence"]):
        return "ml"
    if any(keyword in normalized_role for keyword in ["data", "analytics", "analyst", "scientist"]):
        return "data"
    if any(keyword in normalized_role for keyword in ["cloud", "devops", "sre", "platform", "infrastructure"]):
        return "cloud"
    if any(keyword in normalized_role for keyword in ["security", "cyber", "infosec"]):
        return "security"
    if any(keyword in normalized_role for keyword in ["product", "program manager", "project manager"]):
        return "product"
    if any(keyword in normalized_role for keyword in ["business", "operations", "consult", "finance"]):
        return "business"
    if any(keyword in normalized_role for keyword in ["engineer", "developer", "frontend", "backend", "full stack", "software"]):
        return "software"
    return "general"


def get_curated_sponsors(role, limit=8):
    family = infer_role_family(role)
    companies = ROLE_FAMILY_SPONSORS.get(family, ROLE_FAMILY_SPONSORS["general"])
    curated = []

    for company in companies[:limit]:
        curated.append(
            {
                "company": company,
                "reason": f"Regularly hires for {role} and is a practical target for international candidates in the U.S. market.",
                "sponsorship_signal": "Known sponsor",
                "visa_fit": "Historically active in H-1B sponsorship; verify the specific job posting before applying.",
            }
        )

    return curated


def build_search_prompt(filters):
    return "\n".join(
        [
            f"Role: {filters['role']}",
            f"Location: {filters['location'] or 'Not specified'}",
            f"Experience level: {filters['experience_level']}",
            f"Job modes: {', '.join(filters['job_modes']) if filters['job_modes'] else 'Any'}",
            f"Industry focus: {', '.join(filters['industries']) if filters['industries'] else 'Any'}",
            f"Company stages: {', '.join(filters['company_stages']) if filters['company_stages'] else 'Any'}",
            f"Work authorization focus: {filters['work_auth_focus']}",
            f"Known H-1B sponsors only: {'Yes' if filters['sponsor_only'] else 'No'}",
        ]
    )


def generate_job_search_queries(filters):
    """Uses Gemini to identify target companies based on role, work authorization, and search filters."""
    system_instruction = '''
    You are an expert recruiter for U.S. hiring, with special expertise helping F-1 OPT students,
    STEM OPT candidates, and H-1B visa holders identify realistic employers.

    Based on the provided filters, suggest 6-10 companies that are likely targets for this job search.
    When work authorization constraints are provided, prioritize companies that are more practical for
    international candidates. If the search asks for known H-1B sponsors only, avoid companies that are
    not credible sponsorship targets.

    Return your response STRICTLY as valid JSON with this schema:
    {
        "suggestions": [
            {
                "company": "string",
                "reason": "Short 1-sentence explanation of why it is a good target.",
                "sponsorship_signal": "Known sponsor | Likely sponsor | Unknown",
                "visa_fit": "Short 1-sentence note about OPT/H-1B relevance."
            }
        ]
    }

    Do not output Markdown. Do not wrap the JSON in code fences. Only return raw JSON.
    '''

    try:
        data = generate_json(build_search_prompt(filters), system_instruction=system_instruction, fallback={"suggestions": []})
        if not isinstance(data, dict):
            return []
        return data.get("suggestions", [])
    except Exception:
        return []


def merge_suggestions(ai_suggestions, curated_suggestions, sponsor_only, limit=10):
    merged = []
    seen = set()

    primary = curated_suggestions + ai_suggestions if sponsor_only else ai_suggestions + curated_suggestions

    for item in primary:
        company = item.get("company", "").strip()
        if not company:
            continue

        normalized_company = normalize_company_name(company)
        if normalized_company in seen:
            continue
        if sponsor_only and not is_known_h1b_sponsor(company):
            continue

        merged.append(
            {
                "company": company,
                "reason": item.get("reason", "Relevant employer for this target role."),
                "sponsorship_signal": item.get(
                    "sponsorship_signal",
                    "Known sponsor" if is_known_h1b_sponsor(company) else "Unknown",
                ),
                "visa_fit": item.get(
                    "visa_fit",
                    "Historically active in sponsorship." if is_known_h1b_sponsor(company) else "Confirm sponsorship policy on the posting.",
                ),
            }
        )
        seen.add(normalized_company)

        if len(merged) >= limit:
            break

    return merged


def generate_google_dork(company, filters):
    """Generates a Google query targeting common ATS platforms and visa-relevant keywords."""
    query_parts = [company, f'"{filters["role"]}"']

    if filters["location"]:
        query_parts.append(f'"{filters["location"]}"')

    if filters["experience_level"] != "Any":
        query_parts.append(f'"{filters["experience_level"]}"')

    if filters["job_modes"]:
        mode_clause = " OR ".join(f'"{mode}"' for mode in filters["job_modes"])
        query_parts.append(f"({mode_clause})")

    work_auth_focus = filters["work_auth_focus"]
    if work_auth_focus == "F-1 OPT friendly":
        query_parts.append('(OPT OR "F-1" OR "international students" OR sponsorship)')
    elif work_auth_focus == "STEM OPT friendly":
        query_parts.append('(OPT OR "STEM OPT" OR "F-1" OR sponsorship)')
    elif work_auth_focus == "H-1B sponsorship required":
        query_parts.append('("H1B" OR "H-1B" OR sponsorship OR sponsor OR "work authorization")')
    elif work_auth_focus == "Cap-exempt H-1B only":
        query_parts.append('("cap exempt" OR "cap-exempt" OR university OR nonprofit OR research)')

    query_parts.append('(site:lever.co OR site:greenhouse.io OR site:workday.com OR site:icims.com OR site:myworkdayjobs.com)')
    base_query = " ".join(query_parts)
    encoded_query = urllib.parse.quote_plus(base_query)
    return f"https://www.google.com/search?q={encoded_query}"


def generate_ats_specific_links(company, filters):
    ats_domains = {
        "All ATS": "site:lever.co OR site:greenhouse.io OR site:workday.com OR site:icims.com OR site:myworkdayjobs.com",
        "Greenhouse": "site:greenhouse.io",
        "Lever": "site:lever.co",
        "Workday": "site:workday.com OR site:myworkdayjobs.com",
    }
    links = {}
    for label, site_filter in ats_domains.items():
        query = f'{company} "{filters["role"]}" ({site_filter})'
        if filters["location"]:
            query += f' "{filters["location"]}"'
        links[label] = f"https://www.google.com/search?q={urllib.parse.quote_plus(query)}"
    return links


def render_job_finder():
    st.title("🔍 Job Finder & Company Targeter")
    st.markdown(
        "Find realistic target employers for your job search, with extra support for F-1 OPT students, STEM OPT candidates, and H-1B visa holders. Use the filters below to narrow companies by role, work authorization needs, and job setup."
    )

    preset_name = st.selectbox("Search strategy preset", list(SEARCH_PRESETS.keys()))
    preset = SEARCH_PRESETS[preset_name]
    st.caption(preset["description"])

    st.subheader("1. Define your target role")
    role_mode = st.radio(
        "Role selection mode",
        ["Choose from common roles", "Enter my own role"],
        horizontal=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        selected_role = st.selectbox(
            "Common role options",
            COMMON_ROLES,
            index=1,
            disabled=role_mode != "Choose from common roles",
        )
    with col2:
        custom_role = st.text_input(
            "Custom role",
            placeholder="Examples: Quant Analyst, Embedded Software Engineer, AI Product Manager",
            disabled=role_mode != "Enter my own role",
        )

    target_role = selected_role if role_mode == "Choose from common roles" else custom_role.strip()

    st.subheader("2. Add filters")
    col3, col4 = st.columns(2)
    with col3:
        target_location = st.text_input("Location", "Remote")
        experience_level = st.selectbox(
            "Experience level",
            ["Any", "Internship", "New Grad", "Entry Level", "Mid Level", "Senior"],
            index=["Any", "Internship", "New Grad", "Entry Level", "Mid Level", "Senior"].index(preset["experience_level"]),
        )
        work_auth_focus = st.selectbox("Work authorization focus", WORK_AUTH_OPTIONS, index=WORK_AUTH_OPTIONS.index(preset["work_auth_focus"]))
    with col4:
        job_modes = st.multiselect("Job mode", JOB_MODE_OPTIONS, default=preset["job_modes"])
        industries = st.multiselect("Industry focus", INDUSTRY_OPTIONS, default=preset["industries"])
        company_stages = st.multiselect("Company stage", COMPANY_STAGE_OPTIONS)

    default_sponsor_only = preset["sponsor_only"] or work_auth_focus in ["H-1B sponsorship required", "Cap-exempt H-1B only"]
    sponsor_only = st.checkbox(
        "Only show known H-1B sponsoring companies",
        value=default_sponsor_only,
        help="Uses a curated list of frequent H-1B sponsors and filters the recommendations accordingly.",
    )

    if st.button("Generate Targets & Queries", use_container_width=True):
        if not target_role.strip():
            st.warning("Please enter a Target Role.")
            return

        filters = {
            "role": target_role.strip(),
            "location": target_location.strip(),
            "experience_level": experience_level,
            "job_modes": job_modes,
            "industries": industries,
            "company_stages": company_stages,
            "work_auth_focus": work_auth_focus,
            "sponsor_only": sponsor_only,
        }

        with st.spinner(f"Analyzing companies hiring for {target_role}..."):
            ai_suggestions = generate_job_search_queries(filters)
            curated_suggestions = get_curated_sponsors(target_role)
            suggestions = merge_suggestions(ai_suggestions, curated_suggestions, sponsor_only)

            if not suggestions:
                st.error("Failed to generate suggestions. Please try again.")
            else:
                st.markdown("---")
                st.subheader("🎯 Suggested Target Companies")
                st.info(
                    "These targets reflect your role, search filters, and visa constraints. Use the Google links to search company ATS boards directly instead of relying only on general job boards."
                )

                active_filters = [
                    f"Role: {filters['role']}",
                    f"Authorization: {filters['work_auth_focus']}",
                    f"Experience: {filters['experience_level']}",
                ]
                if filters["location"]:
                    active_filters.append(f"Location: {filters['location']}")
                if filters["job_modes"]:
                    active_filters.append(f"Mode: {', '.join(filters['job_modes'])}")
                st.caption(" | ".join(active_filters))

                for item in suggestions:
                    company = item.get("company", "Unknown")
                    reason = item.get("reason", "")
                    sponsorship_signal = item.get("sponsorship_signal", "Unknown")
                    visa_fit = item.get("visa_fit", "Confirm sponsorship details on the job posting.")

                    search_link = generate_google_dork(company, filters)
                    ats_links = generate_ats_specific_links(company, filters)

                    st.markdown(f"### **{company}**")
                    st.markdown(f"*{reason}*")
                    st.write(f"Sponsorship signal: {sponsorship_signal}")
                    st.write(f"Visa note: {visa_fit}")
                    st.markdown(f"[🔍 Search active {target_role} listings at {company} on Google]({search_link})")
                    st.caption(
                        " | ".join(
                            [f"[{label}]({url})" for label, url in ats_links.items()]
                        )
                    )
                    st.markdown("---")
