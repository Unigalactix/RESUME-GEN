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
            pdf.set_font("helvetica", "B", 18)
            pdf.set_text_color(31, 78, 121) # Dark Blue (matches typical template blue)
            pdf.cell(0, 8, line_clean[2:], ln=True, align='C')
            pdf.ln(1)
            
        elif line_clean.startswith('## '):
            # Section Titles
            pdf.ln(3) # Space before new section
            pdf.set_font("helvetica", "B", 12)
            pdf.set_text_color(0, 51, 102) # Dark Blue
            pdf.cell(0, 5, line_clean[3:], ln=True)
            pdf.set_draw_color(0, 51, 102)
            pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 186, pdf.get_y())
            pdf.ln(2)
            pdf.set_text_color(0, 0, 0) # Reset to black
            
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
            # Restore the bullets if they were sanitized to hyphens, or just use middle dots
            contact_text = contact_text.replace('-', '\xb7')
            
            # Use fpdf2 HTML rendering to color links securely without messing up centered alignment
            html_text = f'''<p align="center"><font face="helvetica" size="10" color="#000000">{contact_text}</font></p>'''
            
            # Color specific known elements to blue
            blue_hex = '"#1f4e79"'
            html_text = html_text.replace('rajeshkodaganti.work@gmail.com', f'<a href="mailto:rajeshkodaganti.work@gmail.com"><font color={blue_hex}>rajeshkodaganti.work@gmail.com</font></a>')
            html_text = html_text.replace('GitHub', f'<a href="https://github.com"><font color={blue_hex}>GitHub</font></a>')
            html_text = html_text.replace('LinkedIN', f'<a href="https://linkedin.com"><font color={blue_hex}>LinkedIN</font></a>')
            # FPDF2 treats urls starting with # as internal document links. We use a placeholder URL or just color it.
            html_text = html_text.replace('Portfolio', f'<font color={blue_hex}>Portfolio</font>')
            
            pdf.write_html(html_text)
            pdf.ln(2)
            
        elif line_clean.startswith('*') and line_clean.endswith('*'):
            # Italicized dates/locations
            pdf.set_font("helvetica", "I", 10)
            pdf.cell(0, 4, line_clean.replace('*', ''), ln=True)
            
        else:
            # Regular body text (Summary, Skills, Degrees)
            pdf.set_font("helvetica", "", 10)
            pdf.multi_cell(0, 4, line_clean.replace('**', ''))

    return bytes(pdf.output(dest='S'))
