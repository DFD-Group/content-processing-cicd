START TRANSACTION;
ALTER TABLE auth.api_keys ALTER COLUMN api_key_id SET DEFAULT (gen_random_uuid());

COMMIT;