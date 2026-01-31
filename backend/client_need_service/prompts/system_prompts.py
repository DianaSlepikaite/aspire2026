"""
System prompts and function definitions for Azure OpenAI conversations.
"""

from typing import Dict, Any, List


SYSTEM_PROMPT = """You are an expert client needs analyst for ASPIRE, a freelance matching platform that connects clients with skilled professionals.

Your role is to conduct natural, empathetic conversations with clients to understand their project requirements comprehensively. You should extract information across these key areas:

1. **Project Details**
   - Project title and description
   - Type of project (web development, mobile app, data analytics, etc.)
   - Industry or domain
   - Key challenges and goals

2. **Skills and Requirements**
   - Required technical skills
   - Preferred skills (nice-to-have)
   - Skill level needed (junior, mid, senior, expert)
   - Any certifications required

3. **Budget and Compensation**
   - Budget range (minimum and maximum)
   - Budget type (hourly, fixed price, monthly retainer)
   - Currency
   - Payment terms or expectations

4. **Timeline and Schedule**
   - Preferred start date
   - End date or project duration
   - Timeline flexibility
   - Importance of start date

5. **Urgency and Priority**
   - Overall urgency level
   - Priority score
   - Any time-sensitive milestones

6. **Work Arrangement**
   - Work location (remote, onsite, hybrid)
   - Location details if applicable
   - Work hours requirements
   - Time zone considerations

7. **Additional Details**
   - Team size needed
   - Collaboration tools preferences
   - Communication style preferences

**Conversation Guidelines:**

- Be warm, professional, and empathetic
- Ask clarifying questions when information is vague or incomplete
- Guide the conversation naturally without interrogating
- Acknowledge and summarize understanding periodically
- Use follow-up questions to extract specific, actionable information
- If the client seems uncertain, offer examples or typical scenarios
- Maintain context throughout the conversation

**Function Calling:**

When you extract information from the conversation, use the provided functions to structure the data. You can call multiple functions in a single response if you've gathered information across multiple areas.

**Important:**
- Don't rush to complete the conversation - ensure you have sufficient information
- It's okay to ask multiple questions across several turns
- Prioritize understanding their needs over extracting every single field
- Focus on the most critical information first (project details, skills, budget, timeline)

When you believe you have enough information to create a useful profile (even if not 100% complete), indicate this by summarizing what you've gathered and asking if there's anything else they'd like to add."""


EXTRACTION_FUNCTIONS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "update_project_details",
            "description": "Update project information including title, description, type, and industry",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_title": {
                        "type": "string",
                        "description": "Brief title for the project"
                    },
                    "project_description": {
                        "type": "string",
                        "description": "Detailed description of the project"
                    },
                    "project_type": {
                        "type": "string",
                        "description": "Type of project",
                        "enum": [
                            "web_development",
                            "mobile_app",
                            "data_analytics",
                            "machine_learning",
                            "devops",
                            "design",
                            "content_creation",
                            "consulting",
                            "other"
                        ]
                    },
                    "industry": {
                        "type": "string",
                        "description": "Industry or domain of the project"
                    },
                    "key_challenges": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Main challenges or problems to solve"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_skill_requirements",
            "description": "Update required and preferred skills, skill level, and certifications",
            "parameters": {
                "type": "object",
                "properties": {
                    "required_skills": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of required technical skills"
                    },
                    "preferred_skills": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of preferred but not required skills"
                    },
                    "skill_level": {
                        "type": "string",
                        "enum": ["junior", "mid", "senior", "expert"],
                        "description": "Required skill level"
                    },
                    "certifications_required": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Any required certifications"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_budget_information",
            "description": "Update budget details including range, type, and currency",
            "parameters": {
                "type": "object",
                "properties": {
                    "budget_min": {
                        "type": "number",
                        "description": "Minimum budget amount"
                    },
                    "budget_max": {
                        "type": "number",
                        "description": "Maximum budget amount"
                    },
                    "budget_currency": {
                        "type": "string",
                        "description": "Currency code (e.g., USD, EUR, GBP)",
                        "default": "USD"
                    },
                    "budget_type": {
                        "type": "string",
                        "enum": ["hourly", "fixed", "monthly"],
                        "description": "How the budget is structured"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_timeline_details",
            "description": "Update project timeline including start date, duration, and flexibility",
            "parameters": {
                "type": "object",
                "properties": {
                    "timeline_start_date": {
                        "type": "string",
                        "format": "date",
                        "description": "Preferred project start date (YYYY-MM-DD)"
                    },
                    "timeline_end_date": {
                        "type": "string",
                        "format": "date",
                        "description": "Expected project end date (YYYY-MM-DD)"
                    },
                    "timeline_duration_weeks": {
                        "type": "integer",
                        "description": "Project duration in weeks"
                    },
                    "timeline_flexibility": {
                        "type": "string",
                        "enum": ["flexible", "somewhat_flexible", "strict"],
                        "description": "How flexible the timeline is"
                    },
                    "start_date_importance": {
                        "type": "string",
                        "enum": ["flexible", "preferred", "mandatory"],
                        "description": "Importance of the start date"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_urgency_and_priority",
            "description": "Update urgency level and priority information",
            "parameters": {
                "type": "object",
                "properties": {
                    "urgency_level": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"],
                        "description": "Overall urgency level"
                    },
                    "priority_score": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 10,
                        "description": "Priority score from 1 (lowest) to 10 (highest)"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_work_arrangement",
            "description": "Update work location and arrangement details",
            "parameters": {
                "type": "object",
                "properties": {
                    "work_location": {
                        "type": "string",
                        "enum": ["remote", "onsite", "hybrid"],
                        "description": "Type of work arrangement"
                    },
                    "work_location_details": {
                        "type": "object",
                        "properties": {
                            "city": {"type": "string"},
                            "country": {"type": "string"},
                            "timezone": {"type": "string"}
                        },
                        "description": "Specific location details if applicable"
                    },
                    "work_hours_requirement": {
                        "type": "string",
                        "description": "Work hours requirements or preferences"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_additional_requirements",
            "description": "Update team size, tools, and communication preferences",
            "parameters": {
                "type": "object",
                "properties": {
                    "team_size_needed": {
                        "type": "integer",
                        "description": "Number of people needed for the project"
                    },
                    "collaboration_tools": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Preferred collaboration tools (Slack, Jira, etc.)"
                    },
                    "communication_preferences": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Communication style or frequency preferences"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_client_information",
            "description": "Update client contact and company information",
            "parameters": {
                "type": "object",
                "properties": {
                    "client_name": {
                        "type": "string",
                        "description": "Client's full name"
                    },
                    "client_email": {
                        "type": "string",
                        "format": "email",
                        "description": "Client's email address"
                    },
                    "client_phone": {
                        "type": "string",
                        "description": "Client's phone number"
                    },
                    "client_company": {
                        "type": "string",
                        "description": "Client's company name"
                    }
                }
            }
        }
    }
]


GREETING_MESSAGE = """Hello! I'm here to help you find the perfect professional for your project.

I'd like to understand your needs by asking a few questions about what you're looking for. We'll cover things like the type of project, skills required, budget, and timeline.

To start, could you tell me a bit about your project? What are you looking to accomplish?"""


COMPLETION_PROMPT = """Based on the conversation history and extracted information, generate a comprehensive summary of the client's needs.

The summary should include:
1. Project overview and objectives
2. Key requirements and challenges
3. Skills and expertise needed
4. Timeline and urgency considerations
5. Budget expectations
6. Work arrangement preferences
7. Any notable concerns or special requirements

Make the summary clear, concise, and actionable for matching with professionals."""


def get_conversation_context(extracted_data: Dict[str, Any]) -> str:
    """
    Generate context about currently extracted information to inject into the system prompt.

    Args:
        extracted_data: Dictionary of extracted information

    Returns:
        Context string describing what's been extracted
    """
    if not extracted_data:
        return "No information extracted yet."

    context_parts = ["Currently extracted information:"]

    if extracted_data.get("project_title"):
        context_parts.append(f"- Project: {extracted_data['project_title']}")

    if extracted_data.get("required_skills"):
        skills = ", ".join(extracted_data["required_skills"])
        context_parts.append(f"- Required skills: {skills}")

    if extracted_data.get("budget_min") or extracted_data.get("budget_max"):
        budget_str = f"${extracted_data.get('budget_min', '?')} - ${extracted_data.get('budget_max', '?')}"
        context_parts.append(f"- Budget: {budget_str}")

    if extracted_data.get("urgency_level"):
        context_parts.append(f"- Urgency: {extracted_data['urgency_level']}")

    return "\n".join(context_parts)
