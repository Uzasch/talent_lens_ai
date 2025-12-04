# TalentLens AI

**Intelligent Resume Shortlisting with Transparent AI Reasoning**

---

## Overview

TalentLens AI is an AI-powered resume shortlisting tool that helps HR professionals quickly identify top candidates from large applicant pools. Unlike traditional ATS systems that act as black-box filters, TalentLens provides **transparent reasoning** — explaining WHY each candidate is ranked, not just WHO made the list.

---

## Client

**Yoboho Company** — HR Department

---

## Problem Statement

HR professionals face decision fatigue after reviewing 50+ resumes. Current tools only do keyword matching — they can't distinguish between two candidates who both list "React" when one built production apps for 10K users and the other completed a tutorial. Worse, they can't explain their rankings, leaving HR to justify choices on gut feeling.

---

## Solution

TalentLens AI uses Google Gemini to semantically analyze resumes against job descriptions, surfacing the **Top 6 candidates** with transparent reasoning:

- **Match Score Breakdown** — Education, Experience, Projects
- **WHY Explanations** — Clear reasoning for each candidate's ranking
- **Tie-Breaker Logic** — Explains differences between similar candidates
- **One-Click Action** — Send interview invites directly from the dashboard

---

## Key Features

| Feature | Description |
|---------|-------------|
| Smart Upload | Drag & drop up to 50+ PDF resumes |
| AI Analysis | Gemini-powered semantic matching (not just keywords) |
| Transparent Ranking | See WHY each candidate was selected |
| Score Breakdown | Education / Experience / Projects metrics |
| One-Click Email | Send interview invites to Top 6 instantly |
| Session History | Revisit past analyses anytime |

---

## Technologies Used

### Frontend
| Technology | Purpose |
|------------|---------|
| React 18 | UI Framework |
| Vite | Build Tool & Dev Server |
| Tailwind CSS | Styling |
| shadcn/ui | UI Component Library |
| Recharts | Data Visualization |
| React Router | Navigation |
| Axios | HTTP Client |
| react-dropzone | File Upload |
| Lucide React | Icons |

### Backend
| Technology | Purpose |
|------------|---------|
| Flask | Python Web Framework |
| SQLite | Database |
| PyMuPDF (fitz) | PDF Text Extraction |
| Google Generative AI | Gemini API Integration |
| Flask-CORS | Cross-Origin Support |
| smtplib | Email (Gmail SMTP) |

### AI
| Technology | Purpose |
|------------|---------|
| Google Gemini 1.5 Flash | Resume Analysis & Scoring |

---

## Architecture

```
┌─────────────────┐         ┌─────────────────┐
│                 │  REST   │                 │
│  React Frontend │ ◄─────► │  Flask Backend  │
│  (localhost:5173)│  API   │  (localhost:5000)│
│                 │         │                 │
└─────────────────┘         └────────┬────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
                    ▼                ▼                ▼
             ┌──────────┐    ┌──────────┐    ┌──────────┐
             │  SQLite  │    │  Gemini  │    │  Gmail   │
             │ Database │    │   API    │    │  SMTP    │
             └──────────┘    └──────────┘    └──────────┘
```

---

## Screens

1. **Home / Upload** — Enter job details, upload resumes
2. **Dashboard** — View Top 6 candidates with scores and WHY explanations
3. **History** — Access past analysis sessions

---

## Project Structure

```
resume-shortlister/
├── frontend/                # React application
│   ├── src/
│   │   ├── components/      # UI components
│   │   ├── pages/           # Page components
│   │   └── services/        # API calls
│   └── ...
├── backend/                 # Flask API
│   ├── app.py               # Main application
│   ├── services/            # Business logic
│   ├── models.py            # Database operations
│   └── data/                # SQLite database
└── docs/                    # Project documentation
```

---

## Setup & Installation

### Prerequisites
- Node.js 18+
- Python 3.10+
- Google Gemini API Key
- Gmail App Password

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### Environment Variables
Create `backend/.env`:
```env
GEMINI_API_KEY=your_api_key
GMAIL_ADDRESS=your_email@gmail.com
GMAIL_APP_PASSWORD=your_app_password
```

---

## Author

**Uzasch**

---

## License

This project is developed for Yoboho Company HR Department.

---

*Built with AI-powered transparency — because hiring decisions deserve explanations.*
