"""
Static ManagedObjects along with default Definitions used at database build

See /app/models/aci/managed_objects for expected format.  
"""

STATIC_MANAGED_OBJECTS = [

    #{
    #    "classname": "acls",
    #    "description": "pseudo class representing concrete ACLs. This MO collects and analyzes actrlRule and actrlEntry objects",
    #    "analyzer": "acls",
    #    "pseudo": True,
    #},
    #{
    #    "classname": "actrlRsToCopyDestGrp",
    #    "description": "ACL relationship to copy service group",
    #},
    #{
    #    "classname": "actrlRsToRedirDestGrp",
    #    "description": "ACL relationship to redirect group",
    #},
    {
        "classname": "arpAdjEp",
        "description": "ARP adjacency",
        "remap": ['all'],
        "attributes": [
            {
                "name": "ifId",
                "remap": ['all'],
            },
            {
                "name": "physIfId",
                "remap": ['all'],
            },
        ],
    },
    {
        "classname": "bgpDTEp",
        "description": "BGP discovered tunnel endpoint",
    },
    {
        "classname": "bgpDom",
        "description": "The object that represents all the BGP domain (VRF) information.",
    },
    {
        "classname": "bgpInst",
        "description": "BGP Instance",
    },
    {
        "classname": "bgpPeer",
        "description": "BGP Peer",
        "attributes": [
            {
                "name": "srcIf",
                "remap": ['all'],
            },
        ],
    },
    {
        "classname": "bgpPeerAfEntry",
        "description": "The operational status information for a BGP peer address family. Each address family maintains a separate BGP database, which allows you to configure BGP policy on per-address family basis.",
        "attributes": [
            {
                "name": "memAccPaths",
                "labels": ['dynamic'],
            },
            {
                "name": "peerTblVer",
                "labels": ["statistic"]
            },
            {
                "name": "tblVer",
                "labels": ["statistic"]
            },
        ],
    },
    {
        "classname": "bgpPeerEntry",
        "description": "The BGP peer status specifies the status of a relationship between BGP speakers. A BGP peer is a BGP speaker that has an active TCP connection to another BGP speaker.",
        "attributes": [
            {
                "name": "remotePort",
                "labels": ['dynamic'],
            },
            {
                "name": "fd",
                "labels": ['dynamic'],
            },
            {
                "name": "connIf",
                "remap": ['all'],
            },
            {
                "name": "peerIdx",
                "labels": ['dynamic'],
            },
            {
                "name": "localPort",
                "labels": ['dynamic'],
            },
            {
                "name": "connAttempts",
                "labels": ["statistic"],
            },
        ],
    },
    #{
    #    "classname": "bgpRoute",
    #    "description": "BGP route table for a particular address family (IPv4 unicast and IPv6 unicast), which contains all the routes advertised by peers and also redistributed into BGP from other routing protocols. This route table is per tenant context (per VRF)",
    #},
    #{
    #    "classname": "bgpPath",
    #    "description": "BGP AS path",
    #    "severity": "info",
    #},
    {
        "classname": "cdpAdjEp",
        "description": "CDP neighbor information",
    },
    {
        "classname": "cdpIf",
        "description": "CDP information that is operated at a interface level. CDP is used to obtain protocol addresses of neighboring devices and discover the platform of those devices. CDP is also used to display information about the neighboring interfaces/devices",
    },
    {
        "classname": "cdpInst",
        "description": "The object that represents the CDP instance information. Currently only one CDP instance is supported",
    },
    {
        "classname": "coopDTEp",
        "description": "COOP discovered tunnel endpoints",
    },
    {
        "classname": "eigrpAdjEp",
        "description": "EIGRP neighbor information",
        "exclude": ['lastHelloTs'],
        "remap": ['all'],
    },
    {
        "classname": "eigrpDom",
        "description": "EIGRP domain (VRF) information",
    },
    {
        "classname": "eigrpDomAf",
        "description": "EIGRP address family domain (VRF) information",
    },
    {
        "classname": "eigrpIf",
        "description": "EIGRP enabled interface",
        "exclude": ['id'],
        "remap": ['all'],
    },
    {
        "classname": "eigrpIfAf",
        "description": "EIGRP address family interface",
        "remap": ['all'],
    },
    {
        "classname": "eigrpInst",
        "description": "EIGRP Instance",
    },
    {
        "classname": "eigrpNexthop",
        "description": "EIGRP next-hop information for a particular route",
        "exclude": ['if'],
        "remap": ['all'],
    },
    {
        "classname": "eigrpRoute",
        "description": "EIGRP route table for a particular address family (IPv4 unicast and IPv6 unicast)",
    },
    {
        "classname": "epmDTEp",
        "description": "EPM discovered tunnel endpoint",
        "labels": ['dynamic'],
    },
    {
        "classname": "endpoints",
        "description": "pseudo class representing local endpoints per-node. This MO collects and analyzes epmIpEp, epmMacEp, and epmRsMacEpToIpEpAtt objects",
        "pseudo": True,
        "analyzer": "endpoints",
        "include": ["addr","createTs","flags","ifId","modTs","pcTag","mac"],
        "attributes": [
            {
                "name": "ifId",
                "remap": ["all"],
            },
        ],
    },
    {
        "classname": "eqptCh",
        "description": "Equipment Chassis. The hardware chassis container contains chassis properties such as its role in the fabric (spine/tor) and a description of switch",
        "attributes": [
            {
                "name": "operSt",
                "severity": "warn",
            },
        ],
    },
    {
        "classname": "eqptFC",
        "description": "Equipment fabric card. The fabric card, which connects different IO cards and stores all fabric related information",
        "attributes": [
            {
                "name": "operSt",
                "severity": "warn",
            },
            {
                "name": "rdSt",
                "severity": "warn",
            },
        ],
    },
    {
        "classname": "eqptFlash",
        "description": "Equipment flash. A flash memory unit.",
        "attributes": [
            {
                "name": "operSt",
                "severity": "warn",
            },
            {
                "name": "gbb",
                "labels": ["dynamic"],
            },
            {
                "name": "lba",
                "labels": ["dynamic"],
            },
            {
                "name": "peCycles",
                "labels": ["dynamic"],
            },
            {
                "name": "tbw",
                "labels": ["dynamic"],
            },
            {
                "name": "wlc",
                "labels": ["dynamic"],
            },
        ],
    },
    {
        "classname": "eqptFt",
        "description": "Equipment fan tray",
        "attributes": [
            {
                "name": "operSt",
                "severity": "warn",
            },
        ],
    },
    {
        "classname": "eqptPsu",
        "description": "Equipment power supply unit",
        "attributes": [
            {
                "name": "operSt",
                "severity": "warn",
            },
        ],
    },
    {
        "classname": "eqptSupC",
        "description": "Equipment supervisor card",
        "attributes": [
            {
                "name": "operSt",
                "severity": "warn",
            },
            {
                "name": "rdSt",
                "severity": "warn",
            },
        ],
    },
    {
        "classname": "eqptSysC",
        "description": "Equipment system controller card",
        "attributes": [
            {
                "name": "operSt",
                "severity": "warn",
            },
            {
                "name": "rdSt",
                "severity": "warn",
            },
        ],
    },
    {
        "classname": "eqptcapacityL2RemoteUsage5min",
        "description": "Equipment capacity: remote MAC learns",
        "uri": "/api/class/eqptcapacityEntity.json?query-target=self&rsp-subtree-include=stats&rsp-subtree-class=eqptcapacityL2RemoteUsage5min",
        "include": ['remoteEpCum', 'remoteEpCapCum'],
        "severity": "info",
        "labels": ["no-key"],
    },
    {
        "classname": "eqptcapacityL2TotalUsage5min",
        "description": "Equipment capacity: total (remote + local) MAC learns",
        "uri": "/api/class/eqptcapacityEntity.json?query-target=self&rsp-subtree-include=stats&rsp-subtree-class=eqptcapacityL2TotalUsage5min",
        "include": ['totalEpCum', 'totalEpCapCum'],
        "severity": "info",
        "labels": ["no-key"],
    },
    {
        "classname": "eqptcapacityL2Usage5min",
        "description": "Equipment capacity: local MAC learns",
        "uri": "/api/class/eqptcapacityEntity.json?query-target=self&rsp-subtree-include=stats&rsp-subtree-class=eqptcapacityL2Usage5min",
        "include": ['localEpCum', 'localEpCapCum'],
        "labels": ["no-key"],
    },
    {
        "classname": "eqptcapacityL3RemoteUsage5min",
        "description": "Equipment capacity: remote IP learns",
        "uri": "/api/class/eqptcapacityEntity.json?query-target=self&rsp-subtree-include=stats&rsp-subtree-class=eqptcapacityL3RemoteUsage5min",
        "include": ['v4RemoteEpCum', 'v6RemoteEpCum'],
        "severity": "info",
        "labels": ["no-key"],
    },
    {
        "classname": "eqptcapacityL3TotalUsage5min",
        "description": "Equipment capacity: total (remote + local) IP learns",
        "uri": "/api/class/eqptcapacityEntity.json?query-target=self&rsp-subtree-include=stats&rsp-subtree-class=eqptcapacityL3TotalUsage5min",
        "include": ['v4TotalEpCum', 'v6TotalEpCum'],
        "severity": "info",
        "labels": ["no-key"],
    },
    {
        "classname": "eqptcapacityL3Usage5min",
        "description": "Equipment capacity: local IP learns",
        "uri": "/api/class/eqptcapacityEntity.json?query-target=self&rsp-subtree-include=stats&rsp-subtree-class=eqptcapacityL3Usage5min",
        "include": ['v4LocalEpCum', 'v6LocalEpCum'],
        "labels": ["no-key"],
    },
    {
        "classname": "eqptcapacityMcastUsage5min",
        "description": "Equipment capacity: multicast entries",
        "uri": "/api/class/eqptcapacityEntity.json?query-target=self&rsp-subtree-include=stats&rsp-subtree-class=eqptcapacityMcastUsage5min",
        "include": ['localEpCum', 'localEpCapCum'],
        "labels": ["no-key"],
    },
    {
        "classname": "eqptcapacityPolUsage5min",
        "description": "Equipment capacity: policy tcam usage",
        "uri": "/api/class/eqptcapacityEntity.json?query-target=self&rsp-subtree-include=stats&rsp-subtree-class=eqptcapacityPolUsage5min",
        "include": ['polUsageCum', 'polUsageCapCum'],
        "labels": ["no-key"],
    },
    {
        "classname": "eqptcapacityVlanUsage5min",
        "description": "Equipment capacity: vlan usage",
        "uri": "/api/class/eqptcapacityEntity.json?query-target=self&rsp-subtree-include=stats&rsp-subtree-class=eqptcapacityVlanUsage5min",
        "include": ['totalCum', 'totalCapCum'],
        "labels": ["no-key"],
    },
    {
        "classname": "eqptdiagSubj",
        "description": "Equipment Diagnostics",
        "include": ['operSt', 'lastExecFailTs'],
        "attributes": [
            {
                "name": "numExecFail",
                "labels": ['statistic'],
            },
            {
                "name": "numExecConsFail",
                "labels": ['statistic'],
            },
        ],
    },
    {
        "classname": "ethpmFcot",
        "description": "Transceiver information",
        "include": ['isFcotPresent', 'state', 'status', 'flags', 'type', 'typeName', 'guiName', 'guiPN', 'guiRev', 'guiSN', 'guiCiscoEID', 'guiCiscoPID', 'guiCiscoPN'],
    },
    {
        "classname": "ethpmAggrIf",
        "description":"port-channel interface runtime information",
        "exclude": ["bundleBupId","bundleIndex", "iod", "userCfgdFlags","operBitset"],
        "remap": ['agg'],
        "attributes": [
            {
                "name": "activeMbrs",
                "labels": ["list"],
            },
            {
                "name": "accessVlan",
                "remap": ["vlan"],
            },
            {
                "name": "allowedVlans",
                "labels": ["list-expand"],
                "remap": ["vlan"],
            },
            {
                "name": "cfgAccessVlan",
                "remap": ["vlan"],
            },
            {
                "name": "cfgNativeVlan",
                "remap": ["vlan"],
            },
            {
                "name": "errVlans",
                "remap": ["vlan"],
            },
            {
                "name": "nativeVlan",
                "remap": ["vlan"],
            },
            {
                "name": "operVlans",
                "labels": ["list-expand"],
                "remap": ["vlan"],
            },
            {
                "name": "primaryVlan",
                "remap": ["vlan"],
            },
            {
                "name": "hwBdId",
                "labels": ["dynamic"],
            },
            {
                "name": "hwResourceId",
                "labels": ["dynamic"],
            },
            {
                "name": "lastLinkStChg",
                "labels": ["timestamp"],
            },
        ],
    },
    {
        "classname": "ethpmPhysIf",
        "description":"physical interface runtime information",
        "exclude": ["iod", "userCfgdFlags", "operBitset"],
        "attributes": [
            {
                "name": "accessVlan",
                "remap": ["vlan"],
            },
            {
                "name": "allowedVlans",
                "labels": ["list-expand"],
                "remap": ["vlan"],
            },
            {
                "name": "bundleBupId",
                "labels": ["dynamic"],
            },
            {
                "name": "bundleIndex",
                "remap": ["agg"],
            },
            {
                "name": "cfgAccessVlan",
                "remap": ["vlan"],
            },
            {
                "name": "cfgNativeVlan",
                "remap": ["vlan"],
            },
            {
                "name": "errVlans",
                "labels": ["list-expand"],
                "remap": ["vlan"],
            },
            {
                "name": "nativeVlan",
                "remap": ["vlan"],
            },
            {
                "name": "operVlans",
                "labels": ["list-expand"],
                "remap": ["vlan"],
            },
            {
                "name": "primaryVlan",
                "remap": ["vlan"],
            },
            {
                "name": "hwBdId",
                "labels": ["dynamic"],
            },
            {
                "name": "hwResourceId",
                "labels": ["dynamic"],
            },
            {
                "name": "lastLinkStChg",
                "labels": ["timestamp"],
            },
        ],
    },
    {
        "classname": "ethpmEncRtdIf",
        "description": "Encapsulated routed interface (sub-interface) runtime information",
        "remap": ['encrtd'],
        "include": ["operBitset", "operMtu", "operSt", "operStQual"],
    },
    {
        "classname": "ethpmLbRtdIf",
        "description": "Loopback interface runtime information",
        "remap": ['loopback'],
        "include": ["operSt", "operStQual", "status"],
    },
    {
        "classname": "fabricNode",
        "description": "Fabric node details",
    },
    {
        "classname": "faultInst",
        "description": "Fault instance. Contains detailed information of a fault. This object is attached as a child of the object on which the fault condition occurred. One instance object is created for each fault condition of the parent object. A fault instance object is identified by a fault code",
    },
    {
        "classname": "firmwareCtrlrRunning",
        "description": "Information about each controller firmware that is running",
    },
    {
        "classname": "firmwareRunning",
        "description": "Information about switch firmware running on a node",
    },
    {
        "classname": "ipv4Addr",
        "description": "Ipv4 address",
        "remap": ['all'],
    },
    {
        "classname": "ipv4If",
        "description": "IPv4 interface. A container for IPv4 information that is operated at an interface level",
        "exclude": ['id'],
        "remap": ['all'],
    },
    {
        "classname": "ipv4Nexthop",
        "description": "IPv4 next hop information for ipv4Route object",
        "remap": ['all'],
        "attributes": [
            {
                "name": "nhIf",
                "remap": ['all'],
            },
        ],
    },
    {
        "classname": "ipv4Route",
        "description": "IPv4 route definition",
    },
    {
        "classname": "ipv6Addr",
        "description": "IPv6 address",
        "remap": ['all'],
    },
    {
        "classname": "ipv6If",
        "description": "IPv6 interface. A container for IPv6 information that is operated at an interface level",
        "exclude": ['id'],
        "remap": ['all'],
    },
    {
        "classname": "ipv6Nexthop",
        "description": "IPv6 next hop information for ipv6Route object",
        "remap": ['all'],
        "attributes": [
            {
                "name": "nhIf",
                "remap": ['all'],
            },
        ],
    },
    {
        "classname": "ipv6Route",
        "description": "IPv6 route definition",
    },
    {
        "classname": "isisAdjEp",
        "description": "ISIS adjacency neighbor endpoint is a managed object that captures ISIS adjacency specific information such as peer system identifier and peer circuit identifier",
        "remap": ['encrtd'],
    },
    {
        "classname": "isisDTEp",
        "description": "ISIS discovered tunnel endpoint",
    },
    {
        "classname": "isisDom",
        "description": "ISIS domain (vrf) information",
        "severity": "info",
        "attributes": [
            {
                "name": "lspRefreshed",
                "labels": ["statistic"],
            },
            {
                "name": "lspSourced",
                "labels": ["statistic"],
            },
            {
                "name": "lspPurged",
                "labels": ["statistic"],
            },
            {
                "name": "fastCsnps",
                "labels": ["statistic"],
            },
            {
                "name": "fastLsps",
                "labels": ["statistic"],
            },
            {
                "name": "spfCalculated",
                "labels": ["statistic"],
            },
            {
                "name": "contextId",
                "labels": ["dynamic"],
            },
        ],
    },
    {
        "classname": "isisFmcastTree",
        "description": "ISIS Fabric Multicast(ftag) tree element is a manged object that captures ISIS fabric wide multicast tree membership information.",
        "severity": "info",
        "attributes": [
            {
                "name": "rootPort",
                "remap": ['encrtd'],
            },
        ],
    },
    {
        "classname": "isisInst",
        "description": "ISIS instance",
        "severity": "info",
    },
    {
        "classname": "isisNexthop",
        "description": "ISIS nexthop for isisRoute objects",
        "exclude": ['if'],
        "remap": ['all'],
        "severity": "info",
        "attributes": [
            {
                "name": "nhIf",
                "remap": ['all'],
            },
        ],
    },
    {
        "classname": "isisOifListLeaf",
        "description": "ISIS outgoing interface list on the leaf switch",
        "severity": "info",
        "attributes": [
            {
                "name": "oifList",
                "remap": ['all'],
                "labels": ["list"],
            },
        ],
    },
    {
        "classname": "isisOifListSpine",
        "description": "ISIS outgoing interface list on the spine switch",
        "severity": "info",
        "attributes": [
            {
                "name": "oifList",
                "remap": ['all'],
                "labels": ["list"],
            },
        ],
    },

    {
        "classname": "isisRoute",
        "description": "ISIS route is a managed object that captures the routing information learned through ISIS protocol",
    },
    {
        "classname": "l1PhysIf",
        "description": "Layer1 physical interface",
    },
    {
        "classname": "l2BD",
        "description": "Layer 2 Bridge-domain identifies the boundary of a tenant's bridged/layer2 traffic.",
        "attributes": [
            {
                "name": "hwResourceId",
                "labels": ['dynamic'],
            },
            {
                "name": "hwId",
                "labels": ['dynamic'],
            },
            {
                "name": "id",
                "labels": ['dynamic'],
            },
        ],
    },
    {
        "classname": "l3Ctx",
        "description": "Tenant context information is equivalent to a virtual routing and forwarding (VRF) instance created for the tenant's L3 network. Similar to a VRF in traditional Cisco routers, the tenant context isolates the IP addresses of the tenant, allowing different tenants to have overlapping IP addresses",
        "attributes": [
            {
                "name": "secLbl",
                "labels": ['dynamic'],
            },
            {
                "name": "v4TibId",
                "labels": ['dynamic'],
            },
            {
                "name": "resourceId",
                "labels": ['dynamic'],
            },
            {
                "name": "v6TibId",
                "labels": ['dynamic'],
            },
            {
                "name": "hwResourceId",
                "labels": ['dynamic'],
            },
            {
                "name": "id",
                "labels": ['dynamic'],
            },
        ],
    },
    {
        "classname": "l3EncRtdIf",
        "description": "Layer 3 encapsulated routed interface. The routed interface corresponds to a sub-interface in Cisco routing terminology. A sub-interface is a logical L3 interface created on an underlying physical L3 port (the parent interface). Each sub-interface is associated with an 802.1Q VLAN tag. The traffic that comes on the parent interface with that tag is considered for that sub-interface. The existence of a routed interface under a VRF or infra VRF also implies that the interface belongs to that VRF. An L3 interface can only belong to one VRF at a time",
        "remap": ['encrtd'],
    },
    {
        "classname": "l3LbRtdIf",
        "description": "Layer 3 routed loopback interface",
        "remap": ['loopback'],
    },
    {
        "classname": "l3RtdIf",
        "description": "Layer 3 routed interface. A target relation to the routed concrete interface. This corresponds to a physical L3 interface. The existence of a routed concrete interface under a VRF or infra VRF also implies that interface belongs to that VRF. An L3 interface can belong to only one VRF at a time",
    },
    {
        "classname": "l3extLoopBackIfP",
        "description": "Layer 3 external loopback interface policy",
    },
    {
        "classname": "lacpAdjEp",
        "description": "LACP neighbor information",
        "attributes": [
            {
                "name": "port",
                "labels": ['dynamic'],
            },
            {
                "name": "portPrio",
                "labels": ['dynamic'],
            },
        ],
    },
    {
        "classname": "lacpIf",
        "description": "LACP information that is operated at an interface (member port of the port channel) level",
        "attributes": [
            {
                "name": "prio",
                "labels": ['dynamic'],
            },
            {
                "name": "port",
                "labels": ['dynamic'],
            },
            {
                "name": "key",
                "labels": ['dynamic'],
            },
            {
                "name": "lastActive",
                "labels": ["timestamp"],
            },
        ],
    },
    {
        "classname": "lacpInst",
        "description": "LACP instance",
    },
    {
        "classname": "lldpAdjEp",
        "description": "LLDP neighbor information",
    },
    {
        "classname": "lldpIf",
        "description": "LLDP interface",
    },
    {
        "classname": "lldpInst",
        "description": "LLDP instance",
    },
    {
        "classname": "ndAdjEp",
        "description": "Neighbor discovery (ND) adjacency",
        "remap": ['all'],
        "attributes": [
            {
                "name": "ifId",
                "remap": ['all'],
            },
            {
                "name": "physIfId",
                "remap": ['all'],
            },
        ],
    },
    {
        "classname": "ndIf",
        "description": "per interface Neighbor discovery (ND) information",
        "exclude": ['id'],
        "remap": ['all'],
    },
    {
        "classname": "ospfAdjEp",
        "description": "OSPF neighbor information",
        "remap": ['all'],
        "attributes": [
            {
                "name": "ifId",
                "labels": ['dynamic'],
            },
        ],
    },
    {
        "classname": "ospfArea",
        "description": "OSPF area information",
    },
    {
        "classname": "ospfDom",
        "description": "per OSPF domain (vrf) information",
    },
    {
        "classname": "ospfIf",
        "description": "OSPF information that is operated at an interface level.",
        "exclude": ['id'],
        "remap": ['all'],
    },
    {
        "classname": "ospfInst",
        "description": "OSPF instance",
    },
    {
        "classname": "ospfLsaRec",
        "description": "OSPF LSA records information",
        "severity": "info",
        "attributes": [
            {
                "name": "ifId",
                "remap": ['all'],
            },
            {
                "name": "seq",
                "labels": ["statistic"],
            },
            {
                "name": "cksum",
                "labels": ["dynamic"],
            },
            {
                "name": "advert",
                "labels": ["dynamic"],
            },
        ],
    },
    {
        "classname": "ospfRoute",
        "description": "OSPF route",
    },
    {
        "classname": "ospfUcNexthop",
        "description": "OSPF unicast nexthop information",
        "exclude": ['if'],
        "remap": ['all'],
        "severity": "info",
    },
    {
        "classname": "ospfv3AdjEp",
        "description": "OSPFv3 neighbor information",
        "remap": ['all'],
        "attributes": [
            {
                "name": "ifId",
                "labels": ['dynamic'],
            },
        ],
    },
    {
        "classname": "ospfv3Area",
        "description": "OSPFv3 area information",
    },
    {
        "classname": "ospfv3Dom",
        "description": "per OSPFv3 domain (vrf) information",
    },
    {
        "classname": "ospfv3If",
        "description": "OSPFv3 information that is operated at an interface level.",
        "exclude": ['id'],
        "remap": ['all'],
    },
    {
        "classname": "ospfv3Inst",
        "description": "OSPFv3 instance",
    },
    {
        "classname": "ospfv3LsaRec",
        "description": "OSPFv3 LSA records information",
        "severity": "info",
        "attributes": [
            {
                "name": "ifId",
                "remap": ['all'],
            },
        ],
    },
    {
        "classname": "ospfv3Route",
        "description": "OSPFv3 route",
    },
    {
        "classname": "ospfv3UcNexthop",
        "description": "OSPFv3 unicast nexthop information",
        "exclude": ['if'],
        "remap": ['all'],
        "severity": "info",
    },
    {
        "classname": "pcAggrIf",
        "description": "Port-channel aggregated interface, which is a collection of physical ports",
        "exclude": ["rowSt"],
        "remap": ['agg'],
        "attributes": [
            {
                "name": "lif",
                "labels": ['dynamic'],
            },
            {
                "name": "fcotChannelNumber",
                "labels": ['dynamic'],
            },
            {
                "name": "pcId",
                "labels": ['dynamic'],
            },
            {
                "name": "iod",
                "labels": ['dynamic'],
            },
            {
                "name": "id",
                "labels": ['dynamic'],
            },
            {
                "name": "ltl",
                "labels": ['dynamic'],
            },
        ],
    },
    {
        "classname": "pcAggrMbrIf",
        "description": "Port-channel member interface information which includes channeling status",
    },
    {
        "classname": "pcRsMbrIfs",
        "description": "Port-channel  source relation to Layer 1 physical ethernet interfaces",
        "remap": ['agg'],
        "attributes": [
            {
                "name": "parentSKey",
                "remap": ['agg'],
            },
        ],
    },
    {
        "classname": "rmonDot3Stats",
        "description": "802.3 (Dot3) statistic counters",
        "labels": ['statistic'],
        "remap": ['vlan', 'agg', 'encrtd'],
        "attributes": [
            {
                "name": "clearTs",
                "severity": "notice",
            },
        ],
    },
    {
        "classname": "rmonEtherStats",
        "description": "Ethernet statistic counters",
        "include": ['cRCAlignErrors', 'dropEvents', 'fragments', 'jabbers', 'undersizePkts', 'clearTs'],
        "labels": ['statistic'],
        "remap": ['vlan', 'agg', 'encrtd'],
        "attributes": [
            {
                "name": "clearTs",
                "severity": "notice",
            },
        ],
    },
    {
        "classname": "rmonIfIn",
        "description": "Interface input counters",
        "include": ['clearTs', 'discards', 'errors', 'unknownProtos'],
        "labels": ['statistic'],
        "remap": ['vlan', 'agg', 'encrtd'],
        "attributes": [
            {
                "name": "clearTs",
                "severity": "notice",
            },
        ],
    },
    {
        "classname": "rmonIfOut",
        "description": "Interface output counters",
        "include": ['clearTs', 'discards', 'errors', 'unknownProtos'],
        "labels": ['statistic'],
        "remap": ['vlan', 'agg', 'encrtd'],
        "attributes": [
            {
                "name": "clearTs",
                "severity": "notice",
            },
        ],
    },
    {
        "classname": "rmonIfStorm",
        "description": "Interface storm control drop counters",
        "labels": ['statistic'],
        "remap": ['vlan', 'agg', 'encrtd'],
        "attributes": [
            {
                "name": "clearTs",
                "severity": "notice",
            },
        ],
    },
    #{
    #    "classname": "svccopyDest",
    #    "description": "Copy destination, represents a destination to which a copy is sent",
    #},
    #{
    #    "classname": "svccopyDestGrp",
    #    "description": "Copy destination group, represents a group of analyzers/destinations",
    #},
    #{
    #    "classname": "svccopyRsCopyDestAtt",
    #    "description": "Attachment to copy destination",
    #},
    #{
    #    "classname": "svcredirDest",
    #    "description": "Redirect destination, represents a destination service ",
    #},
    #{
    #    "classname": "svcredirDestGrp",
    #    "description": "Redirect destination group, represents a service node group ",
    #},
    #{
    #    "classname": "svcredirRsDestAtt",
    #    "description": "Attachment to redirect destination",
    #},
    {
        "classname": "tunnelIf",
        "description": "Tunnel interface",
        "exclude": ["rn", "id"],
        "remap": ['tunnel'],
        "attributes": [
            {
                "name": "iod",
                "labels": ["dynamic"],
            },
        ],
    },
    {
        "classname": "uribv4Nexthop",
        "description": "Unicast RIB IPv4 nexthop",
        "remap": ['all'],
        "attributes": [
            {
                "name": "if",
                "remap": ['all'],
            },
        ],
    },
    {
        "classname": "uribv4Route",
        "description": "Unicast RIB IPv4 route",
    },
    {
        "classname": "uribv6Nexthop",
        "description": "Unicast RIB IPv6 nexthop",
        "remap": ['all'],
        "attributes": [
            {
                "name": "if",
                "remap": ['all'],
            },
        ],
    },
    {
        "classname": "uribv6Route",
        "description": "Unicast RIB IPv6 route",
    },
    {
        "classname": "vlanCktEp",
        "description": "VLAN object created for an endpoint group with an 802.1q encap",
        "attributes": [
            {
                "name": "hwId",
                "labels": ['dynamic'],
            },
            {
                "name": "id",
                "labels": ['dynamic'],
            },
        ],
    },
    {
        "classname": "vpcDom",
        "description": "VPC domain",
    },
    {
        "classname": "vpcIf",
        "description": "VPC interfaces information enables links that are physically connected to two different Fabric devices to appear as a single port channel by a third device. The third device can be a switch, server, or any other networking device that supports port channels. A vPC can provide Layer 2 multipathing, which allows you to create redundancy and increase bisectional bandwidth by enabling multiple parallel paths between nodes and allowing load balancing traffic. ",
        "key": "fabricPathDn",
        "exclude": ["dn"],
    },
    {
        "classname": "vxlanCktEp",
        "description": "VXLAN object created for an endpoint group with an vxlan encap",
        "attributes": [
            {
                "name": "hwId",
                "labels": ['dynamic'],
            },
            {
                "name": "id",
                "labels": ['dynamic'],
            },
        ],
    },


    # VMM  objects
    {
        "classname": "compCtrlr",
        "description": "Compute controller. The operational state of the VM management system controller such as a VMware vCenter, VMware vShield, or Microsoft SCVMM",
    },
    {
        "classname": "compHv",
        "description": "Compute hypervisor",
    },
    {
        "classname": "compHpNic",
        "description": "Compute hypervisor NIC. The physical interface information on the hypervisor",
    },
    {
        "classname": "compMgmtNic",
        "description": "Compute managment NIC. An endpoint or NIC used for management connectivity on the host. For example, vmk interface of a VMware vCenter",
    },
    {
        "classname": "compVm",
        "description": "Compute virtual machine",
    },
    {
        "classname": "compVNic",
        "description": "Compute vnic. The virtual network interface on the VM. ",
    },
    {
        "classname": "compRsDlPol",
        "description": "Compute relation policy.  A source relation to the common policies for the interface connected to the node. Note that this relation is an internal object.  Binds the compVNic to the hvsExtPol (portgroup)",
    },
    {
        "classname": "hvsEncap",
        "description": "Hypervisor encapsulation. Contains the encap and multicast address of the ExtPol. If this child encap exists, the ExtPol uses this encap or the encap properties of the ExtPol",
        "severity": "info",
    },
    {
        "classname": "hvsExtPol",
        "description": "Hypervisor extension policy. The extended policies, which are common policies for VM interfaces. For example, when implementing VMware, this represents the distributed virtual port group",
    },
    {
        "classname": "hvsAdj",
        "description": "hypervisor adjacency. The connectivity to an external network. ",
    },
    {
        "classname": "leqptRsLsNodeToIf",
        "description": "node connectivity to an externally unmanaged node (i.e., blade switch connection to the fabric)",
    },


]
