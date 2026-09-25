# ============================================================
# NetSage AI - Phase 8 Incident Orchestrator
# ============================================================


# ============================================================
# EXTRACT SELECTED DIAGNOSIS
# ============================================================

def extract_selected_diagnosis(
    adaptive_data,
    decision_data=None
):
    """
    Extract the selected diagnosis from Phase 10,
    Phase 9, or older decision structures.
    """

    if not isinstance(adaptive_data, dict):
        adaptive_data = {}

    selected = adaptive_data.get(
        "selected_case"
    )

    if isinstance(selected, dict):
        return selected

    for key in (
        "diagnosis",
        "selected_diagnosis",
        "best_diagnosis",
        "case"
    ):

        candidate = adaptive_data.get(
            key
        )

        if isinstance(candidate, dict):
            return candidate

    ranked = adaptive_data.get(
        "ranked_diagnoses",
        []
    )

    if isinstance(ranked, list) and ranked:

        if isinstance(ranked[0], dict):
            return ranked[0]

    if isinstance(decision_data, dict):

        for key in (
            "selected_case",
            "selected_diagnosis",
            "diagnosis",
            "best_diagnosis",
            "case"
        ):

            candidate = decision_data.get(
                key
            )

            if isinstance(candidate, dict):
                return candidate

        ranked = decision_data.get(
            "ranked_diagnoses",
            []
        )

        if isinstance(ranked, list) and ranked:

            if isinstance(ranked[0], dict):
                return ranked[0]

    return {
        "case_id": "UNKNOWN",
        "title": "Unknown Case",
        "score": 0,
        "confidence": 0
    }


# ============================================================
# EXTRACT CONFIDENCE
# ============================================================

def extract_confidence(
    adaptive_data,
    decision_data=None,
    diagnosis=None
):
    """
    Extract confidence from available decision structures.
    """

    if isinstance(adaptive_data, dict):

        for key in (
            "overall_confidence",
            "adaptive_confidence",
            "confidence"
        ):

            value = adaptive_data.get(
                key
            )

            if value is not None:

                try:
                    return float(value)

                except (
                    TypeError,
                    ValueError
                ):
                    pass

    if isinstance(decision_data, dict):

        for key in (
            "confidence",
            "overall_confidence",
            "decision_confidence"
        ):

            value = decision_data.get(
                key
            )

            if value is not None:

                try:
                    return float(value)

                except (
                    TypeError,
                    ValueError
                ):
                    pass

    if isinstance(diagnosis, dict):

        for key in (
            "confidence",
            "match_confidence",
            "score"
        ):

            value = diagnosis.get(
                key
            )

            if value is not None:

                try:
                    return float(value)

                except (
                    TypeError,
                    ValueError
                ):
                    pass

    return 0.0


# ============================================================
# NORMALIZE DIAGNOSIS
# ============================================================

def normalize_diagnosis(
    diagnosis,
    confidence=0
):
    """
    Convert diagnosis into a stable Phase 8 structure.
    """

    if not isinstance(diagnosis, dict):
        diagnosis = {}

    case_id = (

        diagnosis.get("case_id")
        or diagnosis.get("id")
        or diagnosis.get("case")
        or "UNKNOWN"
    )

    title = (

        diagnosis.get("title")
        or diagnosis.get("name")
        or diagnosis.get("description")
        or "Unknown Case"
    )

    try:

        confidence = float(
            confidence
        )

    except (
        TypeError,
        ValueError
    ):

        confidence = 0.0

    normalized = diagnosis.copy()

    normalized["case_id"] = case_id
    normalized["title"] = title
    normalized["confidence"] = confidence

    return normalized


# ============================================================
# NORMALIZE EVIDENCE
# ============================================================

def normalize_evidence(
    evidence
):
    """
    Make sure network evidence always has
    the expected dictionary structure.
    """

    if not isinstance(evidence, dict):
        evidence = {}

    normalized = evidence.copy()

    if not isinstance(
        normalized.get("pings"),
        list
    ):
        normalized["pings"] = []

    if not isinstance(
        normalized.get("interfaces"),
        list
    ):
        normalized["interfaces"] = []

    if not isinstance(
        normalized.get("vlans"),
        list
    ):
        normalized["vlans"] = []

    if not isinstance(
        normalized.get("fault_indicators"),
        list
    ):
        normalized["fault_indicators"] = []

    if not isinstance(
        normalized.get("trunk"),
        dict
    ):
        normalized["trunk"] = {}

    return normalized


# ============================================================
# BUILD INCIDENT SUMMARY
# ============================================================

def build_incident_summary(
    evidence,
    diagnosis
):
    """
    Build a human-readable incident summary.
    """

    evidence = normalize_evidence(
        evidence
    )

    diagnosis = normalize_diagnosis(
        diagnosis
    )

    interface_count = len(
        evidence.get(
            "interfaces",
            []
        )
    )

    ping_count = len(
        evidence.get(
            "pings",
            []
        )
    )

    vlan_count = len(
        evidence.get(
            "vlans",
            []
        )
    )

    fault_count = len(
        evidence.get(
            "fault_indicators",
            []
        )
    )

    trunk = evidence.get(
        "trunk",
        {}
    )

    trunk_detected = bool(
        trunk.get(
            "is_trunk",
            False
        )
    )

    return {

        "case_id":
            diagnosis.get(
                "case_id",
                "UNKNOWN"
            ),

        "title":
            diagnosis.get(
                "title",
                "Unknown Case"
            ),

        "confidence":
            diagnosis.get(
                "confidence",
                0
            ),

        "evidence_counts": {

            "interfaces":
                interface_count,

            "pings":
                ping_count,

            "vlans":
                vlan_count,

            "fault_indicators":
                fault_count
        },

        "trunk_detected":
            trunk_detected
    }


# ============================================================
# BUILD ORCHESTRATION RESULT
# ============================================================

def orchestrate_incident(
    evidence,
    diagnosis=None,
    adaptive_data=None,
    decision_data=None
):
    """
    Phase 8 Incident Orchestrator.

    Combines evidence, diagnosis, confidence,
    remediation information, and safety state
    into one stable orchestration result.

    No network configuration is automatically applied.
    """

    evidence = normalize_evidence(
        evidence
    )

    if diagnosis is None:

        diagnosis = extract_selected_diagnosis(
            adaptive_data,
            decision_data
        )

    confidence = extract_confidence(
        adaptive_data,
        decision_data,
        diagnosis
    )

    normalized_diagnosis = normalize_diagnosis(
        diagnosis,
        confidence
    )

    summary = build_incident_summary(
        evidence,
        normalized_diagnosis
    )

    recommended_fix = normalized_diagnosis.get(
        "recommended_fix",
        []
    )

    if recommended_fix is None:
        recommended_fix = []

    if not isinstance(
        recommended_fix,
        list
    ):
        recommended_fix = [
            recommended_fix
        ]

    verification = normalized_diagnosis.get(
        "verification",
        []
    )

    if verification is None:
        verification = []

    if not isinstance(
        verification,
        list
    ):
        verification = [
            verification
        ]

    result = {

        "phase":
            8,

        "status":
            "ORCHESTRATED",

        "incident": {

            "case_id":
                normalized_diagnosis.get(
                    "case_id",
                    "UNKNOWN"
                ),

            "title":
                normalized_diagnosis.get(
                    "title",
                    "Unknown Case"
                ),

            "root_cause":
                normalized_diagnosis.get(
                    "root_cause",
                    "Unknown"
                )
        },

        "diagnosis":
            normalized_diagnosis,

        "confidence": {

            "score":
                confidence,

            "level":
                (
                    "HIGH"
                    if confidence >= 80
                    else
                    "MODERATE"
                    if confidence >= 60
                    else
                    "LOW"
                )
        },

        "evidence":
            evidence,

        "summary":
            summary,

        "recommended_fix":
            recommended_fix,

        "verification":
            verification,

        "safety": {

            "automatic_configuration_applied":
                False,

            "human_approval_required":
                True
        }
    }

    return result


# ============================================================
# DISPLAY RESULT
# ============================================================

def display_orchestration_result(
    result
):
    """
    Display Phase 8 orchestration result.
    """

    if not isinstance(
        result,
        dict
    ):
        result = {}

    incident = result.get(
        "incident",
        {}
    )

    confidence = result.get(
        "confidence",
        {}
    )

    summary = result.get(
        "summary",
        {}
    )

    safety = result.get(
        "safety",
        {}
    )

    print()
    print("=" * 60)
    print(
        "          PHASE 8 INCIDENT ORCHESTRATOR"
    )
    print("=" * 60)

    print()

    print(
        f"Status: "
        f"{result.get('status', 'UNKNOWN')}"
    )

    print()

    print(
        "Incident:"
    )

    print(
        f"- Case ID: "
        f"{incident.get('case_id', 'UNKNOWN')}"
    )

    print(
        f"- Title: "
        f"{incident.get('title', 'Unknown Case')}"
    )

    print(
        f"- Root Cause: "
        f"{incident.get('root_cause', 'Unknown')}"
    )

    print()

    print(
        "Confidence:"
    )

    print(
        f"- Score: "
        f"{confidence.get('score', 0)}%"
    )

    print(
        f"- Level: "
        f"{confidence.get('level', 'UNKNOWN')}"
    )

    print()

    print(
        "Evidence Summary:"
    )

    counts = summary.get(
        "evidence_counts",
        {}
    )

    print(
        f"- Interfaces: "
        f"{counts.get('interfaces', 0)}"
    )

    print(
        f"- Pings: "
        f"{counts.get('pings', 0)}"
    )

    print(
        f"- VLANs: "
        f"{counts.get('vlans', 0)}"
    )

    print(
        f"- Fault Indicators: "
        f"{counts.get('fault_indicators', 0)}"
    )

    print(
        f"- Trunk Detected: "
        f"{summary.get('trunk_detected', False)}"
    )

    print()

    print(
        "Recommended Fix:"
    )

    fixes = result.get(
        "recommended_fix",
        []
    )

    if fixes:

        for fix in fixes:

            print(
                f"- {fix}"
            )

    else:

        print(
            "- No remediation command available."
        )

    print()

    print(
        "Verification:"
    )

    checks = result.get(
        "verification",
        []
    )

    if checks:

        for check in checks:

            print(
                f"- {check}"
            )

    else:

        print(
            "- No verification steps available."
        )

    print()

    print(
        "Safety:"
    )

    print(
        "Automatic configuration applied: "
        f"{safety.get('automatic_configuration_applied', False)}"
    )

    print(
        "Human approval required: "
        f"{safety.get('human_approval_required', True)}"
    )

    print()

    print("=" * 60)


# ============================================================
# PHASE 8 TEST
# ============================================================

def test():

    print("=" * 60)
    print(
        "       NetSage AI Phase 8 Orchestrator Test"
    )
    print("=" * 60)

    # --------------------------------------------------------
    # TEST EVIDENCE
    # --------------------------------------------------------

    evidence = {

        "pings": [

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

            "100% packet loss",

            "Destination host unreachable"
        ]
    }

    # --------------------------------------------------------
    # TEST DIAGNOSIS
    # --------------------------------------------------------

    diagnosis = {

        "case_id":
            "case_01",

        "title":
            "Inter-VLAN Routing - Router Subinterface Down",

        "root_cause":
            "Router subinterface is administratively down.",

        "match_score":
            9,

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

    # --------------------------------------------------------
    # RUN ORCHESTRATOR
    # --------------------------------------------------------

    result = orchestrate_incident(

        evidence,

        diagnosis=diagnosis
    )

    # --------------------------------------------------------
    # DISPLAY RESULT
    # --------------------------------------------------------

    display_orchestration_result(
        result
    )

    # --------------------------------------------------------
    # TEST VALIDATION
    # --------------------------------------------------------

    assert isinstance(
        result,
        dict
    )

    assert result.get(
        "phase"
    ) == 8

    assert result.get(
        "status"
    ) == "ORCHESTRATED"

    assert result.get(
        "incident",
        {}
    ).get(
        "case_id"
    ) == "case_01"

    assert result.get(
        "safety",
        {}
    ).get(
        "automatic_configuration_applied"
    ) is False

    assert result.get(
        "safety",
        {}
    ).get(
        "human_approval_required"
    ) is True

    print()
    print(
        "PHASE 8 ORCHESTRATOR TEST COMPLETE"
    )

    print(
        "All Phase 8 assertions passed."
    )

    print(
        "Automatic configuration applied: FALSE"
    )


# ============================================================
# PROGRAM ENTRY
# ============================================================

if __name__ == "__main__":

    test()