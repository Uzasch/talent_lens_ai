"""Email service for sending interview invitations via Gmail SMTP."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails via Gmail SMTP."""

    def __init__(self):
        """Initialize email service with Gmail credentials."""
        self.gmail_address = os.getenv('GMAIL_ADDRESS')
        self.gmail_password = os.getenv('GMAIL_APP_PASSWORD')
        self.smtp_server = 'smtp.gmail.com'
        self.smtp_port = 587

        if not self.gmail_address or not self.gmail_password:
            logger.warning('Gmail credentials not configured in environment')

    def is_configured(self) -> bool:
        """Check if email service is properly configured."""
        return bool(self.gmail_address and self.gmail_password)

    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str
    ) -> dict:
        """Send a single email via Gmail SMTP.

        Args:
            to_email: Recipient email address
            subject: Email subject line
            body: Email body text

        Returns:
            Dict with email, sent status, and optional error
        """
        if not self.is_configured():
            return {
                'email': to_email,
                'sent': False,
                'error': 'Gmail credentials not configured'
            }

        try:
            msg = MIMEMultipart()
            msg['From'] = self.gmail_address
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.gmail_address, self.gmail_password)
                server.send_message(msg)

            logger.info(f'Email sent successfully to {to_email}')
            return {'email': to_email, 'sent': True}

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f'SMTP authentication failed: {e}')
            return {'email': to_email, 'sent': False, 'error': 'Authentication failed'}

        except smtplib.SMTPException as e:
            logger.error(f'SMTP error sending to {to_email}: {e}')
            return {'email': to_email, 'sent': False, 'error': str(e)}

        except Exception as e:
            logger.error(f'Unexpected error sending to {to_email}: {e}')
            return {'email': to_email, 'sent': False, 'error': str(e)}

    def format_slots(self, slots: list) -> str:
        """Format interview slots as bullet list.

        Args:
            slots: List of slot dicts with date and time

        Returns:
            Formatted string with slots
        """
        if not slots:
            return "To be scheduled"

        formatted = []
        for slot in slots:
            # slot: {"date": "Dec 6, 2025", "time": "10:00 AM"}
            date = slot.get('date', 'TBD')
            time = slot.get('time', 'TBD')
            formatted.append(f"  - {date} at {time}")

        return "\n".join(formatted)

    def personalize_message(
        self,
        template: str,
        name: str,
        job_title: str,
        company: str,
        slots: list
    ) -> str:
        """Replace placeholders in message template.

        Args:
            template: Message template with placeholders
            name: Candidate name
            job_title: Position title
            company: Company name
            slots: Interview time slots

        Returns:
            Personalized message string
        """
        formatted_slots = self.format_slots(slots)

        personalized = template
        personalized = personalized.replace('{name}', name or 'Candidate')
        personalized = personalized.replace('{job_title}', job_title or 'the position')
        personalized = personalized.replace('{company}', company or 'our company')
        personalized = personalized.replace('{slots}', formatted_slots)

        return personalized

    def send_bulk(
        self,
        recipients: list,
        job_title: str,
        company: str,
        slots: list,
        message_template: str
    ) -> dict:
        """Send personalized emails to multiple recipients.

        Args:
            recipients: List of dicts with name and email
            job_title: Position title for subject line
            company: Company name for subject line
            slots: Interview time slots
            message_template: Template with placeholders

        Returns:
            Dict with sent count, failed count, and results
        """
        results = []
        sent_count = 0
        failed_count = 0

        subject = f"Interview Invitation - {job_title} at {company}"

        for recipient in recipients:
            name = recipient.get('name', 'Candidate')
            email = recipient.get('email')

            if not email:
                results.append({
                    'email': 'unknown',
                    'sent': False,
                    'error': 'No email address'
                })
                failed_count += 1
                continue

            personalized_body = self.personalize_message(
                message_template,
                name,
                job_title,
                company,
                slots
            )

            result = self.send_email(email, subject, personalized_body)
            results.append(result)

            if result['sent']:
                sent_count += 1
            else:
                failed_count += 1

        return {
            'sent': sent_count,
            'failed': failed_count,
            'results': results
        }


# Default template for interview invitations
DEFAULT_INVITATION_TEMPLATE = """Dear {name},

Congratulations! We are pleased to invite you to interview for the {job_title} position at {company}.

Based on your resume and qualifications, we believe you could be an excellent fit for our team.

Available Interview Slots:
{slots}

Please reply to this email with your preferred time slot, or let us know if none of these work for you.

We look forward to speaking with you!

Best regards,
The {company} Hiring Team
"""
