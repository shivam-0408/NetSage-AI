import re


# ============================================================
# NetSage AI - Verification Engine
# Phase 5
# ============================================================


def find_interface(evidence, interface_name):
    """
    Find an interface from parsed network evidence.
    """

    for interface in evidence.get("interfaces", []):

        if interface.get("interface", "").lower() == interface_name.lower():
            return interface

    return None


def find_vlan(evidence, vlan_id):
    """
    Find a VLAN from parsed network evidence.
    """

    for vlan in evidence.get("vlans", []):

        if vlan.get("vlan_id") == vlan_id:
            return vlan

    return None


def check_ping(evidence, destination):
    """
    Check ping result for a destination IP.
    """

    for ping in evidence.get("pings", []):

        if ping.get("destination") == destination:
            return ping

    return None


def verify_subinterface(evidence, interface_name):
    """
    Verify whether a router subinterface is currently down.
    """

    interface = find_interface(evidence, interface_name)

    if not interface:

        return {
            "passed": False,
            "message": f"{interface_name} was not found in interface evidence."
        }

    status = interface.get("status", "").lower()
    protocol = interface.get("protocol", "").lower()

    if status == "administratively down":

        return {
            "passed": True,
            "message": (
                f"{interface_name} is administratively down, "
                "which supports the recommended no shutdown command."
            )
        }

    if status == "up" and protocol == "up":

        return {
            "passed": False,
            "message": (
                f"{interface_name} is already up/up. "
                "The proposed no shutdown fix may not be necessary."
            )
        }

    return {
        "passed": False,
        "message": (
            f"{interface_name} status is {status}/{protocol}. "
            "Evidence does not clearly confirm an administratively shut interface."
        )
    }


def verify_vlan(evidence, vlan_id):
    """
    Verify that the required VLAN exists and is active.
    """

    vlan = find_vlan(evidence, vlan_id)

    if not vlan:

        return {
            "passed": False,
            "message": f"VLAN {vlan_id} was not found."
        }

    status = vlan.get("status", "").lower()

    if status == "active":

        return {
            "passed": True,
            "message": f"VLAN {vlan_id} exists and is active."
        }

    return {
        "passed": False,
        "message": f"VLAN {vlan_id} exists but status is {status}."
    }


def verify_trunk(evidence, vlan_id):
    """
    Verify that the trunk is active and carries the required VLAN.
    """

    trunk = evidence.get("trunk", {})

    if not trunk.get("is_trunk"):

        return {
            "passed": False,
            "message": "No active trunk was detected."
        }

    allowed = str(trunk.get("allowed_vlans", ""))

    active = str(trunk.get("active_vlans", ""))

    forwarding = str(trunk.get("forwarding_vlans", ""))

    vlan_text = str(vlan_id)

    allowed_ok = (
        vlan_text in allowed
        or "1-1005" in allowed
        or allowed == ""
    )

    active_ok = vlan_text in active if active else True

    forwarding_ok = (
        vlan_text in forwarding
        if forwarding
        else True
    )

    if allowed_ok and active_ok and forwarding_ok:

        return {
            "passed": True,
            "message": (
                f"Trunk is active and VLAN {vlan_id} "
                "appears to be permitted/active."
            )
        }

    return {
        "passed": False,
        "message": (
            f"Trunk exists, but VLAN {vlan_id} "
            "could not be confirmed as allowed/active/forwarding."
        )
    }


def verify_ping(evidence, destination):
    """
    Verify whether the destination is currently reachable.
    """

    ping = check_ping(evidence, destination)

    if not ping:

        return {
            "passed": False,
            "message": f"No ping result found for {destination}."
        }

    status = ping.get("status")

    if status == "Success":

        return {
            "passed": True,
            "message": f"{destination} is reachable."
        }

    return {
        "passed": False,
        "message": (
            f"{destination} is currently unreachable "
            f"(status: {status})."
        )
    }


def verify_case_01(evidence):
    """
    Verification logic for:
    Inter-VLAN Routing - Router Subinterface Down
    """

    checks = []

    # --------------------------------------------------------
    # Check router subinterface
    # --------------------------------------------------------

    checks.append(
        (
            "Router subinterface",
            verify_subinterface(
                evidence,
                "GigabitEthernet0/0.30"
            )
        )
    )

    # --------------------------------------------------------
    # Check VLAN 30
    # --------------------------------------------------------

    checks.append(
        (
            "VLAN 30",
            verify_vlan(
                evidence,
                30
            )
        )
    )

    # --------------------------------------------------------
    # Check trunk
    # --------------------------------------------------------

    checks.append(
        (
            "Trunk",
            verify_trunk(
                evidence,
                30
            )
        )
    )

    # --------------------------------------------------------
    # Check destination ping
    # --------------------------------------------------------

    ping_result = check_ping(
        evidence,
        "192.168.30.10"
    )

    if ping_result:

        if ping_result.get("status") == "Host Unreachable":

            checks.append(
                (
                    "Destination reachability",
                    {
                        "passed": True,
                        "message": (
                            "192.168.30.10 is unreachable, "
                            "which is consistent with the reported fault."
                        )
                    }
                )
            )

        elif ping_result.get("status") == "Failure":

            checks.append(
                (
                    "Destination reachability",
                    {
                        "passed": True,
                        "message": (
                            "192.168.30.10 has packet loss, "
                            "which supports the reported connectivity problem."
                        )
                    }
                )
            )

        else:

            checks.append(
                (
                    "Destination reachability",
                    {
                        "passed": False,
                        "message": (
                            "Destination is already reachable."
                        )
                    }
                )
            )

    # --------------------------------------------------------
    # Calculate verification score
    # --------------------------------------------------------

    passed = 0
    total = len(checks)

    for name, result in checks:

        if result["passed"]:
            passed += 1

    if total > 0:

        score = int((passed / total) * 100)

    else:

        score = 0

    verified = score >= 75

    return {
        "case": "case_01",
        "checks": checks,
        "passed_checks": passed,
        "total_checks": total,
        "verification_score": score,
        "verified": verified
    }


def verify_recommendation(evidence, case_id):
    """
    Main verification function.
    """

    if case_id == "case_01":

        return verify_case_01(evidence)

    return {
        "case": case_id,
        "checks": [],
        "passed_checks": 0,
        "total_checks": 0,
        "verification_score": 0,
        "verified": False,
        "message": "No verification logic exists for this case yet."
    }


def display_verification(result):
    """
    Display verification result.
    """

    print()
    print("=" * 60)
    print("             NetSage AI Verification")
    print("=" * 60)

    print()

    print("Case:")
    print(result["case"])

    print()

    print(
        f"Verification Score: "
        f"{result['verification_score']}%"
    )

    print()

    print("Verification Checks")
    print("-" * 60)

    for name, check in result["checks"]:

        status = "PASS" if check["passed"] else "FAIL"

        print(
            f"[{status}] {name}"
        )

        print(
            f"       {check['message']}"
        )

    print()

    print(
        f"Passed Checks: "
        f"{result['passed_checks']}/"
        f"{result['total_checks']}"
    )

    print()

    if result["verified"]:

        print("=" * 60)
        print("              VERIFICATION PASSED")
        print("=" * 60)

        print()
        print(
            "The available network evidence supports "
            "the recommended troubleshooting action."
        )

    else:

        print("=" * 60)
        print("              VERIFICATION FAILED")
        print("=" * 60)

        print()
        print(
            "The available evidence is insufficient "
            "to safely verify the recommendation."
        )

    print()

    print("-" * 60)
    print("IMPORTANT SAFETY RULE")
    print("-" * 60)

    print(
        "NetSage AI does NOT modify network configuration."
    )

    print(
        "A human network engineer remains responsible "
        "for applying the approved configuration."
    )

    print()
    print("=" * 60)


# ============================================================
# TEST MODE
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("                    NetSage AI")
    print("              Verification Engine")
    print("                    Phase 5")
    print("=" * 60)

    print()
    print("Verification engine loaded successfully.")
    print()