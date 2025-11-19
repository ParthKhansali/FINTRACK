# backend/db_config.py
import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector.pooling import MySQLConnectionPool

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

DB_CONF = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "fintrack"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "finance_tracker"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "charset": "utf8mb4",
    "autocommit": False,
}

_pool = None
_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", 5))

def _init_pool():
    global _pool
    if _pool is None:
        try:
            _pool = MySQLConnectionPool(pool_name="ft_pool", pool_size=_POOL_SIZE, **DB_CONF)
        except mysql.connector.Error as e:
            raise RuntimeError(f"Failed to create MySQL connection pool: {e}") from e

def get_connection():
    if _pool is None:
        _init_pool()
    try:
        return _pool.get_connection()
    except mysql.connector.Error as e:
        raise RuntimeError(f"Failed to obtain MySQL connection from pool: {e}") from e
