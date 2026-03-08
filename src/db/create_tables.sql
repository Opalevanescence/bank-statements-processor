-- Schema for bank statements API
CREATE TABLE IF NOT EXISTS banks (
    id       SERIAL PRIMARY KEY,
    name     TEXT UNIQUE,
    currency TEXT
);

CREATE TABLE IF NOT EXISTS categories (
    id           SERIAL PRIMARY KEY,
    sub_category TEXT,
    category     TEXT,
    UNIQUE (category, sub_category)
);

CREATE TABLE IF NOT EXISTS transactions (
    id              SERIAL PRIMARY KEY,
    date            DATE,
    description     TEXT,
    withdrawal      NUMERIC,
    deposit         NUMERIC,
    sub_category_id INTEGER REFERENCES categories(id),
    bank_id         INTEGER REFERENCES banks(id)
);
