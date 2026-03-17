import pandas as pd
import os
import re


REQUIRED_DATA_FILES = [
    "Profile.csv",
    "Positions.csv",
    "Education.csv",
    "Skills.csv",
    "Projects.csv",
]

OPTIONAL_DATA_FILES = [
    "Certifications.csv",
    "Languages.csv",
    "Publications.csv",
    "Volunteering.csv",
    "Email Addresses.csv",
    "PhoneNumbers.csv",
]


def read_csv_if_exists(path):
    if not os.path.exists(path):
        return pd.DataFrame()
    return pd.read_csv(path).fillna("")


def parse_websites(raw_value):
    links = []
    for label, url in re.findall(r"\[([^:\]]+):([^\]]+)\]", raw_value or ""):
        cleaned_url = url.strip()
        if cleaned_url and not cleaned_url.startswith(("http://", "https://")):
            cleaned_url = f"https://{cleaned_url}"
        links.append({"label": label.strip().title(), "url": cleaned_url})
    return links


def load_contact_details(data_dir="Data"):
    email_path = os.path.join(data_dir, "Email Addresses.csv")
    phone_path = os.path.join(data_dir, "PhoneNumbers.csv")

    emails_df = read_csv_if_exists(email_path)
    phones_df = read_csv_if_exists(phone_path)

    emails = []
    primary_email = ""
    for _, row in emails_df.iterrows():
        email = row.get("Email Address", "").strip()
        if not email:
            continue
        emails.append(email)
        if row.get("Primary", "").strip().lower() == "yes" and not primary_email:
            primary_email = email

    phone_numbers = []
    primary_phone = ""
    for _, row in phones_df.iterrows():
        number = row.get("Number", "").strip()
        if not number:
            continue
        phone_numbers.append(number)
        if not primary_phone and row.get("Type", "").strip().lower() == "mobile":
            primary_phone = number

    if not primary_email and emails:
        primary_email = emails[0]
    if not primary_phone and phone_numbers:
        primary_phone = phone_numbers[0]

    return {
        "email": primary_email,
        "emails": emails,
        "phone": primary_phone,
        "phone_numbers": phone_numbers,
    }

def load_profile(data_dir="Data"):
    path = os.path.join(data_dir, "Profile.csv")
    if not os.path.exists(path):
        return {}
    df = read_csv_if_exists(path)
    if not df.empty:
        row = df.iloc[0]
        return {
            "first_name": row.get("First Name", ""),
            "last_name": row.get("Last Name", ""),
            "headline": row.get("Headline", ""),
            "summary": row.get("Summary", ""),
            "industry": row.get("Industry", ""),
            "location": row.get("Geo Location", ""),
            "websites_raw": row.get("Websites", ""),
            "website_links": parse_websites(row.get("Websites", "")),
        }
    return {}

def load_positions(data_dir="Data"):
    path = os.path.join(data_dir, "Positions.csv")
    if not os.path.exists(path):
        return []
    df = read_csv_if_exists(path)
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
    df = read_csv_if_exists(path)
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
    df = read_csv_if_exists(path)
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
    df = read_csv_if_exists(path)
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


def load_certifications(data_dir="Data"):
    path = os.path.join(data_dir, "Certifications.csv")
    if not os.path.exists(path):
        return []
    df = read_csv_if_exists(path)
    certifications = []
    for _, row in df.iterrows():
        name = row.get("Name", "").strip()
        if name:
            certifications.append(
                {
                    "name": name,
                    "authority": row.get("Authority", ""),
                    "url": row.get("Url", ""),
                    "start": row.get("Started On", ""),
                    "end": row.get("Finished On", ""),
                }
            )
    return certifications


def load_languages(data_dir="Data"):
    path = os.path.join(data_dir, "Languages.csv")
    if not os.path.exists(path):
        return []
    df = read_csv_if_exists(path)
    languages = []
    for _, row in df.iterrows():
        name = row.get("Name", "").strip()
        if name:
            languages.append(
                {
                    "name": name,
                    "proficiency": row.get("Proficiency", ""),
                }
            )
    return languages


def load_publications(data_dir="Data"):
    path = os.path.join(data_dir, "Publications.csv")
    if not os.path.exists(path):
        return []
    df = read_csv_if_exists(path)
    publications = []
    for _, row in df.iterrows():
        name = row.get("Name", "").strip()
        if name:
            publications.append(
                {
                    "name": name,
                    "publisher": row.get("Publisher", ""),
                    "published_on": row.get("Published On", ""),
                    "description": row.get("Description", ""),
                    "url": row.get("Url", ""),
                }
            )
    return publications


def load_volunteering(data_dir="Data"):
    path = os.path.join(data_dir, "Volunteering.csv")
    if not os.path.exists(path):
        return []
    df = read_csv_if_exists(path)
    volunteering = []
    for _, row in df.iterrows():
        company = row.get("Company Name", "").strip()
        if company:
            volunteering.append(
                {
                    "company": company,
                    "role": row.get("Role", ""),
                    "cause": row.get("Cause", ""),
                    "start": row.get("Started On", ""),
                    "end": row.get("Finished On", ""),
                    "description": row.get("Description", ""),
                }
            )
    return volunteering


def get_data_inventory(data_dir="Data"):
    if not os.path.exists(data_dir):
        return {"exists": False, "missing_required": REQUIRED_DATA_FILES, "present_files": [], "optional_present": []}

    present_files = [name for name in os.listdir(data_dir) if os.path.isfile(os.path.join(data_dir, name))]
    return {
        "exists": True,
        "present_files": sorted(present_files),
        "missing_required": [name for name in REQUIRED_DATA_FILES if name not in present_files],
        "optional_present": [name for name in OPTIONAL_DATA_FILES if name in present_files],
    }


def build_profile_completeness_report(data):
    profile = data.get("profile", {})
    positions = data.get("positions", [])
    projects = data.get("projects", [])
    skills = data.get("skills", [])
    certifications = data.get("certifications", [])

    report = {
        "missing_sections": [],
        "warnings": [],
        "highlights": [],
    }

    if not profile.get("summary"):
        report["missing_sections"].append("Summary")
    if not profile.get("email"):
        report["missing_sections"].append("Email")
    if not positions:
        report["missing_sections"].append("Experience")
    if not projects:
        report["missing_sections"].append("Projects")
    if not certifications:
        report["warnings"].append("Add certifications or coursework if you are targeting internship, new grad, or AI roles.")
    if len(skills) < 10:
        report["warnings"].append("Skills coverage is thin. Add more concrete tools, frameworks, and platforms to improve matching.")

    position_descriptions = sum(1 for item in positions if len(str(item.get("description", "")).strip()) >= 40)
    if positions and position_descriptions < len(positions):
        report["warnings"].append("Some experience entries have short descriptions. Richer descriptions improve bullet rewriting and ATS targeting.")

    project_descriptions = sum(1 for item in projects if len(str(item.get("description", "")).strip()) >= 40)
    if projects and project_descriptions == 0:
        report["warnings"].append("Project descriptions are sparse. Add more detail for stronger tailored resumes.")

    report["highlights"].append(f"{len(positions)} experience entries loaded")
    report["highlights"].append(f"{len(skills)} skills loaded")
    report["highlights"].append(f"{len(projects)} projects loaded")
    report["highlights"].append(f"{len(certifications)} certifications loaded")

    return report

def load_all_data(data_dir="Data"):
    profile = load_profile(data_dir)
    profile.update(load_contact_details(data_dir))

    return {
        "profile": profile,
        "positions": load_positions(data_dir),
        "education": load_education(data_dir),
        "skills": load_skills(data_dir),
        "projects": load_projects(data_dir),
        "certifications": load_certifications(data_dir),
        "languages": load_languages(data_dir),
        "publications": load_publications(data_dir),
        "volunteering": load_volunteering(data_dir),
    }
