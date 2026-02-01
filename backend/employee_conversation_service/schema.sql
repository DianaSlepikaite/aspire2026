-- Database schema for Employee Conversation Service
-- Run this in your PostgreSQL database (e.g. psql or pgAdmin)
--
-- 1. Create a database (e.g. employee_conversation_db) or use an existing one.
-- 2. Set env for the employee service: DATABASE_URL or DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
--    (default DB_NAME=employee_conversation_db)
-- 3. Run this entire script in that database.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table: employee_documents (uploaded resumes/CVs, etc.)
CREATE TABLE IF NOT EXISTS employee_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    file_name VARCHAR(500),
    mime_type VARCHAR(100),
    raw_text TEXT,
    source VARCHAR(50) DEFAULT 'upload',  -- upload, conversation

    employee_profile_id UUID,  -- linked after extraction
    blob_url TEXT  -- optional: URL to blob storage if binary stored elsewhere
);

CREATE INDEX IF NOT EXISTS idx_employee_documents_profile_id
    ON employee_documents(employee_profile_id);
CREATE INDEX IF NOT EXISTS idx_employee_documents_created_at
    ON employee_documents(created_at DESC);

-- Table: employee_profiles (extracted profile from documents/conversation)
CREATE TABLE IF NOT EXISTS employee_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    document_id UUID REFERENCES employee_documents(id),

    full_name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    summary TEXT,
    experience_years INTEGER,
    skills JSONB,  -- ["Python", "React", ...]
    certifications JSONB,  -- ["AWS", "PMP", ...]
    education JSONB,  -- [{"degree": "...", "school": "...", "year": ...}, ...]
    experience JSONB,  -- [{"title": "...", "company": "...", "years": ...}, ...]
    preferred_roles JSONB,  -- ["developer", "architect", ...]

    profile_completeness_score INTEGER CHECK (profile_completeness_score BETWEEN 0 AND 100) DEFAULT 0,

    source_channel VARCHAR(50) DEFAULT 'document',
    tags JSONB,
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_employee_profiles_document_id
    ON employee_profiles(document_id);
CREATE INDEX IF NOT EXISTS idx_employee_profiles_created_at
    ON employee_profiles(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_employee_profiles_skills
    ON employee_profiles USING GIN(skills);

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION employee_update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_employee_documents_updated_at ON employee_documents;
CREATE TRIGGER update_employee_documents_updated_at
    BEFORE UPDATE ON employee_documents
    FOR EACH ROW EXECUTE PROCEDURE employee_update_updated_at();

DROP TRIGGER IF EXISTS update_employee_profiles_updated_at ON employee_profiles;
CREATE TRIGGER update_employee_profiles_updated_at
    BEFORE UPDATE ON employee_profiles
    FOR EACH ROW EXECUTE PROCEDURE employee_update_updated_at();

-- Table: employee_conversations (conversation sessions for profile building)
CREATE TABLE IF NOT EXISTS employee_conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL UNIQUE,
    employee_profile_id UUID REFERENCES employee_profiles(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    conversation_status VARCHAR(50) DEFAULT 'in_progress',
    total_messages INTEGER DEFAULT 0,
    conversation_started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    conversation_completed_at TIMESTAMP WITH TIME ZONE,
    source_channel VARCHAR(50) DEFAULT 'web'
);

CREATE INDEX IF NOT EXISTS idx_employee_conversations_conversation_id ON employee_conversations(conversation_id);
CREATE INDEX IF NOT EXISTS idx_employee_conversations_profile_id ON employee_conversations(employee_profile_id);
CREATE INDEX IF NOT EXISTS idx_employee_conversations_status ON employee_conversations(conversation_status);

-- Table: employee_conversation_messages
CREATE TABLE IF NOT EXISTS employee_conversation_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES employee_conversations(conversation_id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    message_type VARCHAR(50) DEFAULT 'text'
);

CREATE INDEX IF NOT EXISTS idx_employee_conversation_messages_conversation_id ON employee_conversation_messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_employee_conversation_messages_created_at ON employee_conversation_messages(created_at);

DROP TRIGGER IF EXISTS update_employee_conversations_updated_at ON employee_conversations;
CREATE TRIGGER update_employee_conversations_updated_at
    BEFORE UPDATE ON employee_conversations
    FOR EACH ROW EXECUTE PROCEDURE employee_update_updated_at();
