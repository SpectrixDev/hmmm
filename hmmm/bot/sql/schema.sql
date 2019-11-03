CREATE TABLE IF NOT EXISTS nsfw_opted (
    guild_id BIGINT UNIQUE
);

CREATE OR REPLACE FUNCTION toggle_nsfw(guildid BIGINT) RETURNS integer AS $$
    BEGIN
        IF EXISTS (SELECT guild_id FROM nsfw_opted WHERE guild_id=guildid) THEN
            DELETE FROM nsfw_opted WHERE nsfw_opted.guild_id=guildid;
            RETURN 1;
        ELSE
            INSERT INTO nsfw_opted VALUES(guildid);
            RETURN 2;
                
        END IF;
    END; $$
LANGUAGE PLPGSQL;
    


