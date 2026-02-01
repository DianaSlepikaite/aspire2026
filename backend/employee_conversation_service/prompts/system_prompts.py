"""
System prompts and function definitions for Azure OpenAI conversations.
Tailored for Publicis Sapient internal talent matching and staffing.
"""

from typing import Dict, Any, List


SYSTEM_PROMPT = """You are an expert talent profiling specialist for ASPIRE, Publicis Sapient's internal talent matching system.

Your role is to conduct natural, supportive conversations with PS employees to understand their skills, project experience, and career aspirations so we can match them with the best internal project opportunities. You should extract information across these key areas:

1. **Basic Identity**
   - Employee name and PS employee ID
   - Email address
   - Location, nearest PS office, timezone
   - Willingness to travel

2. **PS Career Information**
   - Career track (Engineering, Experience Design, Product, Strategy, Data & AI, Cloud & Infrastructure)
   - Experience level/grade (Associate through Senior Director)
   - Years at Publicis Sapient
   - Total years of professional experience

3. **Current Assignment Status**
   - Current bench status (on project, on bench, rolling off, partially allocated)
   - Current project details if applicable (project name, client, role, allocation)
   - Expected roll-off date and availability date

4. **Technical Skills & Expertise**
   - Technical skills with proficiency levels (1-5 scale) and years of experience
   - Soft skills (leadership, communication, mentoring, etc.)
   - Domain expertise / industry knowledge (Banking, Healthcare, Retail, etc.)
   - Methodologies (Agile, Scrum, SAFe, Design Thinking, etc.)
   - Tools and platforms (JIRA, Figma, AWS, Azure, etc.)

5. **PS Project History**
   - Past projects at PS (project name, client, industry, role, duration, technologies)
   - Key responsibilities and achievements on each project
   - Team sizes worked with

6. **Learning & Development**
   - Certifications held (with provider, expiry if applicable)
   - Current courses or learning paths
   - Skills gained through training

7. **Career Goals & Interests**
   - Short-term goals (6-12 months)
   - Long-term goals (2-3 years)
   - Industries of interest
   - Technologies interested in learning/using
   - Preferred project types (greenfield, transformation, maintenance)
   - Preferred client engagement style (long-term, short-term, multiple)
   - Roles interested in taking on

**Conversation Guidelines:**

- Be warm, professional, and collegial - this is an internal conversation with a colleague
- Use PS terminology naturally (career tracks, grades, PIDs, bench status)
- Ask clarifying questions when information is vague or incomplete
- Guide the conversation naturally without interrogating
- Acknowledge skills and achievements to build rapport
- Help employees articulate career goals if they seem uncertain
- Be sensitive to bench anxiety - frame availability positively as opportunity
- Maintain context throughout the conversation

**Function Calling:**

When you extract information from the conversation, use the provided functions to structure the data. You can call multiple functions in a single response if you've gathered information across multiple areas.

**Important:**
- Don't rush to complete the conversation - ensure you have sufficient information
- It's okay to ask multiple questions across several turns
- Prioritize understanding their technical skills, current status, and career goals
- Focus on the most critical information first (skills, bench status, availability, career goals)

When you believe you have enough information to create a useful profile (even if not 100% complete), indicate this by summarizing what you've gathered and asking if there's anything else they'd like to add."""


EXTRACTION_FUNCTIONS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "update_basic_info",
            "description": "Update employee basic information, location, and travel preferences",
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_id": {
                        "type": "string",
                        "description": "PS Employee ID"
                    },
                    "employee_name": {
                        "type": "string",
                        "description": "Employee's full name"
                    },
                    "employee_email": {
                        "type": "string",
                        "format": "email",
                        "description": "Employee's PS email address"
                    },
                    "location": {
                        "type": "object",
                        "properties": {
                            "city": {"type": "string"},
                            "country": {"type": "string"},
                            "timezone": {"type": "string", "description": "e.g., America/New_York"},
                            "ps_office": {"type": "string", "description": "Nearest PS office"},
                            "willing_to_travel": {"type": "boolean"},
                            "travel_percentage_preference": {
                                "type": "integer",
                                "description": "Percentage of time willing to travel (0-100)"
                            }
                        },
                        "description": "Employee location details"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_career_info",
            "description": "Update PS career track, experience level, and years of experience",
            "parameters": {
                "type": "object",
                "properties": {
                    "career_track": {
                        "type": "string",
                        "enum": ["engineering", "experience_design", "product", "strategy", "data_ai", "cloud_infrastructure"],
                        "description": "PS career track/discipline"
                    },
                    "experience_level": {
                        "type": "string",
                        "enum": ["associate", "consultant", "senior_consultant", "manager", "senior_manager", "associate_director", "director", "senior_director"],
                        "description": "PS experience level/grade"
                    },
                    "years_at_ps": {
                        "type": "integer",
                        "description": "Years at Publicis Sapient"
                    },
                    "years_total_experience": {
                        "type": "integer",
                        "description": "Total years of professional experience"
                    },
                    "professional_summary": {
                        "type": "string",
                        "description": "Brief summary of experience and expertise"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_assignment_status",
            "description": "Update current bench status, project assignment, and availability",
            "parameters": {
                "type": "object",
                "properties": {
                    "bench_status": {
                        "type": "string",
                        "enum": ["on_project", "on_bench", "rolling_off", "partially_allocated"],
                        "description": "Current assignment status"
                    },
                    "current_assignment": {
                        "type": "object",
                        "properties": {
                            "project_id": {"type": "string", "description": "Project ID (PID)"},
                            "project_name": {"type": "string"},
                            "client_name": {"type": "string"},
                            "role": {
                                "type": "string",
                                "enum": ["developer", "senior_developer", "tech_lead", "architect", "designer", "lead_designer", "product_manager", "scrum_master", "data_engineer", "data_scientist", "devops_engineer", "qa_engineer"]
                            },
                            "allocation_percentage": {"type": "integer", "description": "0-100"},
                            "start_date": {"type": "string", "format": "date"},
                            "expected_end_date": {"type": "string", "format": "date"},
                            "rolling_off_date": {"type": "string", "format": "date"}
                        },
                        "description": "Current project assignment details"
                    },
                    "availability_date": {
                        "type": "string",
                        "format": "date",
                        "description": "Date when employee will be available for new project (YYYY-MM-DD)"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_skills",
            "description": "Update technical skills, soft skills, domain expertise, methodologies, and tools",
            "parameters": {
                "type": "object",
                "properties": {
                    "technical_skills": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "skill_name": {"type": "string"},
                                "proficiency_level": {
                                    "type": "integer",
                                    "description": "1=Beginner to 5=Expert"
                                },
                                "years_of_experience": {"type": "number"},
                                "last_used": {"type": "string", "format": "date"},
                                "acquired_through": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Where skill was acquired, e.g., project names or training"
                                }
                            }
                        },
                        "description": "Technical skills with proficiency and experience details"
                    },
                    "soft_skills": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Soft skills like Leadership, Client Communication, Mentoring"
                    },
                    "domain_expertise": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Industry domains like Banking, E-commerce, Healthcare"
                    },
                    "methodologies": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Methodologies like Agile, Scrum, SAFe, Design Thinking"
                    },
                    "tools_platforms": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Tools and platforms like JIRA, Figma, AWS, Azure"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_project_history",
            "description": "Update PS project history, achievements, and strengths",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_history": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "project_id": {"type": "string", "description": "Project ID (PID)"},
                                "project_name": {"type": "string"},
                                "client_name": {"type": "string"},
                                "industry": {"type": "string"},
                                "start_date": {"type": "string", "format": "date"},
                                "end_date": {"type": "string", "format": "date"},
                                "duration_months": {"type": "integer"},
                                "role": {
                                    "type": "string",
                                    "enum": ["developer", "senior_developer", "tech_lead", "architect", "designer", "lead_designer", "product_manager", "scrum_master", "data_engineer", "data_scientist", "devops_engineer", "qa_engineer"]
                                },
                                "allocation_percentage": {"type": "integer"},
                                "key_responsibilities": {"type": "array", "items": {"type": "string"}},
                                "technologies_used": {"type": "array", "items": {"type": "string"}},
                                "achievements": {"type": "array", "items": {"type": "string"}},
                                "team_size": {"type": "integer"}
                            }
                        },
                        "description": "Past PS projects in reverse chronological order"
                    },
                    "notable_achievements": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Notable professional achievements"
                    },
                    "strengths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Key strengths identified through conversation"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_learning_development",
            "description": "Update certifications, training, and current learning activities",
            "parameters": {
                "type": "object",
                "properties": {
                    "training_certifications": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "provider": {"type": "string", "description": "e.g., AWS, Coursera, Udemy"},
                                "completion_date": {"type": "string", "format": "date"},
                                "expiry_date": {"type": "string", "format": "date"},
                                "certificate_url": {"type": "string"},
                                "skills_gained": {"type": "array", "items": {"type": "string"}}
                            }
                        },
                        "description": "Certifications and training completed"
                    },
                    "current_learning": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Currently taking courses or certifications"
                    },
                    "areas_for_growth": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Skills or areas interested in developing"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_career_goals",
            "description": "Update career goals, interests, and preferred project types",
            "parameters": {
                "type": "object",
                "properties": {
                    "career_goals": {
                        "type": "object",
                        "properties": {
                            "short_term_goals": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "6-12 month goals"
                            },
                            "long_term_goals": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "2-3 year goals"
                            },
                            "interested_industries": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Industries of interest"
                            },
                            "interested_technologies": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Technologies interested in learning/using"
                            },
                            "preferred_project_types": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "e.g., Greenfield, Transformation, Maintenance"
                            },
                            "preferred_client_engagement": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "e.g., Long-term, Short-term, Multiple clients"
                            },
                            "interested_roles": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "enum": ["developer", "senior_developer", "tech_lead", "architect", "designer", "lead_designer", "product_manager", "scrum_master", "data_engineer", "data_scientist", "devops_engineer", "qa_engineer"]
                                },
                                "description": "Roles interested in taking on"
                            }
                        },
                        "description": "Career goals and aspirations within PS"
                    }
                }
            }
        }
    }
]


GREETING_MESSAGE = """Hello! Welcome to the ASPIRE talent profiling conversation. I'm here to help build your skills profile so we can match you with the best project opportunities at PS.

We'll have a casual chat covering your current skills, project experience, and what you're looking for next. This helps our staffing team find the right fit for you.

To get started, could you tell me a bit about your current role and what you've been working on recently?"""


RETURNING_USER_GREETING_PROMPT = """You are the ASPIRE talent profiling specialist welcoming back a returning Publicis Sapient employee.

The following information was gathered from a previous conversation:
{profile_context}

Generate a warm, personalized welcome-back greeting that:
1. Acknowledges the employee by name (if known)
2. Briefly mentions 1-2 key details you already know about them (e.g., their career track, a recent project, or a skill)
3. Explains that their previous profile information has been carried forward
4. Asks what has changed since their last conversation (new projects, new skills, updated goals)
5. Keeps a collegial, supportive tone

Keep the greeting concise (3-5 sentences). Do not list all their information back to them."""


RESUME_GREETING_PROMPT = """You are the ASPIRE talent profiling specialist helping a Publicis Sapient employee resume an in-progress conversation.

The following information has been gathered so far:
{profile_context}

Here are the last few messages from the conversation:
{last_messages}

Generate a brief welcome-back message that:
1. Warmly acknowledges their return
2. Briefly recaps where the conversation left off (1-2 sentences)
3. Suggests what to cover next based on missing information
4. Keeps a natural, conversational tone

Keep the message concise (2-4 sentences)."""


COMPLETION_PROMPT = """Based on the conversation history and extracted information, generate a comprehensive summary of the employee's professional profile for internal staffing purposes.

The summary should include:
1. Professional overview (career track, level, years of experience)
2. Current assignment status and availability
3. Core technical skills and domain expertise
4. Notable PS project experience and achievements
5. Certifications and ongoing learning
6. Career goals and project preferences
7. Key strengths and growth areas

Make the summary clear, concise, and actionable for staffing managers matching employees to project opportunities."""


def get_conversation_context(
    extracted_data: Dict[str, Any],
    is_returning_user: bool = False
) -> str:
    """
    Generate context about currently extracted information to inject into the system prompt.

    Args:
        extracted_data: Dictionary of extracted information
        is_returning_user: Whether this data was carried forward from a previous conversation

    Returns:
        Context string describing what's been extracted
    """
    if not extracted_data:
        return "No information extracted yet."

    context_parts = []

    if is_returning_user:
        context_parts.append(
            "This employee is a returning user. The following was carried forward "
            "from previous conversations. Verify whether this is still accurate "
            "and ask about any changes."
        )
        context_parts.append("")

    context_parts.append("Currently extracted information:")

    if extracted_data.get("employee_name"):
        context_parts.append(f"- Name: {extracted_data['employee_name']}")

    if extracted_data.get("career_track"):
        context_parts.append(f"- Career track: {extracted_data['career_track']}")

    if extracted_data.get("experience_level"):
        context_parts.append(f"- Level: {extracted_data['experience_level']}")

    if extracted_data.get("bench_status"):
        context_parts.append(f"- Bench status: {extracted_data['bench_status']}")

    if extracted_data.get("technical_skills"):
        skills = extracted_data["technical_skills"]
        if isinstance(skills, list) and len(skills) > 0:
            if isinstance(skills[0], dict):
                skill_names = [s.get("skill_name", "") for s in skills[:5]]
            else:
                skill_names = skills[:5]
            context_parts.append(f"- Technical skills: {', '.join(skill_names)}")

    if extracted_data.get("years_total_experience"):
        context_parts.append(f"- Total experience: {extracted_data['years_total_experience']} years")

    if extracted_data.get("domain_expertise"):
        domains = ", ".join(extracted_data["domain_expertise"])
        context_parts.append(f"- Domain expertise: {domains}")

    if extracted_data.get("career_goals"):
        goals = extracted_data["career_goals"]
        if isinstance(goals, dict) and goals.get("short_term_goals"):
            context_parts.append(f"- Short-term goals: {', '.join(goals['short_term_goals'][:2])}")

    return "\n".join(context_parts)
