BEGIN;

CREATE SCHEMA auth;
CREATE SCHEMA app;

CREATE TYPE app.pdf_to_images_status AS ENUM (
  'pending',
  'processing',
  'completed',
  'failed'
);

CREATE TABLE auth.api_keys (
  api_key_id       UUID PRIMARY KEY,
  secret_hash  CHAR(64) NOT NULL
    CHECK (octet_length(trim(secret_hash::text)) = 64 AND trim(secret_hash::text) ~ '^[0-9a-fA-F]{64}$'),
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  expires_at   TIMESTAMPTZ NULL,
  revoked_at   TIMESTAMPTZ NULL,
  scopes       TEXT[] NULL
    CHECK (
      scopes IS NULL
      OR scopes <@ ARRAY[
        'content:read',
        'content:write',
        'iam:admin'
      ]::text[]
    ),
  name         TEXT NULL,
  created_by   TEXT NULL
);

COMMENT ON COLUMN auth.api_keys.scopes IS
  'content:read — list/download metadata, job status, results; '
  'content:write — enqueue renders, update pipeline-owned fields, attach paths; '
  'iam:admin — create users, mint/revoke API keys.';

-- Parent first; image_id FK added after app.images exists.
CREATE TABLE app.pdf_to_images (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  pdf_path     TEXT NOT NULL,
  first_page_image_id     UUID NULL,
  pdf_sha256   CHAR(64) NOT NULL
    CHECK (octet_length(trim(pdf_sha256::text)) = 64 AND trim(pdf_sha256::text) ~ '^[0-9a-fA-F]{64}$'),
  status       app.pdf_to_images_status NOT NULL DEFAULT 'pending',
  error_message TEXT NULL,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE app.images (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  pdf_to_images_id UUID NOT NULL
    REFERENCES app.pdf_to_images (id) ON DELETE CASCADE,
  image_path      TEXT NOT NULL,
  image_sha256    CHAR(64) NOT NULL
    CHECK (octet_length(trim(image_sha256::text)) = 64 AND trim(image_sha256::text) ~ '^[0-9a-fA-F]{64}$'),
  page_number      INTEGER NOT NULL CHECK (page_number >= 0),
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_images_pdf_to_images_id ON app.images (pdf_to_images_id);

ALTER TABLE app.pdf_to_images
  ADD CONSTRAINT fk_pdf_to_images_first_page_image_id
  FOREIGN KEY (first_page_image_id) REFERENCES app.images (id)
  ON DELETE SET NULL;

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
