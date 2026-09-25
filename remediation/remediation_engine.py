
import os
from datetime import datetime


# ============================================================
# NetSage AI - Phase 12
# Remediation Planning Engine
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


# ============================================================
# SAFETY POLICY
# ============================================================

AUTOMATIC_EXECUTION = False
HUMAN_APPROVAL_REQUIRED = True


# ============================================================
# ACTION REGISTRY
# ============================================================

ACTION_REGISTRY = {
    "case_01": {
        "name": "Enable Router Subinterface",
        "commands": [
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
    },

    "case_02": {
        "name": "Correct VLAN Assignment",
        "commands": [
            "enable",
            "configure terminal",
            "interface <affected-interface>",
            "switchport mode access",
            "switchport access vlan <correct-vlan>",
            "end"
        ],
        "verification": [
            "show vlan brief",
            "show interfaces switchport"
        ]
    },

    "case_03": {
        "name": "Correct Default Gateway",
        "commands": [
            "Update the affected host default gateway",
            "Verify gateway configuration"
        ],
        "verification": [
            "ipconfig",
            "ping <default-gateway>",
            "ping <destination>"
        ]
    }
}


# ============================================================
# HELPERS
# ============================================================

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


def confidence_level(confidence):

    confidence = safe_float(
        confidence
    )

    if confidence >= 80:
        return "HIGH"

    if confidence >= 60:
        return "MODERATE"

    return "LOW"


def risk_level(risk_score):

    risk_score = safe_float(
        risk_score
    )

    if risk_score >= 75:
        return "CRITICAL"

    if risk_score >= 50:
        return "HIGH"

    if risk_score >= 25:
        return "MODERATE"

    return "LOW"


# ============================================================
# EXTRACT VALUES
# ============================================================

def extract_confidence(
    diagnosis,
    decision_data
):

    if not isinstance(
        decision_data,
        dict
    ):
        decision_data = {}

    if not isinstance(
        diagnosis,
        dict
    ):
        diagnosis = {}

    confidence = decision_data.get(
        "overall_confidence",
        decision_data.get(
            "confidence",
            diagnosis.get(
                "confidence",
                diagnosis.get(
                    "confidence_score",
                    0
                )
            )
        )
    )

    return safe_float(
        confidence
    )


def extract_risk_score(
    risk_data
):

    if isinstance(
        risk_data,
        dict
    ):

        return clamp(
            safe_float(
                risk_data.get(
                    "risk_score",
                    risk_data.get(
                        "score",
                        0
                    )
                )
            )
        )

    return clamp(
        safe_float(
            risk_data
        )
    )


def extract_case_id(
    diagnosis,
    decision_data
):

    if not isinstance(
        diagnosis,
        dict
    ):
        diagnosis = {}

    if not isinstance(
        decision_data,
        dict
    ):
        decision_data = {}

    selected_case = decision_data.get(
        "selected_case",
        {}
    )

    if not isinstance(
        selected_case,
        dict
    ):
        selected_case = {}

    return selected_case.get(
        "case_id",
        diagnosis.get(
            "case_id",
            diagnosis.get(
                "id",
                "UNKNOWN"
            )
        )
    )


def extract_title(
    diagnosis,
    decision_data
):

    if not isinstance(
        diagnosis,
        dict
    ):
        diagnosis = {}

    if not isinstance(
        decision_data,
        dict
    ):
        decision_data = {}

    selected_case = decision_data.get(
        "selected_case",
        {}
    )

    if not isinstance(
        selected_case,
        dict
    ):
        selected_case = {}

    return selected_case.get(
        "title",
        diagnosis.get(
            "title",
            diagnosis.get(
                "name",
                "Unknown Case"
            )
        )
    )


# ============================================================
# SAFETY EVALUATION
# ============================================================

def evaluate_action(
    action,
    confidence,
    risk_score,
    human_approval=False
):

    confidence = safe_float(
        confidence
    )

    risk_score = clamp(
        safe_float(
            risk_score
        )
    )

    reasons = []
    warnings = []

    # --------------------------------------------------------
    # Automatic execution is NEVER enabled.
    # --------------------------------------------------------

    automatic_execution = False

    if risk_score >= 75:

        reasons.append(
            "Network risk is critical; "
            "human review is mandatory."
        )

    elif risk_score >= 50:

        reasons.append(
            "Network risk is high; "
            "human review is required."
        )

    if confidence >= 80:

        reasons.append(
            "Diagnostic confidence is high, "
            "but confidence does not authorize "
            "automatic execution."
        )

    else:

        reasons.append(
            "Diagnostic confidence does not "
            "meet the threshold for independent action."
        )

    if not human_approval:

        reasons.append(
            "Human approval has not been provided."
        )

    warnings.append(
        "Automatic network configuration execution "
        "is disabled by policy."
    )

    warnings.append(
        "Proposed commands are recommendations "
        "for human review only."
    )

    allowed = True

    status = (
        "APPROVED"
        if human_approval
        else "READY_FOR_HUMAN_REVIEW"
    )

    return {
        "allowed": allowed,
        "status": status,
        "confidence": confidence,
        "risk_score": risk_score,
        "human_approval_required": True,
        "automatic_execution": automatic_execution,
        "automatic_configuration_applied": False,
        "reasons": reasons,
        "warnings": warnings,
        "action": action
    }


# ============================================================
# BUILD REMEDIATION PLAN
# ============================================================

def build_remediation_plan(
    evidence=None,
    diagnosis=None,
    decision_data=None,
    risk_data=None,
    human_approval=False
):
    """
    Build a safe Phase 12 remediation plan.

    Parameters:
        evidence:
            Network evidence collected by previous phases.

        diagnosis:
            Selected diagnosis.

        decision_data:
            Phase 7/10 decision information.

        risk_data:
            Phase 11 network risk information.

        human_approval:
            Explicit human approval flag.

    Automatic network configuration is NEVER executed.
    """

    # --------------------------------------------------------
    # Backward compatibility
    # --------------------------------------------------------

    if diagnosis is None:

        diagnosis = {}

    if decision_data is None:

        decision_data = {}

    if risk_data is None:

        risk_data = {}

    if evidence is None:

        evidence = {}

    # --------------------------------------------------------
    # Handle old-style calls:
    #
    # build_remediation_plan(diagnosis, risk_data)
    #
    # The orchestrator previously used this form.
    # --------------------------------------------------------

    if (
        isinstance(evidence, dict)
        and isinstance(diagnosis, dict)
        and risk_data == {}
        and (
            "case_id" in evidence
            or "title" in evidence
            or "root_cause" in evidence
        )
    ):

        old_diagnosis = evidence
        old_risk_data = diagnosis

        evidence = {}
        diagnosis = old_diagnosis
        decision_data = {}
        risk_data = old_risk_data

    # --------------------------------------------------------
    # Extract decision information
    # --------------------------------------------------------

    case_id = extract_case_id(
        diagnosis,
        decision_data
    )

    title = extract_title(
        diagnosis,
        decision_data
    )

    confidence = extract_confidence(
        diagnosis,
        decision_data
    )

    risk_score = extract_risk_score(
        risk_data
    )

    # --------------------------------------------------------
    # Find registered action
    # --------------------------------------------------------

    action = ACTION_REGISTRY.get(
        case_id
    )

    if action is None:

        action = {
            "name": (
                diagnosis.get(
                    "recommended_action",
                    "Review Recommended Fix"
                )
                if isinstance(
                    diagnosis,
                    dict
                )
                else "Review Recommended Fix"
            ),

            "commands": (
                diagnosis.get(
                    "recommended_fix",
                    []
                )
                if isinstance(
                    diagnosis,
                    dict
                )
                else []
            ),

            "verification": [
                "Repeat relevant diagnostic checks",
                "Confirm service connectivity"
            ]
        }

    action_name = action.get(
        "name",
        "Review Recommended Fix"
    )

    commands = action.get(
        "commands",
        []
    )

    verification = action.get(
        "verification",
        []
    )

    # --------------------------------------------------------
    # Safety gate
    # --------------------------------------------------------

    safety = evaluate_action(
        action_name,
        confidence,
        risk_score,
        human_approval
    )

    # --------------------------------------------------------
    # Remediation risk classification
    #
    # This is the risk of the proposed remediation action,
    # not the network health risk.
    # --------------------------------------------------------

    if risk_score >= 75:

        remediation_risk = "MODERATE"

    elif risk_score >= 50:

        remediation_risk = "MODERATE"

    else:

        remediation_risk = "LOW"

    # --------------------------------------------------------
    # Build plan
    # --------------------------------------------------------

    return {
        "phase": "Phase 12",

        "generated_at": datetime.now().isoformat(),

        "status": (
            "APPROVED_FOR_HUMAN_EXECUTION"
            if human_approval
            else "READY_FOR_HUMAN_REVIEW"
        ),

        "incident": {
            "case_id": case_id,
            "title": title
        },

        "diagnosis": diagnosis,

        "confidence": confidence,

        "confidence_level": confidence_level(
            confidence
        ),

        "risk": {
            "score": risk_score,
            "level": risk_level(
                risk_score
            )
        },

        "remediation": {
            "action": action_name,
            "risk_level": remediation_risk,
            "commands": commands,
            "verification": verification
        },

        "safety": {
            "allowed": safety["allowed"],
            "status": safety["status"],
            "human_approval_required": True,
            "human_approval_received": bool(
                human_approval
            ),
            "automatic_execution": False,
            "automatic_configuration_applied": False,
            "reasons": safety["reasons"],
            "warnings": safety["warnings"]
        }
    }


# ============================================================
# DISPLAY
# ============================================================

def display_remediation_plan(
    plan
):

    print()
    print("=" * 60)
    print(
        "          PHASE 12 REMEDIATION PLAN"
    )
    print("=" * 60)

    incident = plan.get(
        "incident",
        {}
    )

    remediation = plan.get(
        "remediation",
        {}
    )

    risk = plan.get(
        "risk",
        {}
    )

    safety = plan.get(
        "safety",
        {}
    )

    print()
    print(
        "Selected Diagnosis:"
    )

    print(
        f"{incident.get('case_id', 'UNKNOWN')} - "
        f"{incident.get('title', 'Unknown Case')}"
    )

    print()
    print(
        f"Confidence: "
        f"{plan.get('confidence', 0)}%"
    )

    print(
        f"Risk Score: "
        f"{risk.get('score', 0)}/100"
    )

    print()
    print(
        "Recommended Action:"
    )

    print(
        f"{remediation.get('action', 'None')}"
    )

    print()
    print(
        "Risk Level:"
    )

    print(
        f"{remediation.get('risk_level', 'UNKNOWN')}"
    )

    print()
    print(
        "Proposed Configuration:"
    )

    print("-" * 60)

    commands = remediation.get(
        "commands",
        []
    )

    if commands:

        for command in commands:

            print(
                f"  {command}"
            )

    else:

        print(
            "  No configuration commands generated."
        )

    print()
    print(
        "Verification:"
    )

    print("-" * 60)

    verification = remediation.get(
        "verification",
        []
    )

    if verification:

        for command in verification:

            print(
                f"  {command}"
            )

    else:

        print(
            "  No verification commands generated."
        )

    print()
    print(
        "Safety:"
    )

    print("-" * 60)

    print(
        "Human approval required: "
        f"{str(safety.get('human_approval_required', True)).upper()}"
    )

    print(
        "Automatic configuration applied: "
        f"{str(safety.get('automatic_configuration_applied', False)).upper()}"
    )

    print(
        "Automatic execution: "
        f"{str(safety.get('automatic_execution', False)).upper()}"
    )

    print()
    print(
        f"Remediation Status: "
        f"{plan.get('status', 'UNKNOWN')}"
    )

    print()
    print("=" * 60)
    print(
        "IMPORTANT:"
    )

    print(
        "NetSage AI does NOT execute network configuration."
    )

    print(
        "The commands above are recommendations "
        "for human review only."
    )

    print("=" * 60)


# ============================================================
# TEST
# ============================================================

def test():

    print("=" * 60)
    print(
        "       NetSage AI Phase 12 Remediation Engine"
    )
    print("=" * 60)

    diagnosis = {
        "case_id": "case_01",

        "title": (
            "Inter-VLAN Routing - "
            "Router Subinterface Down"
        ),

        "problem": (
            "PC0 cannot communicate "
            "with VLAN 30 server."
        ),

        "root_cause": (
            "GigabitEthernet0/0.30 "
            "is administratively down."
        ),

        "match_score": 23,

        "recommended_fix": [
            "enable",
            "configure terminal",
            "interface GigabitEthernet0/0.30",
            "no shutdown",
            "end"
        ]
    }

    decision_data = {
        "overall_confidence": 82,

        "decision_status": (
            "HIGH-CONFIDENCE DIAGNOSIS"
        ),

        "selected_case": {
            "case_id": "case_01",
            "title": (
                "Inter-VLAN Routing - "
                "Router Subinterface Down"
            )
        }
    }

    risk_data = {
        "risk_score": 100,
        "risk_level": "CRITICAL",
        "priority": "P1 - IMMEDIATE"
    }

    plan = build_remediation_plan(
        evidence={},
        diagnosis=diagnosis,
        decision_data=decision_data,
        risk_data=risk_data,
        human_approval=False
    )

    display_remediation_plan(
        plan
    )

    print()
    print(
        "Phase 12 remediation engine test complete."
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    test()
