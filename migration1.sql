CREATE TABLE IF NOT EXISTS cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    master_id TEXT,
    slave_id TEXT,
    city TEXT
);