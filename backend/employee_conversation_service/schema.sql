-- ============================================
-- Employee Conversation Service Agent Schema
-- Aligned with schemas.py (Pydantic models)
-- ============================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ======================
-- ENUMS
-- ======================

CREATE TYPE conversation_status AS ENUM (
  'in_progress',
  'completed',
  'abandoned'
);

CREATE TYPE bench_status AS ENUM (
  'on_project',
  'on_bench',
  'rolling_off',
  'partially_allocated'
);

CREATE TYPE career_track AS ENUM (
  'engineering',
  'experience_design',
  'product',
  'strategy',
  'data_ai',
  'cloud_infrastructure'
);

CREATE TYPE experience_level AS ENUM (
  'associate',
  'consultant',
  'senior_consultant',
  'manager',
  'senior_manager',
  'associate_director',
  'director',
  'senior_director'
);

CREATE TYPE message_role AS ENUM (
  'user',
  'assistant',
  'system'
);

CREATE TYPE message_type AS ENUM (
  'text',
  'speech',
  'system'
);

-- ======================
-- EMPLOYEE PROFILES
-- ======================

CREATE TABLE IF NOT EXISTS employee_profiles (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  conversation_id UUID UNIQUE NOT NULL,

  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),

  -- Conversation state
  conversation_status conversation_status DEFAULT 'in_progress',
  total_messages INTEGER DEFAULT 0,
  conversation_started_at TIMESTAMPTZ DEFAULT now(),
  conversation_completed_at TIMESTAMPTZ,

  -- Basic info
  employee_id VARCHAR(50),
  employee_name VARCHAR(255),
  employee_email VARCHAR(255),

  -- Location & PS info
  location JSONB,
  career_track career_track,
  experience_level experience_level,
  years_at_ps INTEGER CHECK (years_at_ps >= 0),
  years_total_experience INTEGER CHECK (years_total_experience >= 0),

  -- Assignment / bench
  bench_status bench_status DEFAULT 'on_bench',
  current_assignment JSONB,
  availability_date DATE,

  -- Skills & expertise
  technical_skills JSONB,
  soft_skills JSONB,
  domain_expertise JSONB,
  methodologies JSONB,
  tools_platforms JSONB,

  -- Project history
  project_history JSONB,
  notable_achievements JSONB,

  -- Learning & certs
  training_certifications JSONB,
  current_learning JSONB,

  -- Career goals
  career_goals JSONB,

  -- AI-generated insights
  professional_summary TEXT,
  strengths JSONB,
  areas_for_growth JSONB,

  -- Extraction metrics
  extraction_confidence DECIMAL(3,2),
  profile_completeness_score INTEGER DEFAULT 0 CHECK (profile_completeness_score BETWEEN 0 AND 100),
  missing_information JSONB,

  -- Raw data
  conversation_transcript JSONB,
  raw_audio_references JSONB,

  -- Metadata
  source_channel VARCHAR(50) DEFAULT 'web',
  language VARCHAR(10) DEFAULT 'en',
  notes TEXT
);

-- ======================
-- INDEXES
-- ======================

CREATE INDEX IF NOT EXISTS idx_employee_profiles_conversation_id
  ON employee_profiles(conversation_id);

CREATE INDEX IF NOT EXISTS idx_employee_profiles_status
  ON employee_profiles(conversation_status);

CREATE INDEX IF NOT EXISTS idx_employee_profiles_bench_status
  ON employee_profiles(bench_status);

CREATE INDEX IF NOT EXISTS idx_employee_profiles_experience_level
  ON employee_profiles(experience_level);

CREATE INDEX IF NOT EXISTS idx_employee_profiles_career_track
  ON employee_profiles(career_track);

CREATE INDEX IF NOT EXISTS idx_employee_profiles_created_at
  ON employee_profiles(created_at DESC);

-- ======================
-- UPDATED_AT TRIGGER
-- ======================

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_employee_profiles_updated_at
BEFORE UPDATE ON employee_profiles
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

-- ======================
-- CONVERSATION MESSAGES
-- ======================

CREATE TABLE IF NOT EXISTS employee_conversation_messages (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  conversation_id UUID NOT NULL,

  created_at TIMESTAMPTZ DEFAULT now(),

  role message_role NOT NULL,
  content TEXT NOT NULL,
  message_type message_type DEFAULT 'text',

  audio_url TEXT,
  transcription_confidence DECIMAL(3,2),

  tokens_used INTEGER,
  model_version VARCHAR(100),
  processing_time_ms INTEGER,

  CONSTRAINT fk_conversation_messages
    FOREIGN KEY (conversation_id)
    REFERENCES employee_profiles(conversation_id)
    ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_messages_conversation_id
  ON employee_conversation_messages(conversation_id);

CREATE INDEX IF NOT EXISTS idx_messages_created_at
  ON employee_conversation_messages(created_at);

-- ======================
-- EXTRACTION HISTORY
-- ======================

CREATE TABLE IF NOT EXISTS employee_extraction_history (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  conversation_id UUID NOT NULL,

  created_at TIMESTAMPTZ DEFAULT now(),

  extracted_field VARCHAR(100) NOT NULL,
  extracted_value JSONB NOT NULL,
  confidence_score DECIMAL(3,2),
  extraction_method VARCHAR(50),

  CONSTRAINT fk_extraction_conversation
    FOREIGN KEY (conversation_id)
    REFERENCES employee_profiles(conversation_id)
    ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_extraction_conversation_id
  ON employee_extraction_history(conversation_id);

CREATE INDEX IF NOT EXISTS idx_extraction_created_at
  ON employee_extraction_history(created_at);
