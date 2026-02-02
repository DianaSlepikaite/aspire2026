import { Github, Link2, Linkedin } from "lucide-react";

export const coreProfile = {
  fullName: "Sarah Jenkins",
  title: "Senior Project Manager",
  department: "Staffing Tech Div.",
  manager: "Alicia Romero",
  location: "Austin, TX",
  email: "sarah.jenkins@aspire.io",
  phone: "+1 (512) 555-0184",
  startDate: "April 14, 2021",
  employmentType: "Full-time",
  summary:
    "Program leader focused on cross-functional delivery, portfolio health, and stakeholder alignment across enterprise initiatives.",
  strengths: "Agile delivery, executive reporting, risk mitigation, data storytelling, vendor management.",
  goals: "Move into Director-level program leadership within 18 months.",
  topSkills: ["Agile Leadership", "Data Visualization", "Stakeholder Mgmt", "Python", "SQL", "Team Building", "Scrum"],
  certifications: ["PMP (Active)", "CSM", "ICAgile ICP-APM"],
  education: [
    { school: "University of Texas at Austin", degree: "B.S. Information Systems", year: "2016" },
    { school: "Kellogg Executive Education", degree: "Leadership in Digital Transformation", year: "2022" },
  ],
  experienceHighlights: [
    "Led a $12M enterprise migration program, achieving 18% delivery acceleration.",
    "Standardized program reporting for 9 global teams, reducing status churn by 30%.",
    "Mentored 6 project leads and built succession plans for critical initiatives.",
  ],
};

export const integrations = [
  {
    name: "LinkedIn",
    description: "Sync roles, endorsements, and profile summary.",
    icon: Linkedin,
    connected: true,
    handle: "linkedin.com/in/sarah-jenkins",
  },
  {
    name: "GitHub",
    description: "Pull repositories and contribution signals.",
    icon: Github,
    connected: false,
    handle: "github.com/sarahjenkins",
  },
  {
    name: "Portfolio",
    description: "External project showcase or personal site.",
    icon: Link2,
    connected: false,
    handle: "sarahjenkins.io",
  },
];
