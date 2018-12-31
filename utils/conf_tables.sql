--
-- Bacula conf builder TABLEs for PostgreSQL
--

SET client_encoding = 'SQL_ASCII';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Cleaning
--
DROP VIEW IF EXISTS conf_all_data;
DROP TABLE IF EXISTS conf_parameter;
DROP SEQUENCE IF EXISTS conf_parameter_parid_seq;
DROP TABLE IF EXISTS conf_resource;
DROP SEQUENCE IF EXISTS conf_resource_resid_seq;
DROP TABLE IF EXISTS conf_component;
DROP SEQUENCE IF EXISTS conf_component_compid_seq;
DROP TABLE IF EXISTS conf_rtype;

--
-- Name: conf_component; Type: TABLE;
--
-- 'F': File Daemon
-- 'D': Director
-- 'S': Storage Daemon
CREATE TABLE conf_component (
    compid serial PRIMARY KEY,
    type character(1) DEFAULT 'F'::bpchar NOT NULL,
    name varchar NOT NULL,
    UNIQUE (type,name),
    CONSTRAINT conf_component_type_check CHECK (type = ANY (ARRAY['D'::bpchar, 'F'::bpchar, 'S'::bpchar, 'C'::bpchar]))
);
GRANT all on conf_component to bacula;
GRANT all on conf_component_compid_seq to bacula;

--
-- Name: conf_rtype; Type: TABLE; Schema: public;
--
CREATE TABLE conf_rtype (
    typeid integer PRIMARY KEY,
    name varchar UNIQUE NOT NULL
);
GRANT select on conf_rtype to bacula;

--
-- Data for Name: conf_rtype; Type: TABLE DATA;
--

INSERT INTO conf_rtype (typeid, name) VALUES (1, 'Director');
INSERT INTO conf_rtype (typeid, name) VALUES (2, 'Storage');
INSERT INTO conf_rtype (typeid, name) VALUES (3, 'FileDaemon');
INSERT INTO conf_rtype (typeid, name) VALUES (4, 'Client');
INSERT INTO conf_rtype (typeid, name) VALUES (5, 'Messages');
INSERT INTO conf_rtype (typeid, name) VALUES (6, 'Catalog');
INSERT INTO conf_rtype (typeid, name) VALUES (7, 'Schedule');
INSERT INTO conf_rtype (typeid, name) VALUES (8, 'Job');
INSERT INTO conf_rtype (typeid, name) VALUES (9, 'JobDefs');
INSERT INTO conf_rtype (typeid, name) VALUES (10, 'Fileset');
INSERT INTO conf_rtype (typeid, name) VALUES (11, 'Pool');
INSERT INTO conf_rtype (typeid, name) VALUES (12, 'Device');
INSERT INTO conf_rtype (typeid, name) VALUES (13, 'Autochanger');
INSERT INTO conf_rtype (typeid, name) VALUES (14, 'Include');
INSERT INTO conf_rtype (typeid, name) VALUES (15, 'Exclude');
INSERT INTO conf_rtype (typeid, name) VALUES (16, 'Options');


--
-- Name: conf_resource; Type: TABLE;
--
CREATE TABLE conf_resource (
    resid serial PRIMARY KEY,
    compid integer REFERENCES conf_component(compid),
    type integer REFERENCES conf_rtype(typeid),
    sub integer DEFAULT NULL,
    name varchar NOT NULL,
    description varchar
);
GRANT all on conf_resource to bacula;
GRANT all on conf_resource_resid_seq to bacula;

--
-- Name: conf_parameter; Type: TABLE;
--
CREATE TABLE conf_parameter (
    parid serial PRIMARY KEY,
    resid integer REFERENCES conf_resource(resid),
    name varchar NOT NULL,
    value varchar NOT NULL,
    str boolean DEFAULT False,
    enc boolean DEFAULT False
);
GRANT all on conf_parameter to bacula;
GRANT all on conf_parameter_parid_seq to bacula;

--
-- Common configuration view
--
CREATE OR REPLACE VIEW conf_all_data AS
select C.name as Component, T.name as Resource,  COALESCE (R.name,S.name,S1.name) as Name, P.name as Parameter, P.value as Value, P.enc as Encrypted
from
        conf_component C, conf_rtype T, conf_parameter P,
                conf_resource R LEFT OUTER JOIN conf_resource S on R.sub=S.resid LEFT OUTER JOIN conf_resource S1 on S.sub=S1.resid
where
        C.compid = R.compid and
        T.typeid = R.type and
        P.resid = R.resid
;
GRANT select on conf_all_data to bacula;
