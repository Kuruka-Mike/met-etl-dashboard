import os, time
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential
from azure.monitor.query import LogsQueryClient

# ── 0. Load creds & client ─────────────────────────────────────
load_dotenv()
cred = ClientSecretCredential(
    tenant_id    = os.getenv("AZURE_TENANT_ID"),
    client_id    = os.getenv("AZURE_CLIENT_ID"),
    client_secret= os.getenv("AZURE_CLIENT_SECRET"),
)
logs = LogsQueryClient(cred)
workspace_id = os.getenv("APP_INSIGHTS_ID")
assert workspace_id, "APP_INSIGHTS_ID missing in .env"

# ── 1. Build Kusto query ───────────────────────────────────────
app = "trendlinemetdatafunc"
query = f"""
requests
| where timestamp > ago(30d)
| where cloud_RoleName == "{app}"
| summarize Success=countif(resultType == "Success"), Failure=countif(resultType != "Success") by name
"""

# ── 2. Define timespan as (start_datetime, end_datetime) ───────
end   = datetime.now(timezone.utc)
start = end - timedelta(days=30)
ts    = (start, end)

# ── 3. Run & print ─────────────────────────────────────────────
t0 = time.perf_counter()
resp = logs.query_workspace(
    workspace_id=workspace_id,
    query       =query,
    timespan    =ts
)
assert resp.status == "Success", f"Kusto query failed: {resp.status}"

# Header
cols = [c.name for c in resp.tables[0].columns]
print(" | ".join(cols))
print("-" * 40)

# Rows
for row in resp.tables[0].rows:
    print(" | ".join(str(x) for x in row))

print(f"\nDone in {time.perf_counter() - t0:.2f}s")
