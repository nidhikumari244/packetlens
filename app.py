
from __future__ import annotations

import os
from datetime import datetime

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from ai_engine import diagnose_with_ai
from classifier import classify_issue
from database import (
    delete_diagnosis,
    get_dashboard_stats,
    get_diagnoses,
    init_db,
    row_to_diagnosis,
    save_diagnosis,
)
from report_generator import generate_report


load_dotenv()
init_db()

st.set_page_config(page_title="AI Network Troubleshooting Assistant", layout="wide")


CATEGORIES = ["All", "DNS", "TCP/IP", "HTTP/HTTPS", "DHCP", "Routing", "Firewall", "Wi-Fi", "Unknown"]
SEVERITY_COLORS = {"High": "#dc2626", "Medium": "#d97706", "Low": "#16a34a"}


st.markdown(
    """
    <style>
        .main .block-container {
            max-width: 1240px;
            padding-top: 1.2rem;
            padding-bottom: 3rem;
        }
        .app-hero {
            border: 1px solid #d8dee4;
            border-radius: 8px;
            padding: 22px 24px;
            background: linear-gradient(120deg, #0f172a 0%, #164e63 56%, #14532d 100%);
            color: white;
            margin-bottom: 18px;
        }
        .app-hero h1 {
            font-size: 2rem;
            margin: 0 0 8px 0;
            letter-spacing: 0;
        }
        .app-hero p {
            margin: 0;
            color: #dbeafe;
            max-width: 860px;
        }
        .kpi-card {
            border: 1px solid #d8dee4;
            border-radius: 8px;
            padding: 16px;
            background: #ffffff;
            min-height: 112px;
        }
        .kpi-label {
            color: #57606a;
            font-size: 0.88rem;
            text-transform: uppercase;
            letter-spacing: 0;
        }
        .kpi-value {
            font-size: 2rem;
            font-weight: 760;
            color: #0f172a;
            margin-top: 4px;
        }
        .panel {
            border: 1px solid #d8dee4;
            border-radius: 8px;
            padding: 18px;
            background: #ffffff;
        }
        .incident-card {
            border: 1px solid #d8dee4;
            border-left: 5px solid #0f766e;
            border-radius: 8px;
            padding: 18px;
            background: #ffffff;
            margin: 12px 0;
        }
        .muted {
            color: #57606a;
            font-size: 0.92rem;
        }
        .chip {
            display: inline-block;
            padding: 5px 10px;
            margin: 3px 6px 3px 0;
            border-radius: 999px;
            background: #eef6ff;
            border: 1px solid #bfdbfe;
            color: #1e3a8a;
            font-size: 0.85rem;
        }
        .status-pill {
            display: inline-block;
            padding: 4px 9px;
            border-radius: 999px;
            color: white;
            font-weight: 700;
            font-size: 0.82rem;
        }
        .command-box {
            border: 1px solid #d8dee4;
            border-radius: 8px;
            background: #0f172a;
            color: #dbeafe;
            padding: 10px 12px;
            margin-bottom: 8px;
            font-family: Consolas, monospace;
            font-size: 0.92rem;
        }
        .section-title {
            font-size: 1.05rem;
            font-weight: 740;
            color: #0f172a;
            margin-bottom: 8px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def main() -> None:
    with st.sidebar:
        st.title("PacketLens")
        st.caption("Network Incident Analyzer")

        page = st.radio(
            "Navigation",
            ["Dashboard", "Diagnose Issue", "History", "About PacketLens"],
            label_visibility="collapsed",
        )

        st.divider()

        # NEW CONTROL CENTER
        st.markdown("## Incident Filters")

        protocol_filter = st.selectbox(
            "Protocol Scope",
            ["All", "DNS", "TCP/IP", "HTTP/HTTPS", "DHCP", "Routing", "Firewall", "Wi-Fi"]
        )

        severity_threshold = st.slider(
            "Severity Threshold",
            0,
            100,
            50
        )

        st.divider()

        # SYSTEM HEALTH PANEL
        st.markdown("## System Status")

        st.success("Rule Engine: Active")

        if os.getenv("GROQ_API_KEY"):
            st.success("AI Service: Available")
        else:
            st.error("AI Service: Unavailable")

        st.info("Database: Connected")

        st.info("Processing Mode: Hybrid")

    if page == "Dashboard":
        dashboard_page()
    elif page == "Diagnose Issue":
        diagnose_page()
    elif page == "History":
        history_page()
    else:
        about_page()


def hero(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="app-hero">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def dashboard_page() -> None:
    hero(
    "PacketLens Network Operations Dashboard",
    "Analyze network incidents, identify likely root causes, and track troubleshooting history across DNS, DHCP, Routing, Firewall, and TCP/IP issues."
    )
    stats = get_dashboard_stats()
    high_rate = round(
    (stats["high"] / stats["total"]) * 100,
    1
) if stats["total"] else 0

    if stats["high"] >= 5:
        st.error("Critical Network Risk Detected")
    elif stats["high"] >= 2:
        st.warning("⚠ Elevated Operational Risk")
    else:
        st.success("System Status: Healthy")
    col1, col2, col3, col4 = st.columns(4)
    render_kpi(col1, "Active Incidents", stats["total"], "Tracked incidents")
    render_kpi(col2, "Critical Alerts", stats["high"], "Immediate attention required")
    render_kpi(col3, "Protocol Coverage", len(stats["by_category"]), "Network domains monitored")
    render_kpi(
    col4,
    "High Severity Rate",
    f"{high_rate}%",
    "Percentage of incidents marked high severity"
)

    st.markdown("## Incident Processing Pipeline")
    st.code("""
            User Input
                │
                ▼
            Issue Classification
                │
                ▼
            Root Cause Analysis
                │
                ▼
            Severity Assessment
                │
                ▼
            Incident Storage
                │
                ▼
            Dashboard Analytics
            """)
    

    left, right = st.columns([1.25, 1])
    with left:
        st.subheader("Incidents by Category")
        if stats["by_category"]:
            chart_data = pd.DataFrame(stats["by_category"], columns=["Category", "Count"])
            st.bar_chart(chart_data.set_index("Category"), height=260)
        else:
            st.info("No incidents yet. Run a diagnosis to populate the dashboard.")

    with right:
        st.subheader("Incident Severity Breakdown")
        if stats["by_severity"]:
            severity_data = pd.DataFrame(stats["by_severity"], columns=["Severity", "Count"])
            st.bar_chart(severity_data.set_index("Severity"), height=260)
        else:
            st.info("Severity analytics will appear after the first diagnosis.")

    

    st.subheader("Recent Incident Stream")
    recent_rows = stats.get("recent_rows", [])
    if recent_rows:
        for row in recent_rows:
            diagnosis = row_to_diagnosis(row)
            render_incident_summary(row["id"], row["user_input"], diagnosis, row["created_at"])
    else:
        st.write("No incidents available yet.")


def render_kpi(column, label: str, value: object, caption: str) -> None:
    column.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="muted">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def diagnose_page() -> None:
    hero(
        "Diagnose Network Issue",
        "Paste symptoms, CLI output, or incident notes. The app classifies the protocol, estimates severity, and generates a structured troubleshooting playbook.",
    )

    examples = {
        "DNS resolution failure": "DNS lookup failed for portal.company.com. Ping to 8.8.8.8 works, but nslookup portal.company.com times out.",
        "Packet loss": "High packet loss when pinging the gateway 192.168.1.1. Users report slow application access and intermittent timeout.",
        "Routing break": "traceroute stops after gateway while accessing 10.20.30.40. Other local network devices are reachable.",
        "DHCP lease failure": "DHCP not assigning IP. Client has 169.254.10.22 address and cannot access internal resources.",
        "Firewall block": "Application traffic is blocked on port 443 after a firewall policy update. Ping works but HTTPS fails.",
        "Wi-Fi Authentication Failure": "Users disconnect from the corporate Wi-Fi every 10 minutes. Signal strength is strong but authentication repeatedly fails.",
        "VPN Connection Failure": "Remote users can authenticate to the VPN but cannot access internal applications after connection.",
        "SSL Certificate Error": "Users receive SSL certificate warnings when accessing the company portal after a server migration.",
        "HTTP Timeout": "The company website frequently returns HTTP 504 Gateway Timeout errors during peak hours.",
        
    }

    col_left, col_right = st.columns([1.15, 0.85])
    with col_left:
        selected = st.selectbox("Load sample incident", ["Custom"] + list(examples.keys()))
        default_text = "" if selected == "Custom" else examples[selected]
        user_input = st.text_area(
            "Incident description, logs, or command output",
            value=default_text,
            height=240,
            placeholder="Example: nslookup fails, ping 8.8.8.8 works, browser cannot open HTTPS site...",
        )
        analyze = st.button("Run AI Triage", type="primary", use_container_width=True)

    with col_right:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Triage Pipeline</div>', unsafe_allow_html=True)
        st.write("1. Parse symptoms and command output")
        st.write("2. Classify protocol with deterministic rules")
        st.write("3. Estimate severity and confidence")
        st.write("4. Generate AI or fallback playbook")
        st.write("5. Store incident and export report")
        st.markdown("</div>", unsafe_allow_html=True)

    if analyze:
        if not user_input.strip():
            st.error("Enter an incident description or command output before running triage.")
            return

        classification = classify_issue(user_input)
        with st.spinner("Running rule engine, AI diagnosis, and report preparation..."):
            diagnosis = diagnose_with_ai(
                user_input=user_input,
                category=str(classification["category"]),
                severity=str(classification["severity"]),
            )
            diagnosis.setdefault("confidence", classification["confidence"])
            diagnosis.setdefault("confidence_score", classification["confidence_score"])
            diagnosis.setdefault("evidence", classification["evidence"])
            issue_id = save_diagnosis(user_input, diagnosis)

        if diagnosis.get("api_status"):
            st.warning(str(diagnosis["api_status"]))
        st.success(f"Incident #{issue_id} triaged and stored.")
        render_diagnosis(user_input, diagnosis, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), issue_id)


def history_page() -> None:
    hero(
        "Incident History",
        "Search previous diagnoses, filter by protocol category, delete stale entries, and export incident-ready reports.",
    )
    col1, col2, col3 = st.columns([1, 1, 2])
    category = col1.selectbox(
        "Incident Category",
        CATEGORIES
        )
    severity = col2.selectbox(
        "Severity",
        ["All", "High", "Medium", "Low"]
        )
    search_text = col3.text_input(
        "Search issue text or diagnosis"
        
        )
    rows = get_diagnoses(
        category=category,
        search_text=search_text.strip()
        )
    if severity != "All":
        rows = [
            row for row in rows
            if row["severity"] == severity
            ]

    st.caption(f"{len(rows)} record(s) found")
    if not rows:
        st.info("No matching incident records found.")
        return

    for row in rows:
        diagnosis = row_to_diagnosis(row)
        title = f"Incident #{row['id']} | {row['category']} | {row['severity']} | {row['created_at']}"
        with st.expander(title):
            render_diagnosis(row["user_input"], diagnosis, row["created_at"], row["id"], compact=True)
            report = generate_report(row["user_input"], diagnosis, row["created_at"])
            c1, c2 = st.columns(2)
            c1.download_button(
                "Download Incident Report",
                report,
                file_name=f"network_incident_report_{row['id']}.txt",
                mime="text/plain",
                key=f"history_download_{row['id']}",
            )
            if c2.button("Delete Incident", key=f"delete_{row['id']}"):
                delete_diagnosis(row["id"])
                st.success(f"Incident #{row['id']} deleted.")
                st.rerun()


def about_page() -> None:
    hero(
    "About PacketLens",
    "PacketLens is a network incident analysis tool that helps identify and troubleshoot common DNS, DHCP, Routing, Firewall, TCP/IP, and HTTP/HTTPS issues.",
)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("What It Does")
        st.write(
    "The application analyzes network symptoms, classifies the issue category, estimates severity, and generates troubleshooting recommendations. Diagnoses are stored for future analysis and reporting."
)
        st.subheader("Tech Stack")
        st.write("Python, Streamlit, Groq API, SQLite, Pandas, python-dotenv")

    with col2:
        st.subheader("Industry Use Case")
        st.write(
    "The system can assist helpdesk teams, NOC analysts, and network administrators in identifying common network issues and reviewing recommended troubleshooting steps."
)
        st.subheader("Key Features")
        st.write("""
• Network issue classification

• Root cause analysis

• Severity assessment

• Incident history tracking

• Report generation

• Dashboard analytics
""")

    st.subheader("Architecture")
    st.code(
        """app.py -> Streamlit UI and workflow orchestration
classifier.py -> protocol classification, evidence extraction, severity logic
ai_engine.py -> Groq prompt, JSON response normalization, fallback handling
database.py -> SQLite persistence and dashboard analytics
report_generator.py -> downloadable incident reports""",
        language="text",
    )

    st.subheader("Future Enhancements")
    st.write("""
• FastAPI backend

• Docker deployment

• User authentication

• PDF report generation

• Automated testing with pytest

• Cisco IOS troubleshooting templates
""")

def render_diagnosis(
    issue_description: str,
    diagnosis: dict,
    timestamp: str,
    issue_id: int,
    compact: bool = False,
) -> None:
    category = str(diagnosis.get("category", "Unknown"))
    severity = str(diagnosis.get("severity", "Low"))
    confidence_score = int(diagnosis.get("confidence_score", 70))
    severity_color = SEVERITY_COLORS.get(severity, "#64748b")

    st.markdown(
        f"""
        <div class="incident-card">
            <div class="muted">Incident #{issue_id} | {timestamp} | Source: {diagnosis.get("source", "AI/Rules")}</div>
            <h3>{category} Incident Triage</h3>
            <span class="status-pill" style="background:{severity_color};">{severity}</span>
            <span class="chip">Confidence: {confidence_score}%</span>
            <span class="chip">{diagnosis.get("confidence", "AI-assisted")}</span>
            <p><strong>Probable root cause:</strong> {diagnosis.get("root_cause", "Not available")}</p>
            <p><strong>Business impact:</strong> {diagnosis.get("impact", "Impact needs validation.")}</p>
            <p><strong>Simple explanation:</strong> {diagnosis.get("explanation", "Not available")}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.progress(max(0, min(100, confidence_score)) / 100)

    if not compact:
        st.subheader("Original Incident")
        st.code(issue_description, language="text")

    evidence = diagnosis.get("evidence", {})
    if isinstance(evidence, dict):
        render_evidence(evidence)

    tab1, tab2, tab3, tab4 = st.tabs(["Playbook", "Commands", "Escalation", "Report"])
    with tab1:
        st.subheader("Step-by-Step Troubleshooting")
        render_numbered(diagnosis.get("troubleshooting_steps", []))
        st.subheader("Prevention Tips")
        render_bullets(diagnosis.get("prevention_tips", []))

    with tab2:
        st.subheader("Recommended Commands")
        for command in as_list(diagnosis.get("recommended_commands", [])):
            st.markdown(f'<div class="command-box">{command}</div>', unsafe_allow_html=True)

    with tab3:
        st.subheader("Escalation Guidance")
        render_bullets(diagnosis.get("escalation_guidance", []))

    with tab4:
        report = generate_report(issue_description, diagnosis, timestamp)
        st.download_button(
            "Download Incident Report",
            report,
            file_name=f"network_incident_report_{issue_id}.txt",
            mime="text/plain",
            key=f"diagnosis_download_{issue_id}_{compact}",
        )
        st.text_area("Report Preview", report, height=260)


def render_incident_summary(issue_id: int, description: str, diagnosis: dict, timestamp: str) -> None:
    severity = str(diagnosis.get("severity", "Low"))
    color = SEVERITY_COLORS.get(severity, "#64748b")
    st.markdown(
        f"""
        <div class="panel">
            <div class="muted">Incident #{issue_id} | {timestamp}</div>
            <strong>{diagnosis.get("category", "Unknown")}</strong>
            <span class="status-pill" style="background:{color};">{severity}</span>
            <p>{description}</p>
            <p><strong>Root cause:</strong> {diagnosis.get("root_cause", "Not available")}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_evidence(evidence: dict) -> None:
    st.subheader("Extracted Evidence")
    chips = []
    for label, values in (
        ("IP", evidence.get("ip_addresses", [])),
        ("Domain", evidence.get("domains", [])),
        ("Command", evidence.get("commands_detected", [])),
    ):
        for value in values:
            chips.append(f'<span class="chip">{label}: {value}</span>')
    if chips:
        st.markdown(" ".join(chips), unsafe_allow_html=True)
    else:
        st.caption("No explicit IPs, domains, or commands were detected in the input.")


def render_numbered(items: object) -> None:
    for index, item in enumerate(as_list(items), start=1):
        st.write(f"{index}. {item}")


def render_bullets(items: object) -> None:
    for item in as_list(items):
        st.write(f"- {item}")


def as_list(items: object) -> list[str]:
    if isinstance(items, list):
        return [str(item) for item in items]
    if isinstance(items, str) and items.strip():
        return [items]
    return ["Not available."]


if __name__ == "__main__":
    main()
from __future__ import annotations

import os
from datetime import datetime

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from ai_engine import diagnose_with_ai
from classifier import classify_issue
from database import (
    delete_diagnosis,
    get_dashboard_stats,
    get_diagnoses,
    init_db,
    row_to_diagnosis,
    save_diagnosis,
)
from report_generator import generate_report


load_dotenv()
init_db()

st.set_page_config(page_title="AI Network Troubleshooting Assistant", layout="wide")


CATEGORIES = ["All", "DNS", "TCP/IP", "HTTP/HTTPS", "DHCP", "Routing", "Firewall", "Wi-Fi", "Unknown"]
SEVERITY_COLORS = {"High": "#dc2626", "Medium": "#d97706", "Low": "#16a34a"}


st.markdown(
    """
    <style>
        .main .block-container {
            max-width: 1240px;
            padding-top: 1.2rem;
            padding-bottom: 3rem;
        }
        .app-hero {
            border: 1px solid #d8dee4;
            border-radius: 8px;
            padding: 22px 24px;
            background: linear-gradient(120deg, #0f172a 0%, #164e63 56%, #14532d 100%);
            color: white;
            margin-bottom: 18px;
        }
        .app-hero h1 {
            font-size: 2rem;
            margin: 0 0 8px 0;
            letter-spacing: 0;
        }
        .app-hero p {
            margin: 0;
            color: #dbeafe;
            max-width: 860px;
        }
        .kpi-card {
            border: 1px solid #d8dee4;
            border-radius: 8px;
            padding: 16px;
            background: #ffffff;
            min-height: 112px;
        }
        .kpi-label {
            color: #57606a;
            font-size: 0.88rem;
            text-transform: uppercase;
            letter-spacing: 0;
        }
        .kpi-value {
            font-size: 2rem;
            font-weight: 760;
            color: #0f172a;
            margin-top: 4px;
        }
        .panel {
            border: 1px solid #d8dee4;
            border-radius: 8px;
            padding: 18px;
            background: #ffffff;
        }
        .incident-card {
            border: 1px solid #d8dee4;
            border-left: 5px solid #0f766e;
            border-radius: 8px;
            padding: 18px;
            background: #ffffff;
            margin: 12px 0;
        }
        .muted {
            color: #57606a;
            font-size: 0.92rem;
        }
        .chip {
            display: inline-block;
            padding: 5px 10px;
            margin: 3px 6px 3px 0;
            border-radius: 999px;
            background: #eef6ff;
            border: 1px solid #bfdbfe;
            color: #1e3a8a;
            font-size: 0.85rem;
        }
        .status-pill {
            display: inline-block;
            padding: 4px 9px;
            border-radius: 999px;
            color: white;
            font-weight: 700;
            font-size: 0.82rem;
        }
        .command-box {
            border: 1px solid #d8dee4;
            border-radius: 8px;
            background: #0f172a;
            color: #dbeafe;
            padding: 10px 12px;
            margin-bottom: 8px;
            font-family: Consolas, monospace;
            font-size: 0.92rem;
        }
        .section-title {
            font-size: 1.05rem;
            font-weight: 740;
            color: #0f172a;
            margin-bottom: 8px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def main() -> None:
    with st.sidebar:
        st.title("PacketLens")
        st.caption("Network Incident Analyzer")

        page = st.radio(
            "Navigation",
            ["Dashboard", "Diagnose Issue", "History", "About PacketLens"],
            label_visibility="collapsed",
        )

        st.divider()

        # NEW CONTROL CENTER
        st.markdown("## Incident Filters")

        protocol_filter = st.selectbox(
            "Protocol Scope",
            ["All", "DNS", "TCP/IP", "HTTP/HTTPS", "DHCP", "Routing", "Firewall", "Wi-Fi"]
        )

        severity_threshold = st.slider(
            "Severity Threshold",
            0,
            100,
            50
        )

        st.divider()

        # SYSTEM HEALTH PANEL
        st.markdown("## System Status")

        st.success("Rule Engine: Active")

        if os.getenv("GROQ_API_KEY"):
            st.success("AI Service: Available")
        else:
            st.error("AI Service: Unavailable")

        st.info("Database: Connected")

        st.info("Processing Mode: Hybrid")

    if page == "Dashboard":
        dashboard_page()
    elif page == "Diagnose Issue":
        diagnose_page()
    elif page == "History":
        history_page()
    else:
        about_page()


def hero(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="app-hero">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def dashboard_page() -> None:
    hero(
    "PacketLens Network Operations Dashboard",
    "Analyze network incidents, identify likely root causes, and track troubleshooting history across DNS, DHCP, Routing, Firewall, and TCP/IP issues."
    )
    stats = get_dashboard_stats()
    high_rate = round(
    (stats["high"] / stats["total"]) * 100,
    1
) if stats["total"] else 0

    if stats["high"] >= 5:
        st.error("Critical Network Risk Detected")
    elif stats["high"] >= 2:
        st.warning("⚠ Elevated Operational Risk")
    else:
        st.success("System Status: Healthy")
    col1, col2, col3, col4 = st.columns(4)
    render_kpi(col1, "Active Incidents", stats["total"], "Tracked incidents")
    render_kpi(col2, "Critical Alerts", stats["high"], "Immediate attention required")
    render_kpi(col3, "Protocol Coverage", len(stats["by_category"]), "Network domains monitored")
    render_kpi(
    col4,
    "High Severity Rate",
    f"{high_rate}%",
    "Percentage of incidents marked high severity"
)

    st.markdown("## Incident Processing Pipeline")
    st.code("""
            User Input
                │
                ▼
            Issue Classification
                │
                ▼
            Root Cause Analysis
                │
                ▼
            Severity Assessment
                │
                ▼
            Incident Storage
                │
                ▼
            Dashboard Analytics
            """)
    

    left, right = st.columns([1.25, 1])
    with left:
        st.subheader("Incidents by Category")
        if stats["by_category"]:
            chart_data = pd.DataFrame(stats["by_category"], columns=["Category", "Count"])
            st.bar_chart(chart_data.set_index("Category"), height=260)
        else:
            st.info("No incidents yet. Run a diagnosis to populate the dashboard.")

    with right:
        st.subheader("Incident Severity Breakdown")
        if stats["by_severity"]:
            severity_data = pd.DataFrame(stats["by_severity"], columns=["Severity", "Count"])
            st.bar_chart(severity_data.set_index("Severity"), height=260)
        else:
            st.info("Severity analytics will appear after the first diagnosis.")

    

    st.subheader("Recent Incident Stream")
    recent_rows = stats.get("recent_rows", [])
    if recent_rows:
        for row in recent_rows:
            diagnosis = row_to_diagnosis(row)
            render_incident_summary(row["id"], row["user_input"], diagnosis, row["created_at"])
    else:
        st.write("No incidents available yet.")


def render_kpi(column, label: str, value: object, caption: str) -> None:
    column.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="muted">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def diagnose_page() -> None:
    hero(
        "Diagnose Network Issue",
        "Paste symptoms, CLI output, or incident notes. The app classifies the protocol, estimates severity, and generates a structured troubleshooting playbook.",
    )

    examples = {
        "DNS resolution failure": "DNS lookup failed for portal.company.com. Ping to 8.8.8.8 works, but nslookup portal.company.com times out.",
        "Packet loss": "High packet loss when pinging the gateway 192.168.1.1. Users report slow application access and intermittent timeout.",
        "Routing break": "traceroute stops after gateway while accessing 10.20.30.40. Other local network devices are reachable.",
        "DHCP lease failure": "DHCP not assigning IP. Client has 169.254.10.22 address and cannot access internal resources.",
        "Firewall block": "Application traffic is blocked on port 443 after a firewall policy update. Ping works but HTTPS fails.",
        "Wi-Fi Authentication Failure": "Users disconnect from the corporate Wi-Fi every 10 minutes. Signal strength is strong but authentication repeatedly fails.",
        "VPN Connection Failure": "Remote users can authenticate to the VPN but cannot access internal applications after connection.",
        "SSL Certificate Error": "Users receive SSL certificate warnings when accessing the company portal after a server migration.",
        "HTTP Timeout": "The company website frequently returns HTTP 504 Gateway Timeout errors during peak hours.",
        "Gateway Unreachable": "Multiple devices cannot access the internet. The default gateway 192.168.1.1 is unreachable from all client systems.",

"DNS Slow Resolution": "Users report that websites eventually load, but DNS queries take more than 10 seconds to resolve.",

"DHCP Scope Exhausted": "New devices cannot obtain IP addresses because the DHCP address pool has been fully allocated.",

"OSPF Neighbor Failure": "OSPF neighbors between branch routers remain stuck in INIT state and routing tables are not updating.",

"Firewall Rule Conflict": "A recently deployed firewall rule is blocking communication between application servers and the database server.",

"Wireless Interference": "Employees experience intermittent Wi-Fi disconnections during office hours despite strong signal strength.",

"HTTPS Certificate Mismatch": "Browsers display certificate mismatch warnings when users access the internal HR portal.",

"VPN Tunnel Instability": "VPN sessions disconnect every few minutes, causing interruptions for remote employees.",

"Web Server Unreachable": "Users can ping the web server successfully, but HTTP and HTTPS services are unavailable.",

"Switch Port Failure": "Devices connected to switch port Gi0/24 cannot access network resources after a maintenance window.",

"ARP Conflict": "Multiple systems are reporting duplicate IP address warnings and intermittent connectivity issues.",

"Bandwidth Saturation": "Network monitoring shows WAN utilization consistently above 95%, causing slow application performance.",

"Database Connectivity Issue": "Application servers cannot connect to the backend database despite successful network pings.",

"Email Service Outage": "Users cannot send or receive emails. Mail clients report connection timeouts to the mail server.",

"Load Balancer Misconfiguration": "Traffic is not being distributed evenly across web servers, causing one server to become overloaded."
        
    }

    col_left, col_right = st.columns([1.15, 0.85])
    with col_left:
        selected = st.selectbox("Load sample incident", ["Custom"] + list(examples.keys()))
        default_text = "" if selected == "Custom" else examples[selected]
        user_input = st.text_area(
            "Incident description, logs, or command output",
            value=default_text,
            height=240,
            placeholder="Example: nslookup fails, ping 8.8.8.8 works, browser cannot open HTTPS site...",
        )
        analyze = st.button("Run AI Triage", type="primary", use_container_width=True)

    with col_right:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Triage Pipeline</div>', unsafe_allow_html=True)
        st.write("1. Parse symptoms and command output")
        st.write("2. Classify protocol with deterministic rules")
        st.write("3. Estimate severity and confidence")
        st.write("4. Generate AI or fallback playbook")
        st.write("5. Store incident and export report")
        st.markdown("</div>", unsafe_allow_html=True)

    if analyze:
        if not user_input.strip():
            st.error("Enter an incident description or command output before running triage.")
            return

        classification = classify_issue(user_input)
        with st.spinner("Running rule engine, AI diagnosis, and report preparation..."):
            diagnosis = diagnose_with_ai(
                user_input=user_input,
                category=str(classification["category"]),
                severity=str(classification["severity"]),
            )
            diagnosis.setdefault("confidence", classification["confidence"])
            diagnosis.setdefault("confidence_score", classification["confidence_score"])
            diagnosis.setdefault("evidence", classification["evidence"])
            issue_id = save_diagnosis(user_input, diagnosis)

        if diagnosis.get("api_status"):
            st.warning(str(diagnosis["api_status"]))
        st.success(f"Incident #{issue_id} triaged and stored.")
        render_diagnosis(user_input, diagnosis, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), issue_id)


def history_page() -> None:
    hero(
        "Incident History",
        "Search previous diagnoses, filter by protocol category, delete stale entries, and export incident-ready reports.",
    )
    col1, col2, col3 = st.columns([1, 1, 2])
    category = col1.selectbox(
        "Incident Category",
        CATEGORIES
        )
    severity = col2.selectbox(
        "Severity",
        ["All", "High", "Medium", "Low"]
        )
    search_text = col3.text_input(
        "Search issue text or diagnosis"
        
        )
    rows = get_diagnoses(
        category=category,
        search_text=search_text.strip()
        )
    if severity != "All":
        rows = [
            row for row in rows
            if row["severity"] == severity
            ]

    st.caption(f"{len(rows)} record(s) found")
    if not rows:
        st.info("No matching incident records found.")
        return

    for row in rows:
        diagnosis = row_to_diagnosis(row)
        title = f"Incident #{row['id']} | {row['category']} | {row['severity']} | {row['created_at']}"
        with st.expander(title):
            render_diagnosis(row["user_input"], diagnosis, row["created_at"], row["id"], compact=True)
            report = generate_report(row["user_input"], diagnosis, row["created_at"])
            c1, c2 = st.columns(2)
            c1.download_button(
                "Download Incident Report",
                report,
                file_name=f"network_incident_report_{row['id']}.txt",
                mime="text/plain",
                key=f"history_download_{row['id']}",
            )
            if c2.button("Delete Incident", key=f"delete_{row['id']}"):
                delete_diagnosis(row["id"])
                st.success(f"Incident #{row['id']} deleted.")
                st.rerun()


def about_page() -> None:
    hero(
    "About PacketLens",
    "PacketLens is a network incident analysis tool that helps identify and troubleshoot common DNS, DHCP, Routing, Firewall, TCP/IP, and HTTP/HTTPS issues.",
)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("What It Does")
        st.write(
    "The application analyzes network symptoms, classifies the issue category, estimates severity, and generates troubleshooting recommendations. Diagnoses are stored for future analysis and reporting."
)
        st.subheader("Tech Stack")
        st.write("Python, Streamlit, Groq API, SQLite, Pandas, python-dotenv")

    with col2:
        st.subheader("Industry Use Case")
        st.write(
    "The system can assist helpdesk teams, NOC analysts, and network administrators in identifying common network issues and reviewing recommended troubleshooting steps."
)
        st.subheader("Key Features")
        st.write("""
• Network issue classification

• Root cause analysis

• Severity assessment

• Incident history tracking

• Report generation

• Dashboard analytics
""")

    st.subheader("Architecture")
    st.code(
        """app.py -> Streamlit UI and workflow orchestration
classifier.py -> protocol classification, evidence extraction, severity logic
ai_engine.py -> Groq prompt, JSON response normalization, fallback handling
database.py -> SQLite persistence and dashboard analytics
report_generator.py -> downloadable incident reports""",
        language="text",
    )

    st.subheader("Future Enhancements")
    st.write("""
• FastAPI backend

• Docker deployment

• User authentication

• PDF report generation

• Automated testing with pytest

• Cisco IOS troubleshooting templates
""")

def render_diagnosis(
    issue_description: str,
    diagnosis: dict,
    timestamp: str,
    issue_id: int,
    compact: bool = False,
) -> None:
    category = str(diagnosis.get("category", "Unknown"))
    severity = str(diagnosis.get("severity", "Low"))
    confidence_score = int(diagnosis.get("confidence_score", 70))
    severity_color = SEVERITY_COLORS.get(severity, "#64748b")

    st.markdown(
        f"""
        <div class="incident-card">
            <div class="muted">Incident #{issue_id} | {timestamp} | Source: {diagnosis.get("source", "AI/Rules")}</div>
            <h3>{category} Incident Triage</h3>
            <span class="status-pill" style="background:{severity_color};">{severity}</span>
            <span class="chip">Confidence: {confidence_score}%</span>
            <span class="chip">{diagnosis.get("confidence", "AI-assisted")}</span>
            <p><strong>Probable root cause:</strong> {diagnosis.get("root_cause", "Not available")}</p>
            <p><strong>Business impact:</strong> {diagnosis.get("impact", "Impact needs validation.")}</p>
            <p><strong>Simple explanation:</strong> {diagnosis.get("explanation", "Not available")}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.progress(max(0, min(100, confidence_score)) / 100)

    if not compact:
        st.subheader("Original Incident")
        st.code(issue_description, language="text")

    evidence = diagnosis.get("evidence", {})
    if isinstance(evidence, dict):
        render_evidence(evidence)

    tab1, tab2, tab3, tab4 = st.tabs(["Playbook", "Commands", "Escalation", "Report"])
    with tab1:
        st.subheader("Step-by-Step Troubleshooting")
        render_numbered(diagnosis.get("troubleshooting_steps", []))
        st.subheader("Prevention Tips")
        render_bullets(diagnosis.get("prevention_tips", []))

    with tab2:
        st.subheader("Recommended Commands")
        for command in as_list(diagnosis.get("recommended_commands", [])):
            st.markdown(f'<div class="command-box">{command}</div>', unsafe_allow_html=True)

    with tab3:
        st.subheader("Escalation Guidance")
        render_bullets(diagnosis.get("escalation_guidance", []))

    with tab4:
        report = generate_report(issue_description, diagnosis, timestamp)
        st.download_button(
            "Download Incident Report",
            report,
            file_name=f"network_incident_report_{issue_id}.txt",
            mime="text/plain",
            key=f"diagnosis_download_{issue_id}_{compact}",
        )
        st.text_area("Report Preview", report, height=260)


def render_incident_summary(issue_id: int, description: str, diagnosis: dict, timestamp: str) -> None:
    severity = str(diagnosis.get("severity", "Low"))
    color = SEVERITY_COLORS.get(severity, "#64748b")
    st.markdown(
        f"""
        <div class="panel">
            <div class="muted">Incident #{issue_id} | {timestamp}</div>
            <strong>{diagnosis.get("category", "Unknown")}</strong>
            <span class="status-pill" style="background:{color};">{severity}</span>
            <p>{description}</p>
            <p><strong>Root cause:</strong> {diagnosis.get("root_cause", "Not available")}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_evidence(evidence: dict) -> None:
    st.subheader("Extracted Evidence")
    chips = []
    for label, values in (
        ("IP", evidence.get("ip_addresses", [])),
        ("Domain", evidence.get("domains", [])),
        ("Command", evidence.get("commands_detected", [])),
    ):
        for value in values:
            chips.append(f'<span class="chip">{label}: {value}</span>')
    if chips:
        st.markdown(" ".join(chips), unsafe_allow_html=True)
    else:
        st.caption("No explicit IPs, domains, or commands were detected in the input.")


def render_numbered(items: object) -> None:
    for index, item in enumerate(as_list(items), start=1):
        st.write(f"{index}. {item}")


def render_bullets(items: object) -> None:
    for item in as_list(items):
        st.write(f"- {item}")


def as_list(items: object) -> list[str]:
    if isinstance(items, list):
        return [str(item) for item in items]
    if isinstance(items, str) and items.strip():
        return [items]
    return ["Not available."]


if __name__ == "__main__":
    main()
