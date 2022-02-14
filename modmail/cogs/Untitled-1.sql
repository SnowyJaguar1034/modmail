-- Table: public.data

-- DROP TABLE IF EXISTS public.data;

CREATE TABLE IF NOT EXISTS public.data
(
    guild bigint NOT NULL,
    prefix text COLLATE pg_catalog."default",
    category bigint,
    accessrole bigint[] NOT NULL,
    logging bigint,
    welcome text COLLATE pg_catalog."default",
    goodbye text COLLATE pg_catalog."default",
    loggingplus boolean NOT NULL,
    pingrole bigint[] NOT NULL,
    blacklist bigint[] NOT NULL,
    anonymous boolean NOT NULL,
    lockedroles bigint[],
    raidchannel bigint[],
    currentcount bigint NOT NULL DEFAULT 0,
    raidmode boolean NOT NULL DEFAULT false,
    acc_age bigint NOT NULL DEFAULT 7,
    raidlog bigint,
    mistakesrole bigint[],
    joinleavelog bigint,
    raidrole bigint,
    isolationtime bigint DEFAULT 0,
    guildmistakes bigint NOT NULL DEFAULT 0,
    countchannel bigint,
    deletedmessages bigint,
    editedmessages bigint,
    suggestions bigint,
    sugcount bigint NOT NULL DEFAULT 0,
    starboard bigint,
    badwords text[] COLLATE pg_catalog."default",
    CONSTRAINT data_pkey PRIMARY KEY (guild)
)