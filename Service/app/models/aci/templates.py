"""
Statically defined templates that creates Definition templates for the user.  Note, a 'full' 
definition containing all objects is also created at setup
"""
TEMPLATES = {

    "Access": {
        "description": """
        This template collects access information including basic interface status, switch 
        inventory information, along with L1/L2 state.
        """,
        "objects":[
            "eqptCh",
            "eqptFC",   
            "eqptFlash",
            "eqptFt",
            "eqptPsu",
            "eqptSupC",
            "eqptSysC",
            "eqptdiagSubj",
            "l2BD",
            "vlanCktEp",
            "vxlanCktEp",
            "ethpmPhysIf",
            "pcAggrMbrIf",
            "lldpAdjEp",
            "cdpAdjEp",
        ],
    },

    "Routing": {
        "description": """
        This template collects basic information about L2/L3 local endpoint and route reachability 
        state. This includes protocol status, adjacency information, and routing information base 
        (RIB) state.
        """,
        "objects": [
            "endpoints",
            "bgpDom",
            "ospfDom",
            "eigrpDom",
            "bgpPeerEntry",
            "ospfAdjEp",
            "eigrpAdjEp",
            "uribv4Nexthop",
            "uribv4Route",
            "uribv6Nexthop",
            "uribv6Route",
        ],
    },

    "VMM": {
        "description":"""
        This template collects virtual machine manager (VMM) information focusing on hypervisor
        connectivity, inventory, and topology state.
        """,
        "objects": [
            "compCtrlr",
            "compHv",
            "compHpNic",
            "compMgmtNic",
            "compVm",
            "compVNic",
            "compRsDlPol",
            "hvsEncap",
            "hvsExtPol",
            "hvsAdj",
            "lldpAdjEp",
            "cdpAdjEp",
            "l2BD",
            "vlanCktEp",
            "vxlanCktEp",
        ],
    }
}

