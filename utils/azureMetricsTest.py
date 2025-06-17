"""
pip install azure-identity azure-monitor-query azure-mgmt-sql python-dotenv plotly pandas
.env: AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID, TARGET_DB_RESOURCE_ID
"""
import os, time, re
from datetime import timedelta
import pandas as pd, plotly.express as px, plotly.graph_objects as go
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential
from azure.monitor.query import MetricsQueryClient, MetricAggregationType
from azure.mgmt.sql import SqlManagementClient

# ── 1.  Auth ──────────────────────────────────────────────────────────────────
load_dotenv()
cred = ClientSecretCredential(
    tenant_id=os.getenv("AZURE_TENANT_ID"),
    client_id=os.getenv("AZURE_CLIENT_ID"),
    client_secret=os.getenv("AZURE_CLIENT_SECRET"),
)
resource_id = os.getenv("TARGET_DB_RESOURCE_ID")

# ── 2.  Pull last-hour metrics (used-bytes + CPU/IO) ──────────────────────────
m_client  = MetricsQueryClient(cred)
span, gran = timedelta(hours=1), timedelta(minutes=5)
resp = m_client.query_resource(
    resource_id,
    metric_names=["storage", "cpu_percent",
                  "physical_data_read_percent", "log_write_percent"],
    timespan=span,
    granularity=gran,
    aggregations=[MetricAggregationType.MAXIMUM, MetricAggregationType.AVERAGE],
)

# helper → dict {metric: [pts…]} + latest value
series, latest = {}, {}
for m in resp.metrics:
    pts = m.timeseries[0].data
    val = pts[-1].maximum if m.name == "storage" else pts[-1].average
    latest[m.name] = val
    series[m.name] = [(p.timestamp, p.maximum if m.name == "storage" else p.average)
                      for p in pts]

# ── 3.  Fetch max-size-bytes via management API ───────────────────────────────
subs, rg, server, db = re.match(
    r"/subscriptions/([^/]+)/resourceGroups/([^/]+)/providers/Microsoft\.Sql/servers/([^/]+)/databases/(.+)",
    resource_id).groups()

sql_client = SqlManagementClient(cred, subs)
max_bytes  = int(sql_client.databases.get(rg, server, db).max_size_bytes)

# ── 4.  Plotly figs ───────────────────────────────────────────────────────────
# 4A Donut
used_gb = latest["storage"] / 1_073_741_824
max_gb  = max_bytes          / 1_073_741_824
remain  = max(0, max_gb - used_gb)
fig_donut = px.pie(
    names=["Used", "Remaining"],
    values=[used_gb, remain],
    hole=0.6,
    title=f"Database data storage • {used_gb:,.0f} GB used of {max_gb:,.0f} GB",
)
fig_donut.update_traces(textinfo="percent+label")

# 4B Line – CPU, Data-IO, Log-IO
records = []
for metric, pts in series.items():
    if metric == "storage":   # skip
        continue
    for ts, val in pts:
        records.append({"timestamp": ts, "metric": metric, "value": val})
df = pd.DataFrame(records)
fig_line = px.line(df, x="timestamp", y="value", color="metric",
                   title="Compute utilisation (last hour)", labels={"value": "%"})
fig_line.update_layout(yaxis_range=[0, max(5, df["value"].max()*1.2)])

fig_donut.show()
fig_line.show()
print(f"Done in {time.perf_counter():.2f}s")
