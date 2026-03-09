from fpdf import FPDF
import io
import re

def sanitize_text(text):
    if not isinstance(text, str):
        return ""
    replacements = {
        '•': '-', '’': "'", '‘': "'", '”': '"', '“': '"',
        '–': '-', '—': '--', '…': '...', '★': '*', '✓': 'v',
        '\u2013': '-', '\u2014': '--', '\u2018': "'", '\u2019': "'",
        '\u201c': '"', '\u201d': '"', '\u2022': '-', '\u00a0': ' '
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text.encode('latin-1', 'ignore').decode('latin-1')
import io

class ResumePDF(FPDF):
    def header(self):
        # We handle header manually in content to allow dynamic name
        pass

    def footer(self):
        # Add page numbers
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def chapter_title(self, label):
        label = sanitize_text(label)
        self.set_font("helvetica", "B", 14)
        self.set_text_color(0, 51, 102) # Dark Blue
        self.cell(0, 8, label, ln=True)
        self.set_draw_color(0, 51, 102)
        self.line(self.get_x(), self.get_y(), self.get_x() + 190, self.get_y())
        self.ln(4)
        self.set_text_color(0, 0, 0) # Back to black

    def chapter_body(self, text):
        text = sanitize_text(text)
        self.set_font("helvetica", "", 11)
        self.multi_cell(0, 5, text)
        self.ln(2)

def generate_pdf(profile, top_skills, experience, education, projects):
    """
    Generates a PDF resume in memory and returns the byte data.
    """
    pdf = ResumePDF()
    pdf.add_page()
    
    # --- HEADER (Name and Contact Info) ---
    pdf.set_font("helvetica", "B", 24)
    name = sanitize_text(f"{profile.get('first_name', '')} {profile.get('last_name', '')}".strip())
    pdf.cell(0, 10, name, ln=True, align='C')
    
    pdf.set_font("helvetica", "", 10)
    contact_info = sanitize_text(profile.get("websites", ""))
    if contact_info:
        pdf.cell(0, 5, contact_info, ln=True, align='C')
    pdf.ln(5)

    # --- SUMMARY ---
    summary = profile.get("summary", "")
    if summary:
        pdf.chapter_title("Professional Summary")
        pdf.chapter_body(summary)
        pdf.ln(2)

    # --- SKILLS ---
    if top_skills:
        pdf.chapter_title("Top Skills")
        pdf.set_font("helvetica", "", 11)
        skills_str = sanitize_text(" | ".join(top_skills))
        pdf.multi_cell(0, 5, skills_str)
        pdf.ln(5)

    # --- EXPERIENCE ---
    if experience:
        pdf.chapter_title("Professional Experience")
        for job in experience:
            pdf.set_font("helvetica", "B", 12)
            title_comp = sanitize_text(f"{job.get('title', '')} at {job.get('company', '')}")
            pdf.cell(0, 6, title_comp, ln=True)
            
            pdf.set_font("helvetica", "I", 10)
            date_range = f"{job.get('start', '')} - {job.get('end', '')}"
            location = job.get('location', '')
            loc_date = sanitize_text(f"{location} | {date_range}" if location else date_range)
            pdf.cell(0, 5, loc_date, ln=True)
            
            pdf.set_font("helvetica", "", 11)
            bullets = job.get('bullets', [])
            for bullet in bullets:
                bullet_clean = sanitize_text(bullet.lstrip("•- "))
                pdf.set_x(15)
                pdf.multi_cell(0, 5, f"- {bullet_clean}")
            pdf.ln(3)

    # --- PROJECTS ---
    if projects:
        pdf.chapter_title("Projects")
        for proj in projects:
            pdf.set_font("helvetica", "B", 12)
            proj_title = sanitize_text(proj.get('title', ''))
            pdf.cell(0, 6, proj_title, ln=True)
            
            pdf.set_font("helvetica", "I", 10)
            date_range = sanitize_text(f"{proj.get('start', '')} - {proj.get('end', '')}")
            pdf.cell(0, 5, date_range, ln=True)
            
            pdf.set_font("helvetica", "", 11)
            bullets = proj.get('bullets', [])
            for bullet in bullets:
                bullet_clean = sanitize_text(bullet.lstrip("•- "))
                pdf.set_x(15)
                pdf.multi_cell(0, 5, f"- {bullet_clean}")
            pdf.ln(3)

    # --- EDUCATION ---
    if education:
        pdf.chapter_title("Education")
        for edu in education:
            pdf.set_font("helvetica", "B", 12)
            school = sanitize_text(edu.get('school', ''))
            pdf.cell(0, 6, school, ln=True)
            
            pdf.set_font("helvetica", "I", 11)
            degree = sanitize_text(edu.get('degree', ''))
            pdf.cell(0, 5, degree, ln=True)
            
            pdf.set_font("helvetica", "", 10)
            date_range = sanitize_text(f"{edu.get('start', '')} - {edu.get('end', '')}")
            pdf.cell(0, 5, date_range, ln=True)
            pdf.ln(3)

    return bytes(pdf.output(dest='S'))
