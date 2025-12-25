-- =======================================================
-- Telegram Course Sales Bot - Database Schema (PostgreSQL)
-- Tables: courses, orders, wishlist
-- Safe to run multiple times (uses IF NOT EXISTS)
-- =======================================================

-- Enable UUIDs if you ever want them later (optional)
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================
-- TABLE: courses
-- =====================

CREATE TABLE IF NOT EXISTS courses (
    id              SERIAL PRIMARY KEY,
    title           VARCHAR(150) NOT NULL,
    description     TEXT NOT NULL,
    category        VARCHAR(100),
    price           NUMERIC(10, 2) NOT NULL CHECK (price >= 0),

    -- Telegram / media fields
    demo_video_id   TEXT,
    ai_caption      TEXT,
    channel_post_id BIGINT,

    -- Social proof
    rating          NUMERIC(3, 2) DEFAULT 0 CHECK (rating >= 0 AND rating <= 5),
    reviews         INTEGER       DEFAULT 0 CHECK (reviews >= 0),

    -- Timestamps
    created_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);

-- Helpful indexes for courses
CREATE INDEX IF NOT EXISTS idx_courses_created_at
    ON courses (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_courses_category_created_at
    ON courses (category, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_courses_deleted_at
    ON courses (deleted_at);


-- =====================
-- TABLE: orders
-- =====================

CREATE TABLE IF NOT EXISTS orders (
    id              SERIAL PRIMARY KEY,
    user_id         BIGINT       NOT NULL,              -- Telegram user id
    user_name       TEXT,                               -- Telegram full name or username
    course_id       INTEGER      NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    price           NUMERIC(10, 2) NOT NULL CHECK (price >= 0),

    payment_status  VARCHAR(20)  NOT NULL DEFAULT 'pending',  -- pending, completed, failed
    transaction_id  TEXT,

    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- Common lookups on orders
CREATE INDEX IF NOT EXISTS idx_orders_user_id_created_at
    ON orders (user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_orders_course_id_status
    ON orders (course_id, payment_status);

CREATE INDEX IF NOT EXISTS idx_orders_payment_status_created_at
    ON orders (payment_status, created_at DESC);


-- =====================
-- TABLE: wishlist
-- =====================

CREATE TABLE IF NOT EXISTS wishlist (
    id          SERIAL PRIMARY KEY,
    user_id     BIGINT    NOT NULL,
    course_id   INTEGER   NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uniq_wishlist_user_course
        UNIQUE (user_id, course_id)
);

CREATE INDEX IF NOT EXISTS idx_wishlist_user_id
    ON wishlist (user_id);

CREATE INDEX IF NOT EXISTS idx_wishlist_course_id
    ON wishlist (course_id);


-- =====================
-- TRIGGERS: updated_at
-- =====================

-- Generic function to auto-update updated_at
CREATE OR REPLACE FUNCTION set_updated_at_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for courses
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_trigger
        WHERE tgname = 'trg_set_courses_updated_at'
    ) THEN
        CREATE TRIGGER trg_set_courses_updated_at
        BEFORE UPDATE ON courses
        FOR EACH ROW
        EXECUTE FUNCTION set_updated_at_timestamp();
    END IF;
END;
$$;

-- Trigger for orders
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_trigger
        WHERE tgname = 'trg_set_orders_updated_at'
    ) THEN
        CREATE TRIGGER trg_set_orders_updated_at
        BEFORE UPDATE ON orders
        FOR EACH ROW
        EXECUTE FUNCTION set_updated_at_timestamp();
    END IF;
END;
$$;

-- =======================================================
-- END OF SCHEMA
-- =======================================================
