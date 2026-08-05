# AI Support Ticket System

## Overview

A full-stack support ticket management system built with Databricks Apps and Lakebase (serverless Postgres). This application demonstrates the integration of:

* **Frontend**: Streamlit-based interactive UI
* **Backend**: Lakebase Postgres Autoscaling database
* **Deployment**: Databricks Apps platform

## Features

✅ **View All Tickets**: Browse all support tickets with status filtering  
✅ **Ticket Details**: View complete ticket information and message history  
✅ **Create Tickets**: Submit new support requests  
✅ **Add Messages**: Post follow-up messages to existing tickets  
✅ **Update Status**: Change ticket status (open → in_progress → resolved)  
✅ **Real-time Persistence**: All data stored in Lakebase with immediate updates  

## Architecture

### Database Schema

**tickets table:**
```sql
CREATE TABLE tickets (
    ticket_id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'open',
    created_by VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

**ticket_messages table:**
```sql
CREATE TABLE ticket_messages (
    message_id SERIAL PRIMARY KEY,
    ticket_id INTEGER NOT NULL REFERENCES tickets(ticket_id) ON DELETE CASCADE,
    message_text TEXT NOT NULL,
    author VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### Lakebase Configuration

* **Project**: `ai-support-app`
* **Branch**: `production`
* **Database**: `databricks_postgres`
* **PostgreSQL Version**: 17
* **Endpoint**: Autoscaling compute with scale-to-zero

## Sample Data

The database contains 3 pre-populated support tickets:

1. **Dashboard Access Issue** (Status: open) - 3 messages
2. **Pipeline Failure** (Status: in_progress) - 3 messages  
3. **Permission Request** (Status: resolved) - 3 messages

## Deployment

### Prerequisites

* Databricks workspace with Apps enabled
* Lakebase project: `ai-support-app`
* Service Principal with database permissions

### Deploy the App

```bash
apps deploy ai-support-app --source-code-path /Workspace/Users/<your-email>/Assigmentsubmission/ai-support-app
```

The app will automatically:
* Connect to the Lakebase database using OAuth credentials
* Inject environment variables for database connection
* Start on Databricks Apps infrastructure

## Local Development

**Note**: For local development with a deployed app's schema, you must:

1. Deploy the app first (so the Service Principal creates the schema)
2. Grant yourself `databricks_superuser` role in the Lakebase UI
3. Then run locally with your credentials

This ensures proper schema ownership and permissions.

## Tech Stack

* **Application Framework**: Streamlit
* **Database**: Lakebase Postgres Autoscaling
* **Deployment Platform**: Databricks Apps
* **Language**: Python 3.12
* **Database Driver**: psycopg2

## Project Structure

```
ai-support-app/
├── app.py              # Main Streamlit application
├── app.yaml            # Databricks Apps configuration
└── README.md           # Project documentation
```

## Environment Variables

Configured automatically by Databricks Apps:

* `LAKEBASE_HOST`: Postgres endpoint hostname
* `LAKEBASE_DATABASE`: Database name
* `LAKEBASE_USER`: OAuth user (injected from Postgres resource)
* `LAKEBASE_PASSWORD`: OAuth token (injected from Postgres resource)

## Testing

After deployment, verify:

1. **✅ Data Load**: Navigate to "All Tickets" - should see 3 sample tickets
2. **✅ Create**: Click "Create New Ticket" and submit a new ticket
3. **✅ View**: Click "View" on any ticket to see details
4. **✅ Add Message**: Post a new message to a ticket
5. **✅ Update Status**: Change a ticket's status
6. **✅ Persistence**: Refresh the page - all changes should persist

## Future Enhancements

* User authentication and authorization
* Email notifications for new messages
* File attachments support
* Advanced search and filtering
* Analytics dashboard
* Integration with external ticketing systems

## License

MIT License - Day 1 Homework Assignment

## Author

Built for the Databricks Lakebase Boot Camp
