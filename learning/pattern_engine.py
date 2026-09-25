from collections import Counter


def extract_patterns(incidents):
    """
    Extract recurring evidence patterns from verified incidents.
    """

    counter = Counter()

    for incident in incidents:

        if not incident.get("verified", False):
            continue

        evidence = incident.get(
            "supporting_evidence",
            []
        )

        if not isinstance(evidence, list):
            continue

        for item in evidence:

            if isinstance(item, str):
                counter[item] += 1

    patterns = []

    for pattern, count in counter.most_common():

        patterns.append(
            {
                "pattern": pattern,
                "occurrences": count
            }
        )

    return patterns


def find_matching_patterns(
    current_evidence,
    patterns
):
    """
    Compare current evidence against historical patterns.
    """

    if not isinstance(current_evidence, list):
        return []

    matches = []

    current_text = " ".join(
        str(item).lower()
        for item in current_evidence
    )

    for pattern in patterns:

        pattern_text = str(
            pattern.get("pattern", "")
        ).lower()

        if not pattern_text:
            continue

        if pattern_text in current_text:

            matches.append(pattern)

    return matches


def print_patterns(patterns):

    print()
    print("=" * 60)
    print("             LEARNED EVIDENCE PATTERNS")
    print("=" * 60)

    if not patterns:

        print()
        print("No recurring verified patterns found.")
        return

    print()

    for item in patterns:

        print(
            f"- {item['pattern']} "
            f"(occurrences: {item['occurrences']})"
        )