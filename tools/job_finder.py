import streamlit as st
import google.generativeai as genai
import os
import urllib.parse
import json

def generate_job_search_queries(role, location):
    """Uses Gemini to identify top companies hiring for this role and generates queries."""
    system_instruction = '''
    You are an expert technical recruiter and career coach.
    Based on the provided User Target Role and Location (optional), suggest 5-10 top companies 
    that are highly likely to be hiring for this type of role. Focus on a mix of tech giants 
    and high-growth startups depending on the nature of the role.
    
    You must return your analysis STRICTLY as a JSON object with the following schema:
    {
        "suggestions": [
            {
                "company": "string",
                "reason": "Short 1-sentence explanation of why it's a good target for this role."
            }
        ]
    }
    DO NOT output Markdown. DO NOT output ```json ``` blocks. ONLY output raw, valid JSON.
    '''
    
    prompt = f"Role: {role}\nLocation: {location}"
    
    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=system_instruction,
            generation_config={"response_mime_type": "application/json"}
        )
        response = model.generate_content(prompt)
        # Parse the JSON
        data = json.loads(response.text)
        return data.get("suggestions", [])
    except Exception as e:
        return []

def generate_google_dork(company, role):
    """Generates a boolean Google search query targeting common ATS platforms."""
    base_query = f'{company} "{role}" (site:lever.co OR site:greenhouse.io OR site:workday.com OR site:icims.com OR site:myworkdayjobs.com)'
    encoded_query = urllib.parse.quote_plus(base_query)
    return f"https://www.google.com/search?q={encoded_query}"

def render_job_finder():
    st.title("🔍 Job Finder & Company Targeter")
    st.markdown("Looking for a specific role? Tell us what you're looking for, and our AI will suggest top target companies and give you direct Google 'Dork' links to bypass generic job boards and find their hidden ATS listings.")
    
    col1, col2 = st.columns(2)
    with col1:
        target_role = st.text_input("Target Role (e.g. Senior Data Engineer)", "Data Engineer")
    with col2:
        target_location = st.text_input("Location (Optional) (e.g. Remote, San Francisco)", "Remote")
        
    if st.button("Generate Targets & Queries", use_container_width=True):
        if not target_role.strip():
            st.warning("Please enter a Target Role.")
            return
            
        with st.spinner(f"Analyzing companies hiring for {target_role}..."):
            suggestions = generate_job_search_queries(target_role, target_location)
            
            if not suggestions:
                st.error("Failed to generate suggestions. Please try again.")
            else:
                st.markdown("---")
                st.subheader("🎯 Suggested Target Companies")
                st.info("Click the links below to instantly search the company's ATS boards (Greenhouse, Lever, Workday) using advanced Google search operators.")
                
                for item in suggestions:
                    company = item.get("company", "Unknown")
                    reason = item.get("reason", "")
                    
                    # Generate search link
                    search_link = generate_google_dork(company, target_role)
                    
                    st.markdown(f"### **{company}**")
                    st.markdown(f"*{reason}*")
                    st.markdown(f"[🔍 Search active `{target_role}` listings at {company} on Google]({search_link})")
                    st.markdown("---")
