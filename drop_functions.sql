-- Step 1: Drop all existing functions
-- Run this FIRST, then run database_migration.sql

-- Drop functions without specifying parameters (drops all overloads)
DROP FUNCTION IF EXISTS match_movies CASCADE;
DROP FUNCTION IF EXISTS match_books CASCADE;
DROP FUNCTION IF EXISTS get_popular_items CASCADE;
DROP FUNCTION IF EXISTS get_collaborative_recommendations CASCADE;

-- Verify functions are dropped
SELECT 'Functions dropped successfully' as status;
