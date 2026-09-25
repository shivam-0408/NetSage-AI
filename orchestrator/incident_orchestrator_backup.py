

def extract_selected_diagnosis(adaptive_data, decision_data=None):
    """
    Phase 13 compatibility layer.

    Phase 10 build_adaptive_decision() returns:
        selected_case
        overall_confidence
        confidence_level
        ranked_diagnoses

    This function extracts the actual selected diagnosis
    without destroying the original Phase 10 structure.
    """

    if not isinstance(adaptive_data, dict):
        adaptive_data = {}

    # Primary Phase 10 structure
    selected = adaptive_data.get("selected_case")

    if isinstance(selected, dict):
        return selected

    # Compatibility: some older decision engines may return
    # the selected diagnosis under another key.
    for key in (
        "diagnosis",
        "selected_diagnosis",
        "best_diagnosis",
        "case"
    ):
        candidate = adaptive_data.get(key)

        if isinstance(candidate, dict):
            return candidate

    # Compatibility with ranked diagnosis output
    ranked = adaptive_data.get(
        "ranked_diagnoses",
        []
    )

    if isinstance(ranked, list) and ranked:
        if isinstance(ranked[0], dict):
            return ranked[0]

    # Fall back to decision engine output
    if isinstance(decision_data, dict):

        for key in (
            "selected_case",
            "selected_diagnosis",
            "diagnosis",
            "best_diagnosis"
        ):
            candidate = decision_data.get(key)

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
# NORMALIZE CONFIDENCE
# ============================================================

def extract_confidence(
    adaptive_data,
    decision_data=None,
    diagnosis=None
):
    """
    Extract confidence from the Phase 10/Phase 9 structures.
    """

    if isinstance(adaptive_data, dict):

        for key in (
            "overall_confidence",
            "adaptive_confidence",
            "confidence"
        ):

            value = adaptive_data.get(key)

            if value is not None:

                try:
                    return float(value)

                except (TypeError, ValueError):
                    pass

    if isinstance(decision_data, dict):

        for key in (
            "confidence",
            "overall_confidence",
            "decision_confidence"
        ):

            value = decision_data.get(key)

            if value is not None:

                try:
                    return float(value)

                except (TypeError, ValueError):
                    pass

    if isinstance(diagnosis, dict):

        for key in (
            "confidence",
            "match_confidence",
            "score"
        ):

            value = diagnosis.get(key)

            if value is not None:

                try:
                    return float(value)

                except (TypeError, ValueError):
                    pass

    return 0.0


# ============================================================
# NORMALIZE DIAGNOSIS
# ============================================================

def normalize_diagnosis(
    diagnosis,
    confidence=0
):

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
        confidence = float(confidence)

    except (TypeError, ValueError):
        confidence = 0.0

    normalized = diagnosis.copy()

    normalized["case_id"] = case_id
    normalized["title"] = title
    normalized["confidence"] = confidence

    return normalized