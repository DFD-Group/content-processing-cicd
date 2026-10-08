CREATE TABLE app.viber_jobs (
    id UUID DEFAULT gen_random_uuid() NOT NULL,
    plate_size VARCHAR(32) NOT NULL,
    plate_sign VARCHAR(64) NOT NULL,
    plate_count INTEGER NOT NULL,
    dfd_order_number VARCHAR(32) NOT NULL,
    customer_order_number VARCHAR(32) NOT NULL,
    expedition_date DATE NOT NULL,
    message_text TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' NOT NULL,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    sent_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT viber_jobs_pkey PRIMARY KEY (id)
);