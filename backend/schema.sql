-- Database schema for Client Need Service Agent
-- Run this script in your Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table: client_needs
CREATE TABLE IF NOT EXISTS client_needs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Conversation Metadata
    conversation_id UUID NOT NULL UNIQUE,
    conversation_status VARCHAR(50) DEFAULT 'in_progress', -- in_progress, completed, abandoned
    total_messages INTEGER DEFAULT 0,
    conversation_started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    conversation_completed_at TIMESTAMP WITH TIME ZONE,

    -- Client Information
    client_name VARCHAR(255),
    client_email VARCHAR(255),
    client_phone VARCHAR(50),
    client_company VARCHAR(255),

    -- Project Details
    project_title VARCHAR(500),
    project_description TEXT,
    project_type VARCHAR(100), -- web_development, mobile_app, data_analytics, etc.
    industry VARCHAR(100),

    -- Skills and Requirements (JSONB for flexibility)
    required_skills JSONB,
    preferred_skills JSONB,
    skill_level VARCHAR(50), -- junior, mid, senior, expert
    certifications_required JSONB,

    -- Budget
    budget_min DECIMAL(12, 2),
    budget_max DECIMAL(12, 2),
    budget_currency VARCHAR(10) DEFAULT 'USD',
    budget_type VARCHAR(50), -- hourly, fixed, monthly

    -- Timeline
    timeline_start_date DATE,
    timeline_end_date DATE,
    timeline_duration_weeks INTEGER,
    timeline_flexibility VARCHAR(50), -- flexible, somewhat_flexible, strict

    -- Urgency and Priority
    urgency_level VARCHAR(50), -- low, medium, high, critical
    priority_score INTEGER CHECK (priority_score BETWEEN 1 AND 10),
    start_date_importance VARCHAR(50), -- flexible, preferred, mandatory

    -- Work Arrangement
    work_location VARCHAR(100), -- remote, onsite, hybrid
    work_location_details JSONB, -- {"city": "New York", "country": "USA", "timezone": "EST"}
    work_hours_requirement VARCHAR(100), -- flexible, business_hours, overlap_required

    -- Additional Requirements
    team_size_needed INTEGER,
    collaboration_tools JSONB, -- ["Slack", "Jira", "GitHub", ...]
    communication_preferences JSONB,

    -- AI-Generated Insights
    needs_summary TEXT,
    key_challenges JSONB,
    success_criteria JSONB,
    risk_factors JSONB,

    -- Profile Completeness
    extraction_confidence DECIMAL(3, 2), -- 0.00 to 1.00
    missing_information JSONB, -- ["budget", "timeline", ...]
    profile_completeness_score INTEGER CHECK (profile_completeness_score BETWEEN 0 AND 100) DEFAULT 0,

    -- Raw Conversation Data
    conversation_transcript JSONB, -- Array of message objects
    raw_audio_references JSONB, -- References to audio files if stored

    -- Metadata
    source_channel VARCHAR(50) DEFAULT 'web', -- web, mobile, api
    language VARCHAR(10) DEFAULT 'en',
    tags JSONB,
    notes TEXT,

    -- Search and Indexing
    search_vector tsvector GENERATED ALWAYS AS (
        to_tsvector('english',
            COALESCE(project_title, '') || ' ' ||
            COALESCE(project_description, '') || ' ' ||
            COALESCE(needs_summary, '')
        )
    ) STORED
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_client_needs_conversation_id ON client_needs(conversation_id);
CREATE INDEX IF NOT EXISTS idx_client_needs_status ON client_needs(conversation_status);
CREATE INDEX IF NOT EXISTS idx_client_needs_created_at ON client_needs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_client_needs_urgency ON client_needs(urgency_level);
CREATE INDEX IF NOT EXISTS idx_client_needs_search_vector ON client_needs USING GIN(search_vector);
CREATE INDEX IF NOT EXISTS idx_client_needs_skills ON client_needs USING GIN(required_skills);

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_client_needs_updated_at
BEFORE UPDATE ON client_needs
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Table: conversation_messages
CREATE TABLE IF NOT EXISTS conversation_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    role VARCHAR(50) NOT NULL, -- user, assistant, system
    content TEXT NOT NULL,
    message_type VARCHAR(50) DEFAULT 'text', -- text, speech, system

    -- Speech-specific fields
    audio_url TEXT,
    audio_duration_seconds DECIMAL(8, 2),
    transcription_confidence DECIMAL(3, 2),

    -- Metadata
    tokens_used INTEGER,
    model_version VARCHAR(100),
    processing_time_ms INTEGER,

    CONSTRAINT fk_conversation
        FOREIGN KEY (conversation_id)
        REFERENCES client_needs(conversation_id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_conversation_messages_conversation_id ON conversation_messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_conversation_messages_created_at ON conversation_messages(created_at);

-- Table: extraction_history (tracks incremental extraction)
CREATE TABLE IF NOT EXISTS extraction_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    extracted_field VARCHAR(100) NOT NULL,
    extracted_value JSONB NOT NULL,
    confidence_score DECIMAL(3, 2),
    extraction_method VARCHAR(50), -- direct_question, inference, clarification

    CONSTRAINT fk_extraction_conversation
        FOREIGN KEY (conversation_id)
        REFERENCES client_needs(conversation_id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_extraction_history_conversation_id ON extraction_history(conversation_id);
CREATE INDEX IF NOT EXISTS idx_extraction_history_created_at ON extraction_history(created_at);

-- Enable Row Level Security (optional, for production)
-- ALTER TABLE client_needs ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE conversation_messages ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE extraction_history ENABLE ROW LEVEL SECURITY;

-- Create policies as needed for your security requirements
-- Example policy (customize based on your auth setup):
-- CREATE POLICY "Enable read access for authenticated users" ON client_needs
--     FOR SELECT USING (auth.role() = 'authenticated');
