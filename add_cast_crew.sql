-- Add cast and crew columns to movies table
-- Run this in Supabase SQL Editor

-- Add new columns for cast and crew (cast is a reserved keyword, so we quote it)
ALTER TABLE movies 
ADD COLUMN IF NOT EXISTS "cast" JSONB,
ADD COLUMN IF NOT EXISTS crew JSONB,
ADD COLUMN IF NOT EXISTS director TEXT,
ADD COLUMN IF NOT EXISTS genres TEXT[];

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_movies_director ON movies(director);
CREATE INDEX IF NOT EXISTS idx_movies_genres ON movies USING GIN(genres);

-- Verify the changes
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'movies' 
AND column_name IN ('cast', 'crew', 'director', 'genres')
ORDER BY ordinal_position;
