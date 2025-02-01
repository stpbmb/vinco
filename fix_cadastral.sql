-- First, update any NULL values to empty string
UPDATE vineyards_vineyard SET cadastral_county = '' WHERE cadastral_county IS NULL;

-- Then allow NULL values
ALTER TABLE vineyards_vineyard ALTER COLUMN cadastral_county DROP NOT NULL;
