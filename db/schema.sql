--   -------------------------------------------------- 
--   Generated by Enterprise Architect Version 8.0.864
--   Created On : Monday, 08 October, 2012 
--   DBMS       : PostgreSQL 
--   -------------------------------------------------- 

CREATE OR REPLACE FUNCTION make_plpgsql()
RETURNS VOID
LANGUAGE SQL
AS $$
CREATE LANGUAGE plpgsql;
$$;
 
SELECT
    CASE
    WHEN EXISTS(
        SELECT 1
        FROM pg_catalog.pg_language
        WHERE lanname='plpgsql'
    )
    THEN NULL
    ELSE make_plpgsql() END;
 
DROP FUNCTION make_plpgsql();

--  Drop Tables, Stored Procedures and Views 

DROP TABLE IF EXISTS Arch CASCADE
;
DROP TABLE IF EXISTS BuildClients CASCADE
;
DROP TABLE IF EXISTS Distribution CASCADE
;
DROP TABLE IF EXISTS Format CASCADE
;
DROP TABLE IF EXISTS Job CASCADE
;
DROP TABLE IF EXISTS JobStatus CASCADE
;
DROP TABLE IF EXISTS Package CASCADE
;
DROP TABLE IF EXISTS PackageInstance CASCADE
;
DROP TABLE IF EXISTS Status CASCADE
;
DROP TABLE IF EXISTS Suite CASCADE
;
DROP TABLE IF EXISTS SuiteArches CASCADE
;
DROP TABLE IF EXISTS Blacklist CASCADE
;
DROP TABLE IF EXISTS BuildRequest CASCADE
;
DROP TABLE IF EXISTS BuildEnv CASCADE
;
DROP TABLE IF EXISTS BuildEnvSuiteArch CASCADE
;

DROP TABLE IF EXISTS schema_version CASCADE
;
--  Create Tables - Changed to add NOT NULLs
CREATE TABLE schema_version
(
	id SERIAL PRIMARY KEY NOT NULL
);
-- The schema version has to be updated every time we change the schema.
-- Make sure to create an update script in vN.sql in updates to allow
-- existing databases to be upgraded
INSERT INTO schema_version(id) VALUES (5);

CREATE TABLE Arch ( 
	id SERIAL PRIMARY KEY NOT NULL,
	Name text NOT NULL
)
;

CREATE TABLE BuildClients ( 
	id SERIAL PRIMARY KEY NOT NULL,
	Name text NOT NULL
)
;

CREATE TABLE Distribution ( 
	id SERIAL PRIMARY KEY NOT NULL,
	Name text NOT NULL
)
;
COMMENT ON TABLE Distribution
    IS 'For example this could be Debian Squeeze, Ubuntu, Windows 7'
;

CREATE TABLE Format ( 
	id SERIAL PRIMARY KEY NOT NULL,
	Name text NOT NULL
)
;
COMMENT ON TABLE Format
    IS 'This is the format of the package instance, for example MSI, deb, rpm, tarball'
;

CREATE TABLE Job ( 
	id SERIAL PRIMARY KEY NOT NULL,
	PackageInstance_id bigint NOT NULL,
	BuildClient_id bigint
)
;
COMMENT ON TABLE Job
    IS 'A Job is how we build a given package instance, multiple jobs may be submitted for a single package.'
;

CREATE TABLE JobStatus ( 
	id SERIAL PRIMARY KEY NOT NULL,
	Job_id bigint NOT NULL,
	Status_id bigint NOT NULL,
	time timestamp NOT NULL DEFAULT now()
)
;

CREATE TABLE Package ( 
	id SERIAL PRIMARY KEY NOT NULL,
	Version text NOT NULL,
	Name text NOT NULL
)
;

CREATE TABLE Blacklist (
	id SERIAL PRIMARY KEY NOT NULL,
	field text NOT NULL,
	regex text NOT NULL
);

COMMENT ON TABLE Blacklist
	IS 'Blacklist is used internally by submitjob to determine if certain packages are centrally blacklisted using regexes'
;

CREATE TABLE PackageInstance ( 
	id SERIAL PRIMARY KEY NOT NULL,
	Package_id bigint NOT NULL,
	BuildEnv_id bigint,
	Arch_id bigint NOT NULL,
	Suite_id bigint NOT NULL,
	Dist_id bigint NOT NULL,
	Format_id bigint NOT NULL,
	master boolean NOT NULL DEFAULT false   --  Master tell us if this instance is the first submitted for a given package, this information is acted on by certain build clients 
)
;
COMMENT ON COLUMN PackageInstance.master
    IS 'Master tell us if this instance is the first submitted for a given package, this information is acted on by certain build clients'
;

CREATE TABLE Status ( 
	id SERIAL PRIMARY KEY NOT NULL,
	Name text NOT NULL
)
;

CREATE TABLE Suite ( 
	id SERIAL PRIMARY KEY NOT NULL,
	Name text NOT NULL
)
;

CREATE TABLE SuiteArches (
	id SERIAL PRIMARY KEY NOT NULL,
	Suite_id bigint NOT NULL,
	Arch_id bigint NOT NULL,
	master_weight bigint NOT NULL DEFAULT 0
)
;

CREATE TABLE BuildRequest (
	id SERIAL PRIMARY KEY NOT NULL,
	job bigint NOT NULL,
	method text NOT NULL,
	uri text NOT NULL,
	vcs_id text NOT NULL,
	buildenv_name text DEFAULT ''
);


CREATE TABLE BuildEnv
(
    id SERIAL PRIMARY KEY NOT NULL,
    Name text NOT NULL
)
;

CREATE TABLE BuildEnvSuiteArch
(
    id SERIAL PRIMARY KEY NOT NULL,
    BuildEnv_id BIGINT NOT NULL,
    SuiteArch_id BIGINT NOT NULL,
    FOREIGN KEY (BuildEnv_id) REFERENCES BuildEnv (id),
    FOREIGN KEY (SuiteArch_id) REFERENCES SuiteArches (id)
)
;

COMMENT ON TABLE BuildRequest
	IS 'BuildRequest is used to log build details so they can in future be requeued.'
;

--  Create Indexes
ALTER TABLE Arch
	ADD CONSTRAINT UQ_Arch_id UNIQUE (id)
;
ALTER TABLE BuildClients
	ADD CONSTRAINT UQ_BuildClients_id UNIQUE (id)
;
ALTER TABLE Distribution
	ADD CONSTRAINT UQ_Distribution_id UNIQUE (id)
;
ALTER TABLE Format
	ADD CONSTRAINT UQ_Format_id UNIQUE (id)
;
ALTER TABLE Job
	ADD CONSTRAINT UQ_Job_id UNIQUE (id)
;
ALTER TABLE JobStatus
	ADD CONSTRAINT UQ_JobStatus_id UNIQUE (id)
;
ALTER TABLE Package
	ADD CONSTRAINT UQ_Package_id UNIQUE (id)
;
ALTER TABLE PackageInstance
	ADD CONSTRAINT UQ_PackageInstance_id UNIQUE (id)
;
ALTER TABLE Status
	ADD CONSTRAINT UQ_Status_id UNIQUE (id)
;
ALTER TABLE Suite
	ADD CONSTRAINT UQ_Suite_id UNIQUE (id)
;

ALTER TABLE SuiteArches 
	ADD CONSTRAINT UQ_Stuite_Arches_id UNIQUE (id)
;

ALTER TABLE Blacklist
	ADD CONSTRAINT UQ_Blacklist_id UNIQUE (id)
;

ALTER TABLE BuildRequest
	ADD CONSTRAINT UQ_BuildRequest_id UNIQUE (id)
;
--  Create Constraints for uniqueness of some fields
ALTER TABLE Arch
	ADD CONSTRAINT UQ_Arch_name UNIQUE (name)
;
ALTER TABLE BuildClients
	ADD CONSTRAINT UQ_BuildClients_name UNIQUE (name)
;
ALTER TABLE Distribution
	ADD CONSTRAINT UQ_Distribution_name UNIQUE (name)
;
ALTER TABLE Format
	ADD CONSTRAINT UQ_Format_name UNIQUE (name)
;
ALTER TABLE Package
	ADD CONSTRAINT UQ_Package_name_version UNIQUE (name,version)
;
ALTER TABLE Status
	ADD CONSTRAINT UQ_Status_name UNIQUE (name)
;
ALTER TABLE Suite
	ADD CONSTRAINT UQ_Suite_name UNIQUE (name)
;
--  Create Foreign Key Constraints 
ALTER TABLE Job ADD CONSTRAINT FK_Job_BuildClients 
	FOREIGN KEY (BuildClient_id) REFERENCES BuildClients (id)
;

ALTER TABLE Job ADD CONSTRAINT FK_Job_PackageInstance 
	FOREIGN KEY (PackageInstance_id) REFERENCES PackageInstance (id)
;

ALTER TABLE JobStatus ADD CONSTRAINT FK_JobStatus_Job 
	FOREIGN KEY (Job_id) REFERENCES Job (id)
;

ALTER TABLE JobStatus ADD CONSTRAINT FK_JobStatus_Status 
	FOREIGN KEY (Status_id) REFERENCES Status (id)
;

ALTER TABLE PackageInstance ADD CONSTRAINT FK_PackageInstance_Arch 
	FOREIGN KEY (Arch_id) REFERENCES Arch (id)
;

ALTER TABLE PackageInstance ADD CONSTRAINT FK_PackageInstance_Distribution 
	FOREIGN KEY (Dist_id) REFERENCES Distribution (id)
;

ALTER TABLE PackageInstance ADD CONSTRAINT FK_PackageInstance_Format 
	FOREIGN KEY (Format_id) REFERENCES Format (id)
;

ALTER TABLE PackageInstance ADD CONSTRAINT FK_PackageInstance_Package 
	FOREIGN KEY (Package_id) REFERENCES Package (id)
;

ALTER TABLE PackageInstance ADD CONSTRAINT FK_PackageInstance_Suite 
	FOREIGN KEY (Suite_id) REFERENCES Suite (id)
;

ALTER TABLE SuiteArches ADD CONSTRAINT FK_SuiteArches_Suite
	FOREIGN KEY (Suite_id) REFERENCES Suite (id)
;

ALTER TABLE SuiteArches ADD CONSTRAINT FK_SuiteArches_Arch
	FOREIGN KEY (Arch_id) REFERENCES Arch (id)
;

ALTER TABLE BuildRequest ADD CONSTRAINT FK_BuildRequest_Job
	FOREIGN KEY (job) REFERENCES Job (id)
;

ALTER TABLE PackageInstance ADD CONSTRAINT FK_PackageInstance_BuildEnv 
	FOREIGN KEY (BuildEnv_id) REFERENCES BuildEnv (id)
;
