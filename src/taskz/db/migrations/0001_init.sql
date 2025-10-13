-- Core schema: expenses, receipts, rules, renames, file hashes

CREATE TABLE IF NOT EXISTS expense (
  id INTEGER PRIMARY KEY,
  date TEXT NOT NULL,
  merchant TEXT NOT NULL,
  category TEXT,
  description TEXT,
  amount_net REAL,
  tax REAL DEFAULT 0,
  amount_gross REAL NOT NULL,
  currency TEXT NOT NULL,
  payment_method TEXT,
  tags_csv TEXT,
  source TEXT,
  source_id TEXT,
  receipt_id INTEGER,
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (receipt_id) REFERENCES receipt(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS line_item (
  id INTEGER PRIMARY KEY,
  expense_id INTEGER NOT NULL,
  name TEXT NOT NULL,
  quantity REAL DEFAULT 1,
  unit_price REAL,
  line_total REAL,
  FOREIGN KEY (expense_id) REFERENCES expense(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS receipt (
  id INTEGER PRIMARY KEY,
  source_type TEXT NOT NULL,
  source_path_or_url TEXT NOT NULL,
  content_hash TEXT NOT NULL,
  raw_text TEXT,
  parsed_ok INTEGER DEFAULT 0,
  parsed_at TEXT,
  vendor TEXT,
  meta_json TEXT
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_receipt_hash ON receipt(content_hash);

CREATE TABLE IF NOT EXISTS rule (
  id INTEGER PRIMARY KEY,
  target_field TEXT NOT NULL,
  pattern TEXT NOT NULL,
  action TEXT NOT NULL, -- 'set'
  value TEXT NOT NULL,
  priority INTEGER DEFAULT 100,
  enabled INTEGER DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_rule_prio ON rule(priority);

CREATE TABLE IF NOT EXISTS rename_op (
  id INTEGER PRIMARY KEY,
  batch_id TEXT NOT NULL,
  src_path TEXT NOT NULL,
  dest_path TEXT NOT NULL,
  file_hash TEXT,
  executed_at TEXT DEFAULT (datetime('now')),
  reverted INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS file_hash (
  path TEXT PRIMARY KEY,
  algo TEXT NOT NULL,
  hash TEXT NOT NULL,
  size INTEGER,
  mtime REAL
);