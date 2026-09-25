
import json
import re
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATASET_PATH = os.path.normpath(
    os.path.join(
        BASE_DIR,
        "..",
        "dataset",
        "troubleshooting_cases.json"
    )
)


def load_cases():
    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data["cases"]


def normalize_text(text):

    if not isinstance(text, str):
        text = str(text)

    text = text.lower()
    text = re.sub(r"[^a-z0-9.]+", " ", text)

    return text


def calculate_match_score(user_input, case):

    user_text = normalize_text(user_input)

    score = 0
    matched_evidence = []

    problem_words = normalize_text(
        case.get("problem", "")
    ).split()

    for word in problem_words:

        if len(word) > 3 and word in user_text:
            score += 1

    for symptom in case.get("symptoms", []):

        symptom_words = normalize_text(
            symptom
        ).split()

        symptom_matches = 0

        for word in symptom_words:

            if len(word) > 3 and word in user_text:
                symptom_matches += 1

        if symptom_matches >= 2:

            score += 3
            matched_evidence.append(symptom)

    for command_name, command_output in case.get(
        "show_commands",
        {}
    ).items():

        command_words = normalize_text(
            command_output
        ).split()

        command_matches = 0

        for word in command_words:

            if len(word) > 3 and word in user_text:
                command_matches += 1

        if command_matches >= 2:

            score += 4

            matched_evidence.append(
                f"Matched {command_name}"
            )

    return score, matched_evidence


def find_best_case(user_input, cases):

    best_case = None
    best_score = 0
    best_evidence = []

    for case in cases:

        score, evidence = calculate_match_score(
            user_input,
            case
        )

        if score > best_score:

            best_score = score
            best_case = case
            best_evidence = evidence

    return best_case, best_score, best_evidence


def display_result(case, score, matched_evidence):

    print()
    print("========================================")
    print("        NetSage AI Analysis")
    print("========================================")

    print()
    print("Most Likely Case:")

    print(
        f"{case['case_id']} - {case['title']}"
    )

    print()
    print(f"Confidence Score: {score}")

    print()
    print("Problem:")

    print(case["problem"])

    print()
    print("Likely Root Cause:")

    print(case["root_cause"])

    print()
    print("Matching Evidence:")

    if matched_evidence:

        for evidence in matched_evidence:
            print(f"- {evidence}")

    else:

        print("- No strong evidence matched.")

    print()
    print("Recommended Fix:")

    for command in case.get("recommended_fix", []):

        print(f"  {command}")

    print()
    print("Verification:")

    for command in case.get("verification", []):

        print(f"  {command}")

    print()
    print("Expected Result:")

    print(case["expected_result"])

    print()
    print("----------------------------------------")
    print("HUMAN REVIEW REQUIRED")
    print("----------------------------------------")

    print(
        "NetSage AI only recommends the fix.\n"
        "A human network engineer must review and approve\n"
        "the recommendation before applying any configuration."
    )

    print()
    print("========================================")


def interactive_mode(cases):

    print()
    print("========================================")
    print("          NetSage AI")
    print("   AI Network Troubleshooting Helper")
    print("========================================")

    print()
    print("Enter the network problem and available")
    print("Packet Tracer output.")
    print("You can paste multiple lines.")
    print("Type END on a new line when finished.")
    print()

    user_input_lines = []

    while True:

        line = input()

        if line.strip().upper() == "END":
            break

        user_input_lines.append(line)

    user_input = "\n".join(user_input_lines)

    if not user_input.strip():

        print()
        print("No input provided.")
        return

    print()
    print("Analyzing network problem...")

    best_case, score, matched_evidence = find_best_case(
        user_input,
        cases
    )

    if best_case is None:

        print()
        print("No matching troubleshooting case found.")

        print()
        print(
            "Try providing more information such as:\n"
            "- ping results\n"
            "- show ip interface brief\n"
            "- show vlan brief\n"
            "- show interfaces trunk\n"
            "- interface status"
        )

        return

    display_result(
        best_case,
        score,
        matched_evidence
    )


def main():

    try:

        cases = load_cases()

    except FileNotFoundError:

        print()
        print("ERROR: Troubleshooting dataset not found.")
        print()
        print("Expected dataset location:")
        print(DATASET_PATH)

        return

    except Exception as error:

        print()
        print("ERROR loading troubleshooting dataset:")
        print(error)

        return

    print("NetSage AI")
    print(
        f"Loaded {len(cases)} troubleshooting cases."
    )

    print()
    print("Available cases:")

    for case in cases:

        print(
            f"- {case['case_id']}: "
            f"{case['title']}"
        )

    interactive_mode(cases)


if __name__ == "__main__":
    main()
