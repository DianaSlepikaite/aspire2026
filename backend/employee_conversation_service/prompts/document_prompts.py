"""
Prompts for extracting structured profile data from uploaded CV/resume documents.
Reuses the same EXTRACTION_FUNCTIONS schema from system_prompts.py so that
extracted data produces the identical EmployeeProfileUpdate shape.
"""

from employee_conversation_service.prompts.system_prompts import EXTRACTION_FUNCTIONS


DOCUMENT_EXTRACTION_PROMPT = """You are an expert talent profiling specialist for ASPIRE, Publicis Sapient's internal talent matching system.

You are analysing an uploaded CV/resume document to extract structured profile data. The document is: "{filename}"

**Instructions:**

1. Extract ALL technical skills mentioned, with estimated proficiency levels (1-5 scale):
   - 5 = Expert: Deep expertise, can lead/mentor, primary skill
   - 4 = Advanced: Strong proficiency, used extensively in production
   - 3 = Intermediate: Comfortable using, multiple projects
   - 2 = Basic: Some experience, limited usage
   - 1 = Beginner: Mentioned or learning

2. Extract project history with:
   - Project/company names
   - Dates and duration
   - Technologies used
   - Role and responsibilities
   - Team sizes if mentioned
   - Achievements and outcomes

3. Extract certifications with:
   - Certification name and provider
   - Dates (completion, expiry)
   - Skills gained

4. Map job titles to PS experience levels where possible:
   - Junior/Associate -> associate
   - Mid-level -> consultant
   - Senior -> senior_consultant
   - Lead/Principal -> manager or senior_manager
   - Director/VP -> director or senior_director

5. Map roles to PS career tracks where possible:
   - Software Engineer/Developer -> engineering
   - Designer/UX -> experience_design
   - Product Manager -> product
   - Data Scientist/Engineer -> data_ai
   - DevOps/Cloud -> cloud_infrastructure

6. Create a professional summary from the document content.

7. Extract soft skills, domain expertise, methodologies, and tools/platforms.

8. Extract career goals if any forward-looking statements are present.

**Critical rules:**
- ONLY extract information that is explicitly stated or directly inferable from the document.
- Do NOT fabricate or assume information not present.
- If a field cannot be determined, do not include it.
- Use the provided functions to structure the extracted data.

---

**Document text:**

{document_text}"""


# Reuse the same function calling schema so extraction produces identical shape
DOCUMENT_EXTRACTION_FUNCTIONS = EXTRACTION_FUNCTIONS
