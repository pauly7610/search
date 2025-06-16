import psycopg2
import os

conn = psycopg2.connect(os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/customer_support"))
cur = conn.cursor()
cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
conn.commit()
cur.close()
conn.close()
print("Postgres setup complete.") 