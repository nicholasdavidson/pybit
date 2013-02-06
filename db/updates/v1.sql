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

create or replace function run_update() returns void as
$$
begin
if not exists (SELECT * FROM information_schema.tables WHERE
		table_catalog = CURRENT_CATALOG AND table_schema = CURRENT_SCHEMA
		AND table_name = 'schema_version') then
			CREATE TABLE schema_version
			(
				id SERIAL PRIMARY KEY NOT NULL
			);
			insert into schema_version(id) values (1);
			ALTER TABLE suitearches ADD COLUMN master_weight bigint NOT NULL DEFAULT 0;
end if;
end;
$$ LANGUAGE plpgsql;

SELECT run_update();
