import re
from resume_formatter import get_section_order, extract_city_state

def create_markdown_resume(profile, top_skills, experience, education, projects):
    """
    Generates a Markdown string representing the resume.
    """
    md = []
    
    # 1. HEADER
    name = f"{profile.get('first_name', '')} {profile.get('last_name', '')}".strip()
    md.append(f"# {name}")
    
    contact_info = profile.get("websites", "")
    if contact_info:
        md.append(f"**Contact:** {contact_info}")
    
    # Clean location if available, else skip
    location = extract_city_state(profile.get("location", "")) # Note: we might need to add location to profile dict in data_loader if it exists
    if location:
        md.append(f"**Location:** {location}")
        
    md.append("")

    # Enforce strict section ordering
    section_order = get_section_order()
    
    for section in section_order:
        if section == "Skills" and top_skills:
            md.append("## Top Skills")
            md.append(" | ".join(top_skills))
            md.append("")
            
        elif section == "Experience" and experience:
            md.append("## Professional Experience")
            for job in experience:
                title_comp = f"**{job.get('title', '')}** at {job.get('company', '')}"
                date_range = f"{job.get('start', '')} - {job.get('end', '')}"
                loc = extract_city_state(job.get('location', ''))
                loc_date = f"*{loc} | {date_range}*" if loc else f"*{date_range}*"
                
                md.append(f"### {title_comp}")
                md.append(loc_date)
                
                bullets = job.get('bullets', [])
                for bullet in bullets:
                    bullet_clean = bullet.lstrip("•- ")
                    md.append(f"- {bullet_clean}")
                md.append("")
                
        elif section == "Projects" and projects:
            md.append("## Projects")
            for proj in projects:
                md.append(f"### **{proj.get('title', '')}**")
                
                date_range = f"*{proj.get('start', '')} - {proj.get('end', '')}*"
                md.append(date_range)
                
                bullets = proj.get('bullets', [])
                for bullet in bullets:
                    bullet_clean = bullet.lstrip("•- ")
                    md.append(f"- {bullet_clean}")
                md.append("")
                
        elif section == "Education" and education:
            md.append("## Education")
            for edu in education:
                md.append(f"### **{edu.get('school', '')}**")
                md.append(f"{edu.get('degree', '')}")
                date_range = f"*{edu.get('start', '')} - {edu.get('end', '')}*"
                md.append(date_range)
                md.append("")

    return "\n".join(md)
