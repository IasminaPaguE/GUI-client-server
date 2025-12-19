CREATE TABLE IF NOT EXISTS transfer_metrics (
    id SERIAL PRIMARY KEY,

    file_name TEXT NOT NULL,
    file_size BIGINT NOT NULL,
    file_type TEXT,

    total_transfer_time DOUBLE PRECISION NOT NULL,
    throughput DOUBLE PRECISION NOT NULL,
    peak_throughput DOUBLE PRECISION NOT NULL,

    transfer_byte_difference INTEGER,
    transfer_status TEXT NOT NULL,

    cpu_usage_avg DOUBLE PRECISION,
    cpu_usage_peak DOUBLE PRECISION,
    ram_usage_avg DOUBLE PRECISION,
    ram_usage_peak DOUBLE PRECISION,

    timestamp TIMESTAMPTZ DEFAULT NOW()
);
