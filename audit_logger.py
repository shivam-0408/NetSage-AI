import json
import os
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)

LOG_FILE = os.path.join(
    DATA_DIR,
    "responsible_ai_log.json"
)


def ensure_data_directory():

    os.makedirs(
        DATA_DIR,
        exist_ok=True
    )


def create_audit_record(
    case_id,
    title,
    score,
    root_cause,
    evidence,
    recommended_fix,
    verification,
    human_reviewed,
    approved,
    verification_score,
    verified
):

    return {
        "timestamp": datetime.now().isoformat(),

        "case_id": case_id,

        "title": title,

        "diagnosis": {
            "score": score,
            "root_cause": root_cause,
            "evidence": evidence
        },

        "recommendation": {
            "commands": recommended_fix
        },

        "human_review": {
            "reviewed": human_reviewed,
            "approved": approved
        },

        "verification": {
            "score": verification_score,
            "verified": verified,
            "checks": verification
        },

        "safety": {
            "automatic_configuration_applied": False
        }
    }


def save_audit_record(record):

    ensure_data_directory()

    records = []

    if os.path.exists(LOG_FILE):

        try:

            with open(
                LOG_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                records = json.load(file)

        except (
            json.JSONDecodeError,
            FileNotFoundError
        ):

            records = []

    records.append(record)

    with open(
        LOG_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            records,
            file,
            indent=4
        )


def load_audit_records():

    ensure_data_directory()

    if not os.path.exists(LOG_FILE):

        return []

    try:

        with open(
            LOG_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except (
        json.JSONDecodeError,
        FileNotFoundError
    ):

        return []


if __name__ == "__main__":

    records = load_audit_records()

    print("========================================")
    print("       NetSage AI Audit Logger")
    print("========================================")

    print()

    print(
        f"Audit records: {len(records)}"
    )

    print()

    print(
        f"Log file: {LOG_FILE}"
    )