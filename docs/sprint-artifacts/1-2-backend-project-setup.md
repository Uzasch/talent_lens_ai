# Story 1.2: Backend Project Setup

Status: review

## Story

As a **developer**,
I want **the Flask backend project initialized with all dependencies and proper configuration**,
so that **I can start building API endpoints for TalentLens AI**.

## Acceptance Criteria

1. **AC1.2.1:** Flask project created in `backend/` directory
2. **AC1.2.2:** Virtual environment created and activated
3. **AC1.2.3:** All pip dependencies installed (flask, flask-cors, python-dotenv, google-generativeai, PyMuPDF, spacy)
4. **AC1.2.4:** spaCy model `en_core_web_sm` downloaded
5. **AC1.2.5:** Project structure has `app.py`, `config.py`, `models.py`, `services/`
6. **AC1.2.6:** `.env` file created with placeholder variables (GEMINI_API_KEY, GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
7. **AC1.2.7:** Server runs successfully on localhost:5000

## Tasks / Subtasks

- [x] **Task 1: Create backend directory and virtual environment** (AC: 1.2.1, 1.2.2)
  - [x] Create `backend/` directory at project root
  - [x] Navigate to backend directory
  - [x] Create virtual environment: `python -m venv venv`
  - [x] Activate virtual environment: `source venv/bin/activate` (macOS/Linux)

- [x] **Task 2: Create requirements.txt and install dependencies** (AC: 1.2.3)
  - [x] Create `requirements.txt` with:
    ```
    flask>=3.0.0
    flask-cors
    python-dotenv
    google-generativeai
    PyMuPDF>=1.24.0
    spacy>=3.0.0
    ```
  - [x] Run `pip install -r requirements.txt`
  - [x] Verify all packages installed: `pip list`

- [x] **Task 3: Download spaCy model** (AC: 1.2.4)
  - [x] Run `python -m spacy download en_core_web_sm`
  - [x] Verify model installed: `python -c "import spacy; spacy.load('en_core_web_sm')"`

- [x] **Task 4: Create project structure** (AC: 1.2.5)
  - [x] Create `app.py` (main Flask application)
  - [x] Create `config.py` (environment configuration)
  - [x] Create `models.py` (database operations placeholder)
  - [x] Create `services/` directory
  - [x] Create `services/__init__.py`
  - [x] Create `uploads/` directory for PDF storage
  - [x] Create `data/` directory for SQLite database

- [x] **Task 5: Create .env file with placeholders** (AC: 1.2.6)
  - [x] Create `.env` file:
    ```
    GEMINI_API_KEY=your_gemini_api_key_here
    GMAIL_ADDRESS=your_gmail_address_here
    GMAIL_APP_PASSWORD=your_app_password_here
    FLASK_ENV=development
    FLASK_DEBUG=1
    ```
  - [x] Create `.env.example` with same structure (for git)
  - [x] Add `.env` to `.gitignore`

- [x] **Task 6: Implement basic app.py** (AC: 1.2.7)
  - [x] Create minimal Flask app:
    ```python
    from flask import Flask
    from flask_cors import CORS
    from dotenv import load_dotenv
    import os
    import logging

    load_dotenv()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    app = Flask(__name__)
    CORS(app, origins=['http://localhost:5173'])

    @app.route('/')
    def index():
        return {'message': 'TalentLens AI Backend'}

    if __name__ == '__main__':
        app.run(debug=True, port=5000)
    ```

- [x] **Task 7: Create config.py**
  - [x] Create configuration class:
    ```python
    import os
    from dotenv import load_dotenv

    load_dotenv()

    class Config:
        GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
        GMAIL_ADDRESS = os.getenv('GMAIL_ADDRESS')
        GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')
        DATABASE_PATH = 'data/app.db'
        UPLOAD_FOLDER = 'uploads'
    ```

- [x] **Task 8: Verify server runs** (AC: 1.2.7)
  - [x] Run `python app.py`
  - [x] Confirm server starts at http://localhost:5000
  - [x] Test root endpoint returns JSON response
  - [x] Verify no import errors in console

## Dev Notes

### Architecture Alignment

This story implements the backend foundation per architecture.md:
- **Framework:** Flask 3.x (lightweight, beginner-friendly)
- **CORS:** flask-cors configured for localhost:5173
- **Environment:** python-dotenv for configuration
- **NLP:** spaCy for local name extraction (Epic 3)
- **AI:** google-generativeai for Gemini integration (Epic 3)
- **PDF:** PyMuPDF for resume parsing (Epic 3)

### Project Structure

```
backend/
├── app.py              # Main Flask application
├── config.py           # Environment configuration
├── models.py           # Database CRUD operations
├── services/           # Business logic services
│   └── __init__.py
├── uploads/            # PDF file storage
├── data/               # SQLite database location
├── requirements.txt    # Python dependencies
├── .env                # Environment variables (gitignored)
├── .env.example        # Template for .env
└── venv/               # Virtual environment (gitignored)
```

### Security Notes

- `.env` must be in `.gitignore` - never commit secrets
- Use Gmail App Password, not regular password
- CORS restricted to frontend origin only

[Source: docs/architecture.md#Security]

### Dependencies Purpose

| Package | Purpose | Used In |
|---------|---------|---------|
| flask | Web framework | All API stories |
| flask-cors | CORS handling | Story 1.4 |
| python-dotenv | Environment vars | All stories |
| google-generativeai | Gemini API | Epic 3-4 |
| PyMuPDF | PDF text extraction | Epic 3 |
| spacy | NER for names | Epic 3 |

### Parallel Development Note

Stories 1.1 and 1.2 have no dependencies and can be developed simultaneously.

[Source: docs/sprint-artifacts/tech-spec-epic-1.md#Workflows-and-Sequencing]

### References

- [Source: docs/architecture.md#Backend-Stack]
- [Source: docs/sprint-artifacts/tech-spec-epic-1.md#Story-1.2]
- [Source: docs/epics.md#Story-1.2]

## Dev Agent Record

### Context Reference

None (proceeded without story context file)

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- All dependencies installed successfully including spacy en_core_web_sm model
- Flask test client verified endpoint returns 200 with expected JSON

### Completion Notes List

- All 8 tasks completed successfully
- All 7 acceptance criteria satisfied
- Server returns `{'message': 'TalentLens AI Backend'}` on GET /
- CORS configured for frontend at localhost:5173

### File List

**Created:**
- backend/ (directory)
- backend/venv/ (virtual environment)
- backend/requirements.txt
- backend/app.py
- backend/config.py
- backend/models.py
- backend/services/__init__.py
- backend/uploads/ (directory)
- backend/data/ (directory)
- backend/.env
- backend/.env.example

---

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-12-20 | SM Agent (Bob) | Initial draft created |
| 2025-12-20 | Dev Agent (Amelia) | Implementation complete - all ACs satisfied |
