-- Schema for bank statements API
-- Single table normalized for simplicity
CREATE TABLE IF NOT EXISTS transactions (
    id           SERIAL PRIMARY KEY,
    date         DATE,
    description  TEXT,
    withdrawal   NUMERIC,
    deposit      NUMERIC,
    category     TEXT,
    sub_category TEXT,
    currency     TEXT,
    bank         TEXT
);
