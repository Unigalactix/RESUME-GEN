import re
from resume_formatter import build_contact_line, extract_city_state, get_effective_section_order, get_resume_variant_config

def trim_summary(summary, max_chars=420):
    cleaned = " ".join((summary or "").split())
    if len(cleaned) <= max_chars:
        return cleaned
    return cleaned[: max_chars - 3].rstrip() + "..."


def create_markdown_resume(
    profile,
    top_skills,
    experience,
    education,
    projects,
    certifications=None,
    publications=None,
    languages=None,
    volunteering=None,
    options=None,
):
    """
    Generates a Markdown string representing the resume.
    """
    options = options or {}
    certifications = certifications or []
    publications = publications or []
    languages = languages or []
    volunteering = volunteering or []

    variant_name = options.get("variant", "ATS-safe")
    variant_config = get_resume_variant_config(variant_name)
    md = []

    # 1. HEADER
    name = f"{profile.get('first_name', '')} {profile.get('last_name', '')}".strip()
    if not name:
        name = "Candidate Name"
    md.append(f"# {name}")

    contact_str = build_contact_line(profile)
    if contact_str:
        md.append(f"**Contact:** {contact_str}")
    if profile.get("headline"):
        md.append(profile["headline"])

    md.append("")

    section_order = get_effective_section_order(options.get("section_order"), variant_name)
    
    for section in section_order:
        if section == "Summary" and profile.get("summary") and variant_config.get("include_summary"):
            md.append("## Professional Summary")
            md.append(trim_summary(profile.get("summary", "")))
            md.append("")

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
                
                bullets = job.get('bullets', [])[: variant_config.get("max_experience_bullets", 4)]
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
                
                bullets = proj.get('bullets', [])[: variant_config.get("max_project_bullets", 3)]
                for bullet in bullets:
                    bullet_clean = bullet.lstrip("•- ")
                    md.append(f"- {bullet_clean}")
                md.append("")

        elif section == "Certifications" and certifications:
            md.append("## Certifications")
            for cert in certifications[:6]:
                line = cert.get("name", "")
                if cert.get("authority"):
                    line += f" - {cert['authority']}"
                if cert.get("start"):
                    line += f" ({cert['start']})"
                md.append(f"- {line}")
            md.append("")

        elif section == "Publications" and publications:
            md.append("## Publications")
            for publication in publications[:3]:
                title = publication.get("name", "")
                publisher = publication.get("publisher", "")
                published_on = publication.get("published_on", "")
                suffix = " | ".join(part for part in [publisher, published_on] if part)
                if suffix:
                    md.append(f"- {title} ({suffix})")
                else:
                    md.append(f"- {title}")
            md.append("")

        elif section == "Volunteering" and volunteering:
            md.append("## Volunteering")
            for item in volunteering[:3]:
                role = item.get("role", "Volunteer")
                company = item.get("company", "")
                date_range = " - ".join(part for part in [item.get("start", ""), item.get("end", "Present")] if part)
                line = f"- {role} at {company}"
                if date_range:
                    line += f" ({date_range})"
                md.append(line)
            md.append("")

        elif section == "Languages" and languages:
            md.append("## Languages")
            md.append(" | ".join(
                f"{item.get('name', '')} ({item.get('proficiency', '')})".strip()
                for item in languages if item.get("name")
            ))
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
