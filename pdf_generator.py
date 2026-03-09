from fpdf import FPDF
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
        self.set_font("helvetica", "B", 14)
        self.set_text_color(0, 51, 102) # Dark Blue
        self.cell(0, 8, label, ln=True)
        self.set_draw_color(0, 51, 102)
        self.line(self.get_x(), self.get_y(), self.get_x() + 190, self.get_y())
        self.ln(4)
        self.set_text_color(0, 0, 0) # Back to black

    def chapter_body(self, text):
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
    name = f"{profile.get('first_name', '')} {profile.get('last_name', '')}".strip()
    pdf.cell(0, 10, name, ln=True, align='C')
    
    pdf.set_font("helvetica", "", 10)
    contact_info = profile.get("websites", "")
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
        skills_str = " • ".join(top_skills)
        pdf.multi_cell(0, 5, skills_str)
        pdf.ln(5)

    # --- EXPERIENCE ---
    if experience:
        pdf.chapter_title("Professional Experience")
        for job in experience:
            pdf.set_font("helvetica", "B", 12)
            pdf.cell(0, 6, f"{job.get('title', '')} at {job.get('company', '')}", ln=True)
            
            pdf.set_font("helvetica", "I", 10)
            date_range = f"{job.get('start', '')} - {job.get('end', '')}"
            location = job.get('location', '')
            loc_date = f"{location} | {date_range}" if location else date_range
            pdf.cell(0, 5, loc_date, ln=True)
            
            pdf.set_font("helvetica", "", 11)
            bullets = job.get('bullets', [])
            for bullet in bullets:
                # Remove common bullet prefix matching we did in matcher
                bullet_clean = bullet.lstrip("•- ")
                # Bullet indentation
                pdf.set_x(15)
                # Ensure the bullet uses standard ASCII bullet or a dash
                pdf.multi_cell(0, 5, f"- {bullet_clean}")
            pdf.ln(3)

    # --- PROJECTS ---
    if projects:
        pdf.chapter_title("Projects")
        for proj in projects:
            pdf.set_font("helvetica", "B", 12)
            pdf.cell(0, 6, proj.get('title', ''), ln=True)
            
            pdf.set_font("helvetica", "I", 10)
            date_range = f"{proj.get('start', '')} - {proj.get('end', '')}"
            pdf.cell(0, 5, date_range, ln=True)
            
            pdf.set_font("helvetica", "", 11)
            bullets = proj.get('bullets', [])
            for bullet in bullets:
                bullet_clean = bullet.lstrip("•- ")
                pdf.set_x(15)
                pdf.multi_cell(0, 5, f"- {bullet_clean}")
            pdf.ln(3)

    # --- EDUCATION ---
    if education:
        pdf.chapter_title("Education")
        for edu in education:
            pdf.set_font("helvetica", "B", 12)
            pdf.cell(0, 6, edu.get('school', ''), ln=True)
            
            pdf.set_font("helvetica", "I", 11)
            pdf.cell(0, 5, edu.get('degree', ''), ln=True)
            
            pdf.set_font("helvetica", "", 10)
            date_range = f"{edu.get('start', '')} - {edu.get('end', '')}"
            pdf.cell(0, 5, date_range, ln=True)
            pdf.ln(3)

    return pdf.output(dest='S')
