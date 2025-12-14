import pandas as pd
from app.data.db import connect_database


def insert_ticket(conn, ticket_id, priority, status, category, subject, description=None, created_date=None, resolved_date=None):
    """Insert new IT ticket and return its ID."""
    cursor = conn.cursor()
    sql = """
        INSERT INTO it_tickets
            (ticket_id, priority, status, category, subject, description, created_date, resolved_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    cursor.execute(sql, (ticket_id, priority, status, category, subject, description, created_date, resolved_date))
    conn.commit()
    return cursor.lastrowid


def get_all_tickets(conn):
    """Get all tickets as a DataFrame."""
    return pd.read_sql_query(
        "SELECT * FROM it_tickets ORDER BY id DESC",
        conn
    )


def get_ticket_by_id(conn, db_id):
    """Get one ticket (0 or 1 row) by DB id as a DataFrame."""
    return pd.read_sql_query(
        "SELECT * FROM it_tickets WHERE id = ?",
        conn,
        params=(db_id,)
    )


def update_ticket(conn, db_id, ticket_id, priority, status, category, subject, description=None, created_date=None, resolved_date=None):
    """Full update of a ticket row (updates all editable columns). Returns rows updated (0 if id not found)."""
    cursor = conn.cursor()
    sql = """
        UPDATE it_tickets
        SET ticket_id = ?,
            priority = ?,
            status = ?,
            category = ?,
            subject = ?,
            description = ?,
            created_date = ?,
            resolved_date = ?
        WHERE id = ?
    """
    cursor.execute(sql, (ticket_id, priority, status, category, subject, description, created_date, resolved_date, db_id))
    conn.commit()
    return cursor.rowcount


def update_ticket_status(conn, db_id, new_status):
    """Update the status of a ticket. Returns rows updated (0 if id not found)."""
    cursor = conn.cursor()
    sql = "UPDATE it_tickets SET status = ? WHERE id = ?"
    cursor.execute(sql, (new_status, db_id))
    conn.commit()
    return cursor.rowcount


def update_ticket_priority(conn, db_id, new_priority):
    """Update only the priority of a ticket. Returns rows updated (0 if id not found)."""
    cursor = conn.cursor()
    sql = "UPDATE it_tickets SET priority = ? WHERE id = ?"
    cursor.execute(sql, (new_priority, db_id))
    conn.commit()
    return cursor.rowcount


def delete_ticket(conn, db_id):
    """Delete a ticket by DB id. Returns rows deleted (0 if id not found)."""
    cursor = conn.cursor()
    sql = "DELETE FROM it_tickets WHERE id = ?"
    cursor.execute(sql, (db_id,))
    conn.commit()
    return cursor.rowcount



def get_tickets_by_status_count(conn):
    query = """
    SELECT status, COUNT(*) as count
    FROM it_tickets
    GROUP BY status
    ORDER BY count DESC
    """
    return pd.read_sql_query(query, conn)