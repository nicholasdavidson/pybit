
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
		AND table_name = 'blacklist') then
			CREATE TABLE Blacklist (
				id SERIAL PRIMARY KEY NOT NULL,
				field text NOT NULL,
				regex text NOT NULL
			);
			update schema_version set id =2;
end if;
end;
$$ LANGUAGE plpgsql;

SELECT run_update();
