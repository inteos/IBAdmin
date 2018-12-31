--
-- IBAdmin stat collector TABLEs for PostgreSQL
--

SET client_encoding = 'SQL_ASCII';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Clean
--
DROP TABLE IF EXISTS stat_data;
DROP TABLE IF EXISTS stat_data_hours;
DROP TABLE IF EXISTS stat_data_days;
DROP TABLE IF EXISTS stat_status;
DROP TABLE IF EXISTS stat_daterange;
DROP TABLE IF EXISTS stat_params;

--
-- Name: stat_params; Type: TABLE;
--
-- 'F': type float
-- 'N': type number/integer
-- 'S': type string
CREATE TABLE stat_params(
    parid serial PRIMARY KEY,
    types character(1) DEFAULT 'N'::bpchar NOT NULL,
    name varchar UNIQUE NOT NULL,
    description varchar,
    unit varchar NOT NULL,
    chart integer DEFAULT 0 NOT NULL,
    display integer DEFAULT 1 NOT NULL,
    color varchar DEFAULT '#000000' NOT NULL,
    box varchar DEFAULT 'box-primary' NOT NULL,
    CONSTRAINT conf_component_types_check CHECK (types = ANY (ARRAY['F'::bpchar, 'N'::bpchar, 'S'::bpchar]))
);
GRANT all on stat_params to bacula;
GRANT all on stat_params_parid_seq to bacula;

--
-- Name: stat_data; Type: TABLE;
--
CREATE TABLE stat_data(
    id serial PRIMARY KEY,
    time timestamp with time zone default now(),
    parid integer REFERENCES stat_params(parid),
    nvalue bigint,
    fvalue real,
    svalue varchar
);
CREATE INDEX stat_data_time_idx on stat_data(time);
CREATE INDEX stat_data_param_idx on stat_data(parid);

GRANT all on stat_data to bacula;
GRANT all on stat_data_id_seq to bacula;

--
-- Name: stat_data_hours; Type: TABLE;
--
CREATE TABLE stat_data_hours(
    id serial PRIMARY KEY,
    time timestamp with time zone default now(),
    parid integer REFERENCES stat_params(parid),
    nvalmin bigint,
    nvalmax bigint,
    nvalavg bigint,
    fvalmin real,
    fvalmax real,
    fvalavg real
);
CREATE INDEX stat_data_hours_time_idx on stat_data_hours(time);
CREATE INDEX stat_data_hours_param_idx on stat_data_hours(parid);

GRANT all on stat_data_hours to bacula;
GRANT all on stat_data_hours_id_seq to bacula;

--
-- Name: stat_data_days; Type: TABLE;
--
CREATE TABLE stat_data_days(
    id serial PRIMARY KEY,
    time timestamp with time zone default now(),
    parid integer REFERENCES stat_params(parid),
    nvalmin bigint,
    nvalmax bigint,
    nvalavg bigint,
    fvalmin real,
    fvalmax real,
    fvalavg real
);
CREATE INDEX stat_data_days_time_idx on stat_data_days(time);
CREATE INDEX stat_data_days_param_idx on stat_data_days(parid);

GRANT all on stat_data_days to bacula;
GRANT all on stat_data_days_id_seq to bacula;

--
-- Name: stat_status; Type: TABLE;
--
CREATE TABLE stat_status(
    parid integer PRIMARY KEY REFERENCES stat_params(parid),
    time timestamp with time zone default now(),
    nvalue bigint,
    fvalue real,
    svalue varchar
);
GRANT all on stat_status to bacula;

--
-- Name: stat_daterange; Type: TABLE;
--
CREATE TABLE stat_daterange(
    parid integer PRIMARY KEY REFERENCES stat_params(parid),
    mintime timestamp with time zone default now(),
    maxtime timestamp with time zone default now()
);
GRANT all on stat_daterange to bacula;
