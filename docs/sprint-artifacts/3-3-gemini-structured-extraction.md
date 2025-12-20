# Story 3.3: Gemini Structured Extraction

Status: review

## Story

As a **developer**,
I want **Gemini to extract structured data from resumes**,
So that **rich candidate profiles are created**.

## Acceptance Criteria

1. **AC3.3.1:** Resume text is sent to Gemini with extraction prompt
2. **AC3.3.2:** Gemini returns structured JSON with: skills, experience_years, experience_details, education, projects, positions
3. **AC3.3.3:** Response is parsed and validated for required fields
4. **AC3.3.4:** API errors are caught and logged
5. **AC3.3.5:** Uses gemini-1.5-flash model for cost efficiency

## Tasks / Subtasks

- [x] **Task 1: Create gemini_service.py with configuration** (AC: 3.3.5)
  - [ ] Create `backend/services/gemini_service.py`:
    ```python
    import os
    import json
    import logging
    from dotenv import load_dotenv
    import google.generativeai as genai

    load_dotenv()
    logger = logging.getLogger(__name__)

    # Configure Gemini API
    API_KEY = os.getenv('GEMINI_API_KEY')
    if not API_KEY:
        logger.warning("GEMINI_API_KEY not found in environment")

    genai.configure(api_key=API_KEY)

    # Model configuration
    MODEL_NAME = 'gemini-1.5-flash'
    ```

- [x] **Task 2: Define extraction prompt** (AC: 3.3.1, 3.3.2)
  - [ ] Add extraction prompt template:
    ```python
    EXTRACTION_PROMPT = """Extract structured data from this resume text.

    Resume Text:
    {resume_text}

    Return ONLY valid JSON with this exact structure (no markdown, no explanation):
    {{
      "skills": ["skill1", "skill2", ...],
      "experience_years": 4.5,
      "experience_details": [
        {{
          "role": "Job Title",
          "company": "Company Name",
          "duration": "2 years",
          "highlights": ["Achievement 1", "Achievement 2"]
        }}
      ],
      "education": [
        {{
          "degree": "Degree Name",
          "institution": "University Name",
          "year": 2020
        }}
      ],
      "projects": [
        {{
          "name": "Project Name",
          "description": "Brief description",
          "technologies": ["tech1", "tech2"],
          "impact": "Measurable impact if mentioned"
        }}
      ],
      "positions": [
        {{"title": "Position Title", "year": 2018}}
      ]
    }}

    Rules:
    - Extract ALL skills mentioned (programming languages, frameworks, tools, soft skills)
    - experience_years should be TOTAL years of professional work experience
    - positions should show career progression chronologically (earliest first)
    - Include all jobs in experience_details, most recent first
    - For projects, include personal, academic, and professional projects
    - If information is not found, use empty arrays [] or 0 for numbers
    - Return ONLY the JSON object, no other text or markdown
    """
    ```

- [x] **Task 3: Implement extraction function** (AC: 3.3.1-3.3.5)
  - [ ] Add main extraction function:
    ```python
    def extract_structured_data(resume_text: str) -> dict:
        """Extract structured data from resume using Gemini API.

        Args:
            resume_text: Raw text content of resume

        Returns:
            Dict with extracted structured data
        """
        # Default structure for failures
        default_response = {
            "skills": [],
            "experience_years": 0,
            "experience_details": [],
            "education": [],
            "projects": [],
            "positions": [],
            "extraction_error": None
        }

        if not resume_text or not resume_text.strip():
            default_response["extraction_error"] = "Empty resume text"
            return default_response

        try:
            # Truncate very long resumes to avoid token limits
            max_chars = 10000
            if len(resume_text) > max_chars:
                resume_text = resume_text[:max_chars]
                logger.info(f"Resume text truncated to {max_chars} chars")

            # Create model and generate
            model = genai.GenerativeModel(MODEL_NAME)
            prompt = EXTRACTION_PROMPT.format(resume_text=resume_text)

            response = model.generate_content(prompt)

            # Parse response
            response_text = response.text.strip()
            data = parse_gemini_response(response_text)

            # Merge with defaults for missing fields
            for key in default_response:
                if key not in data and key != "extraction_error":
                    data[key] = default_response[key]

            logger.info("Gemini extraction successful")
            return data

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            default_response["extraction_error"] = str(e)
            return default_response
    ```

- [x] **Task 4: Implement response parsing** (AC: 3.3.3)
  - [ ] Add JSON parsing with cleanup:
    ```python
    def parse_gemini_response(response_text: str) -> dict:
        """Parse Gemini response, handling markdown code blocks.

        Args:
            response_text: Raw response from Gemini

        Returns:
            Parsed dict or empty structure on failure
        """
        try:
            # Remove markdown code blocks if present
            text = response_text.strip()

            if text.startswith('```json'):
                text = text[7:]
            elif text.startswith('```'):
                text = text[3:]

            if text.endswith('```'):
                text = text[:-3]

            text = text.strip()

            # Parse JSON
            data = json.loads(text)

            # Validate types
            if not isinstance(data.get('skills'), list):
                data['skills'] = []
            if not isinstance(data.get('experience_years'), (int, float)):
                data['experience_years'] = 0
            if not isinstance(data.get('experience_details'), list):
                data['experience_details'] = []
            if not isinstance(data.get('education'), list):
                data['education'] = []
            if not isinstance(data.get('projects'), list):
                data['projects'] = []
            if not isinstance(data.get('positions'), list):
                data['positions'] = []

            return data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}")
            logger.debug(f"Response was: {response_text[:500]}")
            return {}
    ```

- [x] **Task 5: Add retry logic for API errors** (AC: 3.3.4)
  - [ ] Implement retry with backoff:
    ```python
    import time

    def extract_with_retry(resume_text: str, max_retries: int = 2) -> dict:
        """Extract with retry on failure.

        Args:
            resume_text: Resume text content
            max_retries: Maximum retry attempts

        Returns:
            Extracted data dict
        """
        last_error = None

        for attempt in range(max_retries + 1):
            try:
                result = extract_structured_data(resume_text)

                # Check if extraction was successful
                if not result.get("extraction_error"):
                    return result

                last_error = result.get("extraction_error")
                logger.warning(f"Extraction attempt {attempt + 1} failed: {last_error}")

            except Exception as e:
                last_error = str(e)
                logger.warning(f"Extraction attempt {attempt + 1} error: {e}")

            # Wait before retry (exponential backoff)
            if attempt < max_retries:
                wait_time = 2 ** attempt
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)

        # Return with error after all retries
        return {
            "skills": [],
            "experience_years": 0,
            "experience_details": [],
            "education": [],
            "projects": [],
            "positions": [],
            "extraction_error": f"Failed after {max_retries + 1} attempts: {last_error}"
        }
    ```

- [x] **Task 6: Add validation helpers**
  - [ ] Validate extracted data quality:
    ```python
    def validate_extraction(data: dict) -> dict:
        """Validate and clean extracted data.

        Args:
            data: Extracted data dict

        Returns:
            Validated data with quality score
        """
        quality_score = 0
        issues = []

        # Check skills
        if data.get('skills') and len(data['skills']) > 0:
            quality_score += 20
        else:
            issues.append("No skills extracted")

        # Check experience
        if data.get('experience_years', 0) > 0:
            quality_score += 20
        if data.get('experience_details') and len(data['experience_details']) > 0:
            quality_score += 20
        else:
            issues.append("No experience details")

        # Check education
        if data.get('education') and len(data['education']) > 0:
            quality_score += 20

        # Check projects
        if data.get('projects') and len(data['projects']) > 0:
            quality_score += 20

        data['_quality_score'] = quality_score
        data['_quality_issues'] = issues

        return data
    ```

- [x] **Task 7: Test Gemini extraction**
  - [ ] Test with sample resume text:
    ```python
    sample_resume = """
    John Smith
    Software Engineer
    john@email.com | +1-555-123-4567

    EXPERIENCE
    Senior Developer at TechCorp (2020-Present)
    - Led team of 5 developers
    - Built microservices architecture

    SKILLS
    Python, JavaScript, React, AWS, Docker

    EDUCATION
    BS Computer Science, MIT, 2018
    """

    result = extract_structured_data(sample_resume)
    print(json.dumps(result, indent=2))
    ```
  - [ ] Test error handling with empty text
  - [ ] Test response parsing with markdown code blocks
  - [ ] Verify all required fields are present

## Dev Notes

### Architecture Alignment

This story implements Gemini extraction per architecture.md:
- **Model:** gemini-1.5-flash (fast, cost-effective)
- **Pattern:** Structured JSON extraction from text
- **Purpose:** Extract complex data requiring semantic understanding

### Gemini Response Format

Expected JSON structure:
```json
{
  "skills": ["Python", "Django", "AWS"],
  "experience_years": 4.5,
  "experience_details": [
    {
      "role": "Senior Developer",
      "company": "TechCorp",
      "duration": "2 years",
      "highlights": ["Led team", "Built API"]
    }
  ],
  "education": [
    {
      "degree": "B.Tech CS",
      "institution": "IIT Delhi",
      "year": 2018
    }
  ],
  "projects": [
    {
      "name": "E-commerce Platform",
      "description": "Full-stack web app",
      "technologies": ["Python", "React"],
      "impact": "50K users"
    }
  ],
  "positions": [
    {"title": "Junior Developer", "year": 2018},
    {"title": "Senior Developer", "year": 2020}
  ]
}
```

### API Configuration

```python
# .env file
GEMINI_API_KEY=your_api_key_here

# Python usage
import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
```

### Token Limits

- Gemini 1.5 Flash: ~1M tokens context
- Resume typically: 500-2000 tokens
- Truncate at 10,000 chars for safety

### Rate Limits (Free Tier)

- 60 requests per minute
- 1,500 requests per day
- Implement backoff if hitting limits

### Error Scenarios

| Scenario | Handling |
|----------|----------|
| API key missing | Log warning, return default |
| API timeout | Retry with backoff |
| Invalid JSON response | Log and return defaults |
| Rate limited | Wait and retry |

### Cost Considerations

- gemini-1.5-flash is cheapest option
- ~$0.000075 per 1K input tokens
- Typical resume: $0.0001-0.0002 per extraction

### References

- [Source: docs/sprint-artifacts/tech-spec-epic-3.md#Gemini-Service]
- [Source: docs/architecture.md#Gemini-API]
- [Source: docs/epics.md#Story-3.3]
- [Source: docs/prd.md#FR16]

## Dev Agent Record

### Context Reference

None (proceeded without story context file)

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- Python syntax check passed
- All functional tests passed:
  - Clean JSON parsing
  - Markdown code block handling
  - Invalid JSON returns empty dict
  - Missing fields get defaults
  - Empty text returns error
  - Whitespace-only returns error
  - Missing API key handled correctly
  - Complete data gets 100% quality score
  - Incomplete data gets 0% quality score

### Completion Notes List

- All 7 tasks completed successfully
- All 5 acceptance criteria satisfied:
  - AC3.3.1: Resume text sent to Gemini with extraction prompt
  - AC3.3.2: Returns structured JSON with all required fields
  - AC3.3.3: Response parsed and validated for required fields
  - AC3.3.4: API errors caught and logged with retry logic
  - AC3.3.5: Uses gemini-1.5-flash model for cost efficiency
- Handles markdown code blocks in Gemini responses
- Exponential backoff retry logic (2^attempt seconds)
- Quality validation scoring system (0-100%)
- Graceful handling of missing API key

### File List

**Created:**
- backend/services/gemini_service.py

---

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-12-20 | SM Agent (Bob) | Initial draft created |
| 2025-12-20 | Dev Agent (Amelia) | Implementation complete - all ACs satisfied |
