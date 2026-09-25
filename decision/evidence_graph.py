import re


def build_evidence_graph(evidence):
    """
    Phase 7 explainable evidence graph.

    Evidence is separated into:

    SUPPORTING
        Evidence directly supporting a fault.

    EXCLUSION
        Evidence that eliminates competing faults.

    CONTRADICTING
        Evidence that genuinely conflicts with a diagnosis.
    """

    graph = {
        "nodes": [],
        "relationships": [],
        "supporting_evidence": [],
        "exclusion_evidence": [],
        "contradicting_evidence": [],
    }

    # ========================================================
    # PINGS
    # ========================================================

    for ping in evidence.get("pings", []):

        destination = ping.get(
            "destination",
            "unknown"
        )

        status = str(
            ping.get("status", "unknown")
        )

        loss = ping.get(
            "loss_percentage",
            0
        )

        node_id = "ping_" + destination

        graph["nodes"].append({
            "id": node_id,
            "type": "ping",
            "destination": destination,
            "status": status,
            "loss_percentage": loss,
        })

        if str(loss) == "100" or loss == 100:

            graph["supporting_evidence"].append(
                f"Ping to {destination} has 100% packet loss."
            )

        if "unreachable" in status.lower():

            graph["supporting_evidence"].append(
                f"Destination {destination} is unreachable."
            )

        if status.lower() == "success":

            graph["exclusion_evidence"].append(
                f"Ping to {destination} succeeds."
            )

    # ========================================================
    # INTERFACES
    # ========================================================

    for interface in evidence.get(
        "interfaces",
        []
    ):

        name = interface.get(
            "interface",
            "unknown"
        )

        ip = interface.get(
            "ip_address",
            "unknown"
        )

        status = str(
            interface.get(
                "status",
                "unknown"
            )
        )

        protocol = str(
            interface.get(
                "protocol",
                "unknown"
            )
        )

        node_id = "interface_" + name

        graph["nodes"].append({
            "id": node_id,
            "type": "interface",
            "interface": name,
            "ip_address": ip,
            "status": status,
            "protocol": protocol,
        })

        # Direct fault evidence
        if "administratively down" in status.lower():

            graph["supporting_evidence"].append(
                f"{name} is administratively down."
            )

        elif (
            status.lower() != "up"
            or protocol.lower() != "up"
        ):

            graph["supporting_evidence"].append(
                f"{name} is not operationally up/up."
            )

        # Healthy interface can eliminate interface faults
        elif (
            status.lower() == "up"
            and protocol.lower() == "up"
        ):

            graph["exclusion_evidence"].append(
                f"{name} is operationally up/up."
            )

    # ========================================================
    # VLANs
    # ========================================================

    for vlan in evidence.get(
        "vlans",
        []
    ):

        vlan_id = str(
            vlan.get(
                "vlan_id",
                "unknown"
            )
        )

        name = vlan.get(
            "name",
            "unknown"
        )

        status = str(
            vlan.get(
                "status",
                "unknown"
            )
        )

        node_id = "vlan_" + vlan_id

        graph["nodes"].append({
            "id": node_id,
            "type": "vlan",
            "vlan_id": vlan_id,
            "name": name,
            "status": status,
        })

        if status.lower() == "active":

            graph["exclusion_evidence"].append(
                f"VLAN {vlan_id} ({name}) is active."
            )

        else:

            graph["supporting_evidence"].append(
                f"VLAN {vlan_id} ({name}) is not active."
            )

    # ========================================================
    # TRUNK
    # ========================================================

    trunk = evidence.get(
        "trunk",
        {}
    )

    if trunk:

        graph["nodes"].append({
            "id": "trunk",
            "type": "trunk",
            "is_trunk": trunk.get(
                "is_trunk",
                False
            ),
            "ports": trunk.get(
                "ports",
                []
            ),
            "allowed_vlans": trunk.get(
                "allowed_vlans",
                ""
            ),
            "active_vlans": trunk.get(
                "active_vlans",
                ""
            ),
        })

        if trunk.get("is_trunk"):

            graph["exclusion_evidence"].append(
                "An active trunk was detected."
            )

        allowed = str(
            trunk.get(
                "allowed_vlans",
                ""
            )
        )

        active = str(
            trunk.get(
                "active_vlans",
                ""
            )
        )

        if allowed:

            graph["exclusion_evidence"].append(
                f"Trunk allowed VLANs: {allowed}."
            )

        if active:

            graph["exclusion_evidence"].append(
                f"Trunk active VLANs: {active}."
            )

    # ========================================================
    # INTERFACE → VLAN RELATIONSHIPS
    # ========================================================

    interface_nodes = [
        node
        for node in graph["nodes"]
        if node["type"] == "interface"
    ]

    vlan_nodes = [
        node
        for node in graph["nodes"]
        if node["type"] == "vlan"
    ]

    for interface in interface_nodes:

        name = interface["interface"]

        match = re.search(
            r"\.(\d+)$",
            name
        )

        if not match:
            continue

        vlan_id = match.group(1)

        for vlan in vlan_nodes:

            if str(
                vlan["vlan_id"]
            ) == vlan_id:

                graph["relationships"].append({
                    "from": interface["id"],
                    "to": vlan["id"],
                    "type": "represents",
                })

                # Active VLAN + down subinterface:
                # this is exclusion evidence against
                # "VLAN itself is inactive".
                if (
                    "administratively down"
                    in str(
                        interface["status"]
                    ).lower()
                    and
                    str(
                        vlan["status"]
                    ).lower() == "active"
                ):

                    graph["exclusion_evidence"].append(
                        f"VLAN {vlan_id} is active while "
                        f"{name} is administratively down; "
                        "the VLAN itself is therefore less "
                        "likely to be the root cause."
                    )

    return graph


def summarize_evidence_graph(graph):

    return {
        "nodes": len(
            graph.get("nodes", [])
        ),

        "relationships": len(
            graph.get("relationships", [])
        ),

        "supporting": len(
            graph.get(
                "supporting_evidence",
                []
            )
        ),

        "exclusion": len(
            graph.get(
                "exclusion_evidence",
                []
            )
        ),

        "contradicting": len(
            graph.get(
                "contradicting_evidence",
                []
            )
        ),
    }


if __name__ == "__main__":

    print("=" * 60)
    print("NetSage AI Evidence Graph")
    print("=" * 60)

    print()
    print("Evidence graph module loaded successfully.")

    print()
    print("Evidence categories:")
    print("- Supporting evidence")
    print("- Exclusion evidence")
    print("- Contradicting evidence")