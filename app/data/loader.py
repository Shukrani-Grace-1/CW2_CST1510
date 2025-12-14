import pandas as pd
from pathlib import Path


def _table_row_count(conn, table_name: str) -> int:
    """Return how many rows are currently in a table."""
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM {table_name}")
    return int(cur.fetchone()[0])


def load_all_csv_data(conn):
    """Load the 3 coursework CSV files into the 3 SQLite tables.

    This version is intentionally *simple*:
    - Read CSV with pandas
    - Build a NEW DataFrame that matches the table schema columns exactly
    - Append into SQLite with df.to_sql(...)

    It also SKIPS loading if a table already has data (prevents duplicates).

    Returns:
        int: total number of rows loaded across all tables.
    """

    total_rows = 0
    base_path = Path(__file__).resolve().parents[2] / "DATA"

    # -----------------------------
    # 1) cyber_incidents.csv  -> cyber_incidents table
    # Table schema columns:
    #   date, incident_type, severity, status, description, reported_by
    # CSV columns:
    #   incident_id, timestamp, severity, category, status, description
    # -----------------------------
    if _table_row_count(conn, "cyber_incidents") == 0:
        cyber_csv = base_path / "cyber_incidents.csv"
        if cyber_csv.exists():
            df = pd.read_csv(cyber_csv)

            # Build schema-matching DataFrame
            out = pd.DataFrame()
            out["date"] = df["timestamp"].astype(str)                 # timestamp -> date
            out["incident_type"] = df["category"].astype(str)          # category -> incident_type
            out["severity"] = df["severity"].astype(str)
            out["status"] = df["status"].astype(str)
            out["description"] = df["description"].astype(str)
            out["reported_by"] = None                                 # CSV doesn't have this

            out.to_sql("cyber_incidents", conn, if_exists="append", index=False)
            total_rows += len(out)
            print(f"       Loaded {len(out)} rows into cyber_incidents")
        else:
            print("       cyber_incidents.csv not found in DATA/")
    else:
        print("       Skipping cyber_incidents (table already has data)")

    # -----------------------------
    # 2) datasets_metadata.csv -> datasets_metadata table
    # Table schema columns:
    #   dataset_name, category, source, last_updated, record_count, file_size_mb
    # CSV columns:
    #   dataset_id, name, rows, columns, uploaded_by, upload_date
    # -----------------------------
    if _table_row_count(conn, "datasets_metadata") == 0:
        datasets_csv = base_path / "datasets_metadata.csv"
        if datasets_csv.exists():
            df = pd.read_csv(datasets_csv)

            out = pd.DataFrame()
            out["dataset_name"] = df["name"].astype(str)
            out["category"] = None                                   # CSV doesn't have category
            out["source"] = df["uploaded_by"].astype(str)             # use uploader as source
            out["last_updated"] = df["upload_date"].astype(str)
            out["record_count"] = pd.to_numeric(df["rows"], errors="coerce")
            out["file_size_mb"] = None                               # CSV doesn't have size

            out.to_sql("datasets_metadata", conn, if_exists="append", index=False)
            total_rows += len(out)
            print(f"       Loaded {len(out)} rows into datasets_metadata")
        else:
            print("       datasets_metadata.csv not found in DATA/")
    else:
        print("       Skipping datasets_metadata (table already has data)")

    # -----------------------------
    # 3) it_tickets.csv -> it_tickets table
    # Table schema columns:
    #   ticket_id, priority, status, category, subject, description,
    #   created_date, resolved_date
    # CSV columns:
    #   ticket_id, priority, description, status, assigned_to, created_at, resolution_time_hours
    # -----------------------------
    if _table_row_count(conn, "it_tickets") == 0:
        tickets_csv = base_path / "it_tickets.csv"
        if tickets_csv.exists():
            df = pd.read_csv(tickets_csv)

            out = pd.DataFrame()
            out["ticket_id"] = df["ticket_id"].astype(str)
            out["priority"] = df["priority"].astype(str)
            out["status"] = df["status"].astype(str)
            out["category"] = df["assigned_to"].astype(str)           # simple: assign-to as category
            out["subject"] = "Imported ticket"                         # CSV doesn't have subject
            out["description"] = df["description"].astype(str)
            out["created_date"] = df["created_at"].astype(str)

            # Optional: compute a resolved_date if we have resolution_time_hours
            created_dt = pd.to_datetime(df["created_at"], errors="coerce")
            hours = pd.to_numeric(df.get("resolution_time_hours"), errors="coerce")
            resolved_dt = created_dt + pd.to_timedelta(hours, unit="h")
            out["resolved_date"] = resolved_dt.dt.strftime("%Y-%m-%d %H:%M:%S")

            out.to_sql("it_tickets", conn, if_exists="append", index=False)
            total_rows += len(out)
            print(f"       Loaded {len(out)} rows into it_tickets")
        else:
            print("       it_tickets.csv not found in DATA/")
    else:
        print("       Skipping it_tickets (table already has data)")

    conn.commit()
    return total_rows