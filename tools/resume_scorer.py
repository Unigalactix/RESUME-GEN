import streamlit as st
import PyPDF2
from matcher import extract_text_from_url
import google.generativeai as genai
import os
import json

def get_resume_score(resume_text, jd_text):
    """Uses Gemini to score the resume text against the Job Description."""
    system_instruction = '''
    You are an expert ATS (Applicant Tracking System) parser and an elite technical recruiter. 
    Your strict task is to analyze the provided candidate Resume Text against the provided Job Description.
    
    You must return your analysis STRICTLY as a JSON object with the following schema:
    {
        "score": <int between 0 and 100 representing overall match percentage based on skills, impact, and keywords>,
        "strengths": ["string", "string", "string"], (aim for 2-3 points)
        "weaknesses": ["string", "string", "string"], (aim for 2-3 missing skills/keywords or weak areas)
        "actionable_suggestions": ["string", "string", "string"] (aim for 2-3 highly specific bullet points the candidate should add/re-write)
    }
    DO NOT output Markdown. DO NOT output ```json ``` blocks. ONLY output raw, valid JSON.
    '''
    
    prompt = f'''
    ## JOB DESCRIPTION
    {jd_text}
    
    ## RESUME TEXT
    {resume_text}
    '''
    
    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=system_instruction,
            generation_config={"response_mime_type": "application/json"}
        )
        response = model.generate_content(prompt)
        # Parse the JSON
        data = json.loads(response.text)
        return data
    except Exception as e:
        return {"error": str(e)}

def render_resume_scorer():
    st.title("📊 Resume Score & Analysis")
    st.markdown("Upload your existing PDF resume and a Job Description. Our AI will score your alignment and provide actionable feedback.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. Upload Resume")
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
        
    with col2:
        st.subheader("2. Job Description")
        jd_input = st.text_area("Paste JD text or URL:", height=150)
        
    if st.button("Score My Resume", use_container_width=True):
        if not uploaded_file:
            st.warning("Please upload a PDF resume.")
            return
        if not jd_input.strip():
            st.warning("Please provide a Job Description.")
            return
            
        with st.spinner("Analyzing your resume against the Job Description..."):
            # Extract PDF Text
            try:
                reader = PyPDF2.PdfReader(uploaded_file)
                resume_text = ""
                for page in reader.pages:
                    resume_text += page.extract_text() + "\n"
            except Exception as e:
                st.error(f"Failed to read PDF: {e}")
                return
                
            # Process JD Input
            jd = jd_input.strip()
            if jd.startswith("http://") or jd.startswith("https://"):
                jd = extract_text_from_url(jd)
                if jd.startswith("ERROR:"):
                    st.error(f"Failed to extract text from URL: {jd}")
                    return
            
            # Score
            results = get_resume_score(resume_text, jd)
            
            if "error" in results:
                st.error(f"Error during AI analysis: {results['error']}")
            else:
                st.markdown("---")
                st.header("📈 Analysis Results")
                
                # Display Score with conditional coloring
                score = results.get("score", 0)
                if score >= 80:
                    color = "green"
                elif score >= 60:
                    color = "orange"
                else:
                    color = "red"
                    
                st.markdown(f"<h1 style='text-align: center; color: {color}; font-size: 80px;'>{score}/100</h1>", unsafe_allow_html=True)
                
                # Display Strengths, Weaknesses, Suggestions
                c1, c2 = st.columns(2)
                with c1:
                    st.success("✅ **Key Strengths**")
                    for s in results.get("strengths", []):
                        st.write(f"- {s}")
                        
                with c2:
                    st.error("⚠️ **Areas for Improvement**")
                    for w in results.get("weaknesses", []):
                        st.write(f"- {w}")
                        
                st.info("💡 **Actionable Suggestions for Tailoring:**")
                for sug in results.get("actionable_suggestions", []):
                    st.write(f"- {sug}")
