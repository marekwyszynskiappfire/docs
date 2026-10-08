-- QA Studio — SQLite schema (v1)

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS pipeline_run (
  id TEXT PRIMARY KEY,
  label TEXT NOT NULL,
  trigger_type TEXT NOT NULL CHECK (trigger_type IN ('reviewer_folder', 'jql', 'url', 'epic_key')),
  trigger_value TEXT NOT NULL,
  source_path TEXT,
  product_id TEXT,
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'archived')),
  creator_handoff_json TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS review_unit (
  id TEXT PRIMARY KEY,
  pipeline_run_id TEXT NOT NULL REFERENCES pipeline_run(id) ON DELETE CASCADE,
  jira_key TEXT NOT NULL,
  scope_type TEXT,
  summary TEXT,
  gate_status TEXT,
  qa_planning_fit TEXT,
  approved_revision_id INTEGER,
  include_in_creator INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE (pipeline_run_id, jira_key)
);

CREATE TABLE IF NOT EXISTS review_payload_revision (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  review_unit_id TEXT NOT NULL REFERENCES review_unit(id) ON DELETE CASCADE,
  revision INTEGER NOT NULL,
  payload_json TEXT NOT NULL,
  source TEXT NOT NULL CHECK (source IN ('agent', 'human', 'import')),
  created_at TEXT NOT NULL,
  created_by TEXT,
  UNIQUE (review_unit_id, revision)
);

CREATE TABLE IF NOT EXISTS creator_run (
  id TEXT PRIMARY KEY,
  pipeline_run_id TEXT REFERENCES pipeline_run(id) ON DELETE SET NULL,
  review_unit_id TEXT REFERENCES review_unit(id) ON DELETE SET NULL,
  label TEXT NOT NULL,
  source_path TEXT,
  status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'in_review', 'approved', 'imported')),
  approved_revision_id INTEGER,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS test_case_batch_revision (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  creator_run_id TEXT NOT NULL REFERENCES creator_run(id) ON DELETE CASCADE,
  revision INTEGER NOT NULL,
  batch_json TEXT NOT NULL,
  source TEXT NOT NULL CHECK (source IN ('agent', 'human', 'import')),
  created_at TEXT NOT NULL,
  created_by TEXT,
  UNIQUE (creator_run_id, revision)
);

CREATE TABLE IF NOT EXISTS test_case_row (
  id TEXT PRIMARY KEY,
  creator_run_id TEXT NOT NULL REFERENCES creator_run(id) ON DELETE CASCADE,
  draft_id TEXT NOT NULL,
  title TEXT NOT NULL,
  execution_tier TEXT,
  test_type TEXT,
  human_review_status TEXT NOT NULL DEFAULT 'pending'
    CHECK (human_review_status IN ('pending', 'edited', 'approved', 'rejected')),
  automation_candidate INTEGER,
  current_revision_id INTEGER,
  xray_test_key TEXT,
  import_status TEXT,
  updated_at TEXT NOT NULL,
  UNIQUE (creator_run_id, draft_id)
);

CREATE TABLE IF NOT EXISTS test_case_revision (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  test_case_row_id TEXT NOT NULL REFERENCES test_case_row(id) ON DELETE CASCADE,
  revision INTEGER NOT NULL,
  case_json TEXT NOT NULL,
  source TEXT NOT NULL CHECK (source IN ('agent', 'human', 'import')),
  created_at TEXT NOT NULL,
  created_by TEXT,
  UNIQUE (test_case_row_id, revision)
);

CREATE TABLE IF NOT EXISTS metric_event (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  pipeline_run_id TEXT,
  entity_type TEXT NOT NULL,
  entity_id TEXT,
  event_type TEXT NOT NULL,
  payload_json TEXT,
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_review_unit_run ON review_unit(pipeline_run_id);
CREATE INDEX IF NOT EXISTS idx_revision_unit ON review_payload_revision(review_unit_id);
CREATE INDEX IF NOT EXISTS idx_metric_run ON metric_event(pipeline_run_id);
CREATE INDEX IF NOT EXISTS idx_test_case_creator ON test_case_row(creator_run_id);
