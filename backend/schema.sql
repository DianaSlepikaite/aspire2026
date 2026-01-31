-- Database schema for Client Need Service Agent
-- Run this script in your PostgreSQL database

CREATE SCHEMA IF NOT EXISTS client_agent;

CREATE TABLE client_agent.client_needs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  conversation_id UUID UNIQUE NOT NULL,

  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),

  -- Conversation state
  conversation_status conversation_status DEFAULT 'in_progress',
  total_messages INTEGER DEFAULT 0,
  conversation_started_at TIMESTAMPTZ DEFAULT now(),
  conversation_completed_at TIMESTAMPTZ,

  -- Client info
  client_name VARCHAR,
  client_email VARCHAR,
  client_phone VARCHAR,
  client_company VARCHAR,

  -- Project info
  project_title VARCHAR,
  project_description TEXT,
  project_type VARCHAR,
  industry VARCHAR,

  -- Skills
  required_skills JSONB,
  preferred_skills JSONB,
  skill_level VARCHAR,
  certifications_required JSONB,

  -- Budget
  budget_min NUMERIC,
  budget_max NUMERIC,
  budget_currency VARCHAR DEFAULT 'USD',
  budget_type VARCHAR,

  -- Timeline
  timeline_start_date DATE,
  timeline_end_date DATE,
  timeline_duration_weeks INTEGER,
  timeline_flexibility VARCHAR,

  -- Priority
  urgency_level VARCHAR,
  priority_score INTEGER CHECK (priority_score BETWEEN 1 AND 10),
  start_date_importance VARCHAR,

  -- Work setup
  work_location VARCHAR,
  work_location_details JSONB,
  work_hours_requirement VARCHAR,

  -- Additional requirements
  team_size_needed INTEGER,
  collaboration_tools JSONB,
  communication_preferences JSONB,

  -- AI insights
  needs_summary TEXT,
  key_challenges JSONB,
  success_criteria JSONB,
  risk_factors JSONB,

  -- Extraction quality
  extraction_confidence NUMERIC,
  missing_information JSONB,
  profile_completeness_score INTEGER
    DEFAULT 0 CHECK (profile_completeness_score BETWEEN 0 AND 100),

  -- Raw data
  conversation_transcript JSONB,
  raw_audio_references JSONB,

  -- Metadata
  source_channel VARCHAR DEFAULT 'web',
  language VARCHAR DEFAULT 'en',
  tags JSONB,
  notes TEXT
);
