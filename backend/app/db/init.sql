-- FinSense AI – Database Initialisation Script
-- Runs automatically on first Docker Compose startup

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id               SERIAL PRIMARY KEY,
    email            VARCHAR(255) UNIQUE NOT NULL,
    username         VARCHAR(100) UNIQUE NOT NULL,
    full_name        VARCHAR(200),
    hashed_password  VARCHAR(255) NOT NULL,
    is_active        BOOLEAN DEFAULT TRUE,
    created_at       TIMESTAMP DEFAULT NOW(),
    updated_at       TIMESTAMP DEFAULT NOW()
);

-- Expenses table
CREATE TABLE IF NOT EXISTS expenses (
    id                    SERIAL PRIMARY KEY,
    user_id               INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount                NUMERIC(12, 2) NOT NULL CHECK (amount > 0),
    date                  DATE NOT NULL,
    merchant_name         VARCHAR(255) NOT NULL,
    description           VARCHAR(500),
    payment_mode          VARCHAR(50) DEFAULT 'UPI',
    category              VARCHAR(100) NOT NULL DEFAULT 'Miscellaneous',
    category_confidence   NUMERIC(5, 4) DEFAULT 1.0,
    notes                 TEXT,
    created_at            TIMESTAMP DEFAULT NOW(),
    updated_at            TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_expenses_user_id ON expenses(user_id);
CREATE INDEX IF NOT EXISTS idx_expenses_date    ON expenses(date);
CREATE INDEX IF NOT EXISTS idx_expenses_category ON expenses(category);

-- Budgets table
CREATE TABLE IF NOT EXISTS budgets (
    id                SERIAL PRIMARY KEY,
    user_id           INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    month             VARCHAR(7) NOT NULL,   -- YYYY-MM
    category          VARCHAR(100) NOT NULL,
    allocated_amount  NUMERIC(12, 2) NOT NULL CHECK (allocated_amount > 0),
    spent_amount      NUMERIC(12, 2) DEFAULT 0.0,
    created_at        TIMESTAMP DEFAULT NOW(),
    updated_at        TIMESTAMP DEFAULT NOW(),
    UNIQUE (user_id, month, category)
);
CREATE INDEX IF NOT EXISTS idx_budgets_user_month ON budgets(user_id, month);

-- Financial health scores table
CREATE TABLE IF NOT EXISTS financial_scores (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    month       VARCHAR(7) NOT NULL,
    score       NUMERIC(5, 2) NOT NULL CHECK (score >= 0 AND score <= 100),
    breakdown   JSONB,
    explanation VARCHAR(1000),
    created_at  TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_scores_user_month ON financial_scores(user_id, month);
