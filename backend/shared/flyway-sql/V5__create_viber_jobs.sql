CREATE TABLE app.viber_jobs (
    id UUID DEFAULT gen_random_uuid() NOT NULL,
    plate_size TEXT NOT NULL,
    plate_sign TEXT NOT NULL,
    plate_count INTEGER NOT NULL,
    dfd_order_number TEXT NOT NULL,
    expedition_date DATE NOT NULL,
    message_text TEXT NOT NULL,
    status TEXT DEFAULT 'pending' NOT NULL,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    sent_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT viber_jobs_pkey PRIMARY KEY (id)
);