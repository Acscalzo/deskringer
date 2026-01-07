-- Add archived fields to calls table for soft delete functionality

-- Add archived tracking to calls table
ALTER TABLE calls
ADD COLUMN IF NOT EXISTS archived BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS archived_at TIMESTAMP;

-- Create index for better query performance on archived status
CREATE INDEX IF NOT EXISTS idx_calls_archived ON calls(archived);
CREATE INDEX IF NOT EXISTS idx_calls_customer_archived ON calls(customer_id, archived);
