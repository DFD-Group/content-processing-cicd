START TRANSACTION;
DO $EF$
BEGIN
    IF NOT EXISTS(SELECT 1 FROM pg_namespace WHERE nspname = 'auth') THEN
        CREATE SCHEMA auth;
    END IF;
END $EF$;

DO $EF$
BEGIN
    IF NOT EXISTS(SELECT 1 FROM pg_namespace WHERE nspname = 'app') THEN
        CREATE SCHEMA app;
    END IF;
END $EF$;

DO $EF$
BEGIN
    IF NOT EXISTS(SELECT 1 FROM pg_namespace WHERE nspname = 'app') THEN
        CREATE SCHEMA app;
    END IF;
END $EF$;

CREATE TYPE app.pdf_to_images_status AS ENUM ('pending', 'processing', 'completed', 'failed');

CREATE TABLE auth.api_keys (
    api_key_id uuid NOT NULL,
    secret_hash character(64) NOT NULL,
    created_at timestamp with time zone NOT NULL DEFAULT (now()),
    expires_at timestamp with time zone,
    revoked_at timestamp with time zone,
    scopes text[],
    name text,
    created_by text,
    CONSTRAINT pk_api_keys PRIMARY KEY (api_key_id),
    CONSTRAINT ck_api_keys_scopes CHECK (scopes IS NULL OR scopes <@ ARRAY['content:read', 'content:write', 'iam:admin']::text[]),
    CONSTRAINT ck_api_keys_secret CHECK (octet_length(trim(secret_hash::text)) = 64 AND trim(secret_hash::text) ~ '^[0-9a-fA-F]{64}$')
);

CREATE TABLE app.images (
    id uuid NOT NULL DEFAULT (gen_random_uuid()),
    image_path text NOT NULL,
    image_sha256 character(64) NOT NULL,
    page_number integer NOT NULL,
    pdf_to_images_id uuid NOT NULL,
    created_at timestamp with time zone NOT NULL DEFAULT (now()),
    CONSTRAINT pk_images PRIMARY KEY (id),
    CONSTRAINT "CK_images_image_sha256" CHECK (octet_length(trim(image_sha256::text)) = 64 AND trim(image_sha256::text) ~ '^[0-9a-fA-F]{64}$'),
    CONSTRAINT "CK_images_page_number" CHECK (page_number >= 0)
);

CREATE TABLE app.pdf_to_images (
    id uuid NOT NULL DEFAULT (gen_random_uuid()),
    pdf_path text NOT NULL,
    first_page_image_id uuid,
    pdf_sha256 character(64) NOT NULL,
    status app.pdf_to_images_status NOT NULL DEFAULT 'pending'::app.pdf_to_images_status,
    error_message text,
    created_at timestamp with time zone NOT NULL DEFAULT (now()),
    updated_at timestamp with time zone NOT NULL DEFAULT (now()),
    CONSTRAINT pk_pdf_to_images PRIMARY KEY (id),
    CONSTRAINT "CK_pdf_to_images_pdf_sha256" CHECK (octet_length(trim(pdf_sha256::text)) = 64 AND trim(pdf_sha256::text) ~ '^[0-9a-fA-F]{64}$'),
    CONSTRAINT fk_pdf_to_images_first_page_image_id FOREIGN KEY (first_page_image_id) REFERENCES app.images (id) ON DELETE SET NULL
);

CREATE INDEX idx_images_pdf_to_images_id ON app.images (pdf_to_images_id);

CREATE INDEX ix_pdf_to_images_first_page_image_id ON app.pdf_to_images (first_page_image_id);

ALTER TABLE app.images ADD CONSTRAINT fk_images_pdf_to_images_id FOREIGN KEY (pdf_to_images_id) REFERENCES app.pdf_to_images (id) ON DELETE CASCADE;

GRANT USAGE ON SCHEMA auth TO ${app_role};
GRANT USAGE ON SCHEMA app TO ${app_role};

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA auth TO ${app_role};
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA app TO ${app_role};

GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA auth TO ${app_role};
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA app TO ${app_role};

ALTER DEFAULT PRIVILEGES FOR ROLE flyway_migrator IN SCHEMA auth
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO ${app_role};
ALTER DEFAULT PRIVILEGES FOR ROLE flyway_migrator IN SCHEMA app
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO ${app_role};
ALTER DEFAULT PRIVILEGES FOR ROLE flyway_migrator IN SCHEMA auth
  GRANT USAGE, SELECT ON SEQUENCES TO ${app_role};
ALTER DEFAULT PRIVILEGES FOR ROLE flyway_migrator IN SCHEMA app
  GRANT USAGE, SELECT ON SEQUENCES TO ${app_role};

COMMIT;
