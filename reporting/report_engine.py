import os
import json
from datetime import datetime


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

REPORT_DIR = os.path.join(
    BASE_DIR,
    "reports"
)


def ensure_report_directory():
    os.makedirs(
        REPORT_DIR,
        exist_ok=True
    )


def confidence_level(confidence):
    try:
        confidence = float(confidence)
    except (TypeError, ValueError):
        return "UNKNOWN"

    if confidence >= 80:
        return "HIGH"

    if confidence >= 60:
        return "MODERATE"

    return "LOW"


def generate_reasoning(
    title,
    root_cause,
    confidence
):
    level = confidence_level(confidence)

    return (
        f"NetSage AI selected '{title}' because "
        f"the available network evidence most strongly "
        f"supports the identified root cause: "
        f"{root_cause}. "
        f"The resulting decision confidence is "
        f"{confidence}% ({level})."
    )


def build_report(
    evidence,
    diagnosis,
    decision_data,
    verification_result,
    review_result,
    audit_file=None
):
    """
    Build a complete Phase 8 NetSage AI incident report.
    """

    if not isinstance(diagnosis, dict):
        diagnosis = {}

    if not isinstance(decision_data, dict):
        decision_data = {}

    case_id = diagnosis.get(
        "case_id",
        diagnosis.get("id", "UNKNOWN")
    )

    title = diagnosis.get(
        "title",
        diagnosis.get(
            "name",
            "Unknown Case"
        )
    )

    problem = diagnosis.get(
        "problem",
        "Unknown"
    )

    root_cause = diagnosis.get(
        "root_cause",
        "Unknown"
    )

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

    decision_status = decision_data.get(
        "decision_status",
        "UNKNOWN"
    )

    matching_evidence = decision_data.get(
        "matching_evidence",
        diagnosis.get(
            "matching_evidence",
            []
        )
    )

    competing = decision_data.get(
        "competing_diagnoses",
        []
    )

    supporting = decision_data.get(
        "supporting_evidence",
        []
    )

    contradictions = decision_data.get(
        "contradictions",
        []
    )

    report = {
        "report_version": "1.0",

        "generated_at": datetime.now().isoformat(),

        "system": {
            "name": "NetSage AI",
            "phase": "Phase 8",
            "module": "Explainability and Reporting"
        },

        "incident": {
            "case_id": case_id,
            "title": title,
            "problem": problem,
            "root_cause": root_cause
        },

        "decision": {
            "status": decision_status,
            "confidence": confidence,
            "confidence_level": confidence_level(
                confidence
            ),
            "match_score": diagnosis.get(
                "match_score",
                0
            )
        },

        "explanation": {
            "why_selected": matching_evidence,
            "supporting_evidence": supporting,
            "contradictions": contradictions,
            "reasoning": generate_reasoning(
                title,
                root_cause,
                confidence
            )
        },

        "competing_diagnoses": competing,

        "recommended_fix": diagnosis.get(
            "recommended_fix",
            []
        ),

        "verification": verification_result,

        "human_review": review_result,

        "safety": {
            "automatic_configuration_applied": False,
            "human_approval_required": True
        },

        "audit": {
            "audit_file": audit_file
        }
    }

    return report


def save_json_report(report):

    ensure_report_directory()

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    filename = (
        f"netsage_report_{timestamp}.json"
    )

    path = os.path.join(
        REPORT_DIR,
        filename
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4,
            ensure_ascii=False
        )

    return path


def generate_text_report(report):

    incident = report["incident"]
    decision = report["decision"]
    explanation = report["explanation"]

    lines = []

    lines.append("=" * 70)
    lines.append(
        "                    NetSage AI"
    )
    lines.append(
        "             PHASE 8 INCIDENT REPORT"
    )
    lines.append("=" * 70)

    lines.append("")
    lines.append("INCIDENT")
    lines.append("-" * 70)

    lines.append(
        f"Case ID: {incident['case_id']}"
    )

    lines.append(
        f"Diagnosis: {incident['title']}"
    )

    lines.append(
        f"Problem: {incident['problem']}"
    )

    lines.append(
        f"Root Cause: {incident['root_cause']}"
    )

    lines.append("")
    lines.append("DECISION")
    lines.append("-" * 70)

    lines.append(
        f"Status: {decision['status']}"
    )

    lines.append(
        f"Confidence: {decision['confidence']}%"
    )

    lines.append(
        f"Confidence Level: "
        f"{decision['confidence_level']}"
    )

    lines.append(
        f"Match Score: "
        f"{decision['match_score']}"
    )

    lines.append("")
    lines.append(
        "WHY THIS DIAGNOSIS WAS SELECTED"
    )
    lines.append("-" * 70)

    why_selected = explanation.get(
        "why_selected",
        []
    )

    if why_selected:

        for item in why_selected:
            lines.append(
                f"- {item}"
            )

    else:

        lines.append(
            "- No detailed selection evidence recorded."
        )

    lines.append("")
    lines.append("REASONING")
    lines.append("-" * 70)

    lines.append(
        explanation.get(
            "reasoning",
            "No reasoning available."
        )
    )

    lines.append("")
    lines.append("SUPPORTING EVIDENCE")
    lines.append("-" * 70)

    supporting = explanation.get(
        "supporting_evidence",
        []
    )

    if supporting:

        for item in supporting:
            lines.append(
                f"- {item}"
            )

    else:

        lines.append(
            "- None recorded."
        )

    lines.append("")
    lines.append("CONTRADICTIONS")
    lines.append("-" * 70)

    contradictions = explanation.get(
        "contradictions",
        []
    )

    if contradictions:

        for item in contradictions:
            lines.append(
                f"- {item}"
            )

    else:

        lines.append(
            "- None detected."
        )

    lines.append("")
    lines.append("COMPETING DIAGNOSES")
    lines.append("-" * 70)

    competing = report.get(
        "competing_diagnoses",
        []
    )

    if competing:

        for index, item in enumerate(
            competing,
            start=1
        ):

            if isinstance(item, dict):

                item_case = item.get(
                    "case_id",
                    "UNKNOWN"
                )

                item_title = item.get(
                    "title",
                    item.get(
                        "name",
                        ""
                    )
                )

                item_confidence = item.get(
                    "confidence",
                    "UNKNOWN"
                )

                lines.append(
                    f"{index}. "
                    f"{item_case} - "
                    f"{item_title} "
                    f"(confidence="
                    f"{item_confidence}%)"
                )

            else:

                lines.append(
                    f"{index}. {item}"
                )

    else:

        lines.append(
            "- None recorded."
        )

    lines.append("")
    lines.append("RECOMMENDED FIX")
    lines.append("-" * 70)

    fix = report.get(
        "recommended_fix",
        []
    )

    if isinstance(fix, list):

        for command in fix:
            lines.append(
                f"  {command}"
            )

    else:

        lines.append(
            f"  {fix}"
        )

    lines.append("")
    lines.append("HUMAN REVIEW")
    lines.append("-" * 70)

    review = report.get(
        "human_review",
        {}
    )

    lines.append(
        str(review)
    )

    lines.append("")
    lines.append("VERIFICATION")
    lines.append("-" * 70)

    verification = report.get(
        "verification",
        {}
    )

    lines.append(
        str(verification)
    )

    lines.append("")
    lines.append("SAFETY")
    lines.append("-" * 70)

    lines.append(
        "Automatic configuration applied: FALSE"
    )

    lines.append(
        "Human approval required: TRUE"
    )

    lines.append("")
    lines.append("AUDIT")
    lines.append("-" * 70)

    lines.append(
        f"Audit file: "
        f"{report['audit']['audit_file']}"
    )

    lines.append("")
    lines.append("=" * 70)
    lines.append(
        "              PHASE 8 COMPLETE"
    )
    lines.append("=" * 70)

    return "\n".join(lines)


def save_text_report(report):

    ensure_report_directory()

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    filename = (
        f"netsage_report_{timestamp}.txt"
    )

    path = os.path.join(
        REPORT_DIR,
        filename
    )

    text = generate_text_report(
        report
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(text)

    return path


def save_report(report):

    json_path = save_json_report(
        report
    )

    text_path = save_text_report(
        report
    )

    return {
        "json": json_path,
        "text": text_path
    }


def print_report_summary(report):

    incident = report["incident"]
    decision = report["decision"]

    print()
    print("=" * 60)
    print(
        "          PHASE 8 EXPLAINABILITY"
    )
    print("=" * 60)

    print()
    print("Selected Diagnosis:")

    print(
        f"{incident['case_id']} - "
        f"{incident['title']}"
    )

    print()

    print(
        f"Confidence: "
        f"{decision['confidence']}% "
        f"({decision['confidence_level']})"
    )

    print()

    print("Explanation:")

    print(
        report["explanation"]["reasoning"]
    )

    print()

    print(
        "Human Approval Required: TRUE"
    )

    print(
        "Automatic Configuration Applied: FALSE"
    )


def test():

    print("=" * 50)
    print(
        "NetSage AI Phase 8 Report Engine"
    )
    print("=" * 50)

    report = build_report(
        evidence={},

        diagnosis={
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
        },

        decision_data={
            "overall_confidence": 82,

            "decision_status": (
                "HIGH-CONFIDENCE DIAGNOSIS"
            ),

            "matching_evidence": [
                "VLAN 30 subinterface is administratively down.",
                "Destination has 100% packet loss."
            ],

            "supporting_evidence": [
                "VLAN 30 exists.",
                "Trunk is active."
            ],

            "contradictions": [],

            "competing_diagnoses": [
                {
                    "case_id": "case_01",
                    "title": (
                        "Inter-VLAN Routing - "
                        "Router Subinterface Down"
                    ),
                    "confidence": 82
                },

                {
                    "case_id": "case_02",
                    "title": (
                        "Wrong VLAN Assignment"
                    ),
                    "confidence": 61
                }
            ]
        },

        verification_result={
            "verified": True,
            "verification_score": 100
        },

        review_result={
            "reviewed": True,
            "approved": True,
            "decision": "APPROVED"
        },

        audit_file=(
            "data/responsible_ai_log.json"
        )
    )

    print_report_summary(
        report
    )

    paths = save_report(
        report
    )

    print()
    print("JSON report:")
    print(paths["json"])

    print()
    print("Text report:")
    print(paths["text"])

    print()
    print(
        "Phase 8 report engine test complete."
    )


if __name__ == "__main__":
    test()