create or replace function run_update() returns void as
$$
begin
if not exists (SELECT * FROM information_schema.tables WHERE
		table_catalog = CURRENT_CATALOG AND table_schema = CURRENT_SCHEMA
		AND table_name = 'buildenv') then
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
