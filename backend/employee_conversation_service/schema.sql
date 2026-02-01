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
