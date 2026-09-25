
import os
from datetime import datetime


# ============================================================
# NetSage AI - Phase 12
# Safety Gate
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


# ============================================================
# SAFETY POLICY
# ============================================================

AUTOMATIC_EXECUTION_ENABLED = False
HUMAN_APPROVAL_REQUIRED = True


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


# ============================================================
# EVALUATE ACTION
# ============================================================

def evaluate_action(
    action=None,
    confidence=0,
    risk_score=0,
    human_approved=False
):
    """
    Evaluate whether a proposed network remediation action
    may proceed.

    NetSage AI never automatically executes configuration.
    Human approval is always required.
    """

    confidence = clamp(
        safe_float(confidence)
    )

    risk_score = clamp(
        safe_float(risk_score)
    )

    reasons = []
    warnings = []

    # --------------------------------------------------------
    # Safety policy
    # --------------------------------------------------------

    automatic_execution = False
    automatic_configuration_applied = False

    # --------------------------------------------------------
    # Determine readiness
    # --------------------------------------------------------

    if risk_score >= 75:

        reasons.append(
            "Network risk is critical; human review is mandatory."
        )

    elif risk_score >= 50:

        reasons.append(
            "Network risk is high; human review is required."
        )

    else:

        reasons.append(
            "Network risk is within the monitored range."
        )

    if HUMAN_APPROVAL_REQUIRED:

        reasons.append(
            "Human approval is required before any configuration change."
        )

    # --------------------------------------------------------
    # Warnings
    # --------------------------------------------------------

    if confidence >= 80:

        warnings.append(
            "High diagnostic confidence does not authorize automatic execution."
        )

    warnings.append(
        "Automatic network configuration execution is disabled by policy."
    )

    # --------------------------------------------------------
    # Approval logic
    # --------------------------------------------------------

    if human_approved:

        allowed = True
        status = "HUMAN_APPROVED"

    else:

        allowed = True
        status = "READY_FOR_HUMAN_REVIEW"

    # --------------------------------------------------------
    # Never allow automatic execution
    # --------------------------------------------------------

    if not AUTOMATIC_EXECUTION_ENABLED:

        automatic_execution = False

    automatic_configuration_applied = False

    return {
        "phase": "Phase 12",

        "timestamp": datetime.now().isoformat(),

        "allowed": allowed,

        "status": status,

        "confidence": confidence,

        "risk_score": risk_score,

        "human_approval_required": True,

        "human_approved": bool(
            human_approved
        ),

        "automatic_execution": False,

        "automatic_configuration_applied": False,

        "action": action,

        "reasons": reasons,

        "warnings": warnings
    }


# ============================================================
# EVALUATE COMPLETE SAFETY GATE
# ============================================================

def evaluate_safety(
    confidence=0,
    risk_score=0,
    human_approved=False
):
    """
    Compatibility wrapper used by the Phase 12
    safety-gate test and orchestrator.
    """

    return evaluate_action(
        action=None,
        confidence=confidence,
        risk_score=risk_score,
        human_approved=human_approved
    )


# ============================================================
# DISPLAY
# ============================================================

def display_safety_result(
    result
):

    print()
    print("=" * 60)
    print("              PHASE 12 SAFETY GATE")
    print("=" * 60)

    print()
    print("Safety Gate Result")
    print("-" * 50)

    print(
        f"allowed: "
        f"{result.get('allowed')}"
    )

    print(
        f"status: "
        f"{result.get('status')}"
    )

    print(
        f"confidence: "
        f"{result.get('confidence')}"
    )

    print(
        f"risk_score: "
        f"{result.get('risk_score')}"
    )

    print(
        f"human_approval_required: "
        f"{result.get('human_approval_required')}"
    )

    print(
        f"automatic_execution: "
        f"{result.get('automatic_execution')}"
    )

    print(
        f"automatic_configuration_applied: "
        f"{result.get('automatic_configuration_applied')}"
    )

    print()
    print("Reasons:")

    for reason in result.get(
        "reasons",
        []
    ):

        print(
            f"- {reason}"
        )

    print()
    print("Warnings:")

    for warning in result.get(
        "warnings",
        []
    ):

        print(
            f"- {warning}"
        )

    print()
    print(
        "Automatic configuration execution: FALSE"
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

    print("=" * 50)

    print(
        "NetSage AI Phase 12 Safety Gate"
    )

    print("=" * 50)

    result = evaluate_action(
        action={
            "name": "Enable Router Subinterface",
            "commands": [
                "enable",
                "configure terminal",
                "interface GigabitEthernet0/0.30",
                "no shutdown",
                "end"
            ]
        },

        confidence=82,

        risk_score=100,

        human_approved=False
    )

    display_safety_result(
        result
    )

    print()
    print(
        "Phase 12 safety gate test complete."
    )


if __name__ == "__main__":

    test()
