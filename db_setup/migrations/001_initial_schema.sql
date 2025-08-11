-- Initial database setup with common extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Add your initial schema here
-- Example:
-- CREATE TABLE IF NOT EXISTS "users" (
--     "id" uuid PRIMARY KEY DEFAULT (uuid_generate_v4()),
--     "email" varchar UNIQUE,
--     "created_at" timestamp DEFAULT CURRENT_TIMESTAMP
-- );