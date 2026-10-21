-- QA Studio — SQLite schema (v1)

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS pipeline_run (
  id TEXT PRIMARY KEY,
  label TEXT NOT NULL,
  trigger_type TEXT NOT NULL CHECK (trigger_type IN ('reviewer_folder', 'jql', 'url', 'epic_key')),
  trigger_value TEXT NOT NULL,
  source_path TEXT,
  product_id TEXT,
  operator_id TEXT,
  operator_name TEXT,
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'archived')),
  creator_handoff_json TEXT,
  coverage_profile TEXT NOT NULL DEFAULT 'balanced',
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
  coverage_profile TEXT,
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
  automation_fit TEXT CHECK (automation_fit IS NULL OR automation_fit IN ('full', 'partial', 'manual_only')),
  marked_for_xray_import INTEGER NOT NULL DEFAULT 0,
  current_revision_id INTEGER,
  xray_test_key TEXT,
  import_status TEXT,
  rejection_reason TEXT,
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

CREATE TABLE IF NOT EXISTS telemetry_outbox (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  event_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  sent_at TEXT,
  last_error TEXT
);

CREATE INDEX IF NOT EXISTS idx_review_unit_run ON review_unit(pipeline_run_id);
CREATE INDEX IF NOT EXISTS idx_revision_unit ON review_payload_revision(review_unit_id);
CREATE INDEX IF NOT EXISTS idx_metric_run ON metric_event(pipeline_run_id);
CREATE INDEX IF NOT EXISTS idx_test_case_creator ON test_case_row(creator_run_id);

CREATE TABLE IF NOT EXISTS cursor_usage_event (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  pipeline_run_id TEXT,
  creator_run_id TEXT,
  stage TEXT NOT NULL,
  conversation_id TEXT,
  generation_id TEXT,
  model TEXT,
  model_id TEXT,
  duration_ms INTEGER,
  status TEXT,
  input_tokens INTEGER,
  output_tokens INTEGER,
  cache_read_tokens INTEGER,
  cache_write_tokens INTEGER,
  cost_cents INTEGER,
  cost_currency TEXT NOT NULL DEFAULT 'USD',
  source TEXT NOT NULL,
  notes TEXT,
  created_at TEXT NOT NULL,
  billed_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_cursor_usage_pipeline ON cursor_usage_event(pipeline_run_id);
CREATE INDEX IF NOT EXISTS idx_cursor_usage_conversation ON cursor_usage_event(conversation_id);

CREATE TABLE IF NOT EXISTS pipeline_run_report (
  pipeline_run_id TEXT PRIMARY KEY REFERENCES pipeline_run(id) ON DELETE CASCADE,
  schema_version INTEGER NOT NULL,
  report_json TEXT NOT NULL,
  computed_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS pipeline_manifest (
  pipeline_run_id TEXT PRIMARY KEY REFERENCES pipeline_run(id) ON DELETE CASCADE,
  manifest_path TEXT NOT NULL,
  manifest_json TEXT NOT NULL,
  payload_set_hash TEXT NOT NULL,
  imported_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS cursor_handoff (
  id TEXT PRIMARY KEY,
  pipeline_run_id TEXT NOT NULL REFERENCES pipeline_run(id) ON DELETE CASCADE,
  stage TEXT NOT NULL CHECK (stage IN ('review', 'creator_draft')),
  epic_key TEXT NOT NULL DEFAULT '',
  prompt_version TEXT NOT NULL,
  prompt_text TEXT NOT NULL,
  prompt_sha256 TEXT NOT NULL,
  coverage_profile TEXT,
  status TEXT NOT NULL CHECK (status IN (
    'awaiting_cursor', 'output_detected', 'invalid_output', 'imported', 'stale_output'
  )),
  expected_paths_json TEXT NOT NULL,
  expected_hashes_json TEXT NOT NULL,
  copied_at TEXT,
  detected_at TEXT,
  imported_at TEXT,
  retry_count INTEGER NOT NULL DEFAULT 0,
  error TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE (pipeline_run_id, stage, epic_key)
);

CREATE INDEX IF NOT EXISTS idx_cursor_handoff_pipeline ON cursor_handoff(pipeline_run_id);

CREATE TABLE IF NOT EXISTS persona_revision (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  filename TEXT NOT NULL,
  content TEXT NOT NULL,
  content_sha256 TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_persona_revision_file ON persona_revision(filename, id DESC);
