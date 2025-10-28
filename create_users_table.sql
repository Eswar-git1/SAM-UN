-- Create users table for SAM UN authentication
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on username for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- Enable Row Level Security (optional)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Create a policy to allow service role to manage users
CREATE POLICY IF NOT EXISTS "Service role can manage users" ON users
    FOR ALL USING (auth.role() = 'service_role');

-- Create a policy to allow authenticated users to read their own data
CREATE POLICY IF NOT EXISTS "Users can read own data" ON users
    FOR SELECT USING (auth.uid()::text = id::text);

-- Insert test users
INSERT INTO users (username, password, email, role) VALUES
    ('admin', 'admin123', 'admin@un.org', 'admin'),
    ('analyst', 'analyst123', 'analyst@un.org', 'analyst'),
    ('observer', 'observer123', 'observer@un.org', 'observer')
ON CONFLICT (username) DO NOTHING;