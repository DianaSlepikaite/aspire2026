"""
Resume generation service: builds a PDF resume from an extracted employee profile.
Uses a simple template (name, contact, summary, experience, education, skills, certifications).
Requires reportlab (pip install reportlab); imported lazily so the service starts without it.
"""

import io
import logging
from typing import Any, Dict, List, Optional

from employee_conversation_service.models.schemas import EmployeeProfile

_REPORTLAB_ERROR = (
    "reportlab is required for resume generation. Install with: pip install reportlab"
)


def _import_reportlab():
    """Lazy-import reportlab so the app can start without it."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import inch
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

        return (
            colors,
            letter,
            ParagraphStyle,
            getSampleStyleSheet,
            inch,
            Paragraph,
            SimpleDocTemplate,
            Spacer,
        )
    except ImportError as e:
        raise RuntimeError(_REPORTLAB_ERROR) from e


logger = logging.getLogger(__name__)


def _safe_str(value: Any) -> str:
    """Coerce value to string; empty/None -> empty string."""
    if value is None:
        return ""
    if isinstance(value, (list, dict)):
        return str(value)
    return str(value).strip()


def _format_list(items: Optional[List[Any]]) -> str:
    """Format list as comma-separated or bullet lines."""
    if not items:
        return ""
    if all(isinstance(x, str) for x in items):
        return ", ".join(str(x).strip() for x in items)
    return "\n".join(_safe_str(x) for x in items)


def _format_experience(experience: Optional[List[Dict[str, Any]]]) -> List[str]:
    """Format experience entries for display."""
    if not experience or not isinstance(experience, list):
        return []
    lines = []
    for i, entry in enumerate(experience[:15]):  # cap for PDF length
        if not isinstance(entry, dict):
            lines.append(_safe_str(entry))
            continue
        title = entry.get("title") or entry.get("role") or "Role"
        company = entry.get("company") or entry.get("organization") or ""
        years = entry.get("years") or entry.get("duration") or ""
        desc = entry.get("description") or ""
        line = f"• {title}"
        if company:
            line += f" at {company}"
        if years:
            line += f" ({years})"
        line += "\n"
        if desc:
            line += f"  {desc[:200]}{'...' if len(_safe_str(desc)) > 200 else ''}"
        lines.append(line)
    return lines


def _format_education(education: Optional[List[Dict[str, Any]]]) -> List[str]:
    """Format education entries for display."""
    if not education or not isinstance(education, list):
        return []
    lines = []
    for entry in education[:10]:
        if not isinstance(entry, dict):
            lines.append(_safe_str(entry))
            continue
        degree = entry.get("degree") or entry.get("qualification") or "Degree"
        school = entry.get("school") or entry.get("institution") or ""
        year = entry.get("year") or entry.get("graduation_year") or ""
        line = f"• {degree}"
        if school:
            line += f", {school}"
        if year:
            line += f" ({year})"
        lines.append(line)
    return lines


def _escape_html(s: str) -> str:
    """Escape for ReportLab Paragraph (basic)."""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class ResumeGenerationService:
    """
    Generates a PDF resume from an EmployeeProfile using a simple template.
    """

    def __init__(self) -> None:
        self._buffer: Optional[io.BytesIO] = None

    def generate_pdf(self, profile: EmployeeProfile) -> bytes:
        """
        Build a PDF resume from the given employee profile.

        Args:
            profile: EmployeeProfile from storage (after extraction).

        Returns:
            PDF file as bytes.
        """
        (
            colors,
            letter,
            ParagraphStyle,
            getSampleStyleSheet,
            inch,
            Paragraph,
            SimpleDocTemplate,
            Spacer,
        ) = _import_reportlab()
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch,
        )
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "ResumeTitle",
            parent=styles["Heading1"],
            fontSize=18,
            spaceAfter=4,
            textColor=colors.HexColor("#1a1a1a"),
        )
        heading_style = ParagraphStyle(
            "ResumeHeading",
            parent=styles["Heading2"],
            fontSize=12,
            spaceBefore=12,
            spaceAfter=6,
            textColor=colors.HexColor("#333333"),
        )
        body_style = ParagraphStyle(
            "ResumeBody",
            parent=styles["Normal"],
            fontSize=10,
            leading=12,
            spaceAfter=4,
        )

        elements = []

        # Name
        name = _safe_str(profile.full_name) or "Resume"
        elements.append(Paragraph(_escape_html(name), title_style))
        elements.append(Spacer(1, 6))

        # Contact line
        contact_parts = []
        if profile.email:
            contact_parts.append(_safe_str(profile.email))
        if profile.phone:
            contact_parts.append(_safe_str(profile.phone))
        if contact_parts:
            elements.append(
                Paragraph(
                    _escape_html(" | ".join(contact_parts)),
                    body_style,
                )
            )
            elements.append(Spacer(1, 12))

        # Summary
        if profile.summary:
            elements.append(Paragraph("Summary", heading_style))
            elements.append(
                Paragraph(
                    _escape_html(_safe_str(profile.summary)[:1500]).replace(
                        "\n", "<br/>"
                    ),
                    body_style,
                )
            )
            elements.append(Spacer(1, 8))

        # Experience
        experience = getattr(profile, "experience", None)
        if experience and isinstance(experience, list) and len(experience) > 0:
            elements.append(Paragraph("Experience", heading_style))
            for line in _format_experience(experience):
                elements.append(
                    Paragraph(
                        _escape_html(line).replace("\n", "<br/>"),
                        body_style,
                    )
                )
            elements.append(Spacer(1, 8))

        # Education
        education = getattr(profile, "education", None)
        if education and isinstance(education, list) and len(education) > 0:
            elements.append(Paragraph("Education", heading_style))
            for line in _format_education(education):
                elements.append(Paragraph(_escape_html(line), body_style))
            elements.append(Spacer(1, 8))

        # Skills
        skills = getattr(profile, "skills", None)
        if skills and isinstance(skills, list) and len(skills) > 0:
            elements.append(Paragraph("Skills", heading_style))
            elements.append(Paragraph(_escape_html(_format_list(skills)), body_style))
            elements.append(Spacer(1, 8))

        # Certifications
        certs = getattr(profile, "certifications", None)
        if certs and isinstance(certs, list) and len(certs) > 0:
            elements.append(Paragraph("Certifications", heading_style))
            elements.append(Paragraph(_escape_html(_format_list(certs)), body_style))
            elements.append(Spacer(1, 8))

        # Preferred roles
        roles = getattr(profile, "preferred_roles", None)
        if roles and isinstance(roles, list) and len(roles) > 0:
            elements.append(Paragraph("Preferred Roles", heading_style))
            elements.append(Paragraph(_escape_html(_format_list(roles)), body_style))

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()


def generate_resume_pdf(profile: EmployeeProfile) -> bytes:
    """
    Convenience function: generate PDF bytes from an EmployeeProfile.

    Args:
        profile: EmployeeProfile instance.

    Returns:
        PDF file as bytes.
    """
    service = ResumeGenerationService()
    return service.generate_pdf(profile)
