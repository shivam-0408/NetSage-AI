import os
import sys
import json
import streamlit as st

# ============================================================
# NetSage AI - Streamlit Dashboard
# Live Raw Packet Tracer -> Parser -> Diagnosis -> Decision
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

for folder in [
    "parser",
    "engine",
    "decision",
    "verifier",
    "risk",
    "orchestrator",
    "checker",
]:
    path = os.path.join(BASE_DIR, folder)
    if path not in sys.path:
        sys.path.insert(0, path)

from packet_parser import parse_output
from netsage_engine import load_cases, find_best_case

try:
    from verification_engine import verify_recommendation
except Exception:
    verify_recommendation = None

try:
    from risk_engine import assess_risk
except Exception:
    assess_risk = None

try:
    from human_review import human_review
except Exception:
    human_review = None


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="NetSage AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# HELPERS
# ============================================================

def safe_dict(value):
    return value if isinstance(value, dict) else {}


def case_id(case):
    return case.get("case_id", case.get("id", "UNKNOWN"))


def case_title(case):
    return case.get("title", case.get("name", "Unknown Case"))


def normalize_text(value):
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, default=str)
    return str(value).lower()


def ping_is_healthy(evidence):
    pings = evidence.get("pings", [])
    return bool(pings) and all(
        str(p.get("status", "")).lower() == "success"
        and float(p.get("loss_percentage") or 0) == 0
        for p in pings
    )


def has_real_fault(evidence):
    indicators = evidence.get("fault_indicators", [])
    # These are actual failure indicators. "Trunk is active" and
    # "802.1Q encapsulation detected" are healthy/configuration evidence.
    failure_words = (
        "loss",
        "unreachable",
        "timeout",
        "down",
        "failed",
        "error",
        "shutdown",
    )
    return any(
        any(word in str(item).lower() for word in failure_words)
        for item in indicators
    )


def apply_safety_gate(evidence, diagnosis, score):
    """
    Prevent a known class of false positives:
    if the supplied evidence proves the destination is reachable,
    do not present a failure diagnosis as an active incident.
    """
    if ping_is_healthy(evidence):
        if diagnosis:
            title = normalize_text(case_title(diagnosis))
            root = normalize_text(diagnosis.get("root_cause", ""))
            if (
                "down" in title
                or "unreachable" in title
                or "loss" in title
                or "down" in root
                or "unreachable" in root
            ):
                return {
                    "case_id": "HEALTHY",
                    "title": "No Active Network Fault Detected",
                    "problem": "Provided evidence shows successful reachability.",
                    "root_cause": "No confirmed active fault in the supplied evidence.",
                    "matching_evidence": [
                        "Ping completed successfully with 0% packet loss.",
                        "Destination is reachable from the supplied test point.",
                    ],
                    "recommended_fix": [],
                    "verification": [
                        "Continue monitoring.",
                        "No configuration change is recommended.",
                    ],
                    "match_score": 0,
                }, 0, True
    return diagnosis, score, False


def calculate_confidence(evidence, diagnosis, selected_score, cases):
    if not diagnosis or case_id(diagnosis) == "HEALTHY":
        return {
            "overall": 95 if ping_is_healthy(evidence) else 60,
            "level": "HIGH" if ping_is_healthy(evidence) else "MODERATE",
            "match_strength": 100 if ping_is_healthy(evidence) else 60,
            "evidence_strength": 90 if evidence.get("pings") else 50,
            "diagnostic_separation": 100,
            "supporting_evidence": len(evidence.get("fault_indicators", [])),
            "contradicting_evidence": 0,
        }

    scores = []
    try:
        evidence_text = json.dumps(evidence, default=str)
        for case in cases:
            score = 0
            text = normalize_text(evidence_text)

            for word in normalize_text(case.get("problem", "")).split():
                if len(word) > 3 and word in text:
                    score += 1

            for symptom in case.get("symptoms", []):
                matches = sum(
                    1
                    for word in normalize_text(symptom).split()
                    if len(word) > 3 and word in text
                )
                if matches >= 2:
                    score += 3

            for _, output in case.get("show_commands", {}).items():
                matches = sum(
                    1
                    for word in normalize_text(output).split()
                    if len(word) > 3 and word in text
                )
                if matches >= 2:
                    score += 4

            scores.append(score)
    except Exception:
        scores = [selected_score]

    scores.sort(reverse=True)
    second = scores[1] if len(scores) > 1 else 0

    match_strength = 92 if selected_score > 0 else 0
    evidence_strength = min(
        100,
        40
        + len(evidence.get("fault_indicators", [])) * 10
        + len(evidence.get("interfaces", [])) * 3
        + len(evidence.get("vlans", [])) * 3,
    )

    separation = 100 if not scores else (
        round(((scores[0] - second) / scores[0]) * 100)
        if scores[0] else 0
    )

    overall = round(
        match_strength * 0.4
        + evidence_strength * 0.4
        + separation * 0.2
    )
    overall = max(0, min(100, overall))

    return {
        "overall": overall,
        "level": "HIGH" if overall >= 80 else "MODERATE" if overall >= 60 else "LOW",
        "match_strength": match_strength,
        "evidence_strength": evidence_strength,
        "diagnostic_separation": separation,
        "supporting_evidence": len(evidence.get("fault_indicators", [])),
        "contradicting_evidence": 0,
    }


def run_analysis(raw_output):
    evidence = parse_output(raw_output)

    cases = load_cases()
    best_case, best_score, best_evidence = find_best_case(
        evidence, cases
    )

    diagnosis = safe_dict(best_case).copy()
    diagnosis["match_score"] = best_score
    diagnosis["matching_evidence"] = best_evidence

    diagnosis, best_score, safety_override = apply_safety_gate(
        evidence, diagnosis, best_score
    )

    confidence = calculate_confidence(
        evidence, diagnosis, best_score, cases
    )

    risk_score = max(
        0,
        min(
            100,
            len(evidence.get("fault_indicators", [])) * 15
            + sum(
                10
                for p in evidence.get("pings", [])
                if str(p.get("status", "")).lower() != "success"
            ),
        ),
    )

    if assess_risk:
        try:
            risk_result = assess_risk(evidence, diagnosis)
            if isinstance(risk_result, dict):
                risk_score = risk_result.get(
                    "risk_score",
                    risk_result.get("score", risk_score)
                )
        except Exception:
            pass

    verification = None

    return {
        "raw_output": raw_output,
        "evidence": evidence,
        "cases": cases,
        "diagnosis": diagnosis,
        "best_score": best_score,
        "confidence": confidence,
        "risk_score": risk_score,
        "verification": verification,
        "safety_override": safety_override,
        "approved": False,
        "audit_saved": False,
    }


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("NetSage AI")
st.sidebar.caption("AI-Powered Network Troubleshooting")

st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Live Evidence",
        "Network Health",
        "Diagnosis",
        "Risk Analysis",
        "Incident Orchestrator",
        "Pipeline Status",
    ],
)

st.sidebar.divider()

if "analysis" in st.session_state:
    st.sidebar.success("Analysis Engine: ONLINE")
    st.sidebar.success("Live Evidence: LOADED")
else:
    st.sidebar.info("Waiting for Packet Tracer input")

st.sidebar.warning(
    "Automatic configuration is DISABLED.\n\n"
    "Human approval is required before any configuration action."
)


# ============================================================
# HEADER
# ============================================================

st.title("NetSage AI")
st.caption("AI-Powered Network Troubleshooting Dashboard")


# ============================================================
# LIVE INPUT - ALWAYS AVAILABLE
# ============================================================

with st.expander("🚀 Analyze New Packet Tracer Output", expanded="analysis" not in st.session_state):
    st.markdown(
        "Paste the raw output copied from Cisco Packet Tracer, then click "
        "**Analyze Network**."
    )

    raw_output = st.text_area(
        "Raw Packet Tracer Output",
        height=320,
        placeholder=(
            "C:\\>ping 192.168.30.10\n\n"
            "C:\\>show ip interface brief\n"
            "C:\\>show vlan brief\n"
            "C:\\>show interfaces trunk"
        ),
        key="raw_packet_output",
    )

    if st.button("🔎 Analyze Network", type="primary", use_container_width=True):
        if not raw_output.strip():
            st.error("Please paste Packet Tracer output first.")
        else:
            try:
                with st.spinner("Running NetSage AI analysis..."):
                    st.session_state.analysis = run_analysis(raw_output)
                st.session_state.approved = False
                st.session_state.verification = None
                st.success("Analysis completed successfully.")
                st.rerun()
            except Exception as error:
                st.exception(error)


# ============================================================
# GET CURRENT ANALYSIS
# ============================================================

analysis = st.session_state.get("analysis")

if not analysis:
    st.info(
        "No live analysis loaded yet. Paste Packet Tracer output above "
        "and click **Analyze Network**."
    )
    st.stop()

evidence = analysis["evidence"]
diagnosis = analysis["diagnosis"]
confidence = analysis["confidence"]
risk_score = analysis["risk_score"]


# ============================================================
# DASHBOARD
# ============================================================

if page == "Dashboard":

    health = max(0, 100 - risk_score)

    st.header("Network Overview")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Network Health", f"{health}/100")
    c2.metric("Risk Score", f"{risk_score}/100")
    c3.metric("AI Confidence", f"{confidence['overall']}%")
    c4.metric("Fault Indicators", len(evidence.get("fault_indicators", [])))

    st.divider()

    st.subheader("Current Diagnosis")

    if case_id(diagnosis) == "HEALTHY":
        st.success("No Active Network Fault Detected")
    else:
        st.info(f"{case_id(diagnosis)} — {case_title(diagnosis)}")

    st.write(f"**Case ID:** {case_id(diagnosis)}")
    st.write(
        f"**Root Cause:** "
        f"{diagnosis.get('root_cause', 'Not established')}"
    )

    st.divider()

    left, right = st.columns(2)

    with left:
        st.subheader("Evidence Snapshot")
        st.write(f"Interfaces: **{len(evidence.get('interfaces', []))}**")
        st.write(f"Ping Tests: **{len(evidence.get('pings', []))}**")
        st.write(f"VLANs: **{len(evidence.get('vlans', []))}**")
        st.write(
            f"Fault Indicators: "
            f"**{len(evidence.get('fault_indicators', []))}**"
        )
        st.write(
            f"Trunk Detected: "
            f"**{bool(evidence.get('trunk', {}).get('is_trunk'))}**"
        )

    with right:
        st.subheader("Safety State")
        st.success("Automatic configuration: DISABLED")
        st.warning("Human approval required")
        st.info(
            "NetSage AI recommends configuration changes but does not "
            "automatically apply them."
        )

    st.divider()
    st.subheader("Pipeline Health")

    phases = [
        ("Phase 1", "Packet Input", True),
        ("Phase 3", "Packet Parser", True),
        ("Phase 4", "Diagnosis Engine", True),
        ("Phase 7", "Decision Intelligence", True),
        ("Human Review", "Approval Gate", False),
        ("Phase 5", "Verification", False),
        ("Phase 6", "Audit Logging", False),
    ]

    for name, label, done in phases:
        st.write(f"**{name} — {label}**  {'READY' if done else 'WAITING'}")


# ============================================================
# LIVE EVIDENCE
# ============================================================

elif page == "Live Evidence":

    st.header("Live Evidence")

    st.subheader("Raw Packet Tracer Output")
    st.code(analysis["raw_output"], language="text")

    st.subheader("Structured Evidence")

    if evidence.get("pings"):
        st.markdown("### Ping Results")
        st.dataframe(evidence["pings"], use_container_width=True)

    if evidence.get("interfaces"):
        st.markdown("### Interfaces")
        st.dataframe(evidence["interfaces"], use_container_width=True)

    if evidence.get("vlans"):
        st.markdown("### VLANs")
        st.dataframe(evidence["vlans"], use_container_width=True)

    st.markdown("### Trunk")
    st.json(evidence.get("trunk", {}))

    st.markdown("### Fault Indicators")
    if evidence.get("fault_indicators"):
        for item in evidence["fault_indicators"]:
            st.warning(item)
    else:
        st.success("No obvious fault indicators detected.")


# ============================================================
# NETWORK HEALTH
# ============================================================

elif page == "Network Health":

    st.header("Network Health")

    health = max(0, 100 - risk_score)

    st.metric("Health Score", f"{health}/100")

    if health >= 80:
        st.success("Network evidence currently indicates healthy operation.")
    elif health >= 60:
        st.warning("Network has moderate risk indicators.")
    else:
        st.error("Network has significant fault indicators.")

    st.write("### Reachability")
    for ping in evidence.get("pings", []):
        st.write(
            f"**{ping.get('destination')}** — "
            f"{ping.get('status')} — "
            f"{ping.get('loss_percentage')}% loss"
        )

    st.write("### Interfaces")
    for interface in evidence.get("interfaces", []):
        st.write(
            f"**{interface.get('interface')}** — "
            f"{interface.get('status')} / "
            f"{interface.get('protocol')}"
        )


# ============================================================
# DIAGNOSIS
# ============================================================

elif page == "Diagnosis":

    st.header("Diagnosis")

    st.subheader(case_title(diagnosis))
    st.write(f"**Case ID:** {case_id(diagnosis)}")
    st.write(f"**Match Score:** {diagnosis.get('match_score', analysis['best_score'])}")

    st.write(
        f"**Confidence:** {confidence['overall']}% "
        f"({confidence['level']})"
    )

    st.write(
        f"**Root Cause:** "
        f"{diagnosis.get('root_cause', 'Not established')}"
    )

    st.write("### Supporting Evidence")
    items = diagnosis.get("matching_evidence", [])
    if items:
        for item in items:
            st.write(f"- {item}")
    else:
        st.write("No specific matching evidence was returned.")

    st.write("### Recommended Fix")
    fix = diagnosis.get("recommended_fix", [])
    if isinstance(fix, list):
        for command in fix:
            st.code(str(command))
    elif fix:
        st.code(str(fix))
    else:
        st.success("No configuration change recommended.")


# ============================================================
# RISK
# ============================================================

elif page == "Risk Analysis":

    st.header("Risk Analysis")

    st.metric("Risk Score", f"{risk_score}/100")

    if risk_score < 30:
        st.success("LOW RISK")
    elif risk_score < 60:
        st.warning("MODERATE RISK")
    else:
        st.error("HIGH RISK")

    st.write("### Risk Indicators")

    for item in evidence.get("fault_indicators", []):
        st.write(f"- {item}")

    st.info(
        "Risk analysis is advisory. NetSage AI never automatically changes "
        "network configuration."
    )


# ============================================================
# INCIDENT ORCHESTRATOR
# ============================================================

elif page == "Incident Orchestrator":

    st.header("Incident Orchestrator")

    if case_id(diagnosis) == "HEALTHY":
        st.success("No incident should be opened for the supplied evidence.")
    else:
        st.info(
            f"Candidate incident: **{case_id(diagnosis)} — "
            f"{case_title(diagnosis)}**"
        )

        st.write("Recommended workflow:")
        st.write("1. Review diagnosis")
        st.write("2. Review evidence")
        st.write("3. Approve recommendation")
        st.write("4. Run verification")
        st.write("5. Save audit record")

    st.warning("Automatic remediation remains disabled.")


# ============================================================
# PIPELINE STATUS
# ============================================================

elif page == "Pipeline Status":

    st.header("Pipeline Status")

    status_items = [
        ("Raw Packet Input", True),
        ("Phase 3 Parser", True),
        ("Phase 4 Diagnosis", True),
        ("Evidence Analysis", True),
        ("Phase 7 Decision Intelligence", True),
        ("Human Approval Gate", analysis.get("approved", False)),
        ("Phase 5 Verification", analysis.get("verification") is not None),
        ("Phase 6 Audit", analysis.get("audit_saved", False)),
    ]

    for label, ready in status_items:
        if ready:
            st.success(f"{label}: READY")
        else:
            st.info(f"{label}: WAITING")

    st.divider()
    st.write(
        "**Automatic configuration applied:** FALSE"
    )


# ============================================================
# HUMAN APPROVAL / VERIFICATION
# ============================================================

st.divider()
st.header("Human Approval & Verification")

if case_id(diagnosis) == "HEALTHY":
    st.success(
        "No active fault is confirmed. No configuration approval is needed."
    )
else:
    st.write(
        "Review the recommendation before allowing verification to run."
    )

    approved = st.checkbox(
        "I have reviewed the diagnosis and approve the recommendation.",
        value=st.session_state.get("approved", False),
    )

    if approved:
        st.session_state.approved = True

        st.success("Human approval recorded for this session.")

        if st.button("Run Recommendation Verification", type="primary"):
            if verify_recommendation is None:
                st.error("Verification engine could not be imported.")
            else:
                try:
                    with st.spinner("Running verification..."):
                        result = verify_recommendation(
                            evidence,
                            case_id(diagnosis),
                        )
                    st.session_state.verification = result
                    analysis["verification"] = result
                    st.rerun()
                except Exception as error:
                    st.exception(error)

    else:
        st.warning(
            "Verification is locked until a human explicitly approves "
            "the recommendation."
        )

verification = st.session_state.get("verification")

if verification is not None:
    st.subheader("Verification Result")
    if isinstance(verification, dict):
        st.json(verification)
    else:
        st.write(verification)

st.caption(
    "NetSage AI safety policy: automatic network configuration is disabled."
)
