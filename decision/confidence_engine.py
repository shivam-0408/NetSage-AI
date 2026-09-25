def clamp(value, minimum=0, maximum=100):
    return max(
        minimum,
        min(maximum, value)
    )


def calculate_confidence(
    match_score,
    evidence_graph,
    competing_scores=None
):
    """
    Phase 7 explainable confidence model.

    Supporting evidence increases confidence.

    Exclusion evidence increases confidence because
    it eliminates competing explanations.

    Contradicting evidence decreases confidence.

    Separation measures how strongly the selected case
    beats the next-best case.
    """

    try:
        match_score = float(match_score)
    except (TypeError, ValueError):
        match_score = 0

    # --------------------------------------------------------
    # Match strength
    # --------------------------------------------------------

    match_component = clamp(
        match_score * 4
    )

    # --------------------------------------------------------
    # Evidence
    # --------------------------------------------------------

    supporting = len(
        evidence_graph.get(
            "supporting_evidence",
            []
        )
    )

    exclusion = len(
        evidence_graph.get(
            "exclusion_evidence",
            []
        )
    )

    contradicting = len(
        evidence_graph.get(
            "contradicting_evidence",
            []
        )
    )

    support_score = supporting * 15

    exclusion_score = exclusion * 8

    contradiction_penalty = (
        contradicting * 15
    )

    evidence_strength = clamp(
        support_score
        +
        exclusion_score
        -
        contradiction_penalty
    )

    # --------------------------------------------------------
    # Competing diagnosis separation
    # --------------------------------------------------------

    separation = 0

    if competing_scores:

        try:

            scores = sorted(
                [
                    float(score)
                    for score in competing_scores
                ],
                reverse=True
            )

            if len(scores) >= 2:

                highest = scores[0]
                second = scores[1]

                if highest > 0:

                    separation = (
                        (
                            highest - second
                        )
                        /
                        highest
                    ) * 100

        except (
            TypeError,
            ValueError
        ):

            separation = 0

    # --------------------------------------------------------
    # Overall confidence
    # --------------------------------------------------------

    overall = (
        match_component * 0.50
        +
        evidence_strength * 0.35
        +
        separation * 0.15
    )

    overall -= (
        contradiction_penalty * 0.25
    )

    overall = clamp(
        round(overall)
    )

    return {
        "overall_confidence": overall,

        "match_component": round(
            match_component
        ),

        "evidence_strength": round(
            evidence_strength
        ),

        "diagnostic_separation": round(
            separation
        ),

        "contradiction_penalty": round(
            contradiction_penalty
        ),

        "supporting_evidence_count": supporting,

        "exclusion_evidence_count": exclusion,

        "contradicting_evidence_count": contradicting,
    }


def confidence_label(score):

    try:
        score = float(score)
    except (
        TypeError,
        ValueError
    ):
        return "UNKNOWN"

    if score >= 90:
        return "VERY HIGH"

    if score >= 75:
        return "HIGH"

    if score >= 60:
        return "MODERATE"

    if score >= 40:
        return "LOW"

    return "VERY LOW"


def explain_confidence(result):

    score = result.get(
        "overall_confidence",
        0
    )

    return (
        f"Overall Confidence: "
        f"{score}% "
        f"({confidence_label(score)})\n"

        f"Match Strength: "
        f"{result.get('match_component', 0)}%\n"

        f"Evidence Strength: "
        f"{result.get('evidence_strength', 0)}%\n"

        f"Diagnostic Separation: "
        f"{result.get('diagnostic_separation', 0)}%\n"

        f"Supporting Evidence: "
        f"{result.get('supporting_evidence_count', 0)}\n"

        f"Exclusion Evidence: "
        f"{result.get('exclusion_evidence_count', 0)}\n"

        f"Contradicting Evidence: "
        f"{result.get('contradicting_evidence_count', 0)}"
    )


if __name__ == "__main__":

    print("=" * 60)
    print("NetSage AI Confidence Engine")
    print("=" * 60)

    demo_graph = {
        "supporting_evidence": [
            "100% packet loss",
            "Destination unreachable",
            "Subinterface administratively down"
        ],

        "exclusion_evidence": [
            "VLAN active",
            "Trunk active",
            "VLAN permitted"
        ],

        "contradicting_evidence": []
    }

    result = calculate_confidence(
        23,
        demo_graph,
        [23, 17, 15]
    )

    print()
    print(
        explain_confidence(result)
    )

    print()
    print(
        "Confidence engine test complete."
    )