create or replace function run_update() returns void as
$$
begin
if (SELECT count(*) from schema_version WHERE id=4)
then
			ALTER TABLE PackageInstance ADD COLUMN buildenv_id bigint;
			UPDATE schema_version SET id=5;
end if;
end;
$$ LANGUAGE plpgsql;

SELECT run_update();
