-- Supabase Database Schema for Legal AI Assistant
-- Run this in your Supabase SQL Editor to set up the database

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";  -- For pgvector (semantic search)

-- ============================================
-- STATE LAWS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS state_laws (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    state VARCHAR(2) NOT NULL,
    statute_number VARCHAR(100) NOT NULL,
    title TEXT NOT NULL,
    chapter VARCHAR(100),
    section VARCHAR(100),
    full_text TEXT NOT NULL,
    effective_date DATE,
    last_amended DATE,
    jurisdiction VARCHAR(50) DEFAULT 'state',
    source_url TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    embedding VECTOR(1536)  -- For OpenAI ada-002 embeddings
);

-- Indexes for state_laws
CREATE INDEX IF NOT EXISTS idx_state_laws_state ON state_laws(state);
CREATE INDEX IF NOT EXISTS idx_state_laws_statute_number ON state_laws(statute_number);
CREATE INDEX IF NOT EXISTS idx_state_laws_jurisdiction ON state_laws(jurisdiction);
CREATE INDEX IF NOT EXISTS idx_state_laws_created_at ON state_laws(created_at DESC);

-- Full-text search index
CREATE INDEX IF NOT EXISTS idx_state_laws_full_text ON state_laws USING GIN(to_tsvector('english', full_text));

-- Vector similarity index (for semantic search)
CREATE INDEX IF NOT EXISTS idx_state_laws_embedding ON state_laws
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- Unique constraint to prevent duplicate statutes
CREATE UNIQUE INDEX IF NOT EXISTS idx_state_laws_unique ON state_laws(state, statute_number);

-- ============================================
-- FEDERAL LAWS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS federal_laws (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    usc_title INTEGER,
    section VARCHAR(100),
    title TEXT NOT NULL,
    full_text TEXT NOT NULL,
    effective_date DATE,
    agency VARCHAR(200),
    cfr_reference VARCHAR(100),
    source_url TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    embedding VECTOR(1536)
);

-- Indexes for federal_laws
CREATE INDEX IF NOT EXISTS idx_federal_laws_usc_title ON federal_laws(usc_title);
CREATE INDEX IF NOT EXISTS idx_federal_laws_section ON federal_laws(section);
CREATE INDEX IF NOT EXISTS idx_federal_laws_agency ON federal_laws(agency);
CREATE INDEX IF NOT EXISTS idx_federal_laws_full_text ON federal_laws USING GIN(to_tsvector('english', full_text));
CREATE INDEX IF NOT EXISTS idx_federal_laws_embedding ON federal_laws
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- ============================================
-- CASES TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS cases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_name TEXT NOT NULL,
    citation VARCHAR(200) NOT NULL,
    court VARCHAR(200),
    jurisdiction VARCHAR(100),
    date_decided DATE,
    judges TEXT[],  -- Array of judge names
    docket_number VARCHAR(100),
    opinion_text TEXT NOT NULL,
    opinion_type VARCHAR(50) DEFAULT 'majority',  -- majority, dissent, concurring
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    embedding VECTOR(1536)
);

-- Indexes for cases
CREATE INDEX IF NOT EXISTS idx_cases_citation ON cases(citation);
CREATE INDEX IF NOT EXISTS idx_cases_court ON cases(court);
CREATE INDEX IF NOT EXISTS idx_cases_jurisdiction ON cases(jurisdiction);
CREATE INDEX IF NOT EXISTS idx_cases_date_decided ON cases(date_decided DESC);
CREATE INDEX IF NOT EXISTS idx_cases_opinion_text ON cases USING GIN(to_tsvector('english', opinion_text));
CREATE INDEX IF NOT EXISTS idx_cases_embedding ON cases
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- ============================================
-- LEGAL TERMS (DICTIONARY) TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS legal_terms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    term TEXT NOT NULL UNIQUE,
    definition TEXT NOT NULL,
    jurisdiction VARCHAR(100) DEFAULT 'general',
    source VARCHAR(200),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    embedding VECTOR(1536)
);

-- Indexes for legal_terms
CREATE INDEX IF NOT EXISTS idx_legal_terms_term ON legal_terms(term);
CREATE INDEX IF NOT EXISTS idx_legal_terms_jurisdiction ON legal_terms(jurisdiction);
CREATE INDEX IF NOT EXISTS idx_legal_terms_definition ON legal_terms USING GIN(to_tsvector('english', definition));
CREATE INDEX IF NOT EXISTS idx_legal_terms_embedding ON legal_terms
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- ============================================
-- PRECEDENT RELATIONSHIPS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS precedent_relationships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    citing_case_id UUID REFERENCES cases(id) ON DELETE CASCADE,
    cited_case_id UUID REFERENCES cases(id) ON DELETE CASCADE,
    relationship_type VARCHAR(50),  -- 'followed', 'distinguished', 'overruled', 'cited'
    context TEXT,  -- Brief context of how the case was cited
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for precedent_relationships
CREATE INDEX IF NOT EXISTS idx_precedent_citing ON precedent_relationships(citing_case_id);
CREATE INDEX IF NOT EXISTS idx_precedent_cited ON precedent_relationships(cited_case_id);
CREATE INDEX IF NOT EXISTS idx_precedent_type ON precedent_relationships(relationship_type);

-- ============================================
-- UPDATED_AT TRIGGER
-- ============================================

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to all tables with updated_at
CREATE TRIGGER update_state_laws_updated_at
    BEFORE UPDATE ON state_laws
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_federal_laws_updated_at
    BEFORE UPDATE ON federal_laws
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cases_updated_at
    BEFORE UPDATE ON cases
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_legal_terms_updated_at
    BEFORE UPDATE ON legal_terms
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- HELPER FUNCTIONS
-- ============================================

-- Function to search state laws by similarity
CREATE OR REPLACE FUNCTION search_state_laws_by_vector(
    query_embedding VECTOR(1536),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 10,
    filter_state VARCHAR(2) DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    state VARCHAR(2),
    statute_number VARCHAR(100),
    title TEXT,
    full_text TEXT,
    similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        sl.id,
        sl.state,
        sl.statute_number,
        sl.title,
        sl.full_text,
        1 - (sl.embedding <=> query_embedding) AS similarity
    FROM state_laws sl
    WHERE
        (filter_state IS NULL OR sl.state = filter_state)
        AND (1 - (sl.embedding <=> query_embedding)) > match_threshold
    ORDER BY sl.embedding <=> query_embedding
    LIMIT match_count;
END;
$$ LANGUAGE plpgsql;

-- Function to get database statistics
CREATE OR REPLACE FUNCTION get_database_stats()
RETURNS TABLE (
    table_name TEXT,
    row_count BIGINT,
    total_size TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        t.table_name::TEXT,
        (xpath('/row/cnt/text()', xml_count))[1]::text::bigint AS row_count,
        pg_size_pretty(pg_total_relation_size('"' || t.table_name || '"')) AS total_size
    FROM (
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_type = 'BASE TABLE'
        AND table_name IN ('state_laws', 'federal_laws', 'cases', 'legal_terms')
    ) t
    CROSS JOIN LATERAL (
        SELECT query_to_xml(
            format('SELECT COUNT(*) AS cnt FROM %I', t.table_name),
            false,
            true,
            ''
        ) AS xml_count
    ) x;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================

-- Enable RLS on all tables (optional - uncomment if needed)
-- ALTER TABLE state_laws ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE federal_laws ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE cases ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE legal_terms ENABLE ROW LEVEL SECURITY;

-- Create policies (example - adjust based on your auth requirements)
-- CREATE POLICY "Allow public read access" ON state_laws FOR SELECT USING (true);
-- CREATE POLICY "Allow authenticated insert" ON state_laws FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- ============================================
-- INITIAL DATA / REFERENCE TABLES
-- ============================================

-- US States reference table
CREATE TABLE IF NOT EXISTS us_states (
    code VARCHAR(2) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    capital VARCHAR(100),
    population INTEGER,
    metadata JSONB DEFAULT '{}'
);

-- Insert US states
INSERT INTO us_states (code, name) VALUES
    ('AL', 'Alabama'), ('AK', 'Alaska'), ('AZ', 'Arizona'), ('AR', 'Arkansas'),
    ('CA', 'California'), ('CO', 'Colorado'), ('CT', 'Connecticut'), ('DE', 'Delaware'),
    ('FL', 'Florida'), ('GA', 'Georgia'), ('HI', 'Hawaii'), ('ID', 'Idaho'),
    ('IL', 'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'), ('KS', 'Kansas'),
    ('KY', 'Kentucky'), ('LA', 'Louisiana'), ('ME', 'Maine'), ('MD', 'Maryland'),
    ('MA', 'Massachusetts'), ('MI', 'Michigan'), ('MN', 'Minnesota'), ('MS', 'Mississippi'),
    ('MO', 'Missouri'), ('MT', 'Montana'), ('NE', 'Nebraska'), ('NV', 'Nevada'),
    ('NH', 'New Hampshire'), ('NJ', 'New Jersey'), ('NM', 'New Mexico'), ('NY', 'New York'),
    ('NC', 'North Carolina'), ('ND', 'North Dakota'), ('OH', 'Ohio'), ('OK', 'Oklahoma'),
    ('OR', 'Oregon'), ('PA', 'Pennsylvania'), ('RI', 'Rhode Island'), ('SC', 'South Carolina'),
    ('SD', 'South Dakota'), ('TN', 'Tennessee'), ('TX', 'Texas'), ('UT', 'Utah'),
    ('VT', 'Vermont'), ('VA', 'Virginia'), ('WA', 'Washington'), ('WV', 'West Virginia'),
    ('WI', 'Wisconsin'), ('WY', 'Wyoming'), ('DC', 'District of Columbia')
ON CONFLICT (code) DO NOTHING;

-- ============================================
-- VIEWS
-- ============================================

-- View for recent statutes
CREATE OR REPLACE VIEW recent_state_laws AS
SELECT
    state,
    statute_number,
    title,
    SUBSTRING(full_text, 1, 200) AS preview,
    source_url,
    created_at
FROM state_laws
ORDER BY created_at DESC
LIMIT 100;

-- View for state law counts
CREATE OR REPLACE VIEW state_law_counts AS
SELECT
    sl.state,
    us.name AS state_name,
    COUNT(*) AS statute_count,
    MAX(sl.created_at) AS last_updated
FROM state_laws sl
LEFT JOIN us_states us ON sl.state = us.code
GROUP BY sl.state, us.name
ORDER BY statute_count DESC;

-- ============================================
-- COMMENTS (Documentation)
-- ============================================

COMMENT ON TABLE state_laws IS 'State-level statutes and codes from all 50 US states';
COMMENT ON TABLE federal_laws IS 'Federal statutes, USC, and CFR regulations';
COMMENT ON TABLE cases IS 'Legal case opinions and precedents';
COMMENT ON TABLE legal_terms IS 'Legal dictionary and terminology database';
COMMENT ON TABLE precedent_relationships IS 'Citation graph showing relationships between cases';

COMMENT ON COLUMN state_laws.embedding IS 'Vector embedding for semantic search (1536 dimensions for OpenAI ada-002)';
COMMENT ON COLUMN state_laws.metadata IS 'Additional structured metadata in JSON format';

-- ============================================
-- GRANTS (Optional - adjust based on your setup)
-- ============================================

-- Grant read access to anon users (if building public API)
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO anon;

-- Grant full access to authenticated users
-- GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;

-- ============================================
-- COMPLETION MESSAGE
-- ============================================

DO $$
BEGIN
    RAISE NOTICE '✅ Legal AI Database Schema Created Successfully!';
    RAISE NOTICE 'Tables created: state_laws, federal_laws, cases, legal_terms, precedent_relationships';
    RAISE NOTICE 'Extensions enabled: uuid-ossp, vector (pgvector)';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '  1. Configure your .env file with SUPABASE_URL and SUPABASE_KEY';
    RAISE NOTICE '  2. Run the scraper: python scripts/scrape_laws.py --state CA --test';
    RAISE NOTICE '  3. Upload scraped data to Supabase';
END $$;
