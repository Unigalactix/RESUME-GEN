import pandas as pd
import os

def load_profile(data_dir="Data"):
    path = os.path.join(data_dir, "Profile.csv")
    if not os.path.exists(path):
        return {}
    df = pd.read_csv(path)
    if not df.empty:
        row = df.iloc[0]
        return {
            "first_name": row.get("First Name", ""),
            "last_name": row.get("Last Name", ""),
            "headline": row.get("Headline", ""),
            "summary": row.get("Summary", ""),
            "websites": row.get("Websites", "")
        }
    return {}

def load_positions(data_dir="Data"):
    path = os.path.join(data_dir, "Positions.csv")
    if not os.path.exists(path):
        return []
    df = pd.read_csv(path).fillna("")
    positions = []
    for _, row in df.iterrows():
        comp = row.get("Company Name", "").strip()
        if comp:
            positions.append({
                "company": comp,
                "title": row.get("Title", ""),
                "description": row.get("Description", ""),
                "location": row.get("Location", ""),
                "start": row.get("Started On", ""),
                "end": row.get("Finished On", "Present")
            })
    return positions

def load_education(data_dir="Data"):
    path = os.path.join(data_dir, "Education.csv")
    if not os.path.exists(path):
        return []
    df = pd.read_csv(path).fillna("")
    education = []
    for _, row in df.iterrows():
        school = row.get("School Name", "").strip()
        if school:
            education.append({
                "school": school,
                "degree": row.get("Degree Name", ""),
                "start": row.get("Start Date", ""),
                "end": row.get("End Date", "")
            })
    return education

def load_skills(data_dir="Data"):
    path = os.path.join(data_dir, "Skills.csv")
    if not os.path.exists(path):
        return []
    df = pd.read_csv(path).fillna("")
    skills = []
    for _, row in df.iterrows():
        skill = row.get("Name", "").strip()
        if skill:
            skills.append(skill)
    return skills

def load_projects(data_dir="Data"):
    path = os.path.join(data_dir, "Projects.csv")
    if not os.path.exists(path):
        return []
    df = pd.read_csv(path).fillna("")
    projects = []
    for _, row in df.iterrows():
        title = row.get("Title", "").strip()
        if title:
            projects.append({
                "title": title,
                "description": row.get("Description", ""),
                "start": row.get("Started On", ""),
                "end": row.get("Finished On", "Present")
            })
    return projects

def load_all_data(data_dir="Data"):
    return {
        "profile": load_profile(data_dir),
        "positions": load_positions(data_dir),
        "education": load_education(data_dir),
        "skills": load_skills(data_dir),
        "projects": load_projects(data_dir)
    }
