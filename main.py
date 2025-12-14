from app.data.db import connect_database
from app.data.schema import create_all_tables
from app.services.user_services import register_user, login_user, migrate_users_from_file
from app.data.incidents import insert_incident, get_all_incidents, get_incidents_by_type_count, get_high_severity_by_status, get_incident_types_with_many_cases 
from app.services.setup import setup_database_complete 

def main():
    setup_database_complete()
    print("week" * 20)
    print("Week 8: Database Demo")
    print("=" * 60)

    # Keep one connection open for the demo steps below
    conn = connect_database()

    #3.Test authentication
    try:
        success, msg = register_user("alice", "SecurePass123!", "analyst")
        print(msg)
        if not success:
            # If user already exists (or other non-fatal issue), just try logging in
            success, msg = login_user("alice", "SecurePass123!")
            print(msg)
    except Exception as e:
        # Don't stop the demo if registration fails (e.g., UNIQUE constraint on username)
        print(f"Auth step skipped due to error: {type(e).__name__}: {e}")

    try:
        #4.Test CRUD 
        incident_id = insert_incident(
            conn,
            "2024-11-05",
            "Phishing",
            "High",
            "Open",
            "Suspicious email detected",
            "alice"
        )

        print(f"Inserted incident id: {incident_id}")

        #Query data
        df = get_all_incidents(conn)
        print(f"Total incidents: {len(df)}")

        print("\nIncidents by Type:")
        print(get_incidents_by_type_count(conn))

        print("\nHigh Severity Incidents by Status:")
        print(get_high_severity_by_status(conn))

        print("\nIncident Types with Many Cases (>5):")
        print(get_incident_types_with_many_cases(conn, min_count=5))
    finally:
        conn.close()



if __name__ == "__main__":
    main()
    
