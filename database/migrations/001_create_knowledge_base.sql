-- Knowledge Base Database Schema Migration
-- This migration creates the foundational knowledge base table for the customer support system
-- with support for vector similarity search using the pgvector extension.
--
-- Key Features:
-- - UUID primary keys for globally unique identifiers
-- - Vector embeddings for semantic search capabilities
-- - JSONB metadata for flexible attribute storage
-- - Timestamp tracking for audit and lifecycle management
-- - Category-based organization for content management
-- - Full-text content storage with efficient indexing
--
-- The table is designed to support both traditional keyword search and modern
-- semantic search through vector embeddings, enabling hybrid search approaches
-- that combine the best of both methodologies.

-- Enable the pgvector extension for vector similarity search
-- This extension provides vector data types and similarity functions
-- Required for semantic search capabilities using embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- Create the main knowledge base table with comprehensive schema
-- This table stores all knowledge base entries with their content,
-- metadata, and vector embeddings for semantic search
CREATE TABLE IF NOT EXISTS knowledge_base (
    -- Primary key using UUID for global uniqueness across distributed systems
    -- UUIDs prevent ID collision issues in microservice architectures
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Human-readable title for the knowledge base entry
    -- Used for display purposes and administrative management
    title VARCHAR(255) NOT NULL,
    
    -- Main content of the knowledge base entry
    -- Contains the actual information that will be returned to users
    -- TEXT type allows for large content without length restrictions
    content TEXT NOT NULL,
    
    -- Category classification for organizational structure
    -- Enables filtering and organization of knowledge base entries
    -- Examples: 'technical', 'billing', 'general', 'troubleshooting'
    category VARCHAR(100),
    
    -- Vector embedding for semantic similarity search
    -- 1536 dimensions matches OpenAI's text-embedding-3-small model
    -- Enables finding semantically similar content even without keyword matches
    embedding vector(1536) NOT NULL,
    
    -- Flexible metadata storage in JSON format
    -- Allows for extensible attributes without schema changes
    -- Examples: tags, difficulty_level, source, author, version
    metadata JSON,
    
    -- Timestamp for creation tracking
    -- Automatically set to current time when record is created
    -- Useful for analytics, auditing, and content management
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Timestamp for modification tracking
    -- Must be manually updated when content changes
    -- Enables change tracking and cache invalidation
    updated_at TIMESTAMPTZ
); 