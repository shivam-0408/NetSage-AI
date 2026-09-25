import json
import os
import re

# ============================================
# NetSage AI - Local AI Troubleshooting Engine
# ============================================

BASE_DIR = r"D:\NetSage-AI"
DATASET_FILE = os.path.join(
    BASE_DIR,
    "dataset",
    "troubleshooting_cases.json"
)


def load_cases():
    try:
        with open(DATASET_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        return data.get("cases", [])

    except FileNotFoundError:
        print("ERROR: troubleshooting_cases.json not found.")
        return []

    except json.JSONDecodeError:
        print("ERROR: Invalid JSON dataset.")
        return []


def normalize(text):
    return re.sub(r"\s+", " ", text.lower())


def calculate_score(problem, case):
    """
    Compare the user's problem with the known
    troubleshooting case using keyword matching.
    """

    problem_text = normalize(problem)

    searchable_text = " ".join([
        case.get("title", ""),
        case.get("problem", ""),
        case.get("root_cause", ""),
        " ".join(case.get("symptoms", [])),
        " ".join(case.get("evidence", [])),
        str(case.get("show_commands", {}))
    ])

    searchable_text = normalize(searchable_text)

    score = 0
    matched = []

    # Important networking keywords
    keywords = [
        "vlan",
        "trunk",
        "gateway",
        "ping",
        "packet loss",
        "administratively down",
        "down down",
        "up up",
        "subinterface",
        "router",
        "switch",
        "192.168.10.1",
        "192.168.30.1",
        "192.168.30.10",
        "fa0/1",
        "fa0/2",
        "gig0/1",
        "dot1q"
    ]

    for keyword in keywords:

        if keyword in problem_text and keyword in searchable_text:
            score += 5
            matched.append(keyword)

    # Match individual words from title/problem
    problem_words = set(re.findall(r"[a-z0-9./-]+", problem_text))
    case_words = set(re.findall(r"[a-z0-9./-]+", searchable_text))

    common_words = problem_words.intersection(case_words)

    # Avoid giving too much weight to tiny/common words
    useful_words = [
        word for word in common_words
        if len(word) > 3
    ]

    score += min(len(useful_words), 15)

    return score, matched


def analyze(problem, cases):

    results = []

    for case in cases:

        score, matched = calculate_score(problem, case)

        results.append({
            "case": case,
            "score": score,
            "matched": matched
        })

    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return results


def print_analysis(result):

    case = result["case"]
    score = result["score"]
    matched = result["matched"]

    print()
    print("=" * 60)
    print("              NetSage AI Analysis")
    print("=" * 60)

    print()
    print("Most Likely Case:")
    print(
        f"{case.get('case_id')} - "
        f"{case.get('title')}"
    )

    print()
    print(f"Confidence Score: {score}")

    print()
    print("Problem:")
    print(case.get("problem", "Not available"))

    print()
    print("Likely Root Cause:")
    print(case.get("root_cause", "Not available"))

    print()
    print("Matching Evidence:")

    for evidence in case.get("evidence", []):
        print(f"- {evidence}")

    if matched:
        print()
        print("Detected Indicators:")

        for item in matched:
            print(f"- {item}")

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
    print(case.get("expected_result", "Not available"))

    print()
    print("-" * 60)
    print("HUMAN REVIEW REQUIRED")
    print("-" * 60)
    print(
        "NetSage AI only recommends a solution.\n"
        "A human network engineer must review and approve\n"
        "the recommendation before applying configuration."
    )

    print()
    print("=" * 60)


# ============================================
# MAIN PROGRAM
# ============================================

print("=" * 60)
print("                    NetSage AI")
print("          Local Network Troubleshooting AI")
print("=" * 60)

cases = load_cases()

if not cases:
    print("No troubleshooting cases loaded.")
    exit()

print()
print(f"Loaded {len(cases)} troubleshooting cases.")

print()
print("Available cases:")

for case in cases:
    print(
        f"- {case.get('case_id')}: "
        f"{case.get('title')}"
    )

print()
print("=" * 60)
print("Enter the network problem and Packet Tracer output.")
print("Paste multiple lines if necessary.")
print("Type END on a new line when finished.")
print("=" * 60)

lines = []

while True:

    line = input()

    if line.strip().upper() == "END":
        break

    lines.append(line)

problem = "\n".join(lines)

if not problem.strip():
    print("No problem entered.")
    exit()

print()
print("Analyzing network problem...")

results = analyze(problem, cases)

if not results:
    print("Unable to analyze the problem.")
    exit()

best_result = results[0]

print_analysis(best_result)