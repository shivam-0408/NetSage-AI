"""
NetSage AI - Phase 12 Action Registry

Defines safe, human-reviewed remediation actions.
This module NEVER applies configuration automatically.
"""

ACTIONS = {
    "enable_router_subinterface": {
        "action_id": "enable_router_subinterface",
        "name": "Enable Router Subinterface",
        "description": (
            "Enable a router subinterface that is "
            "administratively down."
        ),
        "risk_level": "MODERATE",
        "requires_human_approval": True,
        "automatic_execution": False,
        "commands": [
            "enable",
            "configure terminal",
            "interface {interface}",
            "no shutdown",
            "end"
        ],
        "verification": [
            "show ip interface brief",
            "ping {destination}"
        ]
    },

    "investigate_unreachable_destination": {
        "action_id": "investigate_unreachable_destination",
        "name": "Investigate Unreachable Destination",
        "description": (
            "Investigate connectivity to a destination "
            "with packet loss or host unreachable errors."
        ),
        "risk_level": "LOW",
        "requires_human_approval": True,
        "automatic_execution": False,
        "commands": [
            "show ip interface brief",
            "show vlan brief",
            "show interfaces trunk"
        ],
        "verification": [
            "ping {destination}"
        ]
    },

    "review_vlan_assignment": {
        "action_id": "review_vlan_assignment",
        "name": "Review VLAN Assignment",
        "description": (
            "Review switch port VLAN membership for "
            "the affected endpoint."
        ),
        "risk_level": "LOW",
        "requires_human_approval": True,
        "automatic_execution": False,
        "commands": [
            "show vlan brief",
            "show interfaces switchport"
        ],
        "verification": [
            "show vlan brief"
        ]
    }
}


def get_action(action_id):
    return ACTIONS.get(action_id)


def list_actions():
    return list(ACTIONS.values())


def is_action_safe(action_id):
    action = get_action(action_id)

    if not action:
        return False

    return (
        action.get("requires_human_approval") is True
        and action.get("automatic_execution") is False
    )


if __name__ == "__main__":

    print("=" * 50)
    print("NetSage AI Phase 12 Action Registry")
    print("=" * 50)

    print()
    print("Registered remediation actions:")

    for action in list_actions():

        print(
            f"- {action['action_id']} | "
            f"{action['risk_level']} | "
            f"Human approval: "
            f"{action['requires_human_approval']}"
        )

    print()
    print(
        "Automatic configuration execution: FALSE"
    )