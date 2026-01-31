-- ======================
-- SHARED ENUMS
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
  'senior_associate',
  'manager',
  'senior_manager',
  'associate_director',
  'director',
  'senior_director'
);
