# ============================================================
# NetSage AI - Human Review Module
# Phase 5
# ============================================================


def human_review(diagnosis):
    """
    Ask a human network engineer to review
    the AI-generated troubleshooting recommendation.
    """

    print()
    print("=" * 60)
    print("              HUMAN REVIEW REQUIRED")
    print("=" * 60)

    print()
    print("AI Recommendation")
    print("-" * 60)

    print()

    print("Most Likely Case:")
    print(
        diagnosis.get(
            "case",
            "Unknown"
        )
    )

    print()

    print("Confidence Score:")
    print(
        str(
            diagnosis.get(
                "confidence",
                "Unknown"
            )
        ) + "%"
    )

    print()

    print("Likely Root Cause:")
    print(
        diagnosis.get(
            "root_cause",
            "Unknown"
        )
    )

    print()

    print("Recommended Fix:")
    print("-" * 60)

    fix = diagnosis.get("recommended_fix", "")

    if isinstance(fix, list):

        for command in fix:
            print("  " + command)

    else:

        print(fix)

    print()

    print("Verification:")
    print("-" * 60)

    verification = diagnosis.get(
        "verification",
        ""
    )

    if isinstance(verification, list):

        for command in verification:
            print("  " + command)

    else:

        print(verification)

    print()
    print("-" * 60)

    print("IMPORTANT:")
    print("NetSage AI will NOT automatically apply")
    print("any network configuration.")
    print()
    print("A human network engineer must approve")
    print("the recommendation first.")

    print()
    print("=" * 60)
    print("              REVIEW DECISION")
    print("=" * 60)

    while True:

        choice = input(
            "\nApprove recommendation? "
            "[Y] Approve  [N] Reject  [E] Exit: "
        ).strip().lower()

        if choice == "y":

            print()
            print("=" * 60)
            print("                  APPROVED")
            print("=" * 60)

            print()
            print(
                "Recommendation approved by "
                "human network engineer."
            )

            print()
            print(
                "NetSage AI will NOT automatically "
                "apply the configuration."
            )

            print()
            print("=" * 60)

            return {
                "reviewed": True,
                "approved": True,
                "decision": "APPROVED"
            }

        elif choice == "n":

            print()
            print("=" * 60)
            print("                  REJECTED")
            print("=" * 60)

            print()
            print(
                "Recommendation rejected by "
                "human network engineer."
            )

            print()
            print(
                "No configuration will be applied."
            )

            print()
            print("=" * 60)

            return {
                "reviewed": True,
                "approved": False,
                "decision": "REJECTED"
            }

        elif choice == "e":

            print()
            print("=" * 60)
            print("                   EXITED")
            print("=" * 60)

            print()
            print(
                "Human review cancelled."
            )

            print()
            print("=" * 60)

            return {
                "reviewed": False,
                "approved": False,
                "decision": "EXITED"
            }

        else:

            print()
            print(
                "Invalid choice."
            )

            print(
                "Please enter Y, N, or E."
            )


# ============================================================
# TEST MODE
# ============================================================

if __name__ == "__main__":

    test_diagnosis = {

        "case":
            "case_01 - Inter-VLAN Routing - "
            "Router Subinterface Down",

        "confidence":
            100,

        "root_cause":
            "GigabitEthernet0/0.30 is "
            "administratively shut down.",

        "recommended_fix": [

            "enable",
            "configure terminal",
            "interface GigabitEthernet0/0.30",
            "no shutdown",
            "end"

        ],

        "verification": [

            "show ip interface brief",
            "ping 192.168.30.10"

        ]
    }

    result = human_review(
        test_diagnosis
    )

    print()
    print("Review Result:")
    print(result)