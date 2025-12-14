import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

# ---- Week 9 guard: only allow logged-in users ----
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

if not st.session_state.logged_in:
    st.error("You must be logged in to view the dashboard.")
    if st.button("Go to login page"):
        st.switch_page("Home.py")
    st.stop()

# ---- Imports that depend on your app code ----
from app.data.db import connect_database
from app.data.incidents import (
    get_all_incidents,
    insert_incident,
    update_incident_status,
    delete_incident,
    get_incidents_by_type_count,
    get_high_severity_by_status,
)
from app.data.tickets import (
    get_all_tickets,
    insert_ticket,
    update_ticket_status,
    update_ticket_priority,
    delete_ticket,
    get_tickets_by_status_count,
)


# ---- Small plotting helper (Plotly if installed) ----
def _bar_chart(df: pd.DataFrame, x: str, y: str, title: str):
    try:
        import plotly.express as px

        fig = px.bar(df, x=x, y=y, title=title)
        st.plotly_chart(fig, use_container_width=True)
    except Exception:
        st.subheader(title)
        st.bar_chart(df.set_index(x)[y])


def _line_chart(df: pd.DataFrame, x: str, y: str, title: str):
    try:
        import plotly.express as px

        fig = px.line(df, x=x, y=y, title=title)
        st.plotly_chart(fig, use_container_width=True)
    except Exception:
        st.subheader(title)
        st.line_chart(df.set_index(x)[y])


# ---- Cached reads ----
@st.cache_data(ttl=10)
def _load_incidents() -> pd.DataFrame:
    conn = connect_database()
    try:
        return get_all_incidents(conn)
    finally:
        conn.close()


@st.cache_data(ttl=10)
def _load_tickets() -> pd.DataFrame:
    conn = connect_database()
    try:
        return get_all_tickets(conn)
    finally:
        conn.close()


def _refresh_data():
    _load_incidents.clear()
    _load_tickets.clear()


# ---- Page header ----
st.title("📊 Dashboard")
st.success(f"Hello, **{st.session_state.username}**! You are logged in.")
st.caption("Week 9: Interactive dashboards with CRUD + visualisations.")

# ---- Sidebar controls ----
with st.sidebar:
    st.header("Controls")
    if st.button("🔄 Refresh data", use_container_width=True):
        _refresh_data()
        st.rerun()

    st.divider()
    st.subheader("Global filters")
    show_limit = st.slider("Rows to show", 10, 300, 50)

    st.divider()
    if st.button("Log out", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.switch_page("Home.py")


# =============================
# Tabs for two completed domains
# =============================
inc_tab, ticket_tab = st.tabs(["🛡️ Cyber Incidents", "🎫 IT Tickets"])


# -----------------------------
# CIBERSECURITY: Incidents domain
# -----------------------------
with inc_tab:
    incidents = _load_incidents()

    # --- Filters ---
    c1, c2, c3 = st.columns(3)
    with c1:
        sev_filter = st.multiselect(
            "Severity",
            options=sorted([x for x in incidents["severity"].dropna().unique()]),
            default=sorted([x for x in incidents["severity"].dropna().unique()]),
        )
    with c2:
        status_filter = st.multiselect(
            "Status",
            options=sorted([x for x in incidents["status"].dropna().unique()]),
            default=sorted([x for x in incidents["status"].dropna().unique()]),
        )
    with c3:
        type_filter = st.multiselect(
            "Incident type",
            options=sorted([x for x in incidents["incident_type"].dropna().unique()]),
            default=sorted([x for x in incidents["incident_type"].dropna().unique()]),
        )

    filt = incidents.copy()
    if sev_filter:
        filt = filt[filt["severity"].isin(sev_filter)]
    if status_filter:
        filt = filt[filt["status"].isin(status_filter)]
    if type_filter:
        filt = filt[filt["incident_type"].isin(type_filter)]

    # --- KPIs ---
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Incidents (filtered)", int(len(filt)))
    k2.metric("Open", int((filt["status"] == "Open").sum()))
    k3.metric("High severity", int((filt["severity"] == "High").sum()))
    k4.metric("Unique types", int(filt["incident_type"].nunique()))

    st.divider()

    # --- Visualisations ---
    v1, v2 = st.columns(2)

    with v1:
        # Incidents by type
        try:
            conn = connect_database()
            type_counts = get_incidents_by_type_count(conn)
        finally:
            conn.close()
        _bar_chart(type_counts, x="incident_type", y="count", title="Incidents by Type")

    with v2:
        # High severity by status
        try:
            conn = connect_database()
            high_by_status = get_high_severity_by_status(conn)
        finally:
            conn.close()
        _bar_chart(high_by_status, x="status", y="count", title="High Severity Incidents by Status")

    # Incidents over time (based on the date column)
    # Keep it easy: group by date string (YYYY-MM-DD)
    if "date" in filt.columns and len(filt) > 0:
        tmp = filt.copy()
        tmp["date"] = pd.to_datetime(tmp["date"], errors="coerce")
        tmp = tmp.dropna(subset=["date"])
        if len(tmp) > 0:
            daily = (
                tmp.assign(day=tmp["date"].dt.date)
                .groupby("day", as_index=False)
                .size()
                .rename(columns={"size": "count"})
            )
            _line_chart(daily, x="day", y="count", title="Incidents Over Time")

    st.divider()

    # --- Table ---
    st.subheader("Incident records")
    st.dataframe(filt.head(show_limit), use_container_width=True)

    st.divider()

    # --- CRUD ---
    st.subheader("CRUD: Incidents")

    with st.expander("➕ Create incident"):
        with st.form("create_incident_form", clear_on_submit=True):
            date = st.text_input("Date (YYYY-MM-DD)", value="2024-11-05")
            incident_type = st.text_input("Incident type", value="Phishing")
            severity = st.selectbox("Severity", ["Low", "Medium", "High"], index=2)
            status = st.selectbox("Status", ["Open", "In Progress", "Resolved", "Closed"], index=0)
            description = st.text_area("Description", value="Describe the incident...")
            reported_by = st.text_input("Reported by (optional)", value=st.session_state.username or "")

            submitted = st.form_submit_button("Create", type="primary")
            if submitted:
                conn = connect_database()
                try:
                    new_id = insert_incident(conn, date, incident_type, severity, status, description, reported_by)
                finally:
                    conn.close()
                st.success(f"Created incident with id={new_id}")
                _refresh_data()
                st.rerun()

    with st.expander("✏️ Update incident status"):
        with st.form("update_incident_status_form"):
            incident_id = st.number_input("Incident DB id", min_value=1, step=1)
            new_status = st.selectbox("New status", ["Open", "In Progress", "Resolved", "Closed"])
            submitted = st.form_submit_button("Update", type="primary")
            if submitted:
                conn = connect_database()
                try:
                    rows = update_incident_status(conn, int(incident_id), new_status)
                finally:
                    conn.close()
                if rows == 0:
                    st.warning("No incident updated (check the id).")
                else:
                    st.success("Incident status updated.")
                _refresh_data()
                st.rerun()

    with st.expander("🗑️ Delete incident"):
        with st.form("delete_incident_form"):
            incident_id = st.number_input("Incident DB id to delete", min_value=1, step=1, key="del_inc_id")
            submitted = st.form_submit_button("Delete", type="primary")
            if submitted:
                conn = connect_database()
                try:
                    rows = delete_incident(conn, int(incident_id))
                finally:
                    conn.close()
                if rows == 0:
                    st.warning("No incident deleted (check the id).")
                else:
                    st.success("Incident deleted.")
                _refresh_data()
                st.rerun()


# -----------------------------
# IT Tickets domain
# -----------------------------
with ticket_tab:
    tickets = _load_tickets()

    c1, c2, c3 = st.columns(3)
    with c1:
        prio_filter = st.multiselect(
            "Priority",
            options=sorted([x for x in tickets["priority"].dropna().unique()]),
            default=sorted([x for x in tickets["priority"].dropna().unique()]),
        )
    with c2:
        status_filter = st.multiselect(
            "Status",
            options=sorted([x for x in tickets["status"].dropna().unique()]),
            default=sorted([x for x in tickets["status"].dropna().unique()]),
        )
    with c3:
        cat_filter = st.multiselect(
            "Category",
            options=sorted([x for x in tickets["category"].dropna().unique()]),
            default=sorted([x for x in tickets["category"].dropna().unique()]),
        )

    tf = tickets.copy()
    if prio_filter:
        tf = tf[tf["priority"].isin(prio_filter)]
    if status_filter:
        tf = tf[tf["status"].isin(status_filter)]
    if cat_filter:
        tf = tf[tf["category"].isin(cat_filter)]

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Tickets (filtered)", int(len(tf)))
    k2.metric("Open", int((tf["status"] == "Open").sum()))
    k3.metric("High priority", int((tf["priority"] == "High").sum()))
    k4.metric("Unique categories", int(tf["category"].nunique()))

    st.divider()

    v1, v2 = st.columns(2)
    with v1:
        try:
            conn = connect_database()
            by_status = get_tickets_by_status_count(conn)
        finally:
            conn.close()
        _bar_chart(by_status, x="status", y="count", title="Tickets by Status")

    with v2:
        # Tickets by priority (quick calculation)
        pr = (
            tf.groupby("priority", as_index=False)
            .size()
            .rename(columns={"size": "count"})
        )
        _bar_chart(pr, x="priority", y="count", title="Tickets by Priority (filtered)")

    st.divider()

    st.subheader("Ticket records")
    st.dataframe(tf.head(show_limit), use_container_width=True)

    st.divider()

    st.subheader("CRUD: Tickets")

    with st.expander("➕ Create ticket"):
        with st.form("create_ticket_form", clear_on_submit=True):
            ticket_id = st.text_input("Ticket ID", value="T-0000")
            priority = st.selectbox("Priority", ["Low", "Medium", "High"], index=1)
            status = st.selectbox("Status", ["Open", "In Progress", "Resolved", "Closed"], index=0, key="ticket_status")
            category = st.text_input("Category", value="General")
            subject = st.text_input("Subject", value="New ticket")
            description = st.text_area("Description", value="Describe the issue...")
            created_date = st.text_input("Created date (YYYY-MM-DD HH:MM:SS)", value="")
            resolved_date = st.text_input("Resolved date (optional)", value="")

            submitted = st.form_submit_button("Create", type="primary")
            if submitted:
                conn = connect_database()
                try:
                    new_id = insert_ticket(
                        conn,
                        ticket_id=ticket_id,
                        priority=priority,
                        status=status,
                        category=category,
                        subject=subject,
                        description=description,
                        created_date=created_date or None,
                        resolved_date=resolved_date or None,
                    )
                finally:
                    conn.close()
                st.success(f"Created ticket row id={new_id}")
                _refresh_data()
                st.rerun()

    with st.expander("✏️ Update ticket status"):
        with st.form("update_ticket_status_form"):
            db_id = st.number_input("Ticket DB id", min_value=1, step=1)
            new_status = st.selectbox("New status", ["Open", "In Progress", "Resolved", "Closed"], key="ticket_new_status")
            submitted = st.form_submit_button("Update", type="primary")
            if submitted:
                conn = connect_database()
                try:
                    rows = update_ticket_status(conn, int(db_id), new_status)
                finally:
                    conn.close()
                if rows == 0:
                    st.warning("No ticket updated (check the DB id).")
                else:
                    st.success("Ticket status updated.")
                _refresh_data()
                st.rerun()

    with st.expander("⚡ Update ticket priority"):
        with st.form("update_ticket_priority_form"):
            db_id = st.number_input("Ticket DB id ", min_value=1, step=1, key="prio_dbid")
            new_priority = st.selectbox("New priority", ["Low", "Medium", "High"], key="ticket_new_priority")
            submitted = st.form_submit_button("Update", type="primary")
            if submitted:
                conn = connect_database()
                try:
                    rows = update_ticket_priority(conn, int(db_id), new_priority)
                finally:
                    conn.close()
                if rows == 0:
                    st.warning("No ticket updated (check the DB id).")
                else:
                    st.success("Ticket priority updated.")
                _refresh_data()
                st.rerun()

    with st.expander("🗑️ Delete ticket"):
        with st.form("delete_ticket_form"):
            db_id = st.number_input("Ticket DB id to delete", min_value=1, step=1, key="del_ticket")
            submitted = st.form_submit_button("Delete", type="primary")
            if submitted:
                conn = connect_database()
                try:
                    rows = delete_ticket(conn, int(db_id))
                finally:
                    conn.close()
                if rows == 0:
                    st.warning("No ticket deleted (check the DB id).")
                else:
                    st.success("Ticket deleted.")
                _refresh_data()
                st.rerun()
