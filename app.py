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

# Improved CSS - simpler and compatible
st.markdown("""
<style>
    /* Main styling */
    .main {
        padding: 2rem;
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem;
        font-weight: bold;
    }
    
    /* Better spacing */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-weight: 500;
        font-size: 0.875rem;
    }
    
    .status-open { background-color: #28a745; color: white; }
    .status-in_progress { background-color: #ffc107; color: black; }
    .status-resolved { background-color: #6c757d; color: white; }
    
    .priority-critical { background-color: #dc3545; color: white; }
    .priority-high { background-color: #fd7e14; color: white; }
    .priority-medium { background-color: #ffc107; color: black; }
    .priority-low { background-color: #28a745; color: white; }
    
    /* Better buttons */
    .stButton button {
        border-radius: 0.5rem;
        font-weight: 500;
        transition: all 0.2s;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
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
        st.error(f"❌ Database connection failed: {e}")
        return None

def get_statistics(conn):
    """Get ticket statistics."""
    cursor = conn.cursor()
    
    stats = {}
    
    # Total tickets
    cursor.execute("SELECT COUNT(*) as count FROM tickets")
    stats['total'] = cursor.fetchone()['count']
    
    # By status
    cursor.execute("SELECT status, COUNT(*) as count FROM tickets GROUP BY status")
    stats['by_status'] = {row['status']: row['count'] for row in cursor.fetchall()}
    
    # By priority
    cursor.execute("SELECT priority, COUNT(*) as count FROM tickets GROUP BY priority")
    stats['by_priority'] = {row['priority']: row['count'] for row in cursor.fetchall()}
    
    # By category
    cursor.execute("SELECT category, COUNT(*) as count FROM tickets GROUP BY category")
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

# Sidebar navigation
with st.sidebar:
    st.title("📋 Navigation")
    
    if st.button("🏠 Dashboard", use_container_width=True, type="primary" if st.session_state.view == 'dashboard' else "secondary"):
        st.session_state.view = 'dashboard'
        st.session_state.selected_ticket = None
        st.rerun()
    
    if st.button("📋 All Tickets", use_container_width=True, type="primary" if st.session_state.view == 'list' else "secondary"):
        st.session_state.view = 'list'
        st.session_state.selected_ticket = None
        st.rerun()
    
    if st.button("➕ Create New Ticket", use_container_width=True, type="primary" if st.session_state.view == 'create' else "secondary"):
        st.session_state.view = 'create'
        st.session_state.selected_ticket = None
        st.rerun()
    
    st.divider()
    
    # Quick stats in sidebar
    conn = get_db_connection()
    if conn:
        stats = get_statistics(conn)
        st.metric("📊 Total Tickets", stats['total'])
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("🟢 Open", stats['by_status'].get('open', 0))
            st.metric("🟡 In Progress", stats['by_status'].get('in_progress', 0))
        with col2:
            st.metric("⚫ Resolved", stats['by_status'].get('resolved', 0))
        
        conn.close()
    
    st.divider()
    st.caption("Powered by Lakebase & Databricks")

# Main content area
st.title("🎫 AI Support Ticket System")

# View: Dashboard with statistics
if st.session_state.view == 'dashboard':
    st.header("📊 Support Ticket Dashboard")
    st.markdown("---")
    
    conn = get_db_connection()
    if conn:
        stats = get_statistics(conn)
        
        # Overview metrics in cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="📋 Total Tickets",
                value=stats['total'],
                delta=None,
                help="Total number of support tickets"
            )
        
        with col2:
            st.metric(
                label="🟢 Open",
                value=stats['by_status'].get('open', 0),
                delta=None,
                help="Currently open tickets"
            )
        
        with col3:
            st.metric(
                label="🟡 In Progress",
                value=stats['by_status'].get('in_progress', 0),
                delta=None,
                help="Tickets being worked on"
            )
        
        with col4:
            st.metric(
                label="⚫ Resolved",
                value=stats['by_status'].get('resolved', 0),
                delta=None,
                help="Completed tickets"
            )
        
        st.markdown("---")
        
        # Detailed breakdown
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📌 Priority Distribution")
            priority_order = ['critical', 'high', 'medium', 'low']
            priority_emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}
            
            for priority in priority_order:
                count = stats['by_priority'].get(priority, 0)
                st.markdown(f"{priority_emoji[priority]} **{priority.title()}**: {count} tickets")
        
        with col2:
            st.subheader("📁 Category Distribution")
            category_emoji = {
                'general': '📋',
                'technical': '⚙️',
                'billing': '💳',
                'feature_request': '💡',
                'bug': '🐛'
            }
            
            for category, count in stats['by_category'].items():
                emoji = category_emoji.get(category, '📋')
                label = category.replace('_', ' ').title()
                st.markdown(f"{emoji} **{label}**: {count} tickets")
        
        conn.close()

# View: List all tickets
elif st.session_state.view == 'list':
    st.header("All Support Tickets")
    st.markdown("---")
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        
        # Filters in columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_filter = st.multiselect(
                "🔄 Status",
                ["open", "in_progress", "resolved"],
                default=["open", "in_progress"]
            )
        
        with col2:
            priority_filter = st.multiselect(
                "📌 Priority",
                ["critical", "high", "medium", "low"],
                default=["critical", "high", "medium", "low"]
            )
        
        with col3:
            category_filter = st.multiselect(
                "📁 Category",
                ["general", "technical", "billing", "feature_request", "bug"],
                default=["general", "technical", "billing", "feature_request", "bug"]
            )
        
        st.markdown("---")
        
        # Fetch tickets
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
            filtered_count = 0
            
            for ticket in tickets:
                # Apply filters
                if (ticket['status'] not in status_filter or 
                    ticket['priority'] not in priority_filter or 
                    ticket['category'] not in category_filter):
                    continue
                
                filtered_count += 1
                
                # Display ticket in expander or container
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                    
                    with col1:
                        st.markdown(f"### {ticket['title']}")
                        st.caption(f"Ticket #{ticket['ticket_id']} • {ticket['created_by']} • {ticket['created_at'].strftime('%Y-%m-%d %H:%M')}")
                    
                    with col2:
                        # Status badge
                        status_class = f"status-{ticket['status']}"
                        st.markdown(f'<span class="status-badge {status_class}">{ticket["status"]}</span>', unsafe_allow_html=True)
                    
                    with col3:
                        # Priority badge
                        priority_class = f"priority-{ticket['priority']}"
                        st.markdown(f'<span class="status-badge {priority_class}">{ticket["priority"]}</span>', unsafe_allow_html=True)
                        st.caption(f"📁 {ticket['category'].replace('_', ' ').title()}")
                    
                    with col4:
                        st.caption(f"💬 {ticket['message_count']} messages")
                        if st.button("View Details", key=f"view_{ticket['ticket_id']}", use_container_width=True):
                            st.session_state.selected_ticket = ticket['ticket_id']
                            st.session_state.view = 'detail'
                            st.rerun()
                    
                    st.divider()
            
            if filtered_count == 0:
                st.info("ℹ️ No tickets match the current filters. Try adjusting your selections.")
        else:
            st.info("ℹ️ No tickets found. Create your first ticket to get started!")
        
        cursor.close()
        conn.close()

# View: Ticket detail
elif st.session_state.view == 'detail' and st.session_state.selected_ticket:
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        
        # Fetch ticket
        cursor.execute("""
            SELECT ticket_id, title, status, priority, category, created_by, created_at
            FROM tickets
            WHERE ticket_id = %s
        """, (st.session_state.selected_ticket,))
        ticket = cursor.fetchone()
        
        if ticket:
            # Back button
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("← Back", use_container_width=True):
                    st.session_state.view = 'list'
                    st.session_state.selected_ticket = None
                    st.rerun()
            
            # Ticket header
            st.title(f"Ticket #{ticket['ticket_id']}")
            st.subheader(ticket['title'])
            
            # Badges
            col1, col2, col3 = st.columns([1, 1, 3])
            with col1:
                status_class = f"status-{ticket['status']}"
                st.markdown(f'<span class="status-badge {status_class}">{ticket["status"]}</span>', unsafe_allow_html=True)
            with col2:
                priority_class = f"priority-{ticket['priority']}"
                st.markdown(f'<span class="status-badge {priority_class}">{ticket["priority"]}</span>', unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Ticket info and management
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.markdown(f"**Created by:** {ticket['created_by']}")
                st.markdown(f"**Created:** {ticket['created_at'].strftime('%Y-%m-%d %H:%M')}")
                st.markdown(f"**Category:** {ticket['category'].replace('_', ' ').title()}")
            
            with col2:
                st.markdown("**Update Status:**")
                new_status = st.selectbox(
                    "Select new status",
                    ["open", "in_progress", "resolved"],
                    index=["open", "in_progress", "resolved"].index(ticket['status']),
                    label_visibility="collapsed"
                )
                
                if new_status != ticket['status']:
                    if st.button("✓ Update Status", type="primary", use_container_width=True):
                        cursor.execute("UPDATE tickets SET status = %s WHERE ticket_id = %s", 
                                     (new_status, ticket['ticket_id']))
                        conn.commit()
                        st.success(f"✅ Status updated to '{new_status}'")
                        st.rerun()
            
            with col3:
                st.markdown("**Actions:**")
                if st.session_state.delete_confirm == ticket['ticket_id']:
                    st.warning("⚠️ Confirm delete?")
                    if st.button("✓ Yes, Delete", key="confirm_delete", use_container_width=True):
                        cursor.execute("DELETE FROM ticket_messages WHERE ticket_id = %s", (ticket['ticket_id'],))
                        cursor.execute("DELETE FROM tickets WHERE ticket_id = %s", (ticket['ticket_id'],))
                        conn.commit()
                        st.session_state.delete_confirm = None
                        st.session_state.view = 'list'
                        st.success("✅ Ticket deleted!")
                        st.rerun()
                    if st.button("✗ Cancel", key="cancel_delete", use_container_width=True):
                        st.session_state.delete_confirm = None
                        st.rerun()
                else:
                    if st.button("🗑️ Delete Ticket", key=f"delete_{ticket['ticket_id']}", use_container_width=True):
                        st.session_state.delete_confirm = ticket['ticket_id']
                        st.rerun()
            
            st.markdown("---")
            
            # Messages
            st.subheader("💬 Messages")
            
            cursor.execute("""
                SELECT message_id, message_text, author, created_at
                FROM ticket_messages
                WHERE ticket_id = %s
                ORDER BY created_at ASC
            """, (ticket['ticket_id'],))
            messages = cursor.fetchall()
            
            for message in messages:
                with st.container():
                    st.markdown(f"**{message['author']}** • {message['created_at'].strftime('%Y-%m-%d %H:%M')}")
                    st.markdown(message['message_text'])
                    st.divider()
            
            # Add message form
            st.subheader("➕ Add Message")
            with st.form("add_message_form", clear_on_submit=True):
                col1, col2 = st.columns([1, 3])
                with col1:
                    message_author = st.text_input("Email *", placeholder="your.email@company.com")
                with col2:
                    message_text = st.text_area("Message *", placeholder="Enter your message...", height=100)
                
                submit = st.form_submit_button("Post Message", type="primary", use_container_width=True)
                
                if submit:
                    errors = []
                    if not message_author or not validate_email(message_author):
                        errors.append("Valid email required")
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
                        st.success("✅ Message posted!")
                        st.rerun()
        
        cursor.close()
        conn.close()

# View: Create ticket
elif st.session_state.view == 'create':
    st.header("Create New Ticket")
    st.markdown("---")
    
    if st.button("← Back to All Tickets"):
        st.session_state.view = 'list'
        st.rerun()
    
    with st.form("create_ticket_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            priority = st.selectbox("Priority *", ["low", "medium", "high", "critical"], index=1)
        
        with col2:
            category = st.selectbox("Category *", 
                                   ["general", "technical", "billing", "feature_request", "bug"])
        
        ticket_title = st.text_input("Title *", placeholder="Brief description (10-200 chars)", 
                                     max_chars=200)
        
        created_by = st.text_input("Your Email *", placeholder="your.email@company.com")
        
        initial_message = st.text_area("Description *", 
                                      placeholder="Provide details... (10-5000 chars)", 
                                      height=200, max_chars=5000)
        
        st.caption("* Required fields")
        
        submit = st.form_submit_button("Create Ticket", type="primary", use_container_width=True)
        
        if submit:
            errors = []
            
            is_valid, error_msg = validate_title(ticket_title)
            if not is_valid:
                errors.append(f"Title: {error_msg}")
            
            if not created_by or not validate_email(created_by):
                errors.append("Valid email required")
            
            is_valid, error_msg = validate_message(initial_message)
            if not is_valid:
                errors.append(f"Message: {error_msg}")
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                conn = get_db_connection()
                if conn:
                    cursor = conn.cursor()
                    
                    cursor.execute("""
                        INSERT INTO tickets (title, status, priority, category, created_by)
                        VALUES (%s, 'open', %s, %s, %s)
                        RETURNING ticket_id
                    """, (ticket_title, priority, category, created_by))
                    new_id = cursor.fetchone()['ticket_id']
                    
                    cursor.execute("""
                        INSERT INTO ticket_messages (ticket_id, message_text, author)
                        VALUES (%s, %s, %s)
                    """, (new_id, initial_message, created_by))
                    
                    conn.commit()
                    cursor.close()
                    conn.close()
                    
                    st.success(f"✅ Ticket #{new_id} created successfully!")
                    st.balloons()
                    st.session_state.selected_ticket = new_id
                    st.session_state.view = 'detail'
                    st.rerun()
