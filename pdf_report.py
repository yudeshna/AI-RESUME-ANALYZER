from fpdf import FPDF
import datetime
import re

def clean_text(text):
    # Remove all emojis and non-latin characters
    text = re.sub(r'[^\x00-\xFF]', '', text)
    # Clean up extra spaces left behind
    text = re.sub(r'  +', ' ', text)
    return text.strip()

class ResumePDF(FPDF):
    def header(self):
        self.set_fill_color(13, 17, 23)
        self.rect(0, 0, 210, 30, 'F')
        self.set_font('Arial', 'B', 18)
        self.set_text_color(0, 150, 200)
        self.cell(0, 20, 'AI Resume Analysis Report', ln=True, align='C')
        self.set_text_color(100, 100, 100)
        self.set_font('Arial', '', 9)
        self.cell(0, 8, f'Generated on {datetime.datetime.now().strftime("%d %B %Y, %I:%M %p")}', ln=True, align='C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f'Page {self.page_no()} | AI Resume Analyzer - Powered by Llama 3.2 + Ollama', align='C')

    def section_title(self, title):
        title = clean_text(title)
        self.set_font('Arial', 'B', 13)
        self.set_text_color(0, 150, 200)
        self.set_fill_color(26, 31, 46)
        self.cell(0, 10, title, ln=True, fill=True)
        self.ln(2)

    def body_text(self, text):
        text = clean_text(text)
        self.set_font('Arial', '', 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 7, text)
        self.ln(3)

    def score_box(self, score):
        if score >= 70:
            color = (0, 200, 100)
        elif score >= 50:
            color = (255, 170, 0)
        else:
            color = (220, 50, 50)
        self.set_fill_color(*color)
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 28)
        self.cell(0, 20, f'Resume Score: {score} / 100', ln=True, align='C', fill=True)
        self.ln(5)

    def divider(self):
        self.set_draw_color(0, 150, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

def generate_pdf_report(candidate_name, score, skills, analysis, jobs, questions=""):
    pdf = ResumePDF()
    pdf.add_page()

    # Score box
    pdf.score_box(score)
    pdf.divider()

    # Candidate Info
    pdf.section_title("CANDIDATE OVERVIEW")
    pdf.body_text(f"Name: {candidate_name}")
    pdf.body_text(f"Total Skills Detected: {len(skills)}")
    pdf.body_text(f"Skills: {', '.join(skills)}")
    pdf.divider()

    # AI Analysis
    pdf.section_title("AI ANALYSIS")
    pdf.body_text(analysis)
    pdf.divider()

    # Job Matches
    if jobs:
        pdf.add_page()
        pdf.section_title("TOP JOB MATCHES")
        for i, job in enumerate(jobs[:5], 1):
            job_score = job.get('match_score') or job.get('similarity_score', 0)
            pdf.set_font('Arial', 'B', 11)
            pdf.set_text_color(123, 47, 247)
            pdf.cell(0, 8, f"{i}. {job['title']} - {job_score}% Match", ln=True)
            pdf.set_font('Arial', '', 10)
            pdf.set_text_color(50, 50, 50)
            if 'missing_skills' in job and job['missing_skills']:
                pdf.body_text(f"Missing Skills: {', '.join(job['missing_skills'])}")
            if 'salary' in job:
                pdf.body_text(f"Salary Range: {job['salary']}")
            pdf.ln(2)
        pdf.divider()

    # Interview Questions
    if questions:
        pdf.add_page()
        pdf.section_title("INTERVIEW QUESTIONS")
        pdf.body_text(questions)

    output_path = "resume_analysis_report.pdf"
    pdf.output(output_path)
    return output_path