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

class ResumePDF(FPDF):
    def header(self):
        pass

    def footer(self):
        # Optional: Add page numbers, though minimal resumes often don't need them
        pass

def generate_pdf_from_markdown(markdown_text):
    """
    Parses an edited markdown string and generates a compact, minimal PDF.
    """
    pdf = ResumePDF()
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()
    pdf.set_text_color(0, 0, 0)
    
    # 1. Very tight margins
    pdf.set_margins(left=12, top=12, right=12)
    
    lines = markdown_text.split('\n')
    
    for line in lines:
        line_clean = sanitize_text(line.strip())
        if not line_clean:
            pdf.ln(1) # Very small gap for empty lines
            continue
            
        if line_clean.startswith('# '):
            # Main Header (Name)
            pdf.set_font("helvetica", "B", 16)
            pdf.cell(0, 7, line_clean[2:], ln=True, align='L')
            pdf.ln(0.5)
            
        elif line_clean.startswith('## '):
            # Section Titles
            pdf.ln(2)
            pdf.set_font("helvetica", "B", 11)
            pdf.cell(0, 5, line_clean[3:], ln=True)
            pdf.ln(1)
            
        elif line_clean.startswith('### '):
            # Job Titles / Schools / Projects
            text = line_clean[4:].replace('**', '') # Strip bold markdown syntax for PDF
            pdf.set_font("helvetica", "B", 11)
            pdf.cell(0, 5, text, ln=True)
            
        elif line_clean.startswith('- '):
            # Bullet points
            pdf.set_font("helvetica", "", 10)
            pdf.set_x(16) # Indent bullets
            pdf.multi_cell(0, 4, f"- {line_clean[2:]}")
            
        elif line_clean.startswith('**Contact:**'):
            pdf.set_font("helvetica", "", 10)
            contact_text = line_clean.replace('**Contact:**', '').strip()
            contact_text = contact_text.replace('-', '\xb7')
            pdf.multi_cell(0, 4, contact_text, align='L')
            pdf.ln(1)
            
        elif line_clean.startswith('*') and line_clean.endswith('*'):
            # Italicized dates/locations
            pdf.set_font("helvetica", "I", 10)
            pdf.cell(0, 4, line_clean.replace('*', ''), ln=True)
            
        else:
            # Regular body text (Summary, Skills, Degrees)
            pdf.set_font("helvetica", "", 10)
            pdf.multi_cell(0, 4, line_clean.replace('**', ''))

    return bytes(pdf.output(dest='S'))
