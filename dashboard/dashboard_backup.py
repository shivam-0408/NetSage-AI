import streamlit as st
import sys
import os


# ============================================================
# NETSAGE AI - DASHBOARD
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


# ============================================================
# SAFE IMPORTS
# ============================================================

try:
    from risk.risk_engine import assess_risk
    RISK_ENGINE_AVAILABLE = True
except Exception:
    assess_risk = None
    RISK_ENGINE_AVAILABLE = False


try:
    from orchestrator.incident_orchestrator import (
        orchestrate_incident
    )
    ORCHESTRATOR_AVAILABLE = True
except Exception:
    orchestrate_incident = None
    ORCHESTRATOR_AVAILABLE = False


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="NetSage AI",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM STYLE
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 48px;
        font-weight: 800;
        margin-bottom: 0px;
    }

    .subtitle {
        font-size: 20px;
        opacity: 0.75;
        margin-bottom: 30px;
    }

    .status-card {
        padding: 20px;
        border-radius: 12px;
        border: 1px solid rgba(128,128,128,0.25);
        min-height: 130px;
    }

    .section-title {
        font-size: 28px;
        font-weight: 700;
        margin-top: 20px;
    }

    .small-label {
        font-size: 14px;
        opacity: 0.7;
    }

    .big-number {
        font-size: 38px;
        font-weight: 700;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# DEMO NETWORK EVIDENCE
# ============================================================

DEFAULT_EVIDENCE = {

    "pings": [

        {
            "destination": "192.168.30.10",
            "status": "Host Unreachable",
            "loss_percentage": 100
        }

    ],

    "interfaces": [

        {
            "interface": "GigabitEthernet0/0",
            "ip_address": "unassigned",
            "status": "up",
            "protocol": "up"
        },

        {
            "interface": "GigabitEthernet0/0.30",
            "ip_address": "192.168.30.1",
            "status": "administratively down",
            "protocol": "down"
        }

    ],

    "vlans": [

        {
            "vlan_id": "30",
            "name": "SERVERS",
            "status": "active",
            "ports": "Fa0/2"
        }

    ],

    "trunk": {

        "is_trunk": True,
        "ports": ["Gig0/1"],
        "allowed_vlans": "1-1005",
        "active_vlans": "1,10,30"

    },

    "fault_indicators": [

        "Interface administratively down",
        "100% packet loss",
        "Destination host unreachable"

    ]

}


# ============================================================
# DIAGNOSIS
# ============================================================

DEFAULT_DIAGNOSIS = {

    "case_id":
        "case_01",

    "title":
        "Inter-VLAN Routing - Router Subinterface Down",

    "root_cause":
        "Router subinterface is administratively down.",

    "match_score":
        9,

    "confidence":
        64,

    "recommended_fix": [

        "enable",
        "configure terminal",
        "interface GigabitEthernet0/0.30",
        "no shutdown",
        "end"

    ],

    "verification": [

        "show ip interface brief",
        "ping 192.168.30.10"

    ]

}


# ============================================================
# SESSION STATE
# ============================================================

if "evidence" not in st.session_state:
    st.session_state.evidence = DEFAULT_EVIDENCE.copy()

if "diagnosis" not in st.session_state:
    st.session_state.diagnosis = DEFAULT_DIAGNOSIS.copy()


# ============================================================
# CALCULATE RISK
# ============================================================

if RISK_ENGINE_AVAILABLE:

    try:
        risk_report = assess_risk(
            st.session_state.evidence
        )
    except Exception:
        risk_report = {
            "health_score": 64,
            "health_level": "MODERATE",
            "risk_score": 36,
            "risk_level": "MODERATE",
            "priority": "MEDIUM",
            "findings": [],
            "priority_actions": []
        }

else:

    risk_report = {

        "health_score": 64,
        "health_level": "MODERATE",

        "risk_score": 36,
        "risk_level": "MODERATE",

        "priority": "MEDIUM",

        "findings": [],

        "priority_actions": []

    }


# ============================================================
# ORCHESTRATION
# ============================================================

if ORCHESTRATOR_AVAILABLE:

    try:

        orchestration = orchestrate_incident(

            st.session_state.evidence,

            diagnosis=st.session_state.diagnosis

        )

    except Exception:

        orchestration = {}

else:

    orchestration = {}


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🌐 NetSage AI")

st.sidebar.caption(
    "AI-Powered Network Troubleshooting"
)

st.sidebar.markdown("---")

page = st.sidebar.radio(

    "Navigation",

    [

        "Dashboard",
        "Network Health",
        "Diagnosis",
        "Risk Analysis",
        "Incident Orchestrator",
        "Pipeline Status"

    ]

)

st.sidebar.markdown("---")

st.sidebar.info(
    "Safety Mode\n\n"
    "Automatic configuration: DISABLED\n\n"
    "Human approval: REQUIRED"
)


# ============================================================
# HEADER
# ============================================================

def page_header(title, subtitle):

    st.markdown(
        f'<div class="main-title">{title}</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="subtitle">{subtitle}</div>',
        unsafe_allow_html=True
    )


# ============================================================
# DASHBOARD
# ============================================================

if page == "Dashboard":

    page_header(
        "🌐 NetSage AI",
        "AI-Powered Network Troubleshooting Dashboard"
    )

    st.markdown("---")

    st.subheader("Network Overview")

    col1, col2, col3, col4 = st.columns(4)

    health_score = risk_report.get(
        "health_score",
        64
    )

    risk_score = risk_report.get(
        "risk_score",
        36
    )

    col1.metric(
        "Network Health",
        f"{health_score}/100"
    )

    col2.metric(
        "Risk Score",
        f"{risk_score}/100"
    )

    col3.metric(
        "Active Incidents",
        "1"
    )

    col4.metric(
        "AI Confidence",
        "64%"
    )

    st.markdown("---")

    st.subheader("Current Diagnosis")

    st.info(
        st.session_state.diagnosis.get(
            "title",
            "Unknown"
        )
    )

    st.write(
        "**Root Cause:** "
        + st.session_state.diagnosis.get(
            "root_cause",
            "Unknown"
        )
    )

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Evidence")

        st.write(
            f"Interfaces: "
            f"{len(st.session_state.evidence.get('interfaces', []))}"
        )

        st.write(
            f"Pings: "
            f"{len(st.session_state.evidence.get('pings', []))}"
        )

        st.write(
            f"VLANs: "
            f"{len(st.session_state.evidence.get('vlans', []))}"
        )

        st.write(
            f"Fault Indicators: "
            f"{len(st.session_state.evidence.get('fault_indicators', []))}"
        )

    with col2:

        st.subheader("Safety")

        st.success(
            "Automatic configuration: FALSE"
        )

        st.warning(
            "Human approval required"
        )


# ============================================================
# NETWORK HEALTH
# ============================================================

elif page == "Network Health":

    page_header(
        "Network Health",
        "Phase 11 Network Health and Risk Assessment"
    )

    health = risk_report.get(
        "health_score",
        64
    )

    risk = risk_report.get(
        "risk_score",
        36
    )

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Network Health Score",
            f"{health}/100"
        )

        st.progress(
            max(
                0,
                min(
                    100,
                    int(health)
                )
            ) / 100
        )

        st.write(
            "Health Level:",
            risk_report.get(
                "health_level",
                "UNKNOWN"
            )
        )

    with col2:

        st.metric(
            "Network Risk Score",
            f"{risk}/100"
        )

        st.progress(
            max(
                0,
                min(
                    100,
                    int(risk)
                )
            ) / 100
        )

        st.write(
            "Risk Level:",
            risk_report.get(
                "risk_level",
                "UNKNOWN"
            )
        )

    st.markdown("---")

    st.subheader("Severity Summary")

    summary = risk_report.get(
        "severity_summary",
        {}
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Critical",
        summary.get("critical", 0)
    )

    c2.metric(
        "High",
        summary.get("high", 0)
    )

    c3.metric(
        "Moderate",
        summary.get("moderate", 0)
    )

    st.markdown("---")

    st.subheader("Risk Findings")

    findings = risk_report.get(
        "findings",
        []
    )

    if findings:

        for finding in findings:

            severity = finding.get(
                "severity",
                "UNKNOWN"
            )

            message = finding.get(
                "message",
                ""
            )

            st.warning(
                f"[{severity}] {message}"
            )

    else:

        st.success(
            "No significant risk findings."
        )

    st.subheader("Priority Actions")

    actions = risk_report.get(
        "priority_actions",
        []
    )

    if actions:

        for index, action in enumerate(
            actions,
            start=1
        ):

            st.write(
                f"{index}. {action}"
            )

    else:

        st.write(
            "No priority actions available."
        )


# ============================================================
# DIAGNOSIS
# ============================================================

elif page == "Diagnosis":

    page_header(
        "AI Diagnosis",
        "Network troubleshooting diagnosis generated by NetSage AI"
    )

    diagnosis = st.session_state.diagnosis

    st.subheader(
        diagnosis.get(
            "title",
            "Unknown Case"
        )
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Case ID",
        diagnosis.get(
            "case_id",
            "UNKNOWN"
        )
    )

    col2.metric(
        "Match Score",
        diagnosis.get(
            "match_score",
            0
        )
    )

    col3.metric(
        "Confidence",
        f"{diagnosis.get('confidence', 64)}%"
    )

    st.markdown("---")

    st.subheader("Root Cause")

    st.error(
        diagnosis.get(
            "root_cause",
            "Unknown"
        )
    )

    st.subheader("Recommended Fix")

    fixes = diagnosis.get(
        "recommended_fix",
        []
    )

    st.code(
        "\n".join(
            fixes
        ),
        language="text"
    )

    st.warning(
        "These commands are recommendations only. "
        "NetSage AI does NOT automatically apply them."
    )

    st.subheader("Verification")

    for check in diagnosis.get(
        "verification",
        []
    ):

        st.write(
            "✓",
            check
        )


# ============================================================
# RISK ANALYSIS
# ============================================================

elif page == "Risk Analysis":

    page_header(
        "Risk Analysis",
        "Phase 11 risk intelligence and safety assessment"
    )

    st.metric(
        "Overall Risk",
        f"{risk_report.get('risk_score', 36)}/100"
    )

    st.write(
        "Risk Level:",
        risk_report.get(
            "risk_level",
            "MODERATE"
        )
    )

    st.write(
        "Priority:",
        risk_report.get(
            "priority",
            "MEDIUM"
        )
    )

    st.markdown("---")

    st.subheader("Network Evidence")

    evidence = st.session_state.evidence

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "Interfaces",
            "Pings",
            "VLANs",
            "Fault Indicators"
        ]
    )

    with tab1:

        st.json(
            evidence.get(
                "interfaces",
                []
            )
        )

    with tab2:

        st.json(
            evidence.get(
                "pings",
                []
            )
        )

    with tab3:

        st.json(
            evidence.get(
                "vlans",
                []
            )
        )

    with tab4:

        st.json(
            evidence.get(
                "fault_indicators",
                []
            )
        )


# ============================================================
# INCIDENT ORCHESTRATOR
# ============================================================

elif page == "Incident Orchestrator":

    page_header(
        "Incident Orchestrator",
        "Phase 8 incident coordination and remediation workflow"
    )

    if orchestration:

        incident = orchestration.get(
            "incident",
            {}
        )

        confidence = orchestration.get(
            "confidence",
            {}
        )

        safety = orchestration.get(
            "safety",
            {}
        )

        st.success(
            "Incident Status: "
            + orchestration.get(
                "status",
                "ORCHESTRATED"
            )
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Case ID",
            incident.get(
                "case_id",
                "UNKNOWN"
            )
        )

        col2.metric(
            "Confidence",
            f"{confidence.get('score', 0)}%"
        )

        col3.metric(
            "Confidence Level",
            confidence.get(
                "level",
                "LOW"
            )
        )

        st.markdown("---")

        st.subheader("Incident")

        st.write(
            "**Title:**",
            incident.get(
                "title",
                "Unknown"
            )
        )

        st.write(
            "**Root Cause:**",
            incident.get(
                "root_cause",
                "Unknown"
            )
        )

        st.subheader("Recommended Remediation")

        st.code(
            "\n".join(
                orchestration.get(
                    "recommended_fix",
                    []
                )
            ),
            language="text"
        )

        st.subheader("Verification")

        for check in orchestration.get(
            "verification",
            []
        ):

            st.write(
                "✓",
                check
            )

        st.markdown("---")

        st.subheader("Safety Controls")

        if safety.get(
            "automatic_configuration_applied",
            False
        ):

            st.error(
                "Automatic configuration was applied."
            )

        else:

            st.success(
                "Automatic configuration applied: FALSE"
            )

        if safety.get(
            "human_approval_required",
            True
        ):

            st.warning(
                "Human approval required before configuration."
            )

    else:

        st.error(
            "Incident orchestrator unavailable."
        )


# ============================================================
# PIPELINE STATUS
# ============================================================

elif page == "Pipeline Status":

    page_header(
        "Pipeline Status",
        "NetSage AI implementation status"
    )

    phases = [

        ("Phase 1", "Packet Input", True),
        ("Phase 2", "Packet Parser", True),
        ("Phase 3", "Structured Evidence", True),
        ("Phase 4", "Diagnosis Engine", True),
        ("Phase 5", "Verification Engine", True),
        ("Phase 6", "Audit Logging", True),
        ("Phase 7", "Decision Intelligence", True),
        ("Phase 8", "Incident Orchestrator", True),
        ("Phase 9", "Evidence / Confidence", True),
        ("Phase 10", "Adaptive Decision", True),
        ("Phase 11", "Risk Engine", True),
        ("Dashboard", "Streamlit Dashboard", True)

    ]

    for phase, name, status in phases:

        col1, col2, col3 = st.columns(
            [2, 6, 2]
        )

        col1.write(
            f"**{phase}**"
        )

        col2.write(
            name
        )

        if status:

            col3.success(
                "OK"
            )

        else:

            col3.error(
                "PENDING"
            )

    st.markdown("---")

    st.subheader("System Safety")

    st.success(
        "Automatic network configuration: DISABLED"
    )

    st.warning(
        "Human approval is required before remediation."
    )

    st.info(
        "NetSage AI provides diagnosis and recommended "
        "configuration only."
    )


# ============================================================
# FOOTER
# ============================================================

st.sidebar.markdown("---")

st.sidebar.caption(
    "NetSage AI | Network Troubleshooting Platform"
)

st.sidebar.caption(
    "Phase 8 → Phase 11 → Dashboard"
)