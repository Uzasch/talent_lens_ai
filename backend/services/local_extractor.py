"""Local data extraction service using regex and spaCy NER."""

import re
import spacy
import logging

logger = logging.getLogger(__name__)

# Load spaCy model once at module level
nlp = None


def get_nlp():
    """Lazy load spaCy model."""
    global nlp
    if nlp is None:
        nlp = spacy.load("en_core_web_sm")
    return nlp


def extract_email(text: str) -> str | None:
    """Extract email using regex.

    Args:
        text: Resume text content

    Returns:
        Email address or None if not found
    """
    pattern = r'[\w.-]+@[\w.-]+\.\w+'
    match = re.search(pattern, text)
    return match.group(0).lower() if match else None


def extract_phone(text: str) -> str | None:
    """Extract phone number using regex.

    Handles formats:
    - +1-123-456-7890
    - (123) 456-7890
    - 123.456.7890
    - +92 300 1234567
    - 10+ digit numbers

    Args:
        text: Resume text content

    Returns:
        Phone number or None if not found
    """
    patterns = [
        r'\+?[\d]{1,3}[-.\s]?[\d]{3}[-.\s]?[\d]{3}[-.\s]?[\d]{4}',
        r'\+?[\d]{1,3}[-.\s]?[\d]{3}[-.\s]?[\d]{7}',
        r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        r'\d{10,13}',
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            # Clean up the phone number
            phone = match.group(0).strip()
            return phone

    return None


def extract_name(text: str) -> str | None:
    """Extract candidate name using spaCy NER.

    Strategy:
    1. Look for PERSON entities in first 1000 chars
    2. Prefer entities at the start of the document
    3. Fallback to first non-empty line if no entity found

    Args:
        text: Resume text content

    Returns:
        Candidate name or None if not found
    """
    try:
        nlp_model = get_nlp()

        # Process only first 1000 chars for speed (name usually at top)
        doc = nlp_model(text[:1000])

        # Find PERSON entities
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                name = ent.text.strip()
                # Basic validation: should be 2+ words, reasonable length
                if len(name.split()) >= 2 and len(name) < 50:
                    return name

        # Fallback: first non-empty line might be name
        lines = text.strip().split('\n')
        for line in lines[:5]:
            line = line.strip()
            # Heuristic: name is usually short, no special chars
            if line and len(line) < 40 and not any(c in line for c in ['@', '|', '•', ':']):
                # Check if it looks like a name (mostly letters and spaces)
                if re.match(r'^[A-Za-z\s.-]+$', line):
                    return line

        return None

    except Exception as e:
        logger.error(f"spaCy name extraction failed: {e}")
        return None


def extract_basic_info(text: str) -> dict:
    """Extract name, email, phone from resume text.

    Args:
        text: Resume text content

    Returns:
        Dict with name, email, phone (None for missing fields)
    """
    if not text or not text.strip():
        return {
            "name": None,
            "email": None,
            "phone": None
        }

    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text)
    }


def is_valid_email(email: str) -> bool:
    """Validate email format.

    Args:
        email: Email address to validate

    Returns:
        True if valid email format
    """
    if not email:
        return False
    pattern = r'^[\w.-]+@[\w.-]+\.\w{2,}$'
    return bool(re.match(pattern, email))
