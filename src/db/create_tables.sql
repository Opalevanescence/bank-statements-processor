CREATE TABLE transactions (
    id               SERIAL PRIMARY KEY,
    date             DATE,
    description      TEXT,
    withdrawal       NUMERIC,
    deposit          NUMERIC,
    sub_category_id  TEXT,
    currency         TEXT,
    bank             TEXT,
);

CREATE TABLE sub_categories (
    id          SERIAL PRIMARY KEY,
    name        TEXT,
    category_id NUMERIC,
)

CREATE TABLE categories (
    id    SERIAL PRIMARY KEY,
    name  TEXT,
)

CREATE TABLE keywords (
    id          SERIAL PRIMARY KEY,
    name        TEXT,
    sub_category_id NUMERIC,
)
