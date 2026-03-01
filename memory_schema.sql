-- sifiso54 Memory Database Schema
-- SQLite database for persistent agent memory

-- Interactions log: tracks all agent actions
CREATE TABLE IF NOT EXISTS interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    action_type TEXT NOT NULL,          -- e.g., 'comment', 'upvote', 'post', 'solve_math'
    target_id TEXT,                      -- ID of target post/user/challenge
    content TEXT,                        -- Content of interaction (truncated)
    outcome TEXT,                        -- Result of interaction
    sentiment REAL                       -- 0.0 to 1.0 success metric
);

-- Feed items cache: stores browsed content for analysis
CREATE TABLE IF NOT EXISTS feed_items (
    id TEXT PRIMARY KEY,
    author TEXT,
    content TEXT,
    upvotes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    timestamp TEXT,
    analyzed BOOLEAN DEFAULT 0           -- Whether content has been analyzed
);

-- Learning insights: accumulated knowledge from experience
CREATE TABLE IF NOT EXISTS learning (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    insight TEXT NOT NULL,               -- The learned insight
    category TEXT,                       -- e.g., 'performance', 'pattern', 'strategy'
    applied BOOLEAN DEFAULT 0            -- Whether insight has been applied
);

-- Self-improvement log: tracks behavioral adjustments
CREATE TABLE IF NOT EXISTS self_improvement (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    metric TEXT NOT NULL,                -- e.g., 'comment_probability'
    old_value REAL,
    new_value REAL,
    reason TEXT                          -- Why the change was made
);

-- Math challenges: verification challenges solved
CREATE TABLE IF NOT EXISTS math_challenges (
    id TEXT PRIMARY KEY,
    problem TEXT,
    solution REAL,
    solved BOOLEAN DEFAULT 0,
    solved_at TEXT
);

-- Performance metrics: aggregated stats over time
CREATE TABLE IF NOT EXISTS metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT UNIQUE,
    total_interactions INTEGER DEFAULT 0,
    successful_interactions INTEGER DEFAULT 0,
    avg_sentiment REAL,
    posts_created INTEGER DEFAULT 0,
    comments_made INTEGER DEFAULT 0,
    upvotes_given INTEGER DEFAULT 0,
    challenges_solved INTEGER DEFAULT 0
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_interactions_time ON interactions(timestamp);
CREATE INDEX IF NOT EXISTS idx_interactions_type ON interactions(action_type);
CREATE INDEX IF NOT EXISTS idx_feed_analyzed ON feed_items(analyzed);
CREATE INDEX IF NOT EXISTS idx_learning_category ON learning(category);
CREATE INDEX IF NOT EXISTS idx_metrics_date ON metrics(date);

-- Initial data: agent metadata
INSERT OR IGNORE INTO learning (insight, category) VALUES 
    ('sifiso54 initialized with 2000 IQ capabilities', 'initialization'),
    ('Critical voice enabled for all content analysis', 'behavior'),
    ('Self-improvement loop activated', 'system');
