create or replace function run_update() returns void as
$$
begin
if not exists (SELECT * FROM information_schema.tables WHERE
		table_catalog = CURRENT_CATALOG AND table_schema = CURRENT_SCHEMA
		AND table_name = 'blacklist') then
			CREATE TABLE Blacklist (
				id SERIAL PRIMARY KEY NOT NULL,
				field text NOT NULL,
				regex text NOT NULL
			);
			insert into schema_version(id) values (2);
end if;
end;
$$ LANGUAGE plpgsql;

SELECT run_update();
