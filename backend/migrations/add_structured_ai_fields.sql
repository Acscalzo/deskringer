-- Add structured AI configuration fields to customers table

-- Add new fields for easier AI customization
ALTER TABLE customers
ADD COLUMN IF NOT EXISTS services_offered TEXT,
ADD COLUMN IF NOT EXISTS faqs JSON,
ADD COLUMN IF NOT EXISTS appointment_handling VARCHAR(50) DEFAULT 'collect_details',
ADD COLUMN IF NOT EXISTS pricing_info TEXT,
ADD COLUMN IF NOT EXISTS special_instructions TEXT,
ADD COLUMN IF NOT EXISTS holiday_hours TEXT;

-- No indexes needed for these fields as they're not frequently queried
