-- 🗄️ TELEGRAM COURSE SALES BOT - DATABASE MIGRATIONS
-- Run these SQL commands to set up your database

-- ============================================================================
-- 📚 COURSES TABLE
-- ============================================================================
-- Stores all course information

CREATE TABLE IF NOT EXISTS courses (
    id              SERIAL PRIMARY KEY,
    title           VARCHAR(255) NOT NULL,
    description     TEXT NOT NULL,
    category        VARCHAR(100),
    price           FLOAT NOT NULL,
    demo_video_id   VARCHAR(255),           -- Telegram file_id
    ai_caption      TEXT,                   -- AI-generated marketing caption
    channel_post_id BIGINT,                 -- Telegram message_id in channel
    rating          FLOAT DEFAULT 5.0,
    reviews         INT DEFAULT 0,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at      TIMESTAMP               -- Soft delete
);

CREATE INDEX idx_courses_category ON courses(category);
CREATE INDEX idx_courses_deleted ON courses(deleted_at);
CREATE INDEX idx_courses_channel_post ON courses(channel_post_id);

-- ============================================================================
-- 📦 ORDERS TABLE
-- ============================================================================
-- Tracks all purchases and payments

CREATE TABLE IF NOT EXISTS orders (
    id              SERIAL PRIMARY KEY,
    user_id         BIGINT NOT NULL,
    user_name       VARCHAR(255),
    course_id       INTEGER REFERENCES courses(id),
    price           FLOAT NOT NULL,
    payment_status  VARCHAR(20) DEFAULT 'pending',  -- pending, completed, failed
    transaction_id  VARCHAR(255),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_orders_course ON orders(course_id);
CREATE INDEX idx_orders_status ON orders(payment_status);
CREATE INDEX idx_orders_user_course ON orders(user_id, course_id);

-- ============================================================================
-- ❤️ WISHLIST TABLE
-- ============================================================================
-- Stores user wishlists

CREATE TABLE IF NOT EXISTS wishlist (
    id              SERIAL PRIMARY KEY,
    user_id         BIGINT NOT NULL,
    course_id       INTEGER REFERENCES courses(id),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, course_id)  -- One entry per user per course
);

CREATE INDEX idx_wishlist_user ON wishlist(user_id);
CREATE INDEX idx_wishlist_course ON wishlist(course_id);

-- ============================================================================
-- ✅ VERIFY TABLES CREATED
-- ============================================================================
-- Run this to check if all tables exist:
-- SELECT tablename FROM pg_tables WHERE schemaname = 'public';
-- Expected: courses, orders, wishlist

-- ============================================================================
-- 🧹 CLEANUP (if needed)
-- ============================================================================
-- WARNING: These commands DELETE data. Use only for testing!
--
-- DROP TABLE IF EXISTS wishlist CASCADE;
-- DROP TABLE IF EXISTS orders CASCADE;
-- DROP TABLE IF EXISTS courses CASCADE;
--
-- Then re-run the CREATE TABLE commands above.
