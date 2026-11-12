-- Expand step (APP-14): additive only, so the running release works unchanged against it.
-- A drop, rename, or NOT NULL goes in a later contract migration, released after the old code retires.
CREATE TABLE IF NOT EXISTS {{aggregate_table}} (
  id TEXT PRIMARY KEY,
  status TEXT NOT NULL,
  attachment_object TEXT NULL -- Cloud Storage object reference; the file itself is never in Cloud SQL (§3.5)
);
