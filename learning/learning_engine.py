import os
import json
from datetime import datetime

from case_statistics import calculate_case_statistics
from pattern_engine import extract_patterns


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_DIR = os.path.join(BASE_DIR, "data")

LEARNING_DATABASE = os.path.join(
    DATA_DIR,
    "learning_database.json"
)

AUDIT_DATABASE = os.path.join(
    DATA_DIR,
    "responsible_ai_log.json"
)


def ensure_data_directory():
    os.makedirs(DATA_DIR, exist_ok=True)


def load_learning_database():

    ensure_data_directory()

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
            return json.load(file)

    except (json.JSONDecodeError, OSError):

        return {
            "version": "1.0",
            "incidents": [],
            "case_statistics": {},
            "patterns": []
        }


def save_learning_database(database):

    ensure_data_directory()

    with open(
        LEARNING_DATABASE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            database,
            file,
            indent=4,
            ensure_ascii=False
        )


def load_audit_records():

    if not os.path.exists(AUDIT_DATABASE):
        return []

    try:

        with open(
            AUDIT_DATABASE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

    except (json.JSONDecodeError, OSError):

        return []

    if isinstance(data, list):
        return data

    if isinstance(data, dict):

        for key in [
            "records",
            "incidents",
            "audit_records",
            "logs"
        ]:

            if isinstance(data.get(key), list):
                return data[key]

    return []


def extract_case_id(record):

    possible = [
        record.get("case_id"),
        record.get("selected_case"),
        record.get("case")
    ]

    for value in possible:

        if isinstance(value, str) and value.strip():

            return value

        if isinstance(value, dict):

            nested = value.get(
                "case_id",
                value.get("id")
            )

            if nested:
                return nested

    return "UNKNOWN"


def extract_verification_score(record):

    possible = [
        record.get("verification_score"),
        record.get("verification_result"),
        record.get("verification")
    ]

    for value in possible:

        if isinstance(value, (int, float)):
            return value

        if isinstance(value, dict):

            nested = value.get(
                "verification_score",
                value.get("score", 0)
            )

            if isinstance(nested, (int, float)):
                return nested

    return 0


def extract_verified(record):

    if record.get("verified") is True:
        return True

    if record.get("verification_passed") is True:
        return True

    if record.get("verification_result") is True:
        return True

    verification = record.get(
        "verification"
    )

    if isinstance(verification, dict):

        if verification.get("verified") is True:
            return True

        if verification.get("passed") is True:
            return True

    score = extract_verification_score(
        record
    )

    return score >= 80


def extract_approved(record):

    if record.get("approved") is True:
        return True

    if record.get("human_approved") is True:
        return True

    review = record.get(
        "human_review"
    )

    if isinstance(review, dict):

        if review.get("approved") is True:
            return True

    return False


def extract_supporting_evidence(record):

    evidence = record.get(
        "supporting_evidence",
        []
    )

    if isinstance(evidence, list):
        return evidence

    if isinstance(evidence, str):
        return [evidence]

    return []


def normalize_incident(record, index):

    if not isinstance(record, dict):
        return None

    case_id = extract_case_id(
        record
    )

    verification_score = (
        extract_verification_score(
            record
        )
    )

    verified = extract_verified(
        record
    )

    approved = extract_approved(
        record
    )

    evidence = extract_supporting_evidence(
        record
    )

    incident_id = record.get(
        "incident_id"
    )

    if not incident_id:

        incident_id = record.get(
            "audit_id"
        )

    if not incident_id:

        incident_id = (
            f"audit_{index}"
        )

    return {

        "incident_id": str(
            incident_id
        ),

        "case_id": case_id,

        "verified": verified,

        "verification_score": (
            verification_score
        ),

        "approved": approved,

        "supporting_evidence": evidence,

        "learned_at": datetime.now().isoformat()
    }


def rebuild_learning_model():

    audit_records = load_audit_records()

    database = load_learning_database()

    database["incidents"] = []

    for index, record in enumerate(
        audit_records,
        start=1
    ):

        incident = normalize_incident(
            record,
            index
        )

        if incident is not None:

            database["incidents"].append(
                incident
            )

    incidents = database[
        "incidents"
    ]

    statistics = calculate_case_statistics(
        incidents
    )

    patterns = extract_patterns(
        incidents
    )

    database["case_statistics"] = statistics

    database["patterns"] = patterns

    database["last_updated"] = (
        datetime.now().isoformat()
    )

    save_learning_database(
        database
    )

    return {

        "database": database,

        "new_incidents": len(
            incidents
        ),

        "total_incidents": len(
            incidents
        ),

        "verified_incidents": sum(
            1
            for item in incidents
            if item.get("verified")
        ),

        "case_statistics": statistics,

        "patterns": patterns
    }


def get_case_history(case_id):

    database = load_learning_database()

    return [

        incident

        for incident in database.get(
            "incidents",
            []
        )

        if incident.get(
            "case_id"
        ) == case_id
    ]


def get_learning_bonus(
    case_id,
    base_score
):

    database = load_learning_database()

    statistics = database.get(
        "case_statistics",
        {}
    )

    case_data = statistics.get(
        case_id
    )

    if not case_data:
        return 0

    success_rate = case_data.get(
        "success_rate",
        0
    )

    verified_count = case_data.get(
        "total_verified",
        0
    )

    if verified_count == 0:
        return 0

    if success_rate >= 90:
        return 3

    if success_rate >= 75:
        return 2

    if success_rate >= 60:
        return 1

    return 0


def print_learning_summary(result):

    print()
    print("=" * 60)
    print("          PHASE 9 LEARNING INTELLIGENCE")
    print("=" * 60)

    print()
    print(
        f"Historical incidents loaded: "
        f"{result['total_incidents']}"
    )

    print(
        f"Verified incidents: "
        f"{result['verified_incidents']}"
    )

    print()
    print("Historical Case Performance")
    print("-" * 60)

    statistics = result[
        "case_statistics"
    ]

    if not statistics:

        print(
            "No verified historical incidents available."
        )

    else:

        for case_id, data in statistics.items():

            print(
                f"{case_id}: "
                f"{data['total_verified']} verified | "
                f"{data['successful']} successful | "
                f"{data['failed']} failed | "
                f"{data['success_rate']}% success"
            )

    print()
    print("Learned Evidence Patterns")
    print("-" * 60)

    patterns = result[
        "patterns"
    ]

    if not patterns:

        print(
            "No recurring verified patterns found."
        )

    else:

        for pattern in patterns[:10]:

            print(
                f"- {pattern['pattern']} "
                f"({pattern['occurrences']} occurrences)"
            )

    print()
    print(
        "Learning database:"
    )

    print(
        LEARNING_DATABASE
    )


def test():

    print("=" * 50)
    print("NetSage AI Phase 9 Learning Engine")
    print("=" * 50)

    result = rebuild_learning_model()

    print_learning_summary(
        result
    )

    print()
    print("=" * 50)
    print(
        "Phase 9 learning engine test complete."
    )
    print("=" * 50)


if __name__ == "__main__":
    test()