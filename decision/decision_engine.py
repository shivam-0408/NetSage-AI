def make_decision(evidence, diagnosis=None, cases=None):
    """
    Compatibility interface for Phase 13 orchestration.

    Uses the existing Phase 7 decision engine logic when available.
    """

    # If the existing engine exposes a decision function,
    # use it directly.
    if "run_decision" in globals():
        try:
            result = run_decision(
                evidence,
                diagnosis,
                cases
            )
        except TypeError:
            try:
                result = run_decision(
                    evidence,
                    cases
                )
            except TypeError:
                result = run_decision(
                    evidence
                )

        if isinstance(result, dict):
            return result

    # Build a safe decision object from the diagnosis
    # already selected by the Phase 4 engine.
    diagnosis = diagnosis or {}

    confidence = diagnosis.get(
        "confidence",
        diagnosis.get(
            "confidence_score",
            diagnosis.get(
                "match_score",
                0
            )
        )
    )

    case_id = diagnosis.get(
        "case_id",
        diagnosis.get(
            "id",
            "UNKNOWN"
        )
    )

    title = diagnosis.get(
        "title",
        diagnosis.get(
            "name",
            "Unknown Case"
        )
    )

    matching_evidence = diagnosis.get(
        "matching_evidence",
        []
    )

    if confidence >= 80:
        status = "HIGH-CONFIDENCE DIAGNOSIS"
    elif confidence >= 60:
        status = "MODERATE-CONFIDENCE DIAGNOSIS"
    else:
        status = "LOW-CONFIDENCE DIAGNOSIS"

    return {
        "selected_case": {
            "case_id": case_id,
            "title": title
        },

        "overall_confidence": confidence,

        "decision_status": status,

        "match_score": diagnosis.get(
            "match_score",
            0
        ),

        "matching_evidence": matching_evidence,

        "supporting_evidence": (
            diagnosis.get(
                "supporting_evidence",
                matching_evidence
            )
        ),

        "contradictions": diagnosis.get(
            "contradictions",
            []
        ),

        "competing_diagnoses": []
    }