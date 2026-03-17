import json
import re
import requests
from bs4 import BeautifulSoup
from ai_helper import generate_json, generate_text, is_ai_configured
from resume_formatter import ATS_SYSTEM_INSTRUCTION

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
