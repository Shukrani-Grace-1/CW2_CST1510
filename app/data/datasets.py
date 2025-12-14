import pandas as pd
from app.data.db import connect_database


def insert_dataset(conn, dataset_name, category=None, source=None, last_updated=None, record_count=None, file_size_mb=None):
    """Insert new dataset and return its ID."""
    cursor = conn.cursor()
    sql = """
        INSERT INTO datasets_metadata
            (dataset_name, category, source, last_updated, record_count, file_size_mb)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    cursor.execute(sql, (dataset_name, category, source, last_updated, record_count, file_size_mb))
    conn.commit()
    return cursor.lastrowid


def get_all_datasets(conn):
    """Get all datasets as a DataFrame."""
    return pd.read_sql_query(
        "SELECT * FROM datasets_metadata ORDER BY id DESC",
        conn
    )


def get_dataset_by_id(conn, dataset_id):
    """Get one dataset (0 or 1 row) by id as a DataFrame."""
    return pd.read_sql_query(
        "SELECT * FROM datasets_metadata WHERE id = ?",
        conn,
        params=(dataset_id,)
    )


def get_dataset_by_name(conn, dataset_name):
    """Get one dataset (0 or 1 row) by unique dataset_name as a DataFrame."""
    return pd.read_sql_query(
        "SELECT * FROM datasets_metadata WHERE dataset_name = ?",
        conn,
        params=(dataset_name,)
    )


def update_dataset(conn, dataset_id, dataset_name, category=None, source=None, last_updated=None, record_count=None, file_size_mb=None):
    """Update a dataset by id. Returns rows updated (0 if id not found)."""
    cursor = conn.cursor()
    sql = """
        UPDATE datasets_metadata
        SET dataset_name = ?,
            category = ?,
            source = ?,
            last_updated = ?,
            record_count = ?,
            file_size_mb = ?
        WHERE id = ?
    """
    cursor.execute(sql, (dataset_name, category, source, last_updated, record_count, file_size_mb, dataset_id))
    conn.commit()
    return cursor.rowcount


def delete_dataset(conn, dataset_id):
    """Delete a dataset by id. Returns rows deleted (0 if id not found)."""
    cursor = conn.cursor()
    sql = "DELETE FROM datasets_metadata WHERE id = ?"
    cursor.execute(sql, (dataset_id,))
    conn.commit()
    return cursor.rowcount



def get_datasets_by_category_count(conn):
    query = """
    SELECT category, COUNT(*) as count
    FROM datasets_metadata
    GROUP BY category
    ORDER BY count DESC
    """
    return pd.read_sql_query(query, conn)


def get_top_datasets_by_record_count(conn, limit=10):
    """Return top datasets by record_count (ignores NULL record_count)."""
    query = """
    SELECT dataset_name, record_count
    FROM datasets_metadata
    WHERE record_count IS NOT NULL
    ORDER BY record_count DESC
    LIMIT ?
    """
    return pd.read_sql_query(query, conn, params=(limit,))