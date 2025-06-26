from psycopg2 import pool

db_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=5,
    host='localhost',
    port=yourport,
    database="yourdb",
    user="postgres",
    password="yourpass"
)
