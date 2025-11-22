from fpdf import FPDF
from typing import List, Dict

class ReportPDF(FPDF):
    def header(self):  # pragma: no cover
        self.set_font('Helvetica', 'B', 14)
        self.cell(0, 10, 'Resume Screening Report', ln=1, align='C')
        self.ln(2)


def build_pdf(candidate_name: str, jd_title: str, scores: Dict[str, float], missing_skills: List[str], suggestions: List[str]) -> bytes:
    pdf = ReportPDF()
    pdf.add_page()

    pdf.set_font('Helvetica', '', 12)
    pdf.cell(0, 8, f'Candidate: {candidate_name}', ln=1)
    pdf.cell(0, 8, f'Job Title: {jd_title}', ln=1)
    pdf.ln(4)

    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, 'Score Breakdown', ln=1)
    pdf.set_font('Helvetica', '', 11)
    for k, v in scores.items():
        pdf.cell(0, 6, f'- {k}: {v:.2f}', ln=1)
    pdf.ln(4)

    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, 'Missing Must-Have Skills', ln=1)
    pdf.set_font('Helvetica', '', 11)
    if missing_skills:
        for s in missing_skills:
            pdf.cell(0, 6, f'- {s}', ln=1)
    else:
        pdf.cell(0, 6, 'None', ln=1)
    pdf.ln(4)

    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, 'Suggestions', ln=1)
    pdf.set_font('Helvetica', '', 11)
    if suggestions:
        for s in suggestions:
            pdf.multi_cell(0, 6, f'- {s}')
    else:
        pdf.cell(0, 6, 'No suggestions generated.', ln=1)

    return pdf.output(dest='S').encode('latin-1')
