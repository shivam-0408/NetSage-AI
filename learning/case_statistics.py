import collections


def calculate_case_statistics(incidents):
    """
    Calculate historical statistics from verified incidents.

    Only incidents with a verified outcome are included.
    """

    statistics = {}

    for incident in incidents:

        if not incident.get("verified", False):
            continue

        case_id = incident.get("case_id", "UNKNOWN")

        if case_id not in statistics:

            statistics[case_id] = {
                "case_id": case_id,
                "total_verified": 0,
                "successful": 0,
                "failed": 0,
                "approval_count": 0,
                "success_rate": 0
            }

        record = statistics[case_id]

        record["total_verified"] += 1

        if incident.get("verification_score", 0) >= 80:
            record["successful"] += 1
        else:
            record["failed"] += 1

        if incident.get("approved", False):
            record["approval_count"] += 1

        total = record["total_verified"]

        if total > 0:
            record["success_rate"] = round(
                (record["successful"] / total) * 100,
                2
            )

    return statistics


def rank_cases(statistics):
    """
    Rank historically successful troubleshooting cases.
    """

    ranked = list(statistics.values())

    ranked.sort(
        key=lambda item: (
            item.get("success_rate", 0),
            item.get("total_verified", 0)
        ),
        reverse=True
    )

    return ranked


def print_statistics(statistics):

    print()
    print("=" * 60)
    print("          HISTORICAL CASE STATISTICS")
    print("=" * 60)

    if not statistics:

        print()
        print("No verified historical incidents available.")
        return

    ranked = rank_cases(statistics)

    print()

    for index, case in enumerate(ranked, start=1):

        print(
            f"{index}. {case['case_id']} | "
            f"Verified: {case['total_verified']} | "
            f"Success: {case['success_rate']}%"
        )