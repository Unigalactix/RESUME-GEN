# resume_formatter.py

# System Instructions for Gemini to strictly enforce ATS standards
ATS_SYSTEM_INSTRUCTION = """
You are an expert Executive Resume Writer and Career Coach. 
Your goal is to re-write candidate experience into highly optimized, ATS-friendly bullet points.
Strictly adhere to the following rules:
1. ONLY return the bullet points as a JSON array of strings. Do NOT wrap in markdown quotes.
2. The XYZ Formula: Accomplished [X] as measured by [Y], by doing [Z].
3. Action Verbs: Start every single bullet point with a strong action verb (e.g., Architected, Deployed, Engineered, Optimized). Never use weak openers like "Responsible for" or "Helped with".
4. Quantify: Inject numbers, percentages, and metrics to provide scale (e.g., "by 30%"). If exact numbers aren't provided in the source text, reasonably infer plausible scale if possible, or focus heavily on the impact.
5. No Pronouns: NEVER use "I," "me," "my," "our," or "we". 
6. Conciseness: Keep each bullet point to a maximum of 2 lines.
7. Relevance: Omit entirely any bullet points or details that are completely irrelevant to the target Job Description.
"""

DEFAULT_SECTION_ORDER = [
    "Header",
    "Summary",
    "Skills",
    "Experience",
    "Projects",
    "Certifications",
    "Publications",
    "Volunteering",
    "Languages",
    "Education",
]

RESUME_VARIANTS = {
    "ATS-safe": {
        "section_order": ["Summary", "Skills", "Experience", "Projects", "Certifications", "Education"],
        "include_summary": False,
        "max_experience_bullets": 4,
        "max_project_bullets": 3,
    },
    "Recruiter-friendly": {
        "section_order": ["Summary", "Experience", "Skills", "Projects", "Certifications", "Education", "Languages"],
        "include_summary": True,
        "max_experience_bullets": 3,
        "max_project_bullets": 2,
    },
    "New Grad Focus": {
        "section_order": ["Summary", "Skills", "Projects", "Experience", "Education", "Certifications", "Languages"],
        "include_summary": True,
        "max_experience_bullets": 3,
        "max_project_bullets": 4,
    },
}

def extract_city_state(location_string):
    """
    Cleans up a location string to ensure it's just City, State.
    Example: "123 Main St, Redmond, WA 98052" -> "Redmond, WA"
    """
    if not location_string:
        return ""
    
    parts = [p.strip() for p in location_string.split(',')]
    if len(parts) >= 2:
        # Assuming the last two parts are likely City, State (or State, Country)
        # Strip zip codes from the state part if present
        state_part = ''.join([c for c in parts[-1] if not c.isdigit()]).strip()
        return f"{parts[-2]}, {state_part}"
    return location_string

def get_section_order():
    """
    Returns the strict order of sections for an ATS-friendly technical resume.
    """
    return DEFAULT_SECTION_ORDER


def get_resume_variant_names():
    return list(RESUME_VARIANTS.keys())


def get_resume_variant_config(variant_name):
    return RESUME_VARIANTS.get(variant_name, RESUME_VARIANTS["ATS-safe"]).copy()


def get_effective_section_order(selected_sections=None, variant_name="ATS-safe"):
    configured_order = get_resume_variant_config(variant_name).get("section_order", [])
    ordered_sections = selected_sections or configured_order
    return ["Header"] + [section for section in ordered_sections if section != "Header"]


def build_contact_line(profile):
    parts = []
    if profile.get("phone"):
        parts.append(profile["phone"])
    if profile.get("email"):
        parts.append(profile["email"])
    for website in profile.get("website_links", [])[:3]:
        label = website.get("label") or website.get("url")
        if label:
            parts.append(label)
    if profile.get("location"):
        parts.append(profile["location"])

    seen = set()
    unique_parts = []
    for part in parts:
        normalized = part.strip().lower()
        if normalized and normalized not in seen:
            unique_parts.append(part.strip())
            seen.add(normalized)
    return " • ".join(unique_parts)
