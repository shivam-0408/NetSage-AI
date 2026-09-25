import os
import json
from datetime import datetime


# ============================================================
# NetSage AI - Phase 10 Adaptive Intelligence
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

LEARNING_DATABASE = os.path.join(
    BASE_DIR,
    "data",
    "learning_database.json"
)


# ============================================================
# DATABASE
# ============================================================

def load_learning_database():

    if not os.path.exists(LEARNING_DATABASE):
        return {
            "version": "1.0",
            "incidents": [],
            "case_statistics": {},
            "patterns": []
        }

    try:
        with open(
            LEARNING_DATABASE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError("Learning database must be a JSON object.")

        return data

    except (json.JSONDecodeError, OSError, ValueError):

        return {
            "version": "1.0",
            "incidents": [],
            "case_statistics": {},
            "patterns": []
        }


# ============================================================
# HISTORICAL SUCCESS
# ============================================================

def get_case_history(case_id, database):

    statistics = database.get(
        "case_statistics",
        {}
    )

    return statistics.get(
        case_id,
        {
            "case_id": case_id,
            "total_verified": 0,
            "successful": 0,
            "failed": 0,
            "approval_count": 0,
            "success_rate": 0.0
        }
    )


def calculate_history_score(case_id, database):

    history = get_case_history(
        case_id,
        database
    )

    total_verified = history.get(
        "total_verified",
        0
    )

    success_rate = history.get(
        "success_rate",
        0
    )

    if total_verified <= 0:
        return 0.0

    try:
        success_rate = float(success_rate)

    except (TypeError, ValueError):
        return 0.0

    if total_verified == 1:
        reliability_factor = 0.50

    elif total_verified == 2:
        reliability_factor = 0.75

    else:
        reliability_factor = 1.00

    return round(
        success_rate * reliability_factor,
        2
    )


# ============================================================
# ADAPTIVE BONUS
# ============================================================

def calculate_adaptive_bonus(
    case_id,
    database
):

    history_score = calculate_history_score(
        case_id,
        database
    )

    if history_score >= 90:
        return 10

    if history_score >= 75:
        return 7

    if history_score >= 60:
        return 4

    if history_score > 0:
        return 2

    return 0


# ============================================================
# ADAPTIVE RANKING
# ============================================================

def adapt_diagnoses(
    diagnoses,
    database
):
    """
    Apply verified historical performance as a
    controlled adaptive bonus.

    Original diagnostic scores are preserved.
    """

    if not isinstance(diagnoses, list):
        return []

    adapted = []

    for diagnosis in diagnoses:

        if not isinstance(diagnosis, dict):
            continue

        item = diagnosis.copy()

        case_id = item.get(
            "case_id",
            item.get(
                "id",
                "UNKNOWN"
            )
        )

        original_score = item.get(
            "score",
            item.get(
                "match_score",
                0
            )
        )

        try:
            original_score = float(
                original_score
            )

        except (TypeError, ValueError):
            original_score = 0.0

        history = get_case_history(
            case_id,
            database
        )

        history_score = calculate_history_score(
            case_id,
            database
        )

        adaptive_bonus = calculate_adaptive_bonus(
            case_id,
            database
        )

        adaptive_score = (
            original_score +
            adaptive_bonus
        )

        item["original_score"] = original_score

        item["historical_success_rate"] = history.get(
            "success_rate",
            0
        )

        item["historical_verified"] = history.get(
            "total_verified",
            0
        )

        item["adaptive_bonus"] = adaptive_bonus

        item["adaptive_score"] = adaptive_score

        item["historical_reliability"] = history_score

        adapted.append(item)

    adapted.sort(
        key=lambda item: item.get(
            "adaptive_score",
            0
        ),
        reverse=True
    )

    return adapted


# ============================================================
# ADAPTIVE CONFIDENCE
# ============================================================

def calculate_adaptive_confidence(
    selected,
    original_confidence=0
):

    if not selected:
        return 0

    try:
        original_confidence = float(
            original_confidence
        )

    except (TypeError, ValueError):
        original_confidence = 0

    history_score = selected.get(
        "historical_reliability",
        0
    )

    verified_count = selected.get(
        "historical_verified",
        0
    )

    if verified_count <= 0:

        adaptive_confidence = original_confidence

    else:

        historical_weight = min(
            verified_count * 0.05,
            0.20
        )

        adaptive_confidence = (
            original_confidence *
            (1 - historical_weight)
        ) + (
            history_score *
            historical_weight
        )

    adaptive_confidence = min(
        adaptive_confidence,
        99
    )

    return round(
        adaptive_confidence
    )


# ============================================================
# CONFIDENCE LEVEL
# ============================================================

def confidence_level(confidence):

    try:
        confidence = float(
            confidence
        )

    except (TypeError, ValueError):
        return "UNKNOWN"

    if confidence >= 80:
        return "HIGH"

    if confidence >= 60:
        return "MODERATE"

    return "LOW"


# ============================================================
# BUILD ADAPTIVE DECISION
# ============================================================

def build_adaptive_decision(
    diagnoses,
    original_confidence=0
):

    database = load_learning_database()

    adapted = adapt_diagnoses(
        diagnoses,
        database
    )

    if not adapted:

        return {
            "phase": "Phase 10",
            "status": "NO_DIAGNOSIS",
            "selected_case": None,
            "overall_confidence": 0,
            "confidence_level": "UNKNOWN",
            "adaptive": False,
            "reason": "No diagnosis candidates were supplied.",
            "ranked_diagnoses": [],
            "safety": {
                "automatic_configuration_applied": False,
                "human_approval_required": True
            }
        }

    selected = adapted[0]

    adaptive_confidence = calculate_adaptive_confidence(
        selected,
        original_confidence
    )

    level = confidence_level(
        adaptive_confidence
    )

    verified_count = selected.get(
        "historical_verified",
        0
    )

    success_rate = selected.get(
        "historical_success_rate",
        0
    )

    if verified_count > 0:

        learning_reason = (
            f"Historical learning contains "
            f"{verified_count} verified incident(s) "
            f"for {selected.get('case_id', 'UNKNOWN')} "
            f"with a {success_rate}% success rate."
        )

    else:

        learning_reason = (
            "No verified historical performance "
            "was available for this diagnosis."
        )

    return {
        "phase": "Phase 10",

        "timestamp": datetime.now().isoformat(),

        "status": "ADAPTIVE-DIAGNOSIS",

        "adaptive": True,

        "selected_case": selected,

        "overall_confidence": adaptive_confidence,

        "confidence_level": level,

        "original_confidence": original_confidence,

        "learning": {
            "historical_verified": verified_count,
            "historical_success_rate": success_rate,
            "historical_reliability": selected.get(
                "historical_reliability",
                0
            ),
            "adaptive_bonus": selected.get(
                "adaptive_bonus",
                0
            ),
            "reason": learning_reason
        },

        "ranked_diagnoses": adapted,

        "safety": {
            "automatic_configuration_applied": False,
            "human_approval_required": True
        }
    }


# ============================================================
# COMPATIBILITY FUNCTION
# ============================================================

def adaptive_select(
    diagnoses,
    original_confidence=0
):
    """
    Compatibility interface used by the Phase 13
    incident orchestrator.

    Returns the complete Phase 10 adaptive decision.
    """

    return build_adaptive_decision(
        diagnoses,
        original_confidence
    )


# ============================================================
# DISPLAY
# ============================================================

def display_adaptive_decision(
    decision
):

    print()
    print("=" * 60)
    print("              PHASE 10 ADAPTIVE INTELLIGENCE")
    print("=" * 60)

    selected = decision.get(
        "selected_case"
    )

    if not selected:

        print()
        print(
            "No adaptive diagnosis available."
        )

        return

    case_id = selected.get(
        "case_id",
        "UNKNOWN"
    )

    title = selected.get(
        "title",
        selected.get(
            "name",
            "Unknown Case"
        )
    )

    print()
    print(
        "Adaptively Selected Case:"
    )

    print(
        f"{case_id} - {title}"
    )

    print()
    print(
        f"Original Confidence: "
        f"{decision.get('original_confidence', 0)}%"
    )

    print(
        f"Adaptive Confidence: "
        f"{decision.get('overall_confidence', 0)}% "
        f"({decision.get('confidence_level', 'UNKNOWN')})"
    )

    print()
    print(
        "Historical Learning:"
    )

    learning = decision.get(
        "learning",
        {}
    )

    print(
        f"- Verified incidents: "
        f"{learning.get('historical_verified', 0)}"
    )

    print(
        f"- Historical success rate: "
        f"{learning.get('historical_success_rate', 0)}%"
    )

    print(
        f"- Historical reliability: "
        f"{learning.get('historical_reliability', 0)}"
    )

    print(
        f"- Adaptive bonus: "
        f"+{learning.get('adaptive_bonus', 0)}"
    )

    print()
    print(
        "Why historical learning influenced "
        "the decision:"
    )

    print(
        f"- {learning.get('reason', 'None')}"
    )

    print()
    print(
        "Adaptive Ranking:"
    )

    ranked = decision.get(
        "ranked_diagnoses",
        []
    )

    for index, item in enumerate(
        ranked,
        start=1
    ):

        print(
            f"{index}. "
            f"{item.get('case_id', 'UNKNOWN')} - "
            f"{item.get('title', 'Unknown Case')} "
            f"(original={item.get('original_score', 0)}, "
            f"adaptive={item.get('adaptive_score', 0)})"
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

    print("=" * 50)
    print(
        "NetSage AI Phase 10 Adaptive Engine"
    )
    print("=" * 50)

    database = load_learning_database()

    print()
    print(
        "Learning database:"
    )

    print(
        LEARNING_DATABASE
    )

    statistics = database.get(
        "case_statistics",
        {}
    )

    print()
    print(
        f"Historical cases: "
        f"{len(statistics)}"
    )

    diagnoses = [
        {
            "case_id": "case_01",
            "title": (
                "Inter-VLAN Routing - "
                "Router Subinterface Down"
            ),
            "score": 23
        },
        {
            "case_id": "case_02",
            "title": "Wrong VLAN Assignment",
            "score": 17
        },
        {
            "case_id": "case_03",
            "title": "Wrong Default Gateway",
            "score": 16
        }
    ]

    decision = adaptive_select(
        diagnoses,
        original_confidence=82
    )

    display_adaptive_decision(
        decision
    )

    print()
    print(
        "Phase 10 adaptive engine test complete."
    )


if __name__ == "__main__":
    test()