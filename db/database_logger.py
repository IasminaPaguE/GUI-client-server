import os
import psycopg2
from psycopg2.extras import RealDictCursor


class DatabaseLogger:
    """
    Handles inserting transfer metrics into PostgreSQL.
    Uses a new short-lived connection per insert (thread-safe).
    """

    def __init__(self):
        self.dsn = os.getenv("DATABASE_DSN")

        if not self.dsn:
            raise ValueError("DATABASE_DSN environment variable is not set.")

    def insert_metrics(self, metrics: dict):
        query = """
            INSERT INTO transfer_metrics (
                file_name, file_size, file_type,
                total_transfer_time, throughput, peak_throughput,
                transfer_byte_difference, transfer_status,
                cpu_usage_avg, cpu_usage_peak,
                ram_usage_avg, ram_usage_peak
            )
            VALUES (
                %(file_name)s, %(file_size)s, %(file_type)s,
                %(total_transfer_time)s, %(throughput)s, %(peak_throughput)s,
                %(transfer_byte_difference)s, %(transfer_status)s,
                %(cpu_usage_avg)s, %(cpu_usage_peak)s,
                %(ram_usage_avg)s, %(ram_usage_peak)s
            );
        """

        try:
            with psycopg2.connect(self.dsn) as conn:
                with conn.cursor() as cur:
                    cur.execute(query, metrics)
                    conn.commit()

        except Exception as e:
            # Do NOT crash the application on DB errors
            print(f"[DB ERROR] Failed to insert metrics into database: {e}")
