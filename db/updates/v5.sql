create or replace function run_update() returns void as
$$
begin
if not exists (SELECT * FROM information_schema.tables WHERE
		table_catalog = CURRENT_CATALOG AND table_schema = CURRENT_SCHEMA
			ALTER TABLE PackageInstance ADD buildenv_id;
			UPDATE schema_version SET id=5;
end if;
end;
$$ LANGUAGE plpgsql;

SELECT run_update();