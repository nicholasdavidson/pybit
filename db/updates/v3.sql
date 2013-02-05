create or replace function run_update() returns void as
$$
begin
if not exists (SELECT * FROM information_schema.tables WHERE
		table_catalog = CURRENT_CATALOG AND table_schema = CURRENT_SCHEMA
		AND table_name = 'buildrequest') then
			CREATE TABLE BuildRequest (
				id SERIAL PRIMARY KEY NOT NULL,
				job bigint NOT NULL,
				method text NOT NULL,
				uri text NOT NULL,
				vcs_id text NOT NULL
			);
			insert into schema_version(id) values (3);
end if;
end;
$$ LANGUAGE plpgsql;

SELECT run_update();
