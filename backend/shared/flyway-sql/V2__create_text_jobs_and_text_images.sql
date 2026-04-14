START TRANSACTION;

-- Running upgrade  -> fdc5c79b52c3

CREATE TYPE app.text_job_status AS ENUM ('pending', 'processing', 'completed', 'failed');

CREATE TABLE app.text_jobs (
    id UUID DEFAULT gen_random_uuid() NOT NULL, 
    prompt TEXT NOT NULL, 
    status app.text_job_status DEFAULT 'pending' NOT NULL, 
    error_message TEXT, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (id)
);

CREATE TABLE app.text_images (
    id UUID DEFAULT gen_random_uuid() NOT NULL, 
    image_path TEXT NOT NULL, 
    image_sha256 TEXT NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    text_job_id UUID NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(text_job_id) REFERENCES app.text_jobs (id) ON DELETE CASCADE
);

CREATE INDEX ix_app_text_images_text_job_id ON app.text_images (text_job_id);

GRANT SELECT, INSERT, UPDATE, DELETE ON app.text_jobs TO ${app_role};
GRANT SELECT, INSERT, UPDATE, DELETE ON app.text_images TO ${app_role};

COMMIT;
