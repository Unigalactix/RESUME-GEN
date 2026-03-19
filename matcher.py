import json
import re
import requests
from bs4 import BeautifulSoup
from ai_helper import generate_json, generate_text, is_ai_configured
from resume_formatter import ATS_SYSTEM_INSTRUCTION


STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "in", "into", "is", "it",
    "of", "on", "or", "that", "the", "to", "with", "will", "your", "you", "our", "their", "this",
    "using", "use", "build", "built", "role", "company", "target", "job", "experience", "project",
    "work", "working", "team", "teams", "across", "strong", "relevant", "skills", "skill", "tools",
}


ROLE_TARGET_PROFILES = [
    {
        "keywords": ["backend", "software engineer", "software developer", "full stack", "full-stack"],
        "responsibilities": [
            "design and ship production software features",
            "improve system reliability, scalability, and latency",
            "collaborate with product and cross-functional teams",
            "write maintainable code, tests, and documentation",
        ],
        "skills": ["Python", "Java", "APIs", "System Design", "Testing", "Distributed Systems"],
        "tools": ["Git", "Docker", "CI/CD", "SQL"],
        "domain_terms": ["scalability", "performance", "ownership", "production systems"],
    },
    {
        "keywords": ["frontend", "ui", "web engineer"],
        "responsibilities": [
            "build responsive user interfaces and product experiences",
            "improve usability, accessibility, and performance",
            "partner with design and product stakeholders",
            "maintain reusable components and front-end quality standards",
        ],
        "skills": ["JavaScript", "TypeScript", "React", "CSS", "Accessibility", "Testing"],
        "tools": ["React", "HTML", "CSS", "Git", "Design Systems"],
        "domain_terms": ["user experience", "accessibility", "component architecture", "performance"],
    },
    {
        "keywords": ["data engineer", "analytics engineer"],
        "responsibilities": [
            "build reliable data pipelines and transformation workflows",
            "improve data quality, lineage, and observability",
            "model datasets for analytics and downstream consumers",
            "work with stakeholders to operationalize reporting needs",
        ],
        "skills": ["Python", "SQL", "ETL", "Data Modeling", "Batch Processing", "Automation"],
        "tools": ["Airflow", "Spark", "dbt", "Warehouse Platforms"],
        "domain_terms": ["data reliability", "pipelines", "warehousing", "governance"],
    },
    {
        "keywords": ["data scientist", "analyst", "business analyst"],
        "responsibilities": [
            "analyze data to identify trends and business opportunities",
            "build dashboards, experiments, and decision-support models",
            "communicate findings to technical and non-technical partners",
            "translate ambiguous questions into measurable insights",
        ],
        "skills": ["SQL", "Python", "Statistics", "Experimentation", "Visualization", "Storytelling"],
        "tools": ["Tableau", "Power BI", "Jupyter", "Excel"],
        "domain_terms": ["insights", "KPIs", "experimentation", "stakeholder communication"],
    },
    {
        "keywords": ["machine learning", "ml", "ai engineer"],
        "responsibilities": [
            "build, evaluate, and deploy machine learning solutions",
            "improve model performance, monitoring, and reliability",
            "prepare data and features for experimentation and production",
            "partner with engineering teams to operationalize ML workflows",
        ],
        "skills": ["Python", "Machine Learning", "Model Evaluation", "Data Processing", "Experimentation", "MLOps"],
        "tools": ["PyTorch", "TensorFlow", "MLflow", "Docker"],
        "domain_terms": ["model performance", "feature engineering", "inference", "deployment"],
    },
    {
        "keywords": ["devops", "cloud", "sre", "platform", "infrastructure"],
        "responsibilities": [
            "improve deployment automation and release reliability",
            "monitor production systems and respond to incidents",
            "harden infrastructure, observability, and operational processes",
            "partner with engineers to improve platform efficiency",
        ],
        "skills": ["Cloud Infrastructure", "Automation", "Scripting", "Incident Response", "Reliability", "Networking"],
        "tools": ["AWS", "Azure", "GCP", "Terraform", "Kubernetes", "CI/CD"],
        "domain_terms": ["availability", "monitoring", "infrastructure", "operational excellence"],
    },
    {
        "keywords": ["product manager", "product"],
        "responsibilities": [
            "define product requirements and prioritize roadmap work",
            "align engineering, design, and business stakeholders",
            "analyze outcomes and iterate on product decisions",
            "drive execution from discovery through launch",
        ],
        "skills": ["Roadmapping", "Prioritization", "Stakeholder Management", "Analytics", "Communication", "Execution"],
        "tools": ["SQL", "Product Analytics", "A/B Testing", "Documentation"],
        "domain_terms": ["roadmap", "user needs", "launches", "product strategy"],
    },
]

DEFAULT_ROLE_TARGET_PROFILE = {
    "responsibilities": [
        "deliver measurable business impact in the target role",
        "collaborate effectively with cross-functional stakeholders",
        "solve operational or technical problems with clear ownership",
        "communicate outcomes, tradeoffs, and progress clearly",
    ],
    "skills": ["Problem Solving", "Communication", "Execution", "Collaboration", "Analysis", "Ownership"],
    "tools": ["Documentation", "Analytics", "Automation"],
    "domain_terms": ["impact", "stakeholders", "delivery", "results"],
}

def extract_text_from_url(url):
    """Fetches and cleans visible text from a URL."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
        return soup.get_text(separator=' ', strip=True)
    except Exception as e:
        return f"ERROR: {e}"

def clean_text(text):
    if not isinstance(text, str):
        return ""
    return ' '.join(str(text).split())


def extract_target_keywords(text, max_keywords=25):
    cleaned = clean_text(text).lower()
    if not cleaned:
        return []

    counts = {}
    for token in re.findall(r"[a-z0-9][a-z0-9\+\.#/-]{1,}", cleaned):
        normalized = token.strip("-./")
        if len(normalized) < 3 or normalized in STOPWORDS:
            continue
        counts[normalized] = counts.get(normalized, 0) + 1

    ranked = sorted(counts.items(), key=lambda item: (-item[1], -len(item[0]), item[0]))
    return [keyword for keyword, _ in ranked[:max_keywords]]


def build_targeting_context(jd_text, company_name="", role_name=""):
    context_parts = [clean_text(jd_text), clean_text(company_name), clean_text(role_name)]
    combined_text = " ".join(part for part in context_parts if part)
    keywords = extract_target_keywords(combined_text)
    return {
        "text": combined_text,
        "keywords": keywords,
        "keyword_set": set(keywords),
        "company_name": clean_text(company_name).lower(),
        "role_name": clean_text(role_name).lower(),
    }


def score_target_alignment(text, targeting_context, extra_terms=None):
    combined_text = clean_text(text).lower()
    if not combined_text:
        return 0

    token_set = set(extract_target_keywords(combined_text, max_keywords=40))
    overlap = len(token_set & targeting_context["keyword_set"])
    substring_bonus = 0
    for term in extra_terms or []:
        normalized_term = clean_text(term).lower()
        if normalized_term and normalized_term in combined_text:
            substring_bonus += 2

    role_word_bonus = 0
    for role_word in extract_target_keywords(targeting_context.get("role_name", ""), max_keywords=10):
        if role_word in combined_text:
            role_word_bonus += 2

    return overlap * 3 + substring_bonus + role_word_bonus


def select_top_relevant_items(items, targeting_context, text_builder, max_items=3, min_score=1):
    ranked_items = []
    for index, item in enumerate(items):
        item_text = text_builder(item)
        extra_terms = []
        if targeting_context.get("company_name"):
            extra_terms.append(targeting_context["company_name"])
        if targeting_context.get("role_name"):
            extra_terms.append(targeting_context["role_name"])

        score = score_target_alignment(item_text, targeting_context, extra_terms=extra_terms)
        ranked_items.append((score, -index, item))

    ranked_items.sort(key=lambda entry: (entry[0], entry[1]), reverse=True)
    selected = [item for score, _, item in ranked_items if score >= min_score][:max_items]

    if len(selected) >= 2:
        return selected
    return [item for _, _, item in ranked_items[: min(max_items, len(ranked_items))]]


def get_matched_keywords(item_text, targeting_context):
    """Returns sorted list of target keywords that appear in the given item text."""
    cleaned = clean_text(item_text).lower()
    if not cleaned:
        return []
    token_set = set(extract_target_keywords(cleaned, max_keywords=40))
    return sorted(token_set & targeting_context["keyword_set"])


def is_locally_relevant(item_text, targeting_context, min_score=1):
    """
    Fast local keyword-based relevance gate using score_target_alignment.
    Returns True when the item meets the minimum overlap threshold,
    replacing LLM evaluate_relevance calls for pre-ranked candidate items.
    """
    return score_target_alignment(item_text, targeting_context) >= min_score


def infer_role_target_profile(role_name):
    normalized_role = clean_text(role_name).lower()
    for profile in ROLE_TARGET_PROFILES:
        if any(keyword in normalized_role for keyword in profile["keywords"]):
            return {
                "responsibilities": profile["responsibilities"][:],
                "skills": profile["skills"][:],
                "tools": profile["tools"][:],
                "domain_terms": profile["domain_terms"][:],
            }
    return {
        "responsibilities": DEFAULT_ROLE_TARGET_PROFILE["responsibilities"][:],
        "skills": DEFAULT_ROLE_TARGET_PROFILE["skills"][:],
        "tools": DEFAULT_ROLE_TARGET_PROFILE["tools"][:],
        "domain_terms": DEFAULT_ROLE_TARGET_PROFILE["domain_terms"][:],
    }


def render_target_role_brief(company_name, role_name, profile):
    summary = clean_text(profile.get("summary")) or (
        f"Target role: {role_name} at {company_name}. Focus the resume on quantified results, relevant tools, "
        "and evidence of direct fit for the role."
    )
    responsibilities = [clean_text(item) for item in profile.get("responsibilities", []) if clean_text(item)]
    skills = [clean_text(item) for item in profile.get("skills", []) if clean_text(item)]
    tools = [clean_text(item) for item in profile.get("tools", []) if clean_text(item)]
    domain_terms = [clean_text(item) for item in profile.get("domain_terms", []) if clean_text(item)]

    parts = [
        f"Target Company: {company_name}",
        f"Target Role: {role_name}",
        f"Role Summary: {summary}",
    ]
    if responsibilities:
        parts.append("Core Responsibilities: " + "; ".join(responsibilities[:5]))
    if skills:
        parts.append("Priority Skills: " + ", ".join(skills[:8]))
    if tools:
        parts.append("Likely Tools: " + ", ".join(tools[:6]))
    if domain_terms:
        parts.append("Relevant Terms: " + ", ".join(domain_terms[:6]))
    return "\n".join(parts)


def build_target_role_brief(company_name, role_name, prefer_ai=True):
    company = clean_text(company_name)
    role = clean_text(role_name)
    if not company or not role:
        raise ValueError("Both company name and role name are required.")

    fallback_profile = infer_role_target_profile(role)
    fallback_profile["summary"] = (
        f"Inferred hiring brief for a {role} opening at {company}. Emphasize directly relevant experience, strong execution, "
        "measurable impact, and tools typically expected for this role."
    )

    if not prefer_ai or not is_ai_configured():
        return render_target_role_brief(company, role, fallback_profile)

    prompt = f"""
    Create a compact ATS-focused hiring brief for a candidate targeting the following opening.

    Company: {company}
    Role: {role}

    Return ONLY raw JSON using this exact schema:
    {{
        "summary": "string",
        "responsibilities": ["string"],
        "skills": ["string"],
        "tools": ["string"],
        "domain_terms": ["string"]
    }}

    Requirements:
    - Keep the summary to 1-2 sentences.
    - responsibilities: 4-5 items.
    - skills: 6-8 items.
    - tools: up to 6 items.
    - domain_terms: 4-6 items.
    - Focus on likely hiring expectations, not culture or benefits.
    - Avoid markdown.
    """

    try:
        profile = generate_json(prompt, fallback=fallback_profile)
        if not isinstance(profile, dict):
            profile = fallback_profile
    except Exception:
        profile = fallback_profile

    return render_target_role_brief(company, role, profile)

def match_skills(skills, job_description, top_n=15):
    """
    Uses Gemini to identify which of the user's skills are most relevant to the JD.
    """
    if not skills or not job_description or not is_ai_configured():
        return skills[:top_n]
    
    prompt = f"""
    Here is a Job Description:
    {job_description}
    
    Here is a list of candidate skills:
    {', '.join(skills)}
    
    Based on the Job Description, select up to {top_n} most relevant skills from the candidate's list. 
    Return ONLY a JSON array of strings, nothing else. Do not wrap in markdown quotes.
    """
    
    try:
        selected_skills = generate_json(prompt, fallback=skills[:top_n])
        if not isinstance(selected_skills, list):
            return skills[:top_n]
        
        # Merge picked skills with any missed ones to hit top_n if needed
        valid_skills = [s for s in selected_skills if s in skills]
        for s in skills:
            if s not in valid_skills and len(valid_skills) < top_n:
                valid_skills.append(s)
                
        return valid_skills[:top_n]
    except Exception as e:
        print(f"Error in match_skills with Gemini: {e}")
        return skills[:top_n]

def evaluate_relevance(description, job_description):
    """
    Evaluates if a given job/project description is actually relevant to the JD.
    Returns True if relevant enough to include, False otherwise.
    """
    if not description or not job_description or not is_ai_configured():
        return True # Default to keep if no JD or API key

    prompt = f"""
    Job Description:
    {job_description}

    Candidate Experience:
    {description}

    Is this candidate experience STRONGLY and DIRECTLY relevant to the Job Description? 
    We are trying to fit this on a highly targeted, minimal 1-page resume. 
    If it is only vaguely related or completely unrelated, reply 'NO'. 
    If it provides strong evidence of required skills, reply 'YES'.
    Reply ONLY with 'YES' or 'NO'.
    """
    try:
        text = generate_text(prompt).upper()
        return 'YES' in text
    except Exception as e:
        print(f"Error evaluating relevance: {e}")
        return True

def format_bullet_points(description, job_description=None):
    """
    If JD is provided, uses Gemini to rewrite and organize experience bullet points 
    to highlight relevance to the JD using strict ATS formatting rules. 
    Otherwise, just splits by newlines/bullets.
    """
    if not description:
        return []
    
    if not job_description or not is_ai_configured():
        bullets = re.split(r'•|- |\n', description)
        return [b.strip() for b in bullets if b.strip()]

    prompt = f"""
    {ATS_SYSTEM_INSTRUCTION}
    
    Target Job Description:
    {job_description}
    
    Original Candidate Experience:
    {description}
    
    Rewrite this experience into 3-4 professional bullet points enforcing ALL system instructions (XYZ formula, action verbs, metrics, absolutely no pronouns).
    Return ONLY a JSON array of strings containing the bullet points WITHOUT bullet characters (like -, •). 
    """
    
    try:
        bullets = generate_json(prompt, fallback=[])
        if not isinstance(bullets, list):
            bullets = []
        return bullets
    except Exception as e:
        print(f"Error in format_bullet_points with Gemini: {e}")
        bullets = re.split(r'•|- |\n', description)
        return [b.strip() for b in bullets if b.strip()]

def generate_suggestions(job_description):
    """
    Analyzes the Job Description and suggests 2-3 extra bullet points or keywords 
    the user should manually add to their resume to heavily target the company/role.
    """
    if not job_description or not is_ai_configured():
        return []
        
    prompt = f"""
    Analyze the following Job Description:
    {job_description}
    
    Based on the role and likely company needs inferred from this description, suggest 2 to 3 highly impactful, keyword-rich bullet points (or focus areas) the candidate should ensure are on their resume if they have the experience. 
    Format them as actionable advice.
    Return ONLY a JSON array of strings. Do not wrap in markdown quotes.
    """
    
    try:
        suggestions = generate_json(prompt, fallback=[])
        if not isinstance(suggestions, list):
            suggestions = []
        return suggestions
    except Exception as e:
        print(f"Error generating suggestions: {e}")
        return []
