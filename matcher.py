import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
import re

load_dotenv()

# Configure Google Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def clean_text(text):
    if not isinstance(text, str):
        return ""
    return ' '.join(str(text).split())

def match_skills(skills, job_description, top_n=15):
    """
    Uses Gemini to identify which of the user's skills are most relevant to the JD.
    """
    if not skills or not job_description or not api_key:
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
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Clean up possible markdown wrappers
        if text.startswith('```json'):
            text = text[7:-3].strip()
        elif text.startswith('```'):
            text = text[3:-3].strip()
        
        selected_skills = json.loads(text)
        
        # Merge picked skills with any missed ones to hit top_n if needed
        valid_skills = [s for s in selected_skills if s in skills]
        for s in skills:
            if s not in valid_skills and len(valid_skills) < top_n:
                valid_skills.append(s)
                
        return valid_skills[:top_n]
    except Exception as e:
        print(f"Error in match_skills with Gemini: {e}")
        return skills[:top_n]

def format_bullet_points(description, job_description=None):
    """
    If JD is provided, uses Gemini to rewrite and organize experience bullet points 
    to highlight relevance to the JD. Otherwise, just splits by newlines/bullets.
    """
    if not description:
        return []
    
    if not job_description or not api_key:
        bullets = re.split(r'•|- |\n', description)
        return [b.strip() for b in bullets if b.strip()]

    prompt = f"""
    Here is a Job Description:
    {job_description}
    
    Here is a candidate's experience description for a specific role:
    {description}
    
    Rewrite this experience into 3-4 professional bullet points that highlight the candidate's fit for the Job Description. 
    Keep it truthful to the original text but emphasize relevant aspects (impact, metrics, relevant tech).
    Return ONLY a JSON array of strings containing the bullet points WITHOUT bullet characters (like -, •). 
    Do not wrap in markdown quotes.
    """
    
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        if text.startswith('```json'):
            text = text[7:-3].strip()
        elif text.startswith('```'):
            text = text[3:-3].strip()
            
        bullets = json.loads(text)
        return bullets
    except Exception as e:
        print(f"Error in format_bullet_points with Gemini: {e}")
        bullets = re.split(r'•|- |\n', description)
        return [b.strip() for b in bullets if b.strip()]
