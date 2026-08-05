import streamlit as st
from datetime import datetime
import re
import lakebase

# Page configuration
st.set_page_config(
    page_title="AI Support Ticket System",
    page_icon="🎫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for improved visual design
st.markdown("""
<style>
    .stApp {
        background-color: #f8f9fa;
    }
    .ticket-card {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .priority-critical {
        border-left: 5px solid #dc3545;
    }
    .priority-high {
        border-left: 5px solid #fd7e14;
    }
    .priority-medium {
        border-left: 5px solid #ffc107;
    }
    .priority-low {
        border-left: 5px solid #28a745;
    }
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stat-card h3 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: bold;
    }
    .stat-card p {
        margin: 5px 0 0 0;
        font-size: 1rem;
        opacity: 0.9;
    }
    div.stButton > button {
        border-radius: 5px;
        font-weight: 500;
    }
    .delete-btn {
        background-color: #dc3545 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Utility functions
def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_title(title):
    """Validate ticket title."""
    if not title or len(title.strip()) == 0:
        return False, "Title cannot be empty"
    if len(title) < 10:
        return False, "Title must be at least 10 characters"
    if len(title) > 200:
        return False, "Title must be less than 200 characters"
    return True, ""

def validate_message(message):
    """Validate message text."""
    if not message or len(message.strip()) == 0:
        return False, "Message cannot be empty"
    if len(message) < 10:
        return False, "Message must be at least 10 characters"
    if len(message) > 5000:
        return False, "Message must be less than 5000 characters"
    return True, ""

def get_db_connection():
    """Create a connection to the Lakebase Postgres database."""
    try:
        return lakebase.connect()
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

def get_statistics(conn):
    """Get ticket statistics."""
    cursor = conn.cursor()
    
    stats = {}
    
    # Total tickets
    cursor.execute("SELECT COUNT(*) as count FROM tickets")
    stats['total'] = cursor.fetchone()['count']
    
    # By status
    cursor.execute("""
        SELECT status, COUNT(*) as count 
        FROM tickets 
        GROUP BY status
    """)
    stats['by_status'] = {row['status']: row['count'] for row in cursor.fetchall()}
    
    # By priority
    cursor.execute("""
        SELECT priority, COUNT(*) as count 
        FROM tickets 
        GROUP BY priority
    """)
    stats['by_priority'] = {row['priority']: row['count'] for row in cursor.fetchall()}
    
    # By category
    cursor.execute("""
        SELECT category, COUNT(*) as count 
        FROM tickets 
        GROUP BY category
    """)
    stats['by_category'] = {row['category']: row['count'] for row in cursor.fetchall()}
    
    cursor.close()
    return stats

# Initialize session state
if 'selected_ticket' not in st.session_state:
    st.session_state.selected_ticket = None
if 'view' not in st.session_state:
    st.session_state.view = 'list'
if 'delete_confirm' not in st.session_state:
    st.session_state.delete_confirm = None

# Main UI
st.title("🎫 AI Support Ticket System")
st.markdown("### Enterprise-grade support ticket management powered by Lakebase")

# Sidebar navigation
with st.sidebar:
    st.header("📋 Navigation")
    
    if st.button("🏠 Dashboard", use_container_width=True, type="primary"):
        st.session_state.view = 'dashboard'
        st.session_state.selected_ticket = None
        st.rerun()
    
    if st.button("📋 All Tickets", use_container_width=True):
        st.session_state.view = 'list'
        st.session_state.selected_ticket = None
        st.rerun()
    
    if st.button("➕ Create New Ticket", use_container_width=True):
        st.session_state.view = 'create'
        st.session_state.selected_ticket = None
        st.rerun()
    
    st.divider()
    
    # Quick stats in sidebar
    conn = get_db_connection()
    if conn:
        stats = get_statistics(conn)
        st.metric("Total Tickets", stats['total'])
        st.metric("Open", stats['by_status'].get('open', 0))
        st.metric("In Progress", stats['by_status'].get('in_progress', 0))
        st.metric("Resolved", stats['by_status'].get('resolved', 0))
        conn.close()
    
    st.divider()
    st.caption("Powered by Lakebase & Databricks")

# View: Dashboard with statistics
if st.session_state.view == 'dashboard':
    st.header("📊 Support Ticket Dashboard")
    
    conn = get_db_connection()
    if conn:
        stats = get_statistics(conn)
        
        # Overview metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
                <div class="stat-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                    <h3>{stats['total']}</h3>
                    <p>Total Tickets</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class="stat-card" style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%);">
                    <h3>{stats['by_status'].get('open', 0)}</h3>
                    <p>Open</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
                <div class="stat-card" style="background: linear-gradient(135deg, #ffc107 0%, #ff8800 100%);">
                    <h3>{stats['by_status'].get('in_progress', 0)}</h3>
                    <p>In Progress</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
                <div class="stat-card" style="background: linear-gradient(135deg, #6c757d 0%, #495057 100%);">
                    <h3>{stats['by_status'].get('resolved', 0)}</h3>
                    <p>Resolved</p>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Priority and Category breakdown
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📌 By Priority")
            priority_order = ['critical', 'high', 'medium', 'low']
            priority_colors = {
                'critical': '🔴',
                'high': '🟠',
                'medium': '🟡',
                'low': '🟢'
            }
            for priority in priority_order:
                count = stats['by_priority'].get(priority, 0)
                st.markdown(f"{priority_colors[priority]} **{priority.title()}**: {count} tickets")
        
        with col2:
            st.subheader("📁 By Category")
            category_icons = {
                'general': '📋',
                'technical': '⚙️',
                'billing': '💳',
                'feature_request': '💡',
                'bug': '🐛'
            }
            for category, count in stats['by_category'].items():
                icon = category_icons.get(category, '📋')
                st.markdown(f"{icon} **{category.replace('_', ' ').title()}**: {count} tickets")
        
        conn.close()

# View: List all tickets
elif st.session_state.view == 'list':
    st.header("All Support Tickets")
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        
        # Enhanced filtering
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_filter = st.multiselect(
                "🔄 Filter by Status",
                ["open", "in_progress", "resolved"],
                default=["open", "in_progress"]
            )
        
        with col2:
            priority_filter = st.multiselect(
                "📌 Filter by Priority",
                ["critical", "high", "medium", "low"],
                default=["critical", "high", "medium", "low"]
            )
        
        with col3:
            category_filter = st.multiselect(
                "📁 Filter by Category",
                ["general", "technical", "billing", "feature_request", "bug"],
                default=["general", "technical", "billing", "feature_request", "bug"]
            )
        
        # Fetch all tickets with new fields
        cursor.execute("""
            SELECT ticket_id, title, status, priority, category, created_by, created_at,
                   (SELECT COUNT(*) FROM ticket_messages WHERE ticket_id = tickets.ticket_id) as message_count
            FROM tickets
            ORDER BY 
                CASE priority 
                    WHEN 'critical' THEN 1
                    WHEN 'high' THEN 2
                    WHEN 'medium' THEN 3
                    WHEN 'low' THEN 4
                END,
                created_at DESC
        """)
        tickets = cursor.fetchall()
        
        if tickets:
            # Display tickets as enhanced cards
            filtered_count = 0
            for ticket in tickets:
                # Apply filters
                if (ticket['status'] not in status_filter or 
                    ticket['priority'] not in priority_filter or 
                    ticket['category'] not in category_filter):
                    continue
                
                filtered_count += 1
                
                # Priority and status styling
                priority_icons = {
                    'critical': '🔴',
                    'high': '🟠',
                    'medium': '🟡',
                    'low': '🟢'
                }
                
                status_icons = {
                    'open': '🟢',
                    'in_progress': '🟡',
                    'resolved': '⚫'
                }
                
                category_icons = {
                    'general': '📋',
                    'technical': '⚙️',
                    'billing': '💳',
                    'feature_request': '💡',
                    'bug': '🐛'
                }
                
                priority_class = f"priority-{ticket['priority']}"
                
                # Create card
                with st.container():
                    st.markdown(f'<div class="ticket-card {priority_class}">', unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns([6, 3, 1])
                    
                    with col1:
                        st.markdown(f"### {ticket['title']}")
                        st.caption(f"Ticket #{ticket['ticket_id']} • Created by {ticket['created_by']} • {ticket['created_at'].strftime('%Y-%m-%d %H:%M')}")
                    
                    with col2:
                        st.markdown(f"**Status:** {status_icons.get(ticket['status'], '')} {ticket['status']}")
                        st.markdown(f"**Priority:** {priority_icons.get(ticket['priority'], '')} {ticket['priority'].title()}")
                        st.markdown(f"**Category:** {category_icons.get(ticket['category'], '')} {ticket['category'].replace('_', ' ').title()}")
                        st.caption(f"💬 {ticket['message_count']} messages")
                    
                    with col3:
                        if st.button("View", key=f"view_{ticket['ticket_id']}", use_container_width=True):
                            st.session_state.selected_ticket = ticket['ticket_id']
                            st.session_state.view = 'detail'
                            st.rerun()
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
            
            if filtered_count == 0:
                st.info("No tickets match the current filters. Try adjusting your filter selections.")
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
            SELECT ticket_id, title, status, priority, category, created_by, created_at
            FROM tickets
            WHERE ticket_id = %s
        """, (st.session_state.selected_ticket,))
        ticket = cursor.fetchone()
        
        if ticket:
            # Back button
            if st.button("← Back to All Tickets"):
                st.session_state.view = 'list'
                st.session_state.selected_ticket = None
                st.rerun()
            
            # Ticket header
            priority_icons = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}
            st.header(f"Ticket #{ticket['ticket_id']}: {ticket['title']}")
            st.markdown(f"{priority_icons.get(ticket['priority'], '')} **{ticket['priority'].upper()} Priority**")
            
            # Ticket info and management
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.markdown(f"**Created by:** {ticket['created_by']}")
                st.markdown(f"**Created at:** {ticket['created_at'].strftime('%Y-%m-%d %H:%M')}")
                st.markdown(f"**Category:** {ticket['category'].replace('_', ' ').title()}")
            
            with col2:
                st.markdown("**Update Status:**")
                new_status = st.selectbox(
                    "Change status",
                    ["open", "in_progress", "resolved"],
                    index=["open", "in_progress", "resolved"].index(ticket['status']),
                    key="status_select"
                )
                
                if new_status != ticket['status']:
                    if st.button("✓ Update Status", type="primary"):
                        cursor.execute("""
                            UPDATE tickets
                            SET status = %s
                            WHERE ticket_id = %s
                        """, (new_status, ticket['ticket_id']))
                        conn.commit()
                        st.success(f"Status updated to '{new_status}'")
                        st.rerun()
            
            with col3:
                st.markdown("**Danger Zone:**")
                if st.session_state.delete_confirm == ticket['ticket_id']:
                    st.warning("Are you sure?")
                    col_yes, col_no = st.columns(2)
                    with col_yes:
                        if st.button("Yes, Delete", key="confirm_delete"):
                            # Delete messages first (foreign key)
                            cursor.execute("DELETE FROM ticket_messages WHERE ticket_id = %s", (ticket['ticket_id'],))
                            # Delete ticket
                            cursor.execute("DELETE FROM tickets WHERE ticket_id = %s", (ticket['ticket_id'],))
                            conn.commit()
                            st.session_state.delete_confirm = None
                            st.session_state.view = 'list'
                            st.success("Ticket deleted successfully!")
                            st.rerun()
                    with col_no:
                        if st.button("Cancel", key="cancel_delete"):
                            st.session_state.delete_confirm = None
                            st.rerun()
                else:
                    if st.button("🗑️ Delete", key=f"delete_{ticket['ticket_id']}"):
                        st.session_state.delete_confirm = ticket['ticket_id']
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
            """, (ticket['ticket_id'],))
            messages = cursor.fetchall()
            
            # Display messages
            for message in messages:
                with st.container():
                    st.markdown(f"**{message['author']}** • {message['created_at'].strftime('%Y-%m-%d %H:%M')}")
                    st.markdown(message['message_text'])
                    st.divider()
            
            # Add new message form
            st.subheader("➕ Add Message")
            with st.form("add_message_form"):
                message_author = st.text_input("Your email *", placeholder="your.email@company.com")
                message_text = st.text_area("Message *", placeholder="Enter your message here...", height=150)
                
                submit_message = st.form_submit_button("Post Message", type="primary")
                
                if submit_message:
                    # Validate inputs
                    errors = []
                    
                    if not message_author:
                        errors.append("Email is required")
                    elif not validate_email(message_author):
                        errors.append("Please enter a valid email address (e.g., user@company.com)")
                    
                    is_valid, error_msg = validate_message(message_text)
                    if not is_valid:
                        errors.append(error_msg)
                    
                    if errors:
                        for error in errors:
                            st.error(f"❌ {error}")
                    else:
                        cursor.execute("""
                            INSERT INTO ticket_messages (ticket_id, message_text, author)
                            VALUES (%s, %s, %s)
                        """, (ticket['ticket_id'], message_text, message_author))
                        conn.commit()
                        st.success("✅ Message posted successfully!")
                        st.rerun()
        
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
        st.markdown("### Ticket Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            priority = st.selectbox(
                "Priority *",
                ["low", "medium", "high", "critical"],
                index=1,
                help="Select the urgency level of this ticket"
            )
        
        with col2:
            category = st.selectbox(
                "Category *",
                ["general", "technical", "billing", "feature_request", "bug"],
                help="Select the type of issue"
            )
        
        ticket_title = st.text_input(
            "Ticket Title *", 
            placeholder="Brief description of the issue (10-200 characters)",
            max_chars=200,
            help="Provide a clear, concise title for your ticket"
        )
        
        created_by = st.text_input(
            "Your Email *", 
            placeholder="your.email@company.com",
            help="We'll use this to contact you about the ticket"
        )
        
        initial_message = st.text_area(
            "Initial Message *", 
            placeholder="Provide details about your issue... (10-5000 characters)",
            height=200,
            max_chars=5000,
            help="Include as much detail as possible to help us resolve your issue quickly"
        )
        
        st.caption("* Required fields")
        
        submit_ticket = st.form_submit_button("Create Ticket", type="primary", use_container_width=True)
        
        if submit_ticket:
            # Validate all inputs
            errors = []
            
            is_valid, error_msg = validate_title(ticket_title)
            if not is_valid:
                errors.append(f"Title: {error_msg}")
            
            if not created_by:
                errors.append("Email is required")
            elif not validate_email(created_by):
                errors.append("Please enter a valid email address (e.g., user@company.com)")
            
            is_valid, error_msg = validate_message(initial_message)
            if not is_valid:
                errors.append(f"Message: {error_msg}")
            
            if errors:
                st.error("❌ Please fix the following errors:")
                for error in errors:
                    st.error(f"  • {error}")
            else:
                conn = get_db_connection()
                if conn:
                    cursor = conn.cursor()
                    
                    try:
                        # Insert new ticket with priority and category
                        cursor.execute("""
                            INSERT INTO tickets (title, status, priority, category, created_by)
                            VALUES (%s, 'open', %s, %s, %s)
                            RETURNING ticket_id
                        """, (ticket_title, priority, category, created_by))
                        new_ticket_id = cursor.fetchone()['ticket_id']
                        
                        # Insert initial message
                        cursor.execute("""
                            INSERT INTO ticket_messages (ticket_id, message_text, author)
                            VALUES (%s, %s, %s)
                        """, (new_ticket_id, initial_message, created_by))
                        
                        conn.commit()
                        cursor.close()
                        conn.close()
                        
                        st.success(f"✅ Ticket #{new_ticket_id} created successfully!")
                        st.balloons()
                        st.session_state.selected_ticket = new_ticket_id
                        st.session_state.view = 'detail'
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error creating ticket: {e}")
                        cursor.close()
                        conn.close()
