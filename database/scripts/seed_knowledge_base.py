import psycopg2
import os

conn = psycopg2.connect(os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/customer_support"))
cur = conn.cursor()
cur.execute("""
INSERT INTO knowledge_base (title, content, category, embedding, metadata)
VALUES ('How do I reset my Xfinity modem?', 'To reset your Xfinity modem, unplug the power cable, wait 10 seconds, and plug it back in. Wait for the lights to stabilize.', 'modem_reset', '[0.0, ...]', '{"keywords": ["reset", "modem", "power"]}');
""")
conn.commit()
cur.close()
conn.close()
print("Knowledge base seeded.") 