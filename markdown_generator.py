import re

def create_markdown_resume(profile, top_skills, experience, education, projects):
    """
    Generates a Markdown string representing the resume.
    """
    md = []
    
    # --- HEADER ---
    name = f"{profile.get('first_name', '')} {profile.get('last_name', '')}".strip()
    md.append(f"# {name}")
    
    contact_info = profile.get("websites", "")
    if contact_info:
        md.append(f"**Contact:** {contact_info}")
    md.append("")

    # --- SUMMARY ---
    summary = profile.get("summary", "")
    if summary:
        md.append("## Professional Summary")
        md.append(summary)
        md.append("")

    # --- SKILLS ---
    if top_skills:
        md.append("## Top Skills")
        md.append(" | ".join(top_skills))
        md.append("")

    # --- EXPERIENCE ---
    if experience:
        md.append("## Professional Experience")
        for job in experience:
            title_comp = f"**{job.get('title', '')}** at {job.get('company', '')}"
            date_range = f"{job.get('start', '')} - {job.get('end', '')}"
            location = job.get('location', '')
            loc_date = f"*{location} | {date_range}*" if location else f"*{date_range}*"
            
            md.append(f"### {title_comp}")
            md.append(loc_date)
            
            bullets = job.get('bullets', [])
            for bullet in bullets:
                bullet_clean = bullet.lstrip("•- ")
                md.append(f"- {bullet_clean}")
            md.append("")

    # --- PROJECTS ---
    if projects:
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

    # --- EDUCATION ---
    if education:
        md.append("## Education")
        for edu in education:
            md.append(f"### **{edu.get('school', '')}**")
            md.append(f"{edu.get('degree', '')}")
            date_range = f"*{edu.get('start', '')} - {edu.get('end', '')}*"
            md.append(date_range)
            md.append("")

    return "\n".join(md)
