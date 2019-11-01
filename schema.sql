CREATE TABLE IF NOT EXISTS guild_settings (
    guild_id BIGINT PRIMARY KEY,
    allow_nsfw BOOLEAN DEFAULT FALSE
);
