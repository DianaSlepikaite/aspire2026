-- ======================
-- EMPLOYEE AGENT
-- ======================

CREATE SCHEMA IF NOT EXISTS employee_agent;

CREATE TABLE employee_agent.employee_profiles (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  conversation_id UUID UNIQUE NOT NULL,

  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),

  -- Conversation state
  conversation_status conversation_status DEFAULT 'in_progress',
  total_messages INTEGER DEFAULT 0,
  conversation_started_at TIMESTAMPTZ DEFAULT now(),
  conversation_completed_at TIMESTAMPTZ,

  -- Employee info
  employee_id VARCHAR,
  employee_name VARCHAR,
  employee_email VARCHAR,

  -- Location & career
  location JSONB,
  career_track career_track,
  experience_level experience_level,

  years_at_ps INTEGER CHECK (years_at_ps >= 0),
  years_total_experience INTEGER CHECK (years_total_experience >= 0),

  -- Bench & assignment
  bench_status bench_status DEFAULT 'on_bench',
  current_assignment JSONB,
  availability_date DATE,

  -- Skills
  technical_skills JSONB,
  soft_skills JSONB,
  domain_expertise JSONB,
  methodologies JSONB,
  tools_platforms JSONB,

  -- History & growth
  project_history JSONB,
  notable_achievements JSONB,
  training_certifications JSONB,
  current_learning JSONB,
  career_goals JSONB,

  -- AI insights
  professional_summary TEXT,
  strengths JSONB,
  areas_for_growth JSONB,

  -- Extraction quality
  extraction_confidence NUMERIC,
  profile_completeness_score INTEGER
    DEFAULT 0 CHECK (profile_completeness_score BETWEEN 0 AND 100),
  missing_information JSONB,

  -- Raw data
  conversation_transcript JSONB,
  raw_audio_references JSONB,

  -- Metadata
  source_channel VARCHAR DEFAULT 'web',
  language VARCHAR DEFAULT 'en',
  notes TEXT
);
