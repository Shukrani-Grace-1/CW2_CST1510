import sqlite3
import pandas as pd
import bcrypt
from pathlib import Path

DB_PATH= Path("DATA")/"intelligence_platform.db"

def connect_database(db_path=DB_PATH):
    """Connect to SQL database."""
    return sqlite3.connect(str(db_path))