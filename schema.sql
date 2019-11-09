CREATE TABLE IF NOT EXISTS guild_settings (
    guild_id BIGINT UNIQUE,
    prefix VARCHAR(20) DEFAULT NULL, 
    nsfw_restricted BOOLEAN DEFAULT true
);

CREATE OR REPLACE FUNCTION toggle_nsfw(guildid BIGINT) RETURNS integer AS $$
    BEGIN
        IF (SELECT nsfw_restricted FROM guild_settings WHERE guild_id=guildid) = TRUE THEN
            UPDATE guild_settings SET nsfw_restricted = false WHERE guild_id=guildid;
            RETURN 1;
        ELSE
            INSERT INTO guild_settings VALUES(guildid);
            RETURN 2;
                
        END IF;
    END; $$
LANGUAGE PLPGSQL;
    


