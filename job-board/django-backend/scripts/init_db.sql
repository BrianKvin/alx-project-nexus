-- Initialize job board database
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
SELECT 'Job Board Database initialized successfully!' as message;
