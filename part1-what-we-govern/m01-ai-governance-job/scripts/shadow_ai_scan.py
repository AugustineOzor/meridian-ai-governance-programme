"""Shadow-AI scanner for Meridian Gulf Bank (fictional).

Matches expense and web-proxy records against a catalogue of known AI tools,
compares hits with the approved AI register, and writes:
  outputs/shadow_ai_findings.csv   one row per AI tool detected
  outputs/shadow_ai_summary.md     short summary for the findings report

Usage:  python scripts/shadow_ai_scan.py
"""
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parents[1]
DATA, OUT = BASE / "data", BASE / "outputs"

# Departments where use of an unapproved tool is more likely to involve sensitive data
SENSITIVE_DEPTS = {"HR", "Compliance", "SME Lending", "Finance"}
HIGH_RISK_CATEGORIES = {"model_api", "meeting_notetaker"}


def load():
    cat = pd.read_csv(DATA / "ai_tool_catalogue.csv", dtype=str).fillna("")
    exp = pd.read_csv(DATA / "expenses_q3_2026.csv", parse_dates=["date"])
    prx = pd.read_csv(DATA / "proxy_logs_q3_2026.csv", parse_dates=["date"])
    reg = pd.read_csv(DATA / "ai_register_export.csv", dtype=str)
    return cat, exp, prx, reg


def match(df, column, rules):
    """Tag each row of df with the catalogue tool whose pattern appears in `column`."""
    hits = []
    for _, r in rules.iterrows():
        mask = df[column].str.contains(r["pattern"], case=False, regex=False)
        if mask.any():
            hits.append(df[mask].assign(tool=r["tool"]))
    return pd.concat(hits, ignore_index=True) if hits else df.iloc[0:0].assign(tool=None)


def priority(row):
    if row["approval_status"] == "approved":
        return "Low"
    depts = set(row["departments"].split(", "))
    if row["category"] in HIGH_RISK_CATEGORIES or depts & SENSITIVE_DEPTS:
        return "High"
    return "Medium"


def scan():
    cat, exp, prx, reg = load()
    exp_hits = match(exp, "merchant", cat[cat.match_on == "merchant"]).rename(columns={"employee_id": "user_id"})
    prx_hits = match(prx, "domain", cat[cat.match_on == "domain"])

    tools = cat.drop_duplicates("tool").set_index("tool")[["vendor", "category", "ai_type", "approved_register_id"]]
    rows = []
    for tool in sorted(set(exp_hits.tool) | set(prx_hits.tool)):
        e, p = exp_hits[exp_hits.tool == tool], prx_hits[prx_hits.tool == tool]
        both = pd.concat([e[["date", "user_id", "department"]], p[["date", "user_id", "department"]]])
        info = tools.loc[tool]
        rows.append({
            "tool": tool,
            "vendor": info.vendor,
            "category": info.category,
            "ai_type": info.ai_type,
            "approval_status": "approved" if info.approved_register_id else "unapproved",
            "register_id": info.approved_register_id,
            "distinct_users": both.user_id.nunique(),
            "departments": ", ".join(sorted(both.department.unique())),
            "expense_claims": len(e),
            "spend_qar": round(e.amount_qar.sum(), 2),
            "proxy_requests": int(p.requests.sum()) if len(p) else 0,
            "upload_mb": round(p.bytes_out.sum() / 1e6, 1) if len(p) else 0.0,
            "first_seen": both.date.min().date(),
            "last_seen": both.date.max().date(),
            "discovered_via": "+".join(s for s, d in (("expense_scan", e), ("proxy_scan", p)) if len(d)),
        })
    findings = pd.DataFrame(rows)
    unapproved_tools = set(findings.loc[findings.approval_status == "unapproved", "tool"])
    users = pd.concat([exp_hits[["user_id", "tool"]], prx_hits[["user_id", "tool"]]])
    findings.attrs["unapproved_users"] = users[users.tool.isin(unapproved_tools)].user_id.nunique()
    findings["priority"] = findings.apply(priority, axis=1)
    order = {"High": 0, "Medium": 1, "Low": 2}
    findings = findings.sort_values(["priority", "distinct_users"], key=lambda s: s.map(order) if s.name == "priority" else -s)
    return findings, reg


def summarise(findings, reg):
    unapproved = findings[findings.approval_status == "unapproved"]
    total = len(reg) + len(unapproved)
    lines = [
        "# Shadow-AI scan summary (Q3 2026, synthetic data)",
        "",
        f"- AI tools detected in expenses and proxy logs: **{len(findings)}**",
        f"- Of these, not on the approved AI register: **{len(unapproved)}**",
        f"- Approved register entries: **{len(reg)}**, so unapproved AI is "
        f"**{len(unapproved) / total:.0%}** of the known estate ({len(unapproved)} of {total})",
        f"- Distinct staff using at least one unapproved AI tool: **{findings.attrs['unapproved_users']}** of 120",
        f"- Spend on unapproved AI via expenses: **QAR {unapproved.spend_qar.sum():,.2f}**",
        "",
        "| Priority | Tool | Category | Users | Departments | Upload (MB) |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for _, r in unapproved.iterrows():
        lines.append(f"| {r.priority} | {r.tool} | {r.category} | {r.distinct_users} | {r.departments} | {r.upload_mb} |")
    lines += ["", "_Upload volume is a proxy signal only: it does not show what data left the bank._"]
    return "\n".join(lines)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    findings, reg = scan()
    findings.to_csv(OUT / "shadow_ai_findings.csv", index=False)
    (OUT / "shadow_ai_summary.md").write_text(summarise(findings, reg), encoding="utf-8")
    print(findings[["priority", "tool", "approval_status", "distinct_users", "departments"]].to_string(index=False))
    print(f"\nWrote {OUT / 'shadow_ai_findings.csv'} and shadow_ai_summary.md")
