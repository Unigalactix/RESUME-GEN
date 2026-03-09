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
    return ["Header", "Skills", "Experience", "Projects", "Education"]
