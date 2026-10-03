CREATE TABLE IF NOT EXISTS events (event_id TEXT PRIMARY KEY,timestamp TEXT NOT NULL,source TEXT NOT NULL,event_type TEXT NOT NULL,severity TEXT NOT NULL,raw_json TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS alerts (alert_id TEXT PRIMARY KEY,event_id TEXT,rule_id TEXT,severity TEXT NOT NULL,status TEXT NOT NULL,evidence_json TEXT);
