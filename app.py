import streamlit as st
import psycopg2
import os
from datetime import datetime
from databricks.sdk import WorkspaceClient

# Page configuration
st.set_page_config(
    page_title="AI Support Ticket System",
    page_icon="🎫",
    layout="wide"
)

# Database connection using OAuth tokens
@st.cache_resource(ttl=600)  # Cache for 10 minutes
def get_db_password():
    """Generate OAuth token for Lakebase authentication."""
    w = WorkspaceClient()
    # For Autoscaling Lakebase, use the postgres API
    endpoint = "projects/ai-support-app/branches/production/endpoints/primary"
    try:
        cred = w.postgres.generate_database_credential(endpoint=endpoint)
        return cred.token
    except Exception as e:
        st.error(f"Token generation failed: {e}")
        return None

def get_db_connection():
    """Create a connection to the Lakebase Postgres database."""
    try:
        password = get_db_password()
        if not password:
            return None
            
        conn = psycopg2.connect(
            host=os.environ.get('PGHOST'),
            database=os.environ.get('PGDATABASE', 'databricks_postgres'),
            user=os.environ.get('PGUSER'),
            password=password,
            port=int(os.environ.get('PGPORT', 5432)),
            sslmode='require'
        )
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

# Initialize session state
if 'selected_ticket' not in st.session_state:
    st.session_state.selected_ticket = None
if 'view' not in st.session_state:
    st.session_state.view = 'list'

# Main UI
st.title("🎫 AI Support Ticket System")

# Sidebar navigation
with st.sidebar:
    st.header("Navigation")
    if st.button("📋 All Tickets", use_container_width=True):
        st.session_state.view = 'list'
        st.session_state.selected_ticket = None
        st.rerun()
    
    if st.button("➕ Create New Ticket", use_container_width=True):
        st.session_state.view = 'create'
        st.session_state.selected_ticket = None
        st.rerun()
    
    st.divider()
    st.caption("Powered by Lakebase & Databricks")

# View: List all tickets
if st.session_state.view == 'list':
    st.header("All Support Tickets")
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        
        # Fetch all tickets
        cursor.execute("""
            SELECT ticket_id, title, status, created_by, created_at,
                   (SELECT COUNT(*) FROM ticket_messages WHERE ticket_id = tickets.ticket_id) as message_count
            FROM tickets
            ORDER BY created_at DESC
        """)
        tickets = cursor.fetchall()
        
        if tickets:
            # Filter by status
            status_filter = st.multiselect(
                "Filter by status",
                ["open", "in_progress", "resolved"],
                default=["open", "in_progress", "resolved"]
            )
            
            # Display tickets as cards
            for ticket in tickets:
                ticket_id, title, status, created_by, created_at, message_count = ticket
                
                # Apply filter
                if status not in status_filter:
                    continue
                
                # Status badge color
                status_colors = {
                    "open": "🟢",
                    "in_progress": "🟡",
                    "resolved": "⚫"
                }
                
                with st.container():
                    col1, col2, col3 = st.columns([6, 2, 1])
                    
                    with col1:
                        st.markdown(f"### {status_colors.get(status, '⚪')} {title}")
                        st.caption(f"Ticket #{ticket_id} • Created by {created_by} • {created_at.strftime('%Y-%m-%d %H:%M')}")
                    
                    with col2:
                        st.markdown(f"**Status:** {status}")
                        st.caption(f"💬 {message_count} messages")
                    
                    with col3:
                        if st.button("View", key=f"view_{ticket_id}"):
                            st.session_state.selected_ticket = ticket_id
                            st.session_state.view = 'detail'
                            st.rerun()
                    
                    st.divider()
        else:
            st.info("No tickets found. Create your first ticket to get started!")
        
        cursor.close()
        conn.close()

# View: Ticket detail
elif st.session_state.view == 'detail' and st.session_state.selected_ticket:
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        
        # Fetch ticket details
        cursor.execute("""
            SELECT ticket_id, title, status, created_by, created_at
            FROM tickets
            WHERE ticket_id = %s
        """, (st.session_state.selected_ticket,))
        ticket = cursor.fetchone()
        
        if ticket:
            ticket_id, title, status, created_by, created_at = ticket
            
            # Back button
            if st.button("← Back to All Tickets"):
                st.session_state.view = 'list'
                st.session_state.selected_ticket = None
                st.rerun()
            
            st.header(f"Ticket #{ticket_id}: {title}")
            
            # Ticket info and status update
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Created by:** {created_by}")
                st.markdown(f"**Created at:** {created_at.strftime('%Y-%m-%d %H:%M')}")
            
            with col2:
                st.markdown("**Update Status:**")
                new_status = st.selectbox(
                    "Change status",
                    ["open", "in_progress", "resolved"],
                    index=["open", "in_progress", "resolved"].index(status),
                    key="status_select"
                )
                
                if new_status != status:
                    if st.button("Update Status"):
                        cursor.execute("""
                            UPDATE tickets
                            SET status = %s
                            WHERE ticket_id = %s
                        """, (new_status, ticket_id))
                        conn.commit()
                        st.success(f"Status updated to '{new_status}'")
                        st.rerun()
            
            st.divider()
            
            # Messages section
            st.subheader("💬 Messages")
            
            # Fetch messages
            cursor.execute("""
                SELECT message_id, message_text, author, created_at
                FROM ticket_messages
                WHERE ticket_id = %s
                ORDER BY created_at ASC
            """, (ticket_id,))
            messages = cursor.fetchall()
            
            # Display messages
            for message in messages:
                message_id, message_text, author, msg_created_at = message
                
                with st.container():
                    st.markdown(f"**{author}** • {msg_created_at.strftime('%Y-%m-%d %H:%M')}")
                    st.markdown(message_text)
                    st.divider()
            
            # Add new message form
            st.subheader("➕ Add Message")
            with st.form("add_message_form"):
                message_author = st.text_input("Your email", placeholder="your.email@company.com")
                message_text = st.text_area("Message", placeholder="Enter your message here...")
                
                submit_message = st.form_submit_button("Post Message")
                
                if submit_message:
                    if message_author and message_text:
                        cursor.execute("""
                            INSERT INTO ticket_messages (ticket_id, message_text, author)
                            VALUES (%s, %s, %s)
                        """, (ticket_id, message_text, message_author))
                        conn.commit()
                        st.success("Message posted successfully!")
                        st.rerun()
                    else:
                        st.error("Please fill in all fields.")
        
        cursor.close()
        conn.close()

# View: Create new ticket
elif st.session_state.view == 'create':
    st.header("Create New Ticket")
    
    # Back button
    if st.button("← Back to All Tickets"):
        st.session_state.view = 'list'
        st.rerun()
    
    with st.form("create_ticket_form"):
        ticket_title = st.text_input("Ticket Title", placeholder="Brief description of the issue")
        created_by = st.text_input("Your Email", placeholder="your.email@company.com")
        initial_message = st.text_area("Initial Message", placeholder="Provide details about your issue...")
        
        submit_ticket = st.form_submit_button("Create Ticket")
        
        if submit_ticket:
            if ticket_title and created_by and initial_message:
                conn = get_db_connection()
                if conn:
                    cursor = conn.cursor()
                    
                    # Insert new ticket
                    cursor.execute("""
                        INSERT INTO tickets (title, status, created_by)
                        VALUES (%s, 'open', %s)
                        RETURNING ticket_id
                    """, (ticket_title, created_by))
                    new_ticket_id = cursor.fetchone()[0]
                    
                    # Insert initial message
                    cursor.execute("""
                        INSERT INTO ticket_messages (ticket_id, message_text, author)
                        VALUES (%s, %s, %s)
                    """, (new_ticket_id, initial_message, created_by))
                    
                    conn.commit()
                    cursor.close()
                    conn.close()
                    
                    st.success(f"Ticket #{new_ticket_id} created successfully!")
                    st.session_state.selected_ticket = new_ticket_id
                    st.session_state.view = 'detail'
                    st.rerun()
            else:
                st.error("Please fill in all fields.")
