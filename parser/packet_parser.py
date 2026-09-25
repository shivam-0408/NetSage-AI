import re


# ============================================================
# NetSage AI - Packet Tracer Output Parser
# Phase 3
# ============================================================


def parse_ping(output):
    """Parse ping results from Packet Tracer output."""

    results = []

    # Find every ping command
    matches = list(re.finditer(
        r"(?:C:\\>\s*)?ping\s+(\d+\.\d+\.\d+\.\d+)",
        output,
        re.IGNORECASE
    ))

    for i, match in enumerate(matches):

        destination = match.group(1)

        # Current ping block ends at the next ping command
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(output)

        block = output[start:end]

        result = {
            "type": "ping",
            "destination": destination,
            "sent": None,
            "received": None,
            "lost": None,
            "loss_percentage": None,
            "status": "Unknown"
        }

        # ----------------------------------------------------
        # Packet statistics
        # ----------------------------------------------------

        stats = re.search(
            r"Packets:\s*Sent\s*=\s*(\d+),\s*"
            r"Received\s*=\s*(\d+),\s*"
            r"Lost\s*=\s*(\d+)",
            block,
            re.IGNORECASE
        )

        if stats:

            result["sent"] = int(stats.group(1))
            result["received"] = int(stats.group(2))
            result["lost"] = int(stats.group(3))

        # ----------------------------------------------------
        # Packet loss
        # ----------------------------------------------------

        loss = re.search(
            r"\((\d+)%\s*loss\)",
            block,
            re.IGNORECASE
        )

        if loss:

            result["loss_percentage"] = int(loss.group(1))

            if result["loss_percentage"] == 0:
                result["status"] = "Success"
            else:
                result["status"] = "Failure"

        # ----------------------------------------------------
        # Host unreachable
        # ----------------------------------------------------

        if re.search(
            r"Destination host unreachable",
            block,
            re.IGNORECASE
        ):
            result["status"] = "Host Unreachable"

        # ----------------------------------------------------
        # Timeout
        # ----------------------------------------------------

        elif re.search(
            r"Request timed out",
            block,
            re.IGNORECASE
        ):
            result["status"] = "Timeout"

        # ----------------------------------------------------
        # If received = sent and no loss was found
        # ----------------------------------------------------

        if (
            result["sent"] is not None
            and result["received"] is not None
            and result["received"] == result["sent"]
            and result["status"] == "Unknown"
        ):
            result["loss_percentage"] = 0
            result["status"] = "Success"

        results.append(result)

    return results


def parse_interface_brief(output):
    """Parse Cisco show ip interface brief."""

    interfaces = []

    for line in output.splitlines():

        line = line.strip()

        if not line:
            continue

        if line.lower().startswith("interface"):
            continue

        if line.startswith("----"):
            continue

        # Cisco format:
        #
        # Interface              IP-Address      OK? Method Status                Protocol
        # GigabitEthernet0/0     unassigned      YES unset  up                    up
        #
        match = re.match(
            r"^(\S+)\s+"
            r"(\d+\.\d+\.\d+\.\d+|unassigned)\s+"
            r"(YES|NO)\s+"
            r"(\S+)\s+"
            r"(administratively down|up|down)\s+"
            r"(up|down)$",
            line,
            re.IGNORECASE
        )

        if match:

            interfaces.append({
                "interface": match.group(1),
                "ip_address": match.group(2),
                "status": match.group(5),
                "protocol": match.group(6)
            })

    return interfaces


def parse_vlan_brief(output):
    """Parse Cisco show vlan brief."""

    vlans = []

    for line in output.splitlines():

        line = line.strip()

        if not line:
            continue

        # Example:
        #
        # 10   USERS   active   Fa0/1
        # 30   SERVERS active   Fa0/2
        #
        match = re.match(
            r"^(\d+)\s+"
            r"(.+?)\s+"
            r"(active|act/lshut|suspended)\s*"
            r"(.*)$",
            line,
            re.IGNORECASE
        )

        if match:

            vlans.append({
                "vlan_id": int(match.group(1)),
                "name": match.group(2).strip(),
                "status": match.group(3).strip(),
                "ports": match.group(4).strip()
            })

    return vlans


def parse_trunk(output):
    """Parse Cisco show interfaces trunk."""

    result = {
        "is_trunk": False,
        "ports": [],
        "allowed_vlans": "",
        "active_vlans": "",
        "forwarding_vlans": ""
    }

    text = output.lower()

    # --------------------------------------------------------
    # Detect trunk
    # --------------------------------------------------------

    if "trunking" in text:
        result["is_trunk"] = True

    # --------------------------------------------------------
    # Detect trunk ports
    # --------------------------------------------------------

    for line in output.splitlines():

        line = line.strip()

        # Example:
        #
        # Gig0/1      on      802.1q      trunking      1
        #
        match = re.match(
            r"^(GigabitEthernet\S+|Gig\d+/\d+|"
            r"FastEthernet\S+|Fa\d+/\d+)"
            r"\s+\S+\s+802\.1q\s+trunking",
            line,
            re.IGNORECASE
        )

        if match:

            port = match.group(1)

            if port not in result["ports"]:
                result["ports"].append(port)

    # --------------------------------------------------------
    # Allowed VLANs
    # --------------------------------------------------------

    allowed_match = re.search(
        r"Vlans allowed on trunk\s*\n"
        r"\s*\S+\s+([0-9,\-]+)",
        output,
        re.IGNORECASE
    )

    if allowed_match:
        result["allowed_vlans"] = allowed_match.group(1).strip()

    # --------------------------------------------------------
    # Active VLANs
    # --------------------------------------------------------

    active_match = re.search(
        r"Vlans allowed and active in management domain\s*\n"
        r"\s*\S+\s+([0-9,\-]+)",
        output,
        re.IGNORECASE
    )

    if active_match:
        result["active_vlans"] = active_match.group(1).strip()

    # --------------------------------------------------------
    # Forwarding VLANs
    # --------------------------------------------------------

    forwarding_match = re.search(
        r"Vlans in spanning tree forwarding state and not pruned\s*\n"
        r"\s*\S+\s+([0-9,\-]+)",
        output,
        re.IGNORECASE
    )

    if forwarding_match:
        result["forwarding_vlans"] = forwarding_match.group(1).strip()

    return result


def detect_fault_indicators(output):
    """Detect important network fault indicators."""

    indicators = []

    text = output.lower()

    # --------------------------------------------------------
    # Administrative shutdown
    # --------------------------------------------------------

    if "administratively down" in text:
        indicators.append(
            "Interface administratively down"
        )

    # --------------------------------------------------------
    # Down / Down
    # --------------------------------------------------------

    if re.search(r"\bdown\s+down\b", text):
        indicators.append(
            "Interface status/protocol down"
        )

    # --------------------------------------------------------
    # Packet loss
    # --------------------------------------------------------

    if "100% loss" in text:
        indicators.append(
            "100% packet loss"
        )

    # --------------------------------------------------------
    # Host unreachable
    # --------------------------------------------------------

    if "destination host unreachable" in text:
        indicators.append(
            "Destination host unreachable"
        )

    # --------------------------------------------------------
    # Timeout
    # --------------------------------------------------------

    if "request timed out" in text:
        indicators.append(
            "Request timeout"
        )

    # --------------------------------------------------------
    # Trunk
    # --------------------------------------------------------

    if "trunking" in text:
        indicators.append(
            "Trunk is active"
        )

    # --------------------------------------------------------
    # 802.1Q
    # --------------------------------------------------------

    if "802.1q" in text:
        indicators.append(
            "802.1Q encapsulation detected"
        )

    return indicators


def parse_output(output):
    """
    Main parser function.

    Converts raw Packet Tracer output into
    structured network evidence.
    """

    result = {
        "pings": [],
        "interfaces": [],
        "vlans": [],
        "trunk": {},
        "fault_indicators": []
    }

    # --------------------------------------------------------
    # Ping
    # --------------------------------------------------------

    result["pings"] = parse_ping(output)

    # --------------------------------------------------------
    # Interface
    # --------------------------------------------------------

    if "show ip interface brief" in output.lower():

        result["interfaces"] = parse_interface_brief(output)

    # --------------------------------------------------------
    # VLAN
    # --------------------------------------------------------

    if "show vlan brief" in output.lower():

        result["vlans"] = parse_vlan_brief(output)

    # --------------------------------------------------------
    # Trunk
    # --------------------------------------------------------

    if "show interfaces trunk" in output.lower():

        result["trunk"] = parse_trunk(output)

    # --------------------------------------------------------
    # Fault indicators
    # --------------------------------------------------------

    result["fault_indicators"] = detect_fault_indicators(
        output
    )

    return result


def display_result(result):

    print()
    print("=" * 60)
    print("        NetSage AI - Parsed Network Evidence")
    print("=" * 60)

    # ========================================================
    # PING RESULTS
    # ========================================================

    print()
    print("PING RESULTS")
    print("-" * 60)

    if result["pings"]:

        for ping in result["pings"]:

            print(
                f"Destination : {ping['destination']}"
            )

            print(
                f"Sent        : {ping['sent']}"
            )

            print(
                f"Received    : {ping['received']}"
            )

            print(
                f"Lost        : {ping['lost']}"
            )

            print(
                f"Loss        : {ping['loss_percentage']}%"
            )

            print(
                f"Status      : {ping['status']}"
            )

            print()

    else:

        print("No ping information detected.")

    # ========================================================
    # INTERFACE RESULTS
    # ========================================================

    print("INTERFACE RESULTS")
    print("-" * 60)

    if result["interfaces"]:

        for interface in result["interfaces"]:

            print(
                f"{interface['interface']} | "
                f"IP: {interface['ip_address']} | "
                f"Status: {interface['status']} | "
                f"Protocol: {interface['protocol']}"
            )

    else:

        print("No interface information detected.")

    # ========================================================
    # VLAN RESULTS
    # ========================================================

    print()
    print("VLAN RESULTS")
    print("-" * 60)

    if result["vlans"]:

        for vlan in result["vlans"]:

            print(
                f"VLAN {vlan['vlan_id']} | "
                f"{vlan['name']} | "
                f"{vlan['status']} | "
                f"Ports: {vlan['ports']}"
            )

    else:

        print("No VLAN information detected.")

    # ========================================================
    # TRUNK RESULTS
    # ========================================================

    print()
    print("TRUNK RESULTS")
    print("-" * 60)

    trunk = result["trunk"]

    if trunk.get("is_trunk"):

        print("Trunk detected: YES")

        if trunk.get("ports"):

            print(
                "Trunk ports:",
                ", ".join(trunk["ports"])
            )

        if trunk.get("allowed_vlans"):

            print(
                "Allowed VLANs:",
                trunk["allowed_vlans"]
            )

        if trunk.get("active_vlans"):

            print(
                "Active VLANs:",
                trunk["active_vlans"]
            )

        if trunk.get("forwarding_vlans"):

            print(
                "Forwarding VLANs:",
                trunk["forwarding_vlans"]
            )

    else:

        print("Trunk information not detected.")

    # ========================================================
    # FAULT INDICATORS
    # ========================================================

    print()
    print("FAULT INDICATORS")
    print("-" * 60)

    if result["fault_indicators"]:

        for indicator in result["fault_indicators"]:

            print(f"- {indicator}")

    else:

        print(
            "No obvious fault indicators detected."
        )

    print()
    print("=" * 60)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("                    NetSage AI")
    print("              Packet Tracer Parser")
    print("=" * 60)

    print()
    print("Paste Packet Tracer output.")
    print("Type END when finished.")
    print()

    lines = []

    while True:

        try:
            line = input()

        except EOFError:
            break

        if line.strip().upper() == "END":
            break

        lines.append(line)

    raw_output = "\n".join(lines)

    if not raw_output.strip():

        print("No input provided.")
        exit()

    print()
    print("Parsing Packet Tracer output...")

    parsed_data = parse_output(raw_output)

    display_result(parsed_data)