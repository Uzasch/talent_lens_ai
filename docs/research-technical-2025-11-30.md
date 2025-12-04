# Technical Research Report: AI Resume Shortlister - Complete Tech Guide

**Date:** 2025-11-30
**Prepared for:** Uzasch
**Project:** AI Resume Shortlister (College Project)
**Skill Level:** Beginner-friendly explanations

---

## Executive Summary

This research covers everything you need to build the AI Resume Shortlister:
- **Frontend:** React basics + Tailwind CSS + Recharts
- **Backend:** Flask (Python) basics
- **Database:** SQLite basics
- **AI:** Gemini API for resume analysis
- **Utilities:** PyMuPDF for PDF parsing, Gmail SMTP for emails
- **Competitive:** Existing HR tools and your differentiation

---

## Table of Contents

1. [React Basics](#1-react-basics)
2. [Tailwind CSS Basics](#2-tailwind-css-basics)
3. [Recharts for Visualizations](#3-recharts-for-visualizations)
4. [Flask Backend Basics](#4-flask-backend-basics)
5. [SQLite Database Basics](#5-sqlite-database-basics)
6. [Gemini API for AI](#6-gemini-api-for-ai)
7. [PyMuPDF for PDF Parsing](#7-pymupdf-for-pdf-parsing)
8. [Gmail SMTP for Emails](#8-gmail-smtp-for-emails)
9. [Competitive Analysis](#9-competitive-analysis)
10. [Project Architecture](#10-project-architecture)
11. [Getting Started Checklist](#11-getting-started-checklist)

---

## 1. React Basics

### What is React?
React is a JavaScript library for building user interfaces, created by Facebook. It's known for its **component-based structure** - you build small, reusable pieces (components) that combine to create your full app.

### Key Concepts

| Concept | What It Means |
|---------|---------------|
| **Components** | Reusable building blocks (like a CandidateCard, Dashboard, Button) |
| **JSX** | HTML-like syntax inside JavaScript |
| **Props** | Data passed from parent to child component |
| **State** | Data that changes over time (useState hook) |
| **useEffect** | Run code when something changes (API calls go here) |

### Getting Started (2025 Way - Using Vite)

```bash
# Create new React project with Vite (faster than old create-react-app)
npm create vite@latest resume-shortlister-frontend -- --template react
cd resume-shortlister-frontend
npm install
npm run dev
```

### Simple Component Example

```jsx
// CandidateCard.jsx
function CandidateCard({ name, matchPercent, summary }) {
  return (
    <div className="candidate-card">
      <h3>{name}</h3>
      <p>Match: {matchPercent}%</p>
      <p>{summary}</p>
    </div>
  );
}
export default CandidateCard;
```

### Resources
- [Official React Tutorial](https://react.dev/learn) - Start here!
- [React Tutorial App](https://react-tutorial.app/) - Interactive course
- [W3Schools React](https://www.w3schools.com/REACT/DEFAULT.ASP)

**Current Version:** React 19.1.0 [Verified 2025]

---

## 2. Tailwind CSS Basics

### What is Tailwind CSS?
A CSS framework that uses **utility classes** instead of writing custom CSS. Instead of `style="color: blue; font-size: 20px"`, you write `class="text-blue-500 text-xl"`.

### Why Use It?
- No more switching between CSS and JS files
- Consistent design system
- Responsive design is easy
- Much faster development

### Installation with React + Vite

```bash
npm install tailwindcss @tailwindcss/vite
```

Add to `vite.config.js`:
```javascript
import tailwindcss from "@tailwindcss/vite";
export default { plugins: [tailwindcss()] };
```

Add to your CSS file:
```css
@import "tailwindcss";
```

### Common Classes You'll Use

| What You Want | Tailwind Class |
|---------------|----------------|
| Blue background | `bg-blue-500` |
| White text | `text-white` |
| Rounded corners | `rounded-lg` |
| Shadow | `shadow-md` |
| Padding | `p-4` (all sides) or `px-4 py-2` |
| Margin | `m-4` or `mt-4` (top only) |
| Flex layout | `flex items-center justify-between` |
| Responsive | `md:text-xl` (applies on medium screens+) |

### Example - Styled Button

```jsx
<button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
  Send Email
</button>
```

### Resources
- [Tailwind CSS Docs](https://tailwindcss.com/)
- [Tailwind + React Guide](https://www.contentful.com/blog/react-app-tailwind-css/)
- [Udemy - Tailwind CSS V4 Course](https://www.udemy.com/course/tailwind-css-the-beginner-guide/)

---

## 3. Recharts for Visualizations

### What is Recharts?
A charting library built specifically for React. Uses simple components to create charts - no complex D3.js knowledge needed!

### Installation

```bash
npm install recharts
```

### Chart Types You'll Need

| Chart | Use For |
|-------|---------|
| **BarChart** | Skills comparison, experience breakdown |
| **PieChart** | Distribution (education levels, experience ranges) |
| **RadarChart** | Skills radar (optional - if you add this later) |

### Simple Bar Chart Example

```jsx
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const skillsData = [
  { skill: 'React', score: 85 },
  { skill: 'Python', score: 70 },
  { skill: 'SQL', score: 60 },
];

function SkillsChart() {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={skillsData}>
        <XAxis dataKey="skill" />
        <YAxis />
        <Tooltip />
        <Bar dataKey="score" fill="#3B82F6" />
      </BarChart>
    </ResponsiveContainer>
  );
}
```

### Resources
- [Recharts Official Docs](https://recharts.org/)
- [Recharts GitHub](https://github.com/recharts/recharts)
- [Level Up Coding Tutorial](https://levelup.gitconnected.com/react-recharts-tutorial-199c51dbcbbd)

**Current Version:** Recharts 3.5.1 [Verified 2025]

---

## 4. Flask Backend Basics

### What is Flask?
A **lightweight Python web framework** for building APIs. It's called a "micro-framework" because it gives you just the essentials - no unnecessary complexity.

### Why Flask for Your Project?
- Python-based (same language for AI/Gemini)
- Simple to learn
- Perfect for REST APIs
- Great documentation

### Installation

```bash
pip install flask flask-cors
```

### Basic Flask API Example

```python
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow React frontend to connect

@app.route('/api/analyze', methods=['POST'])
def analyze_resumes():
    data = request.json
    job_description = data['job_description']
    # Your AI analysis logic here
    return jsonify({'status': 'success', 'candidates': []})

@app.route('/api/candidates', methods=['GET'])
def get_candidates():
    # Return ranked candidates from database
    return jsonify({'candidates': []})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

### Your API Endpoints

| Endpoint | Method | What It Does |
|----------|--------|--------------|
| `/api/upload` | POST | Upload resumes (PDF files) |
| `/api/job` | POST | Submit job description |
| `/api/analyze` | POST | Trigger AI analysis |
| `/api/candidates` | GET | Get ranked candidates |
| `/api/candidate/<id>` | GET | Get single candidate details |
| `/api/email` | POST | Send interview emails |
| `/api/history` | GET | Get past sessions |

### Resources
- [Flask Official Tutorial](https://flask.palletsprojects.com/en/stable/tutorial/)
- [Flask REST API Guide](https://auth0.com/blog/developing-restful-apis-with-python-and-flask/)
- [GeeksforGeeks Flask Tutorial](https://www.geeksforgeeks.org/python/flask-tutorial/)

**Current Version:** Flask 3.1.x [Verified 2025]

---

## 5. SQLite Database Basics

### What is SQLite?
A **serverless, file-based database**. No installation needed - Python has it built-in! Perfect for college projects.

### Why SQLite?
- **Zero setup** - just import and use
- **Single file** - easy to backup/share
- **Built into Python** - no extra installation
- **Good enough** for thousands of records

### Basic Usage

```python
import sqlite3

# Connect (creates file if doesn't exist)
conn = sqlite3.connect('resume_shortlister.db')
cursor = conn.cursor()

# Create tables
cursor.execute('''
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS candidates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER,
        name TEXT NOT NULL,
        email TEXT,
        match_score REAL,
        education_score REAL,
        experience_score REAL,
        projects_score REAL,
        ai_summary TEXT,
        ai_reasoning TEXT,
        resume_text TEXT,
        FOREIGN KEY (job_id) REFERENCES jobs(id)
    )
''')

conn.commit()
```

### CRUD Operations

```python
# CREATE - Insert a candidate
cursor.execute('''
    INSERT INTO candidates (job_id, name, email, match_score)
    VALUES (?, ?, ?, ?)
''', (1, 'Rahul Sharma', 'rahul@email.com', 92.5))

# READ - Get all candidates for a job
cursor.execute('SELECT * FROM candidates WHERE job_id = ? ORDER BY match_score DESC', (1,))
candidates = cursor.fetchall()

# UPDATE - Update match score
cursor.execute('UPDATE candidates SET match_score = ? WHERE id = ?', (95.0, 1))

# DELETE - Remove a candidate
cursor.execute('DELETE FROM candidates WHERE id = ?', (1,))

conn.commit()
```

### Your Database Schema

```
jobs
├── id (PRIMARY KEY)
├── title
├── description
├── created_at

candidates
├── id (PRIMARY KEY)
├── job_id (FOREIGN KEY → jobs)
├── name
├── email
├── match_score
├── education_score
├── experience_score
├── projects_score
├── ai_summary
├── ai_reasoning
├── resume_text
```

### Resources
- [Python sqlite3 Documentation](https://docs.python.org/3/library/sqlite3.html)
- [FreeCodeCamp SQLite Handbook](https://www.freecodecamp.org/news/work-with-sqlite-in-python-handbook/)
- [GeeksforGeeks Python SQLite](https://www.geeksforgeeks.org/python/python-sqlite/)

---

## 6. Gemini API for AI

### What is Gemini API?
Google's AI model API. It can understand text, analyze content, compare documents, and generate responses. **Free tier available!**

### Why Gemini for Your Project?
- **Free tier** - generous limits for college project
- **Multimodal** - can understand text and PDFs
- **Powerful** - latest AI reasoning capabilities
- **Python SDK** - easy to use

### Getting Started

1. **Get API Key**: Go to [Google AI Studio](https://aistudio.google.com/apikey) and create a free API key

2. **Install SDK**:
```bash
pip install google-genai
```

3. **Basic Usage**:
```python
from google import genai

# Set up client
client = genai.Client(api_key="YOUR_API_KEY")

# Simple text generation
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="Explain what a REST API is in simple terms"
)
print(response.text)
```

### Resume Analysis Prompt Example

```python
def analyze_resume(resume_text, job_description):
    prompt = f"""
    You are an expert HR analyst. Analyze this resume against the job description.

    JOB DESCRIPTION:
    {job_description}

    RESUME:
    {resume_text}

    Provide analysis in this JSON format:
    {{
        "match_score": <0-100>,
        "education_score": <0-100>,
        "experience_score": <0-100>,
        "projects_score": <0-100>,
        "summary": "<3 bullet points about candidate>",
        "strengths": ["<strength1>", "<strength2>"],
        "gaps": ["<gap1>", "<gap2>"],
        "reasoning": "<why this score, compare to ideal candidate>"
    }}
    """

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    return response.text
```

### Comparing Similar Candidates

```python
def compare_candidates(candidate1, candidate2, job_description):
    prompt = f"""
    Compare these two candidates for the role. Both have similar skills.
    Explain WHY one should be ranked higher.

    JOB: {job_description}

    CANDIDATE 1: {candidate1}
    CANDIDATE 2: {candidate2}

    Explain the key differentiators:
    - Project quality/scale
    - Leadership experience
    - Relevant technologies
    - Growth potential
    """
    # ... call Gemini
```

### Resources
- [Gemini API Quickstart](https://ai.google.dev/gemini-api/docs/quickstart)
- [Gemini API Cookbook](https://github.com/google-gemini/cookbook)
- [ListenData Gemini Tutorial](https://www.listendata.com/2024/05/how-to-use-gemini-in-python.html)

**Current Model:** gemini-2.0-flash (or gemini-2.5-flash for latest) [Verified 2025]

---

## 7. PyMuPDF for PDF Parsing

### What is PyMuPDF?
A Python library (imported as `fitz`) to extract text from PDFs. Fast and reliable!

### Installation

```bash
pip install pymupdf
```

### Extract Text from Resume PDF

```python
import fitz  # PyMuPDF

def extract_resume_text(pdf_path):
    """Extract all text from a PDF resume"""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

# Usage
resume_text = extract_resume_text("resume.pdf")
print(resume_text)
```

### Handle Multiple Resumes

```python
import os

def process_all_resumes(folder_path):
    """Process all PDF resumes in a folder"""
    resumes = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.pdf'):
            filepath = os.path.join(folder_path, filename)
            text = extract_resume_text(filepath)
            resumes.append({
                'filename': filename,
                'text': text
            })
    return resumes
```

### Handle Scanned PDFs (OCR)

```python
def extract_with_ocr(pdf_path):
    """Use OCR for scanned/image-based PDFs"""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        # Try regular extraction first
        page_text = page.get_text()
        if not page_text.strip():
            # Fall back to OCR if no text found
            tp = page.get_textpage_ocr()
            page_text = page.get_text(textpage=tp)
        text += page_text
    doc.close()
    return text
```

### Complete Resume Extraction (with OCR fallback)

```python
import fitz  # PyMuPDF

def extract_resume_text(pdf_path):
    """
    Extract text from PDF with OCR fallback for scanned/image PDFs.
    Normal text PDFs: Direct extraction (fast)
    Scanned PDFs: Uses Tesseract OCR (slower but works)
    """
    doc = fitz.open(pdf_path)
    text = ""

    for page in doc:
        # Try normal extraction first (works for 90% of resumes)
        page_text = page.get_text()

        # If empty, it's probably a scanned image - use OCR
        if not page_text.strip():
            try:
                tp = page.get_textpage_ocr()  # Tesseract OCR
                page_text = page.get_text(textpage=tp)
            except:
                page_text = "[OCR failed for this page]"

        text += page_text

    doc.close()
    return text
```

### Install Tesseract for OCR

```bash
# Mac
brew install tesseract

# Ubuntu/Linux
sudo apt install tesseract-ocr

# Windows - Download installer from:
# https://github.com/UB-Mannheim/tesseract/wiki
```

### Note on Formatting
Gemini AI is smart enough to understand messy/poorly-aligned text. Even if text comes out jumbled, Gemini will parse it correctly.

### Resources
- [PyMuPDF Documentation](https://pymupdf.readthedocs.io/en/latest/)
- [Text Extraction Tutorial](https://pymupdf.readthedocs.io/en/latest/recipes-text.html)
- [Artifex Blog on Text Extraction](https://artifex.com/blog/text-extraction-with-pymupdf)

---

## 8. Gmail SMTP for Emails

### What is SMTP?
Simple Mail Transfer Protocol - the standard way to send emails programmatically.

### Setup Gmail App Password

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable 2-Factor Authentication (if not already)
3. Go to "App passwords"
4. Generate a new app password for "Mail"
5. Save the 16-character password (you'll use this, NOT your regular password)

### Send Email Function

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_interview_email(to_email, candidate_name, job_title, time_slots):
    """Send interview invitation email"""

    # Your Gmail credentials
    sender_email = "your-email@gmail.com"
    app_password = "your-app-password"  # 16-char app password

    # Create message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = f"Interview Invitation - {job_title}"

    # Email body
    body = f"""
    Dear {candidate_name},

    Congratulations! We were impressed with your profile and would like to invite you for an interview for the {job_title} position.

    Please select one of the following time slots:
    {time_slots}

    Please reply to confirm your preferred slot.

    Best regards,
    HR Team
    """

    msg.attach(MIMEText(body, 'plain'))

    # Send email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Enable security
        server.login(sender_email, app_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
```

### Send to Multiple Candidates (Top 6)

```python
def send_bulk_interview_emails(candidates, job_title, time_slots):
    """Send interview emails to all top candidates"""
    results = []
    for candidate in candidates:
        success = send_interview_email(
            to_email=candidate['email'],
            candidate_name=candidate['name'],
            job_title=job_title,
            time_slots=time_slots
        )
        results.append({
            'name': candidate['name'],
            'sent': success
        })
    return results
```

### Important Notes
- **Never commit passwords to Git!** Use environment variables
- Gmail limits: 500 emails/day for free accounts
- Use App Password, not your regular Gmail password

### Resources
- [Mailtrap Python Gmail Tutorial](https://mailtrap.io/blog/python-send-email-gmail/)
- [Real Python Email Guide](https://realpython.com/python-send-email/)
- [GeeksforGeeks Email Tutorial](https://www.geeksforgeeks.org/python/send-mail-gmail-account-using-python/)

---

## 9. Competitive Analysis

### Existing AI Resume Screening Tools (2025)

| Tool | What They Do | Pricing | Your Advantage |
|------|--------------|---------|----------------|
| **LinkedIn Recruiter** | Search + InMail | $$$$ Expensive | You're free for college! |
| **Greenhouse** | Full ATS | $$$ Enterprise | They don't explain WHY |
| **HireVue** | Video + AI screening | $$$ Enterprise | Overkill for screening |
| **Workable** | ATS + AI | $$ Mid-range | No transparent reasoning |
| **Skillate** | AI resume parsing | $$ Mid-range | No comparison logic |

### What Competitors LACK (Your Differentiation!)

| Gap in Market | Your Solution |
|---------------|---------------|
| Black-box AI (no explanation) | Transparent "WHY this candidate" |
| Keyword matching only | Semantic understanding via Gemini |
| No comparison for similar candidates | Side-by-side with tie-breaker logic |
| Complex enterprise setup | Simple 3-screen college project |
| Expensive | Free (college project) |

### Market Stats [2025]
- 98% of Fortune 500 use ATS systems
- AI screening market growing rapidly
- Key trend: **Explainable AI** (what you're building!)

### Resources
- [Best AI Resume Screening Software 2025](https://peoplemanagingpeople.com/tools/best-ai-resume-screening-software/)
- [Resume Screening Tools Comparison](https://toggl.com/blog/resume-screening-tools)
- [AI Recruiting Software Guide](https://www.selectsoftwarereviews.com/buyer-guide/ai-recruiting)

---

## 10. Project Architecture

### Folder Structure

```
resume-shortlister/
├── backend/
│   ├── app.py              # Flask main file
│   ├── routes/
│   │   ├── upload.py       # Upload endpoints
│   │   ├── analyze.py      # AI analysis endpoints
│   │   └── email.py        # Email endpoints
│   ├── services/
│   │   ├── gemini_service.py    # Gemini API calls
│   │   ├── pdf_service.py       # PyMuPDF parsing
│   │   └── email_service.py     # Gmail SMTP
│   ├── database/
│   │   └── db.py           # SQLite functions
│   ├── uploads/            # Uploaded PDFs
│   └── requirements.txt    # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── CandidateCard.jsx
│   │   │   ├── UploadForm.jsx
│   │   │   └── Charts.jsx
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   ├── Results.jsx
│   │   │   └── History.jsx
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── tailwind.config.js
│
├── docs/                   # BMM documentation
└── README.md
```

### Data Flow

```
1. HR uploads resumes (PDF) + Job Description
         ↓
2. Flask receives files, PyMuPDF extracts text
         ↓
3. Gemini API analyzes each resume vs JD
         ↓
4. Results stored in SQLite
         ↓
5. React fetches ranked candidates
         ↓
6. Dashboard displays with charts + reasoning
         ↓
7. One-click sends emails via Gmail SMTP
```

---

## 11. Getting Started Checklist

### Phase 1: Setup (Do First!)

- [ ] Install Python 3.9+
- [ ] Install Node.js 18+
- [ ] Get Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey)
- [ ] Create Gmail App Password
- [ ] Create project folders (backend/, frontend/)

### Phase 2: Backend

- [ ] `pip install flask flask-cors pymupdf google-genai`
- [ ] Create `app.py` with basic Flask server
- [ ] Create SQLite database with tables
- [ ] Test PDF text extraction with PyMuPDF
- [ ] Test Gemini API with sample prompt
- [ ] Create `/api/upload` endpoint
- [ ] Create `/api/analyze` endpoint
- [ ] Create `/api/candidates` endpoint
- [ ] Create `/api/email` endpoint

### Phase 3: Frontend

- [ ] `npm create vite@latest frontend -- --template react`
- [ ] `npm install recharts axios`
- [ ] Setup Tailwind CSS
- [ ] Create Upload page
- [ ] Create Dashboard page
- [ ] Create History page
- [ ] Connect to Flask API

### Phase 4: Integration

- [ ] Test full flow: Upload → Analyze → Display → Email
- [ ] Add error handling
- [ ] Make it look nice with Tailwind

---

## Quick Reference Card

| Task | Command/Code |
|------|--------------|
| Start React dev server | `npm run dev` |
| Start Flask server | `python app.py` |
| Install Python package | `pip install package-name` |
| Install Node package | `npm install package-name` |
| Gemini model to use | `gemini-2.0-flash` |
| Gmail SMTP server | `smtp.gmail.com` port `587` |
| Flask CORS | `CORS(app)` after `app = Flask(__name__)` |

---

## Sources & References

### Official Documentation
- [React Official](https://react.dev/learn)
- [Flask Official](https://flask.palletsprojects.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Recharts](https://recharts.org/)
- [Gemini API](https://ai.google.dev/gemini-api/docs/quickstart)
- [PyMuPDF](https://pymupdf.readthedocs.io/)
- [Python sqlite3](https://docs.python.org/3/library/sqlite3.html)

### Tutorials
- [GeeksforGeeks Flask Tutorial](https://www.geeksforgeeks.org/python/flask-tutorial/)
- [GeeksforGeeks Python SQLite](https://www.geeksforgeeks.org/python/python-sqlite/)
- [Mailtrap Python Email Guide](https://mailtrap.io/blog/python-send-email-gmail/)
- [ListenData Gemini Tutorial](https://www.listendata.com/2024/05/how-to-use-gemini-in-python.html)

### Competitive Research
- [Best AI Resume Screening Software 2025](https://peoplemanagingpeople.com/tools/best-ai-resume-screening-software/)
- [AI Recruiting Software Guide](https://www.selectsoftwarereviews.com/buyer-guide/ai-recruiting)

---

_Research generated using BMad Method Research Workflow | November 2025_
