-- Part A: Freelance Leads
CREATE TABLE IF NOT EXISTS leads (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  platform TEXT NOT NULL,
  channel TEXT,
  title TEXT,
  body TEXT,
  url TEXT UNIQUE NOT NULL,
  author TEXT,
  posted_at DATETIME,
  scraped_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  score INTEGER,
  service_match TEXT,
  urgency TEXT CHECK (urgency IN ('high', 'medium', 'low')),
  pain_point TEXT,
  pass BOOLEAN DEFAULT 0,
  disqualify_reason TEXT,
  generated_message TEXT,
  status TEXT DEFAULT 'new' CHECK (status IN ('new', 'contacted', 'replied', 'closed')),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_created ON leads(created_at DESC);

-- Part B: Internship / Contract Opportunities
CREATE TABLE IF NOT EXISTS opportunities (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT,
  company TEXT,
  source TEXT,
  url TEXT UNIQUE NOT NULL,
  contact_url TEXT,
  contact_type TEXT,
  stack TEXT,
  description TEXT,
  score INTEGER,
  fit_reason TEXT,
  stack_overlap TEXT, -- JSON string in SQLite
  urgency_signal TEXT,
  pass BOOLEAN DEFAULT 0,
  disqualify_reason TEXT,
  generated_subject TEXT,
  generated_message TEXT,
  status TEXT DEFAULT 'new' CHECK (status IN ('new', 'sent', 'replied', 'closed')),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Part C: Cold Email to Founders (global)
CREATE TABLE IF NOT EXISTS cold_emails (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  founder_name TEXT,
  company_name TEXT,
  company_url TEXT,
  email TEXT,
  tech_stack TEXT,
  company_size TEXT,
  activity_signal TEXT,
  score INTEGER,
  fit_reason TEXT,
  generated_subject TEXT,
  generated_message TEXT,
  status TEXT DEFAULT 'new' CHECK (status IN ('new', 'sent', 'replied', 'closed', 'interested')),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Part D: Hyderabad Stealth Hunter
CREATE TABLE IF NOT EXISTS hyderabad_startups (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  company_name TEXT NOT NULL,
  founder_name TEXT,
  source TEXT NOT NULL,          -- thub | github | yourstory | inc42 | product_hunt | domain
  company_url TEXT UNIQUE NOT NULL,
  github_url TEXT,
  email TEXT,
  tech_stack TEXT,               -- JSON string array
  company_size TEXT,
  description TEXT,
  last_activity DATETIME,
  activity_signal TEXT,
  score INTEGER,
  fit_reason TEXT,
  stack_overlap TEXT,            -- JSON string array
  disqualify_reason TEXT,
  pass BOOLEAN DEFAULT 0,
  generated_subject TEXT,
  generated_message TEXT,
  status TEXT DEFAULT 'new' CHECK (status IN ('new', 'drafted', 'sent', 'replied', 'closed', 'interested')),
  notes TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_hyd_status ON hyderabad_startups(status);
CREATE INDEX IF NOT EXISTS idx_hyd_source ON hyderabad_startups(source);
CREATE INDEX IF NOT EXISTS idx_hyd_score ON hyderabad_startups(score DESC);

-- Scan history
CREATE TABLE IF NOT EXISTS scans (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  type TEXT NOT NULL,            -- 'freelance' | 'internship' | 'cold_email' | 'hyderabad'
  started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  finished_at DATETIME,
  items_found INTEGER DEFAULT 0,
  items_passed INTEGER DEFAULT 0,
  error_message TEXT
);
