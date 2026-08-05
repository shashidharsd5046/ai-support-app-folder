"""
One-time setup script: creates the Databricks secret scope and stores the
Lakebase connection URL. Run this from a notebook or with the Databricks CLI.

Usage:
    python setup_secrets.py
"""
from databricks.sdk import WorkspaceClient
from databricks.sdk.service import workspace
import getpass

w = WorkspaceClient()

w.secrets.create_scope(scope="ai-support-database")
w.secrets.put_secret(
    scope="ai-support-database",
    key="lakebase-url",
    string_value=getpass.getpass("Paste your Lakebase URL: ")
)

w.secrets.put_acl(
    scope="ai-support-database",
    principal="users",
    permission=workspace.AclPermission.READ,
)

print("✅ Secret setup complete!")
print("Scope: ai-support-database")
print("Key: lakebase-url")
