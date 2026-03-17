import streamlit as st
import PyPDF2
from ai_helper import generate_json
from matcher import extract_text_from_url

def get_resume_score(resume_text, jd_text):
    """Uses Gemini to score the resume text against the Job Description."""
    system_instruction = '''
    You are an expert ATS parser and technical recruiter.
    Analyze the provided resume against the job description and return highly actionable output.

    Return STRICT JSON with this schema:
    {
        "score": <int between 0 and 100>,
        "score_breakdown": {
            "keyword_match": <int>,
            "technical_alignment": <int>,
            "impact_strength": <int>,
            "experience_alignment": <int>
        },
        "strengths": ["string"],
        "weaknesses": ["string"],
        "missing_keywords": ["string"],
        "missing_tools": ["string"],
        "missing_domain_terms": ["string"],
        "rewrite_priorities": ["string"],
        "rewritten_bullets": ["string"],
        "actionable_suggestions": ["string"]
    }
    Keep each list concise and specific. Only return raw JSON.
    '''
    
    prompt = f'''
    ## JOB DESCRIPTION
    {jd_text}
    
    ## RESUME TEXT
    {resume_text}
    '''
    
    try:
        data = generate_json(prompt, system_instruction=system_instruction)
        if not isinstance(data, dict):
            return {"error": "The AI returned an unexpected response shape."}
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

                breakdown = results.get("score_breakdown", {})
                if breakdown:
                    st.subheader("Score Breakdown")
                    b1, b2, b3, b4 = st.columns(4)
                    b1.metric("Keyword Match", breakdown.get("keyword_match", 0))
                    b2.metric("Technical Alignment", breakdown.get("technical_alignment", 0))
                    b3.metric("Impact Strength", breakdown.get("impact_strength", 0))
                    b4.metric("Experience Alignment", breakdown.get("experience_alignment", 0))
                
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

                g1, g2, g3 = st.columns(3)
                with g1:
                    st.warning("Missing Keywords")
                    for item in results.get("missing_keywords", []):
                        st.write(f"- {item}")
                with g2:
                    st.warning("Missing Tools")
                    for item in results.get("missing_tools", []):
                        st.write(f"- {item}")
                with g3:
                    st.warning("Missing Domain Terms")
                    for item in results.get("missing_domain_terms", []):
                        st.write(f"- {item}")

                if results.get("rewrite_priorities"):
                    st.info("✍️ **Rewrite Priorities**")
                    for item in results.get("rewrite_priorities", []):
                        st.write(f"- {item}")

                if results.get("rewritten_bullets"):
                    st.info("🧱 **Suggested Resume Bullets**")
                    for bullet in results.get("rewritten_bullets", []):
                        st.write(f"- {bullet}")
                        
                st.info("💡 **Actionable Suggestions for Tailoring:**")
                for sug in results.get("actionable_suggestions", []):
                    st.write(f"- {sug}")
