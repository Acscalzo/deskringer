-- Add customer portal fields to customers and calls tables

-- Add password and last_login to customers table
ALTER TABLE customers
ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255),
ADD COLUMN IF NOT EXISTS last_login TIMESTAMP;

-- Add handled tracking to calls table
ALTER TABLE calls
ADD COLUMN IF NOT EXISTS handled BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS handled_at TIMESTAMP;

-- Create index for better query performance
CREATE INDEX IF NOT EXISTS idx_calls_handled ON calls(handled);
CREATE INDEX IF NOT EXISTS idx_calls_customer_created ON calls(customer_id, created_at DESC);
