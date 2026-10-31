CREATE TABLE IF NOT EXISTS views (
  slug  TEXT PRIMARY KEY,
  count INTEGER NOT NULL DEFAULT 0
);

-- One row per counted visit. Location comes from Cloudflare's IP geolocation;
-- the IP address itself is never stored.
CREATE TABLE IF NOT EXISTS visits (
  id       INTEGER PRIMARY KEY AUTOINCREMENT,
  slug     TEXT NOT NULL,
  lang     TEXT,
  ts       TEXT NOT NULL,
  country  TEXT,
  region   TEXT,
  city     TEXT,
  referrer TEXT
);

CREATE INDEX IF NOT EXISTS idx_visits_ts ON visits (ts);
CREATE INDEX IF NOT EXISTS idx_visits_slug_ts ON visits (slug, ts);
