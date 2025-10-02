-- DDL Script: Create Diary Table
-- Created: 2024-01-03
-- Database: PostgreSQL
-- 
-- This script creates a diary table with primary key and timestamp fields
-- Additional fields are included for a complete diary entry structure

-- Drop table if exists (for development/testing purposes)
DROP TABLE IF EXISTS diary CASCADE;

-- Create diary table
CREATE TABLE diary (
    -- Primary key field
    id SERIAL PRIMARY KEY,
    
    -- Timestamp field for when the entry was created
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Additional useful diary fields
    title VARCHAR(255) NOT NULL,
    content TEXT,
    mood VARCHAR(50),
    tags TEXT[],
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT diary_title_not_empty CHECK (LENGTH(TRIM(title)) > 0)
);

-- Create indexes for better performance
CREATE INDEX idx_diary_created_at ON diary(created_at);
CREATE INDEX idx_diary_updated_at ON diary(updated_at);
CREATE INDEX idx_diary_mood ON diary(mood);

-- Create trigger to automatically update the updated_at field
CREATE OR REPLACE FUNCTION update_diary_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_diary_updated_at
    BEFORE UPDATE ON diary
    FOR EACH ROW
    EXECUTE FUNCTION update_diary_updated_at();

-- Add comments for documentation
COMMENT ON TABLE diary IS 'Table to store diary entries with timestamps and metadata';
COMMENT ON COLUMN diary.id IS 'Primary key - auto-incrementing integer';
COMMENT ON COLUMN diary.created_at IS 'Timestamp when the diary entry was first created';
COMMENT ON COLUMN diary.title IS 'Title of the diary entry (required)';
COMMENT ON COLUMN diary.content IS 'Main content/body of the diary entry';
COMMENT ON COLUMN diary.mood IS 'Optional mood indicator for the entry';
COMMENT ON COLUMN diary.tags IS 'Array of tags associated with the entry';
COMMENT ON COLUMN diary.updated_at IS 'Timestamp when the diary entry was last modified';

-- Insert sample data (optional - remove if not needed)
INSERT INTO diary (title, content, mood, tags) VALUES 
    ('First Entry', 'This is my first diary entry!', 'excited', ARRAY['first', 'milestone']),
    ('Daily Reflection', 'Today was a productive day. I learned something new.', 'content', ARRAY['reflection', 'learning']);

-- Display table structure
\d diary;

-- Show sample data
SELECT * FROM diary ORDER BY created_at DESC;
