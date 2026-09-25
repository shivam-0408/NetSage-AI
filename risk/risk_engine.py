import os
from datetime import datetime


# ============================================================
# NetSage AI - Phase 11
# Network Health & Risk Intelligence
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


# ============================================================
# RISK WEIGHTS
# ============================================================

PING_FAILURE_WEIGHT = 20
INTERFACE_DOWN_WEIGHT = 20
ADMIN_DOWN_WEIGHT = 30
PROTOCOL_DOWN_WEIGHT = 15
HOST_UNREACHABLE_WEIGHT = 15
VLAN_INACTIVE_WEIGHT = 20
TRUNK_FAILURE_WEIGHT = 20
TRUNK_MISSING_WEIGHT = 10

# Corroborating evidence should not be counted
# as a completely separate incident.
CORROBORATION_FACTOR = 0.20


# ============================================================
# HELPERS
# ============================================================

def safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def clamp(value, minimum=0, maximum=100):
    return max(
        minimum,
        min(
            maximum,
            value
        )
    )


def risk_level(score):

    score = safe_float(score)

    if score >= 75:
        return "CRITICAL"

    if score >= 50:
        return "HIGH"

    if score >= 25:
        return "MODERATE"

    return "LOW"


def health_level(score):

    score = safe_float(score)

    if score >= 85:
        return "EXCELLENT"

    if score >= 70:
        return "GOOD"

    if score >= 50:
        return "DEGRADED"

    return "CRITICAL"


# ============================================================
# PING ANALYSIS
# ============================================================

def analyze_pings(evidence):

    findings = []
    risk = 0

    pings = evidence.get(
        "pings",
        []
    )

    if not isinstance(pings, list):
        return risk, findings

    for ping in pings:

        if not isinstance(ping, dict):
            continue

        status = str(
            ping.get(
                "status",
                ""
            )
        ).lower()

        loss = safe_float(
            ping.get(
                "loss_percentage",
                0
            )
        )

        destination = ping.get(
            "destination",
            "unknown"
        )

        if loss >= 100:

            risk = max(
                risk,
                PING_FAILURE_WEIGHT
            )

            findings.append(
                {
                    "type": "PING_FAILURE",
                    "severity": "HIGH",
                    "message": (
                        f"Destination {destination} "
                        f"has 100% packet loss."
                    )
                }
            )

        elif loss > 0:

            partial_risk = int(
                PING_FAILURE_WEIGHT *
                (loss / 100)
            )

            risk = max(
                risk,
                partial_risk
            )

            findings.append(
                {
                    "type": "PARTIAL_PACKET_LOSS",
                    "severity": "MODERATE",
                    "message": (
                        f"Destination {destination} "
                        f"has {loss}% packet loss."
                    )
                }
            )

        elif "unreachable" in status:

            risk = max(
                risk,
                HOST_UNREACHABLE_WEIGHT
            )

            findings.append(
                {
                    "type": "HOST_UNREACHABLE",
                    "severity": "HIGH",
                    "message": (
                        f"Destination {destination} "
                        f"is unreachable."
                    )
                }
            )

    return risk, findings


# ============================================================
# INTERFACE ANALYSIS
# ============================================================

def analyze_interfaces(evidence):

    findings = []
    risk = 0

    interfaces = evidence.get(
        "interfaces",
        []
    )

    if not isinstance(interfaces, list):
        return risk, findings

    for interface in interfaces:

        if not isinstance(interface, dict):
            continue

        name = interface.get(
            "interface",
            "unknown"
        )

        status = str(
            interface.get(
                "status",
                ""
            )
        ).lower()

        protocol = str(
            interface.get(
                "protocol",
                ""
            )
        ).lower()

        interface_risk = 0

        if "administratively down" in status:

            interface_risk = max(
                interface_risk,
                ADMIN_DOWN_WEIGHT
            )

            findings.append(
                {
                    "type": "ADMINISTRATIVELY_DOWN",
                    "severity": "CRITICAL",
                    "message": (
                        f"{name} is administratively down."
                    )
                }
            )

        elif status != "up":

            interface_risk = max(
                interface_risk,
                INTERFACE_DOWN_WEIGHT
            )

            findings.append(
                {
                    "type": "INTERFACE_DOWN",
                    "severity": "HIGH",
                    "message": (
                        f"{name} interface status is "
                        f"{status}."
                    )
                }
            )

        # Protocol-down is related to the same interface.
        # Do not add it at full weight on top of admin-down.
        if protocol != "up":

            if interface_risk == 0:
                interface_risk = PROTOCOL_DOWN_WEIGHT

            findings.append(
                {
                    "type": "PROTOCOL_DOWN",
                    "severity": "HIGH",
                    "message": (
                        f"{name} protocol is "
                        f"{protocol}."
                    )
                }
            )

        risk = max(
            risk,
            interface_risk
        )

    return risk, findings


# ============================================================
# VLAN ANALYSIS
# ============================================================

def analyze_vlans(evidence):

    findings = []
    risk = 0

    vlans = evidence.get(
        "vlans",
        []
    )

    if not isinstance(vlans, list):
        return risk, findings

    for vlan in vlans:

        if not isinstance(vlan, dict):
            continue

        vlan_id = vlan.get(
            "vlan_id",
            "unknown"
        )

        status = str(
            vlan.get(
                "status",
                ""
            )
        ).lower()

        if status != "active":

            risk = max(
                risk,
                VLAN_INACTIVE_WEIGHT
            )

            findings.append(
                {
                    "type": "VLAN_INACTIVE",
                    "severity": "HIGH",
                    "message": (
                        f"VLAN {vlan_id} "
                        f"is not active."
                    )
                }
            )

    return risk, findings


# ============================================================
# TRUNK ANALYSIS
# ============================================================

def analyze_trunk(evidence):

    findings = []
    risk = 0

    trunk = evidence.get(
        "trunk",
        {}
    )

    if not isinstance(trunk, dict):
        trunk = {}

    is_trunk = trunk.get(
        "is_trunk",
        False
    )

    if not is_trunk:

        risk = TRUNK_MISSING_WEIGHT

        findings.append(
            {
                "type": "TRUNK_NOT_DETECTED",
                "severity": "MODERATE",
                "message": (
                    "No active trunk was detected "
                    "in the supplied evidence."
                )
            }
        )

        return risk, findings

    ports = trunk.get(
        "ports",
        []
    )

    if not ports:

        risk = TRUNK_FAILURE_WEIGHT

        findings.append(
            {
                "type": "TRUNK_NO_PORTS",
                "severity": "HIGH",
                "message": (
                    "Trunk detected but no trunk "
                    "ports were identified."
                )
            }
        )

    return risk, findings


# ============================================================
# FAULT INDICATOR ANALYSIS
# ============================================================

def analyze_fault_indicators(evidence):

    findings = []
    risk = 0

    indicators = evidence.get(
        "fault_indicators",
        []
    )

    if not isinstance(indicators, list):
        return risk, findings

    for indicator in indicators:

        text = str(
            indicator
        ).lower()

        if "administratively down" in text:

            risk = max(
                risk,
                10
            )

            findings.append(
                {
                    "type": "FAULT_INDICATOR",
                    "severity": "HIGH",
                    "message": str(indicator)
                }
            )

        elif "100% packet loss" in text:

            risk = max(
                risk,
                10
            )

            findings.append(
                {
                    "type": "FAULT_INDICATOR",
                    "severity": "HIGH",
                    "message": str(indicator)
                }
            )

        elif "unreachable" in text:

            risk = max(
                risk,
                10
            )

            findings.append(
                {
                    "type": "FAULT_INDICATOR",
                    "severity": "HIGH",
                    "message": str(indicator)
                }
            )

    return risk, findings


# ============================================================
# PRIORITY
# ============================================================

def determine_priority(
    risk_score,
    findings
):

    critical = any(
        item.get("severity") == "CRITICAL"
        for item in findings
    )

    high = any(
        item.get("severity") == "HIGH"
        for item in findings
    )

    if critical or risk_score >= 75:
        return "P1 - IMMEDIATE"

    if high or risk_score >= 50:
        return "P2 - HIGH"

    if risk_score >= 25:
        return "P3 - MODERATE"

    return "P4 - LOW"


# ============================================================
# PRIORITY ACTIONS
# ============================================================

def generate_actions(findings):

    actions = []
    seen = set()

    for finding in findings:

        finding_type = finding.get(
            "type"
        )

        if finding_type in seen:
            continue

        seen.add(
            finding_type
        )

        if finding_type == "ADMINISTRATIVELY_DOWN":

            actions.append(
                "Review the affected interface and determine whether it should be enabled."
            )

        elif finding_type == "PROTOCOL_DOWN":

            actions.append(
                "Investigate interface protocol state and Layer 2/Layer 3 connectivity."
            )

        elif finding_type == "INTERFACE_DOWN":

            actions.append(
                "Inspect interface status, cabling, and configuration."
            )

        elif finding_type == "PING_FAILURE":

            actions.append(
                "Investigate the path to the unreachable destination."
            )

        elif finding_type == "HOST_UNREACHABLE":

            actions.append(
                "Check routing, VLAN membership, gateway configuration, and destination availability."
            )

        elif finding_type == "PARTIAL_PACKET_LOSS":

            actions.append(
                "Investigate intermittent connectivity and packet loss."
            )

        elif finding_type == "VLAN_INACTIVE":

            actions.append(
                "Verify VLAN configuration and switch port assignments."
            )

        elif finding_type == "TRUNK_NO_PORTS":

            actions.append(
                "Inspect trunk configuration and trunk interface state."
            )

        elif finding_type == "TRUNK_NOT_DETECTED":

            actions.append(
                "Verify whether a trunk is expected and inspect the relevant switch interfaces."
            )

        elif finding_type == "FAULT_INDICATOR":

            actions.append(
                "Review the reported fault indicator against the complete network evidence."
            )

    if not actions:

        actions.append(
            "No immediate corrective action identified from the supplied evidence."
        )

    return actions


# ============================================================
# BUILD NETWORK HEALTH REPORT
# ============================================================

def analyze_network_health(evidence):

    if not isinstance(evidence, dict):
        evidence = {}

    ping_risk, ping_findings = analyze_pings(
        evidence
    )

    interface_risk, interface_findings = analyze_interfaces(
        evidence
    )

    vlan_risk, vlan_findings = analyze_vlans(
        evidence
    )

    trunk_risk, trunk_findings = analyze_trunk(
        evidence
    )

    indicator_risk, indicator_findings = analyze_fault_indicators(
        evidence
    )

    findings = (
        ping_findings
        + interface_findings
        + vlan_findings
        + trunk_findings
        + indicator_findings
    )

    # --------------------------------------------------------
    # IMPORTANT:
    # Evidence sources describe the same incident.
    # We therefore use the strongest primary signal and
    # only a small corroboration contribution from others.
    # This prevents double/triple counting.
    # --------------------------------------------------------

    category_risks = [
        ping_risk,
        interface_risk,
        vlan_risk,
        trunk_risk,
        indicator_risk
    ]

    primary_risk = max(
        category_risks,
        default=0
    )

    secondary_risks = sorted(
        category_risks,
        reverse=True
    )[1:]

    corroboration = sum(
        secondary_risks
    ) * CORROBORATION_FACTOR

    raw_risk = (
        primary_risk
        + corroboration
    )

    risk_score = clamp(
        round(raw_risk, 1)
    )

    health_score = clamp(
        round(
            100 - risk_score,
            1
        )
    )

    risk = risk_level(
        risk_score
    )

    health = health_level(
        health_score
    )

    priority = determine_priority(
        risk_score,
        findings
    )

    actions = generate_actions(
        findings
    )

    critical_count = sum(
        1
        for item in findings
        if item.get("severity") == "CRITICAL"
    )

    high_count = sum(
        1
        for item in findings
        if item.get("severity") == "HIGH"
    )

    moderate_count = sum(
        1
        for item in findings
        if item.get("severity") == "MODERATE"
    )

    return {

        "phase": "Phase 11",

        "generated_at":
            datetime.now().isoformat(),

        "health_score":
            health_score,

        "health_level":
            health,

        "risk_score":
            risk_score,

        "risk_level":
            risk,

        "priority":
            priority,

        "finding_count":
            len(findings),

        "severity_summary": {

            "critical":
                critical_count,

            "high":
                high_count,

            "moderate":
                moderate_count
        },

        "findings":
            findings,

        "priority_actions":
            actions,

        "safety": {

            "automatic_configuration_applied":
                False,

            "human_approval_required":
                True
        }
    }


# ============================================================
# PUBLIC API
# ============================================================

def assess_risk(evidence):

    """
    Public Phase 11 risk-engine interface.
    """

    if not isinstance(evidence, dict):
        evidence = {}

    return analyze_network_health(
        evidence
    )


# ============================================================
# DISPLAY
# ============================================================

def display_health_report(report):

    print()
    print("=" * 60)
    print(
        "              PHASE 11 NETWORK HEALTH"
    )
    print("=" * 60)

    print()

    print(
        f"Network Health Score: "
        f"{report.get('health_score', 0)}/100"
    )

    print(
        f"Health Level: "
        f"{report.get('health_level', 'UNKNOWN')}"
    )

    print()

    print(
        f"Risk Score: "
        f"{report.get('risk_score', 0)}/100"
    )

    print(
        f"Risk Level: "
        f"{report.get('risk_level', 'UNKNOWN')}"
    )

    print(
        f"Priority: "
        f"{report.get('priority', 'UNKNOWN')}"
    )

    print()

    print(
        "Severity Summary:"
    )

    summary = report.get(
        "severity_summary",
        {}
    )

    print(
        f"- Critical: "
        f"{summary.get('critical', 0)}"
    )

    print(
        f"- High: "
        f"{summary.get('high', 0)}"
    )

    print(
        f"- Moderate: "
        f"{summary.get('moderate', 0)}"
    )

    print()

    print(
        "Risk Findings:"
    )

    findings = report.get(
        "findings",
        []
    )

    if findings:

        for finding in findings:

            print(
                f"- "
                f"[{finding.get('severity', 'UNKNOWN')}] "
                f"{finding.get('message', '')}"
            )

    else:

        print(
            "- No significant risk findings."
        )

    print()

    print(
        "Priority Actions:"
    )

    actions = report.get(
        "priority_actions",
        []
    )

    for index, action in enumerate(
        actions,
        start=1
    ):

        print(
            f"{index}. {action}"
        )

    print()

    print(
        "Safety:"
    )

    print(
        "Automatic configuration applied: FALSE"
    )

    print(
        "Human approval required: TRUE"
    )

    print()

    print("=" * 60)


# ============================================================
# TEST
# ============================================================

def test():

    print("=" * 60)
    print(
        "       NetSage AI Phase 11 Risk Engine Test"
    )
    print("=" * 60)

    test_evidence = {

        "pings": [

            {
                "destination":
                    "192.168.10.1",

                "status":
                    "Success",

                "loss_percentage":
                    0
            },

            {
                "destination":
                    "192.168.30.10",

                "status":
                    "Host Unreachable",

                "loss_percentage":
                    100
            }
        ],

        "interfaces": [

            {
                "interface":
                    "GigabitEthernet0/0",

                "ip_address":
                    "unassigned",

                "status":
                    "up",

                "protocol":
                    "up"
            },

            {
                "interface":
                    "GigabitEthernet0/0.10",

                "ip_address":
                    "192.168.10.1",

                "status":
                    "up",

                "protocol":
                    "up"
            },

            {
                "interface":
                    "GigabitEthernet0/0.30",

                "ip_address":
                    "192.168.30.1",

                "status":
                    "administratively down",

                "protocol":
                    "down"
            }
        ],

        "vlans": [

            {
                "vlan_id":
                    "10",

                "name":
                    "USERS",

                "status":
                    "active",

                "ports":
                    "Fa0/1"
            },

            {
                "vlan_id":
                    "30",

                "name":
                    "SERVERS",

                "status":
                    "active",

                "ports":
                    "Fa0/2"
            }
        ],

        "trunk": {

            "is_trunk":
                True,

            "ports":
                [
                    "Gig0/1"
                ],

            "allowed_vlans":
                "1-1005",

            "active_vlans":
                "1,10,30"
        },

        "fault_indicators": [

            "Interface administratively down",

            "Interface status/protocol down",

            "100% packet loss",

            "Destination host unreachable",

            "Trunk is active",

            "802.1Q encapsulation detected"
        ]
    }

    report = assess_risk(
        test_evidence
    )

    display_health_report(
        report
    )

    assert isinstance(
        report,
        dict
    )

    assert report.get(
        "phase"
    ) == "Phase 11"

    assert 0 <= report.get(
        "risk_score",
        -1
    ) <= 100

    assert 0 <= report.get(
        "health_score",
        -1
    ) <= 100

    assert report.get(
        "health_score"
    ) == round(
        100 - report.get(
            "risk_score"
        ),
        1
    )

    assert report.get(
        "safety",
        {}
    ).get(
        "automatic_configuration_applied"
    ) is False

    assert report.get(
        "safety",
        {}
    ).get(
        "human_approval_required"
    ) is True

    print()
    print(
        "PHASE 11 RISK ENGINE TEST COMPLETE"
    )

    print(
        "All Phase 11 assertions passed."
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    test()