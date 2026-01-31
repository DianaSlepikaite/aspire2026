-- ======================
-- EMPLOYEE AGENT
-- ======================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE SCHEMA IF NOT EXISTS employee_agent;

-- Enum types
CREATE TYPE employee_agent.conversation_status AS ENUM (
  'in_progress', 'completed', 'abandoned'
);

CREATE TYPE employee_agent.bench_status AS ENUM (
  'on_project', 'on_bench', 'rolling_off', 'partially_allocated'
);

CREATE TYPE employee_agent.career_track AS ENUM (
  'engineering', 'experience_design', 'product', 'strategy', 'data_ai', 'cloud_infrastructure'
);

CREATE TYPE employee_agent.experience_level AS ENUM (
  'associate', 'consultant', 'senior_consultant', 'manager',
  'senior_manager', 'associate_director', 'director', 'senior_director'
);

-- Employee profiles table
CREATE TABLE employee_agent.employee_profiles (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  conversation_id UUID UNIQUE NOT NULL,

  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),

  -- Conversation state
  conversation_status employee_agent.conversation_status DEFAULT 'in_progress',
  total_messages INTEGER DEFAULT 0,
  conversation_started_at TIMESTAMPTZ DEFAULT now(),
  conversation_completed_at TIMESTAMPTZ,

  -- Employee info
  employee_id VARCHAR,
  employee_name VARCHAR,
  employee_email VARCHAR,

  -- Location & career
  location JSONB,
  career_track employee_agent.career_track,
  experience_level employee_agent.experience_level,

  years_at_ps INTEGER CHECK (years_at_ps >= 0),
  years_total_experience INTEGER CHECK (years_total_experience >= 0),

  -- Bench & assignment
  bench_status employee_agent.bench_status DEFAULT 'on_bench',
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

-- Conversation messages table
CREATE TABLE employee_agent.employee_conversation_messages (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  conversation_id UUID NOT NULL REFERENCES employee_agent.employee_profiles(conversation_id),

  created_at TIMESTAMPTZ DEFAULT now(),

  -- Message content
  role VARCHAR NOT NULL,
  content TEXT NOT NULL,
  message_type VARCHAR DEFAULT 'text',
  audio_url VARCHAR,
  transcription_confidence NUMERIC,

  -- Processing metadata
  tokens_used INTEGER,
  model_version VARCHAR,
  processing_time_ms INTEGER
);

-- Extraction history table
CREATE TABLE employee_agent.employee_extraction_history (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  conversation_id UUID NOT NULL REFERENCES employee_agent.employee_profiles(conversation_id),

  created_at TIMESTAMPTZ DEFAULT now(),

  -- Extraction data
  extracted_field VARCHAR NOT NULL,
  extracted_value JSONB,
  confidence_score NUMERIC,
  extraction_method VARCHAR(50)
);

-- Indexes
CREATE INDEX idx_employee_profiles_conversation_id
  ON employee_agent.employee_profiles(conversation_id);

CREATE INDEX idx_employee_profiles_status
  ON employee_agent.employee_profiles(conversation_status);

CREATE INDEX idx_employee_profiles_bench_status
  ON employee_agent.employee_profiles(bench_status);

CREATE INDEX idx_employee_profiles_career_track
  ON employee_agent.employee_profiles(career_track);

CREATE INDEX idx_employee_profiles_completeness
  ON employee_agent.employee_profiles(profile_completeness_score);

CREATE INDEX idx_employee_conversation_messages_conversation_id
  ON employee_agent.employee_conversation_messages(conversation_id);

CREATE INDEX idx_employee_conversation_messages_created_at
  ON employee_agent.employee_conversation_messages(created_at);

CREATE INDEX idx_employee_extraction_history_conversation_id
  ON employee_agent.employee_extraction_history(conversation_id);
