create or replace function run_update() returns void as
$$
begin
if (SELECT count(*) FROM schema_version WHERE id=3)
then
	CREATE TABLE BuildEnv
	(
	   id SERIAL PRIMARY KEY NOT NULL,
	   Name text NOT NULL
	);
	CREATE TABLE BuildEnvSuiteArch
	(
		id SERIAL PRIMARY KEY NOT NULL,
		BuildEnv_id BIGINT NOT NULL,
		SuiteArch_id BIGINT NOT NULL,
		FOREIGN KEY (BuildEnv_id) REFERENCES BuildEnv (id),
		FOREIGN KEY (SuiteArch_id) REFERENCES SuiteArches (id)
	);
	ALTER TABLE BuildRequest ADD buildenv_name text DEFAULT '';
	UPDATE schema_version SET id=4;
end if;
end;
$$ LANGUAGE plpgsql;

SELECT run_update();
